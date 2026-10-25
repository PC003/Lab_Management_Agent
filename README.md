# 🏥 Lab Management Agent

A **Pathology Laboratory Management System** built with [LangGraph](https://langchain-ai.github.io/langgraph/) that manages the complete lifecycle of pathology lab operations through an intelligent conversational agent.

## Features

- **Test Requests** — Request pathology tests (lab, home, or hospital collection)
- **Test Confirmation** — Automated supply and availability checking (max 3 retries)
- **Lab Test Execution** — Simulated test processing with result generation (max 2 retries)
- **Doctor Verification** — Dr. John (Pathology In-Charge) reviews and verifies results
- **Report Delivery** — Automated report delivery to patients (max 2 retries)
- **Referring Doctor Flow** — If referred by a doctor, the report is shared with them and they can request additional tests
- **Payment Receipts** — Generate payment receipts for completed tests
- **Refund Processing** — Automatic refund when tests cannot be completed
- **Scope Enforcement** — The agent only responds to lab-related queries

## Architecture

```
User Query → LLM Interaction → Test Confirmation → Lab Test → Doctor Verification
                  │                                                     │
                  ├→ Receipt                                    Report Delivery
                  │                                                     │
                  └→ END                                  Referring Doctor Notification
                                                                        │
                                                               (more tests?) → Test Confirmation
                                                                        │
                                                                       END
```

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- A Google API key (for Gemini LLM)

### Installation

```bash
# Clone the repo
cd Lab_Management_Agent

# Install dependencies
uv sync

# Set up your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

Get your Google API key from: https://aistudio.google.com/apikey

### Run

```bash
uv run lab-management-agent
```

## Available Tests

| Test | Price (₹) | Locations |
|------|-----------|-----------|
| Complete Blood Count (CBC) | 500 | Lab, Hospital |
| Blood Sugar (Fasting/PP) | 200 | Lab, Home, Hospital |
| Lipid Profile | 800 | Lab, Hospital |
| Thyroid Profile (T3, T4, TSH) | 1200 | Lab, Hospital |
| Urine Routine & Microscopy | 300 | Lab, Home, Hospital |
| Liver Function Test (LFT) | 900 | Lab, Hospital |
| Kidney Function Test (KFT) | 850 | Lab, Hospital |
| Hemoglobin (Hb) | 150 | Lab, Home, Hospital |
| ESR | 200 | Lab, Hospital |
| Blood Grouping & Rh Typing | 250 | Lab, Hospital |

## Project Structure

```
src/lab_management_agent/
├── __init__.py      # Package entry point
├── cli.py           # Interactive CLI loop
├── graph.py         # LangGraph workflow (nodes + edges)
├── lab_data.py      # Test catalog, supplies, sample results
├── llm.py           # LLM configuration (Google Gemini)
├── nodes.py         # Graph node implementations
└── state.py         # AgentState definition
```

## Workflow Rules

- **LLM Interaction**: Max 2 tries per turn; refuses out-of-scope questions
- **Test Confirmation**: Max 3 tries to confirm test availability
- **Lab Test**: Max 2 tries; triggers refund on failure
- **Doctor Verification**: Dr. John reviews all results; can send back to lab
- **Report Delivery**: Max 2 tries; loops back through LLM on failure
- **Referring Doctor**: Receives report and can order additional tests
