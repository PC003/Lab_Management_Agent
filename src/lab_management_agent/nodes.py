"""Graph nodes — each function is a node in the LangGraph workflow."""

from __future__ import annotations

import json
import random
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from lab_management_agent.lab_data import (
    TEST_CATALOG,
    check_supplies,
    get_available_tests,
    get_test_results,
)
from lab_management_agent.llm import get_llm
from lab_management_agent.state import AgentState

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a Pathology Laboratory Management Assistant. You ONLY help with:
1. Requesting pathology tests (can be done at lab, home, or hospital)
2. Requesting test reports
3. Requesting payment receipts

You must REFUSE to answer anything outside these three topics. Politely say:
"I'm sorry, I can only assist with pathology test requests, report delivery, \
and payment receipts."

Available tests in our lab:
{tests}

When a user wants a test, collect:
- Which test(s) they want
- Where they want it done (lab/home/hospital)
- Patient name
- Whether they were referred by a doctor (and the doctor's name if yes)

Respond in a friendly, professional tone. Be concise.
"""


def _build_system_prompt() -> str:
    tests = get_available_tests()
    test_list = "\n".join(
        f"- {t['name']} (₹{t['price']}) — available at: {', '.join(t['locations'])}"
        for t in tests
    )
    return SYSTEM_PROMPT.format(tests=test_list)


# ---------------------------------------------------------------------------
# 1. LLM Interaction Node
# ---------------------------------------------------------------------------

def llm_interaction(state: AgentState) -> dict:
    """Main LLM node — classifies intent and collects test details.

    Handles: test requests, report requests, receipt requests.
    Refuses anything out of scope.
    Max 2 tries per turn (tracked via llm_tries).
    """
    llm = get_llm()
    messages = state["messages"]

    # Build conversation for the LLM
    sys_msg = SystemMessage(content=_build_system_prompt())
    llm_messages = [sys_msg] + list(messages)

    response = llm.invoke(llm_messages)

    # Classify intent from the conversation
    classify_prompt = [
        SystemMessage(
            content=(
                "Analyze the conversation and return ONLY a JSON object with these fields:\n"
                '  "intent": one of "test_request", "report_request", "receipt_request", "out_of_scope"\n'
                '  "test_id": the test ID if a test was requested (e.g. "CBC", "blood_sugar"), or ""\n'
                '  "test_location": "lab", "home", or "hospital" — or "" if not specified\n'
                '  "patient_name": patient name if mentioned, or ""\n'
                '  "referred_by": doctor name if mentioned, or ""\n'
                "Return ONLY valid JSON, no explanation."
            )
        ),
        *messages,
    ]
    classification = llm.invoke(classify_prompt)

    # Parse classification
    intent = "out_of_scope"
    test_info = state.get("test_info", {})
    referring_doctor = state.get("referring_doctor", "")

    try:
        # Strip markdown code fences if present
        raw = classification.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]  # remove opening fence line
            raw = raw.rsplit("```", 1)[0]  # remove closing fence
        parsed = json.loads(raw)
        intent = parsed.get("intent", "out_of_scope")

        if intent == "test_request" and parsed.get("test_id"):
            test_info = {
                "test_name": parsed["test_id"],
                "test_type": parsed.get("test_location", "lab") or "lab",
                "patient_name": parsed.get("patient_name", ""),
                "referred_by_doctor": parsed.get("referred_by", ""),
            }
            if parsed.get("referred_by"):
                referring_doctor = parsed["referred_by"]
    except (json.JSONDecodeError, KeyError):
        pass

    new_tries = state.get("llm_tries", 0) + 1

    return {
        "messages": [response],
        "user_intent": intent,
        "llm_tries": new_tries,
        "test_info": test_info,
        "referring_doctor": referring_doctor,
        "current_node": "llm_interaction",
    }


# ---------------------------------------------------------------------------
# 2. Test Confirmation Node
# ---------------------------------------------------------------------------

def test_confirmation(state: AgentState) -> dict:
    """Check if the requested test can be performed.

    Verifies:
    - Test exists in our catalog
    - Test is available at the requested location
    - Required supplies are in stock
    Max 3 tries.
    """
    test_info = state.get("test_info", {})
    test_name = test_info.get("test_name", "")
    test_location = test_info.get("test_type", "lab")
    tries = state.get("confirmation_tries", 0) + 1

    # Look up the test
    test = TEST_CATALOG.get(test_name)
    if not test:
        # Try fuzzy match — check if any test name contains the input
        for tid, tdata in TEST_CATALOG.items():
            if test_name.lower() in tdata["name"].lower() or test_name.lower() in tid.lower():
                test_name = tid
                test = tdata
                break

    if not test:
        msg = (
            f"❌ Test '{test_info.get('test_name', '')}' is not available in our catalog. "
            f"(Attempt {tries}/3)"
        )
        return {
            "messages": [AIMessage(content=msg)],
            "confirmation_tries": tries,
            "current_node": "test_confirmation",
        }

    # Check location availability
    if test_location not in test["locations"]:
        available_locs = ", ".join(test["locations"])
        msg = (
            f"⚠️ {test['name']} cannot be performed at {test_location}. "
            f"It's available at: {available_locs}. (Attempt {tries}/3)"
        )
        return {
            "messages": [AIMessage(content=msg)],
            "confirmation_tries": tries,
            "current_node": "test_confirmation",
        }

    # Check supply availability
    supply_check = check_supplies(test_name)
    if not supply_check["available"]:
        missing = ", ".join(supply_check["missing"])
        msg = (
            f"⚠️ We're currently short on some supplies for {test['name']}: {missing}. "
            f"(Attempt {tries}/3)"
        )
        if tries < 3:
            msg += " We'll check again shortly."

        return {
            "messages": [AIMessage(content=msg)],
            "confirmation_tries": tries,
            "current_node": "test_confirmation",
        }

    # All checks passed
    updated_info = {
        **test_info,
        "test_name": test_name,
        "test_possible": True,
        "total_tests_requested": 1,
        "tests_available": 1,
    }
    msg = (
        f"✅ Test Confirmed: **{test['name']}**\n"
        f"📍 Location: {test_location}\n"
        f"💰 Price: ₹{test['price']}\n"
        f"⏱️ Estimated turnaround: {test['turnaround_hours']} hours\n\n"
        "The test will now be processed in our lab."
    )
    return {
        "messages": [AIMessage(content=msg)],
        "test_info": updated_info,
        "confirmation_tries": tries,
        "current_node": "test_confirmation",
    }


# ---------------------------------------------------------------------------
# 3. Lab Test Node
# ---------------------------------------------------------------------------

def lab_test(state: AgentState) -> dict:
    """Execute the lab test and produce raw results.

    Simulates running the test. Max 2 tries.
    """
    test_info = state.get("test_info", {})
    test_name = test_info.get("test_name", "")
    tries = state.get("lab_test_tries", 0) + 1

    results = get_test_results(test_name)

    if results is None:
        # Simulate occasional test failure
        msg = (
            f"⚠️ Lab test execution encountered an issue for {test_name}. "
            f"(Attempt {tries}/2)"
        )
        return {
            "messages": [AIMessage(content=msg)],
            "lab_test_tries": tries,
            "current_node": "lab_test",
        }

    # Format results
    test_display = TEST_CATALOG.get(test_name, {}).get("name", test_name)
    result_lines = [f"🔬 **Lab Test Results — {test_display}**\n"]
    result_lines.append(f"Patient: {test_info.get('patient_name', 'N/A')}")
    result_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    for param, value in results.items():
        result_lines.append(f"  • {param}: {value}")

    result_text = "\n".join(result_lines)

    lab_results = {
        "test_name": test_name,
        "raw_results": result_text,
        "is_verified": False,
        "verification_notes": "",
    }

    msg = f"{result_text}\n\n📋 Results sent to Dr. John for verification."

    return {
        "messages": [AIMessage(content=msg)],
        "lab_results": lab_results,
        "lab_test_tries": tries,
        "current_node": "lab_test",
    }


# ---------------------------------------------------------------------------
# 4. Doctor Verification Node
# ---------------------------------------------------------------------------

def doctor_verification(state: AgentState) -> dict:
    """Dr. John (Pathology Doctor in charge) verifies the lab results.

    Simulates doctor review. If verification fails, test is sent back
    to the lab for a re-run.
    """
    lab_results = state.get("lab_results", {})
    llm = get_llm()

    # Simulate doctor verification with LLM acting as Dr. John
    verify_prompt = [
        SystemMessage(
            content=(
                "You are Dr. John, the Pathology Doctor in charge. "
                "Review the following lab test results. Check if:\n"
                "1. All values are within expected ranges or appropriately flagged\n"
                "2. Results are consistent (no contradictions)\n"
                "3. No obvious errors in the report\n\n"
                "Respond with a JSON object:\n"
                '  "verified": true or false\n'
                '  "notes": your verification notes\n'
                "Return ONLY valid JSON."
            )
        ),
        HumanMessage(content=lab_results.get("raw_results", "No results available")),
    ]

    response = llm.invoke(verify_prompt)

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0]
        result = json.loads(raw)
        verified = result.get("verified", False)
        notes = result.get("notes", "")
    except (json.JSONDecodeError, KeyError):
        # Default to verified if parsing fails
        verified = True
        notes = "Results reviewed and approved."

    updated_results = {
        **lab_results,
        "is_verified": verified,
        "verification_notes": notes,
    }

    if verified:
        msg = (
            f"✅ **Dr. John has verified the results.**\n"
            f"📝 Notes: {notes}\n\n"
            "The report is ready for delivery."
        )
    else:
        msg = (
            f"❌ **Dr. John flagged issues with the results.**\n"
            f"📝 Notes: {notes}\n\n"
            "The test will be re-run in the lab."
        )

    return {
        "messages": [AIMessage(content=msg)],
        "lab_results": updated_results,
        "current_node": "doctor_verification",
    }


# ---------------------------------------------------------------------------
# 5. Report Delivery Node
# ---------------------------------------------------------------------------

def report_delivery(state: AgentState) -> dict:
    """Deliver the verified report to the user.

    Max 2 tries for delivery.
    """
    lab_results = state.get("lab_results", {})
    test_info = state.get("test_info", {})
    tries = state.get("report_delivery_tries", 0) + 1

    # Simulate delivery (small chance of failure for demonstration)
    delivery_success = random.random() > 0.1  # 90% success rate

    if not delivery_success and tries < 2:
        msg = (
            f"⚠️ Report delivery encountered an issue. (Attempt {tries}/2)\n"
            "Retrying delivery..."
        )
        return {
            "messages": [AIMessage(content=msg)],
            "report_delivery_tries": tries,
            "report_delivered": False,
            "current_node": "report_delivery",
        }

    # Successful delivery (or second attempt — always succeeds)
    report = lab_results.get("raw_results", "")
    patient = test_info.get("patient_name", "Patient")

    msg = (
        f"📨 **Report Delivered Successfully!**\n\n"
        f"Dear {patient}, your report is on the way.\n\n"
        f"{report}\n\n"
        f"🩺 Verified by: Dr. John (Pathology In-Charge)\n"
        f"📝 Verification Notes: {lab_results.get('verification_notes', 'Approved')}\n\n"
        "Thank you for choosing our laboratory!"
    )

    return {
        "messages": [AIMessage(content=msg)],
        "report": report,
        "report_delivered": True,
        "report_delivery_tries": tries,
        "current_node": "report_delivery",
    }


# ---------------------------------------------------------------------------
# 6. Referring Doctor Notification Node
# ---------------------------------------------------------------------------

def referring_doctor_notification(state: AgentState) -> dict:
    """Notify the referring doctor about the test results.

    If the patient was referred by a doctor, that doctor receives the
    report and can request additional tests.
    """
    referring_doctor = state.get("referring_doctor", "")
    lab_results = state.get("lab_results", {})
    test_info = state.get("test_info", {})
    llm = get_llm()

    patient = test_info.get("patient_name", "the patient")
    report = lab_results.get("raw_results", "")

    # Simulate doctor reviewing and possibly ordering more tests
    doctor_prompt = [
        SystemMessage(
            content=(
                f"You are Dr. {referring_doctor}, a physician who referred {patient} "
                "for pathology tests. Review the results below.\n\n"
                "Based on the results, decide if additional tests are needed.\n"
                "Respond with JSON:\n"
                '  "recommendation": your brief recommendation\n'
                '  "additional_tests_needed": true or false\n'
                '  "suggested_tests": list of test names (from: CBC, blood_sugar, '
                "lipid_profile, thyroid_profile, urine_routine, liver_function, "
                "kidney_function, hemoglobin, ESR, blood_group) or empty list\n"
                "Return ONLY valid JSON."
            )
        ),
        HumanMessage(content=report),
    ]
    response = llm.invoke(doctor_prompt)

    more_tests = False
    recommendation = ""
    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0]
        parsed = json.loads(raw)
        recommendation = parsed.get("recommendation", "")
        more_tests = parsed.get("additional_tests_needed", False)
    except (json.JSONDecodeError, KeyError):
        recommendation = "Results reviewed. No additional tests required at this time."

    msg = (
        f"👨‍⚕️ **Dr. {referring_doctor} has been notified.**\n\n"
        f"📋 Doctor's Recommendation: {recommendation}\n"
    )
    if more_tests:
        msg += "\n🔄 Dr. has requested additional tests for this patient."

    return {
        "messages": [AIMessage(content=msg)],
        "doctor_notified": True,
        "doctor_requests_more_tests": more_tests,
        "current_node": "referring_doctor_notification",
    }


# ---------------------------------------------------------------------------
# 7. Refund Node
# ---------------------------------------------------------------------------

def refund_node(state: AgentState) -> dict:
    """Process refund when a test cannot be completed after max retries."""
    test_info = state.get("test_info", {})
    test_name = test_info.get("test_name", "")
    test = TEST_CATALOG.get(test_name, {})
    price = test.get("price", 0)

    msg = (
        f"😔 **We're sorry!**\n\n"
        f"We were unable to complete the test: {test.get('name', test_name)}.\n"
        f"A full refund of ₹{price} will be processed to your original payment method.\n"
        f"The refund should reflect within 5-7 business days.\n\n"
        "We apologize for the inconvenience. Please feel free to try again later "
        "or visit us for assistance."
    )

    return {
        "messages": [AIMessage(content=msg)],
        "needs_refund": True,
        "current_node": "refund",
    }


# ---------------------------------------------------------------------------
# 8. Receipt Generation Node
# ---------------------------------------------------------------------------

def generate_receipt(state: AgentState) -> dict:
    """Generate a payment receipt for the user."""
    test_info = state.get("test_info", {})
    test_name = test_info.get("test_name", "")
    test = TEST_CATALOG.get(test_name, {})

    if not test:
        msg = "No test has been booked yet. Please request a test first to get a receipt."
        return {
            "messages": [AIMessage(content=msg)],
            "current_node": "receipt",
        }

    price = test.get("price", 0)
    patient = test_info.get("patient_name", "N/A")

    msg = (
        f"🧾 **Payment Receipt**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  Lab: PathCare Diagnostics\n"
        f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"  Patient: {patient}\n"
        f"  Test: {test.get('name', test_name)}\n"
        f"  Location: {test_info.get('test_type', 'lab')}\n"
        f"  Amount: ₹{price}\n"
        f"  Status: Paid ✅\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Thank you for your payment!"
    )

    return {
        "messages": [AIMessage(content=msg)],
        "current_node": "receipt",
    }
