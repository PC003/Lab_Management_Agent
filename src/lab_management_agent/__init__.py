"""Pathology Laboratory Management System Agent.

A LangGraph-based agent that manages pathology lab operations including:
- Test requests (lab/home/hospital)
- Test confirmation and supply checks
- Lab test execution
- Doctor verification
- Report delivery
- Referring doctor flow
"""

from lab_management_agent.graph import build_graph


def main() -> None:
    """Entry point for the lab management agent CLI."""
    from lab_management_agent.cli import run_cli

    run_cli()
