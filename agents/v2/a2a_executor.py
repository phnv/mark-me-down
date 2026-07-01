"""
A2A executor with BYOK (Bring-Your-Own-Key) support.

Subclasses A2aAgentExecutor to extract `provider` and `api_key` from
the A2A task message body and seed them into session.state before the
ADK workflow runs. This preserves BYOK behaviour across the A2A path.

The A2A client encodes the full request as a JSON string in the first
message part:

    {
      "raw_text": "...",
      "refactor_mode": "conservative",
      "rewrite_mode": "adaptive",
      "include_frontmatter": false,
      "template_selection": "auto",
      "provider": "gemini",
      "api_key": "YOUR_KEY"
    }

router_node and the guardrail callbacks already read provider/api_key
from ctx.state — no changes needed in the workflow.

Thread-safety note
------------------
Setting os.environ per-request is NOT thread-safe under concurrent load.
For single-user local dev this is acceptable. For production deployment
seed session.state only and configure the ADK model client to read from
state rather than env vars.
"""
from __future__ import annotations

import json
import os
import logging
import asyncio

from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from google.adk.runners import Runner

logger = logging.getLogger("mark_me_down.a2a_executor")

# Global lock to ensure thread-safe os.environ mutations across concurrent requests
_byok_lock = asyncio.Lock()

class ByokA2aExecutor(A2aAgentExecutor):
    """A2A executor that seeds provider + api_key from the task message.

    Overrides `execute` to lock the entire ADK execution pipeline so we can
    safely mutate os.environ per-request for LiteLLM.
    Overrides `_prepare_session` to seed session.state for workflow nodes.
    """
    
    def __init__(self, runner):
        # Force legacy mode so that our _prepare_session override is actually called
        super().__init__(runner=runner, use_legacy=True)

    async def execute(self, context, event_queue):
        print(f"========== BYOK EXECUTE CALLED ==========")
        provider = "gemini"
        api_key = ""
        
        # Parse payload
        try:
            parts = getattr(context.message, "parts", [])
            if parts:
                part = parts[0]
                # In a2a.types, Part might be a RootModel or have a direct text attribute.
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    text = part.root.text
                elif hasattr(part, "text"):
                    text = part.text
                else:
                    text = getattr(part, "text", "") or ""
                    
                data = json.loads(text)
                provider = data.get("provider", "gemini")
                api_key = data.get("api_key", "")
        except Exception as exc:
            logger.warning("[BYOK] Failed to parse BYOK fields for lock: %s", exc)
            print(f"Exception parsing BYOK: {exc}")

        env_key = f"{provider.upper()}_API_KEY"

        # Wait for our turn to execute and mutate os.environ
        async with _byok_lock:
            original_key = os.environ.get(env_key)
            print(f"Lock acquired. Setting {env_key}. Original was present: {original_key is not None}")
            if api_key:
                os.environ[env_key] = api_key
            
            try:
                # Proceed with standard A2A execution
                print(f"Executing super().execute...")
                await super().execute(context, event_queue)
                print(f"Finished super().execute.")
            finally:
                # Always clean up the environment variable
                print(f"Cleaning up {env_key}...")
                if original_key is not None:
                    os.environ[env_key] = original_key
                elif env_key in os.environ:
                    del os.environ[env_key]

    async def _prepare_session(self, context, run_request, runner: Runner):
        session = await super()._prepare_session(context, run_request, runner)
        try:
            parts = getattr(context.message, "parts", [])
            if parts:
                part = parts[0]
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    text = part.root.text
                elif hasattr(part, "text"):
                    text = part.text
                else:
                    text = getattr(part, "text", "") or ""
                    
                data = json.loads(text)
                provider = data.get("provider", "gemini")
                api_key = data.get("api_key", "")
                
                # Seed state so workflow nodes read from ctx.state (e.g., guardrails)
                session.state["provider"] = provider
                session.state["api_key"] = api_key
                
                logger.info(
                    "[BYOK] Injected provider=%s api_key_present=%s",
                    provider,
                    bool(api_key),
                )
        except Exception as exc:
            logger.warning("[BYOK] Failed to parse BYOK fields from message: %s", exc)
        return session
