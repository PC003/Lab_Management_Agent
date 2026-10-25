"""LangGraph workflow definition — wires nodes and edges together."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from lab_management_agent.nodes import (
    doctor_verification,
    generate_receipt,
    lab_test,
    llm_interaction,
    refund_node,
    referring_doctor_notification,
    report_delivery,
    test_confirmation,
)
from lab_management_agent.state import AgentState

# ---------------------------------------------------------------------------
# Conditional edge functions
# ---------------------------------------------------------------------------


def route_after_llm(state: AgentState) -> str:
    """Decide where to go after the LLM interaction node.

    Routes:
      - test_request with all info → test_confirmation
      - test_request missing info → END (wait for user input)
      - report_request → report_delivery  (if report is ready)
      - receipt_request → receipt
      - out_of_scope   → END (after max tries) or back to llm_interaction
    """
    intent = state.get("user_intent", "")
    llm_tries = state.get("llm_tries", 0)
    test_info = state.get("test_info", {})

    if intent == "test_request":
        # Check if we have all required info: patient_name is mandatory
        patient_name = test_info.get("patient_name", "")
        if not patient_name:
            # Missing required info — wait for user to provide it
            return END
        return "test_confirmation"
    elif intent == "report_request":
        if state.get("report_delivered"):
            return "report_delivery"
        return END  # No report ready yet
    elif intent == "receipt_request":
        return "receipt"
    else:
        # Out of scope or unclear — allow retry up to 2 times
        if llm_tries >= 2:
            return END
        return END  # Single turn — the user will send another message


def route_after_confirmation(state: AgentState) -> str:
    """Decide where to go after test confirmation.

    Routes:
      - Test possible       → lab_test
      - Max retries reached  → END (with apology)
      - Otherwise            → test_confirmation (retry)
    """
    test_info = state.get("test_info", {})
    tries = state.get("confirmation_tries", 0)

    if test_info.get("test_possible"):
        return "lab_test"

    if tries >= 3:
        return END  # Couldn't confirm after 3 tries

    # Retry confirmation
    return "test_confirmation"


def route_after_lab_test(state: AgentState) -> str:
    """Decide where to go after lab test execution.

    Routes:
      - Results obtained → doctor_verification
      - Max retries (2)  → refund
      - Otherwise        → lab_test (retry)
    """
    lab_results = state.get("lab_results", {})
    tries = state.get("lab_test_tries", 0)

    if lab_results.get("raw_results"):
        return "doctor_verification"

    if tries >= 2:
        return "refund"

    return "lab_test"


def route_after_verification(state: AgentState) -> str:
    """Decide where to go after doctor verification.

    Routes:
      - Verified     → report_delivery
      - Not verified → lab_test (redo, if within lab_test max tries)
      - Max retries  → refund
    """
    lab_results = state.get("lab_results", {})
    lab_tries = state.get("lab_test_tries", 0)

    if lab_results.get("is_verified"):
        return "report_delivery"

    # Doctor rejected — redo the test if we have tries left
    if lab_tries < 2:
        return "lab_test"

    return "refund"


def route_after_report_delivery(state: AgentState) -> str:
    """Decide where to go after report delivery.

    Routes:
      - Delivered + has referring doctor → referring_doctor_notification
      - Delivered, no referring doctor   → END
      - Delivery failed, retries left    → report_delivery (retry)
      - Delivery failed, max retries     → END (with error)
    """
    delivered = state.get("report_delivered", False)
    tries = state.get("report_delivery_tries", 0)
    referring_doctor = state.get("referring_doctor", "")

    if delivered:
        if referring_doctor:
            return "referring_doctor_notification"
        return END

    if tries >= 2:
        return END

    return "report_delivery"


def route_after_doctor_notification(state: AgentState) -> str:
    """Decide where to go after the referring doctor is notified.

    Routes:
      - Doctor requests more tests → test_confirmation (new cycle)
      - No more tests              → END
    """
    if state.get("doctor_requests_more_tests"):
        return "test_confirmation"
    return END


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------


def build_graph() -> StateGraph:
    """Build and compile the lab management LangGraph workflow.

    Node layout:
    ┌──────────────┐
    │ llm_interaction │──┬─→ test_confirmation ──→ lab_test ──→ doctor_verification
    └──────────────┘   │                                          │
                        │                                          ▼
                        │                                   report_delivery
                        │                                          │
                        ├─→ receipt                                 ▼
                        │                           referring_doctor_notification
                        └─→ END                                    │
                                                                   ▼
                                                                  END
    """
    graph = StateGraph(AgentState)

    # --- Add nodes ---
    graph.add_node("llm_interaction", llm_interaction)
    graph.add_node("test_confirmation", test_confirmation)
    graph.add_node("lab_test", lab_test)
    graph.add_node("doctor_verification", doctor_verification)
    graph.add_node("report_delivery", report_delivery)
    graph.add_node("referring_doctor_notification", referring_doctor_notification)
    graph.add_node("refund", refund_node)
    graph.add_node("receipt", generate_receipt)

    # --- Entry point ---
    graph.set_entry_point("llm_interaction")

    # --- Conditional edges ---
    graph.add_conditional_edges(
        "llm_interaction",
        route_after_llm,
        {
            "test_confirmation": "test_confirmation",
            "report_delivery": "report_delivery",
            "receipt": "receipt",
            END: END,
        },
    )

    graph.add_conditional_edges(
        "test_confirmation",
        route_after_confirmation,
        {
            "lab_test": "lab_test",
            "test_confirmation": "test_confirmation",
            END: END,
        },
    )

    graph.add_conditional_edges(
        "lab_test",
        route_after_lab_test,
        {
            "doctor_verification": "doctor_verification",
            "refund": "refund",
            "lab_test": "lab_test",
        },
    )

    graph.add_conditional_edges(
        "doctor_verification",
        route_after_verification,
        {
            "report_delivery": "report_delivery",
            "lab_test": "lab_test",
            "refund": "refund",
        },
    )

    graph.add_conditional_edges(
        "report_delivery",
        route_after_report_delivery,
        {
            "referring_doctor_notification": "referring_doctor_notification",
            "report_delivery": "report_delivery",
            END: END,
        },
    )

    graph.add_conditional_edges(
        "referring_doctor_notification",
        route_after_doctor_notification,
        {
            "test_confirmation": "test_confirmation",
            END: END,
        },
    )

    # Terminal nodes → END
    graph.add_edge("refund", END)
    graph.add_edge("receipt", END)

    return graph.compile()
