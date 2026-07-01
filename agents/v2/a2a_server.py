"""
A2A server entry point for mark-me-down.

Run with:
    uvicorn agents.v2.a2a_server:app --host 0.0.0.0 --port 8001 [--reload]

The A2A server is a SEPARATE PROCESS from the Streamlit UI (port 8501).
Both share the same Python package code but run independently.

Runtime architecture:
    Process 1 — Streamlit (port 8501):  streamlit run app.py
    Process 2 — A2A server (port 8001): uvicorn agents.v2.a2a_server:app --port 8001

Endpoints exposed automatically by to_a2a():
    GET  /.well-known/agent-card.json   — A2A AgentCard (capability description)
    POST /                              — A2A task execution endpoint

BYOK (Bring-Your-Own-Key):
    The client sends provider + api_key inside the task message JSON.
    ByokA2aExecutor extracts them and seeds session.state so the ADK workflow
    reads them via ctx.state exactly as in the Streamlit path.

Example client call:
    from a2a.client import A2AClient

    async with A2AClient(base_url="http://localhost:8001") as client:
        task = await client.send_message(
            message={
                "role": "user",
                "parts": [{
                    "text": json.dumps({
                        "raw_text": "meeting notes from today",
                        "refactor_mode": "conservative",
                        "rewrite_mode": "adaptive",
                        "include_frontmatter": False,
                        "template_selection": "auto",
                        "provider": "gemini",
                        "api_key": "YOUR_GEMINI_API_KEY"
                    })
                }]
            }
        )
"""
from __future__ import annotations

import sys
import logging

# Windows asyncio workaround — must be set before any async imports
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from google.adk.a2a.utils.agent_to_a2a import to_a2a  # noqa: E402
from agents.v2.workflow import get_refactor_workflow       # noqa: E402
from agents.v2.a2a_executor import ByokA2aExecutor        # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mark_me_down.a2a_server")

import os

# Build the Starlette ASGI app.
# to_a2a() uses the workflow for AgentCard introspection only (to auto-generate
# /.well-known/agent-card.json). The actual per-request runner is created by
# ByokA2aExecutor which injects the BYOK provider/api_key from the message body.
host = os.environ.get("A2A_HOST", "localhost")
port = int(os.environ.get("PORT", "8001"))
protocol = os.environ.get("A2A_PROTOCOL", "http")

app = to_a2a(
    get_refactor_workflow("gemini"),   # provider here only affects AgentCard metadata
    host=host,
    port=port,
    protocol=protocol,
    agent_executor_factory=lambda runner: ByokA2aExecutor(runner=runner),
)

logger.info(f"mark-me-down A2A app configured — running on {protocol}://{host}:{port}")
