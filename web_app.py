"""Streamlit web app for the Pathology Lab Management Agent."""

from __future__ import annotations

import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from lab_management_agent.graph import build_graph

# Page config
st.set_page_config(
    page_title="PathCare Diagnostics — Lab Assistant",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "state" not in st.session_state:
    st.session_state.state = {"messages": []}

if "app" not in st.session_state:
    try:
        st.session_state.app = build_graph()
        st.session_state.graph_ready = True
    except ValueError as e:
        st.session_state.graph_ready = False
        st.session_state.graph_error = str(e)


def process_user_input(user_input: str) -> None:
    """Process user input through the LangGraph agent."""
    # Add user message to state
    st.session_state.state["messages"].append(HumanMessage(content=user_input))
    st.session_state.state["llm_tries"] = 0

    # Track message count before
    prev_msg_count = len(st.session_state.state["messages"])

    try:
        result = st.session_state.app.invoke(st.session_state.state)
    except Exception as e:
        st.error(f"Error: {e}")
        return

    # Update state
    st.session_state.state = result

    # Get new AI messages
    new_messages = result["messages"][prev_msg_count:]
    for msg in new_messages:
        if isinstance(msg, AIMessage):
            st.session_state.messages.append({"role": "assistant", "content": msg.content})


# Sidebar
with st.sidebar:
    st.markdown("### 🏥 PathCare Diagnostics")
    st.markdown(
        """
    **Available Services:**
    - Request pathology tests (lab / home / hospital)
    - Check test reports
    - Get payment receipts
    
    **Available Tests:**
    - CBC (Complete Blood Count)
    - Blood Sugar (Fasting/PP)
    - Lipid Profile
    - Thyroid Profile
    - Urine Routine
    - Liver Function Test
    - Kidney Function Test
    - Hemoglobin
    - ESR
    - Blood Grouping
    
    *Type 'quit' to reset conversation.*
    """
    )

    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.state = {"messages": []}
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# Main header
st.title("🏥 PathCare Diagnostics")
st.caption("Lab Management Assistant")

# Check if graph is ready
if not st.session_state.get("graph_ready", False):
    st.error(f"⚠️ Setup Error: {st.session_state.get('graph_error', 'Unknown error')}")
    st.info("Please add your GROQ_API_KEY to the .env file and restart the app.")
    st.stop()

# Display chat history using Streamlit's native chat_message
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type your message here... (e.g., 'I want a CBC test at lab for John Doe')")

if user_input:
    if user_input.lower() in {"quit", "exit", "q"}:
        st.session_state.messages = []
        st.session_state.state = {"messages": []}
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    else:
        # Add user message to display immediately
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Process through agent
        process_user_input(user_input)
        st.rerun()