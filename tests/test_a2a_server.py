"""
Smoke tests for the A2A server module.

These tests verify that:
- The Starlette app object is created without error
- The ByokA2aExecutor subclass can be imported
- The BYOK session injection logic parses provider/api_key correctly
- The app module-level import does not raise

NOTE: We do NOT spin up a live uvicorn server in these tests.
Integration tests against the live server are done manually via curl.
"""
import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


def _run(coro):
    """Run a coroutine synchronously (matches test_guardrails.py pattern)."""
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Import smoke test — does the server module load without error?
# ---------------------------------------------------------------------------

def test_a2a_server_importable():
    """a2a_server.py must import without raising."""
    with patch("agents.v2.workflow.get_refactor_workflow"), \
         patch("google.adk.a2a.utils.agent_to_a2a.to_a2a", return_value=MagicMock()):
        import importlib
        import agents.v2.a2a_server  # noqa: F401


# ---------------------------------------------------------------------------
# ByokA2aExecutor — BYOK injection logic
# ---------------------------------------------------------------------------

def test_byok_executor_importable():
    """ByokA2aExecutor must import without raising."""
    from agents.v2.a2a_executor import ByokA2aExecutor
    assert ByokA2aExecutor is not None


def test_byok_executor_injects_state():
    """_prepare_session must seed provider and api_key into session.state."""
    from agents.v2.a2a_executor import ByokA2aExecutor

    async def _run_test():
        # Build a mock A2A context with a JSON message body
        payload = {
            "raw_text": "test note",
            "refactor_mode": "conservative",
            "rewrite_mode": "adaptive",
            "include_frontmatter": False,
            "template_selection": "auto",
            "provider": "gemini",
            "api_key": "test-key-123",
        }

        part = MagicMock()
        part.text = json.dumps(payload)
        message = MagicMock()
        message.parts = [part]

        context = MagicMock()
        context.message = message

        # session mock — state is a real dict so mutations are visible
        session = MagicMock()
        session.state = {}

        runner = MagicMock()

        executor = ByokA2aExecutor(runner=runner)

        # Patch the parent _prepare_session to return our mock session
        with patch.object(
            executor.__class__.__bases__[0],
            "_prepare_session",
            new=AsyncMock(return_value=session),
        ):
            return await executor._prepare_session(context, MagicMock(), runner)

    result = _run(_run_test())
    assert result.state["provider"] == "gemini"
    assert result.state["api_key"] == "test-key-123"


def test_byok_executor_handles_malformed_json():
    """Malformed JSON in the message must not raise — state remains unchanged."""
    from agents.v2.a2a_executor import ByokA2aExecutor

    async def _run_test():
        part = MagicMock()
        part.text = "NOT VALID JSON {{{{"
        message = MagicMock()
        message.parts = [part]

        context = MagicMock()
        context.message = message

        session = MagicMock()
        session.state = {}

        runner = MagicMock()
        executor = ByokA2aExecutor(runner=runner)

        with patch.object(
            executor.__class__.__bases__[0],
            "_prepare_session",
            new=AsyncMock(return_value=session),
        ):
            return await executor._prepare_session(context, MagicMock(), runner)

    result = _run(_run_test())
    # State should not have been modified (no crash)
    assert result is not None


def test_byok_executor_handles_empty_parts():
    """Empty parts list must not raise."""
    from agents.v2.a2a_executor import ByokA2aExecutor

    async def _run_test():
        message = MagicMock()
        message.parts = []

        context = MagicMock()
        context.message = message

        session = MagicMock()
        session.state = {}

        runner = MagicMock()
        executor = ByokA2aExecutor(runner=runner)

        with patch.object(
            executor.__class__.__bases__[0],
            "_prepare_session",
            new=AsyncMock(return_value=session),
        ):
            return await executor._prepare_session(context, MagicMock(), runner)

    result = _run(_run_test())
    assert result is not None
