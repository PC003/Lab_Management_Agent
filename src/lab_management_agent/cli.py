"""Interactive CLI for the lab management agent."""

from __future__ import annotations

from langchain_core.messages import HumanMessage

from lab_management_agent.graph import build_graph


BANNER = """\
╔══════════════════════════════════════════════════════════════╗
║         🏥  PathCare Diagnostics — Lab Assistant  🏥        ║
╠══════════════════════════════════════════════════════════════╣
║  I can help you with:                                       ║
║    • Request a pathology test (lab / home / hospital)        ║
║    • Check your test report                                  ║
║    • Get a payment receipt                                   ║
║                                                              ║
║  Type 'quit' or 'exit' to leave.                             ║
╚══════════════════════════════════════════════════════════════╝
"""


def run_cli() -> None:
    """Run the interactive conversation loop."""
    print(BANNER)

    try:
        app = build_graph()
    except ValueError as exc:
        print(f"⚠️  Setup error: {exc}")
        return

    # Persistent state across turns
    state: dict = {"messages": []}

    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! Stay healthy. 👋")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            print("\nGoodbye! Stay healthy. 👋")
            break

        # Track message count before invocation to print only new messages
        prev_msg_count = len(state["messages"])

        # Add user message and invoke the graph
        state["messages"].append(HumanMessage(content=user_input))

        # Reset per-turn counters (LLM tries resets each turn)
        state["llm_tries"] = 0

        try:
            result = app.invoke(state)
        except Exception as exc:
            print(f"\n❌ Error: {exc}")
            continue

        # Update state with the result
        state = result

        # Print only the NEW AI messages from this turn
        new_messages = result["messages"][prev_msg_count:]
        for msg in new_messages:
            if hasattr(msg, "type") and msg.type == "ai":
                print(f"\n🤖 Assistant: {msg.content}")
