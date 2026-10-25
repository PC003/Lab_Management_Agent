"""State definitions for the lab management agent graph."""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Literal

from langgraph.graph import MessagesState


@dataclass
class TestInfo:
    """Details about a requested test."""

    test_name: str = ""
    test_type: Literal["lab", "home", "hospital"] = "lab"
    patient_name: str = ""
    referred_by_doctor: str = ""  # Empty string means self-referred
    test_possible: bool = False
    partial_tests: list[str] = field(default_factory=list)
    total_tests_requested: int = 0
    tests_available: int = 0


@dataclass
class LabResult:
    """Results from lab test execution."""

    test_name: str = ""
    raw_results: str = ""
    is_verified: bool = False
    verification_notes: str = ""


class AgentState(MessagesState):
    """Complete state for the lab management graph.

    Tracks conversation flow, retry counts, test details, results,
    and referring doctor information throughout the workflow.
    """

    # --- User intent ---
    user_intent: str = ""  # "test_request" | "report_request" | "receipt_request" | "out_of_scope"

    # --- Retry counters ---
    llm_tries: int = 0
    confirmation_tries: int = 0
    lab_test_tries: int = 0
    report_delivery_tries: int = 0

    # --- Test details ---
    test_info: dict = field(default_factory=dict)

    # --- Lab results ---
    lab_results: dict = field(default_factory=dict)

    # --- Report ---
    report: str = ""
    report_delivered: bool = False

    # --- Referring doctor ---
    referring_doctor: str = ""
    doctor_notified: bool = False
    doctor_requests_more_tests: bool = False

    # --- Flow control ---
    current_node: str = ""
    needs_refund: bool = False
    error_message: str = ""
