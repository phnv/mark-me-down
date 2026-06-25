import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path().resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from agents.note_profiler.app.agent import root_agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

async def main():
    app = App(name="app", root_agent=root_agent)
    runner = InMemoryRunner(app=app)

    session = await runner.session_service.create_session(
        app_name="app", user_id="dev_user"
    )

    agent_input = "Name: Test Note\nInstructions: A simple test note\nTemplate: # Test\nThis is a test note."

    print("Running workflow...")
    async for event in runner.run_async(
        user_id="dev_user",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part.from_text(text=agent_input)]),
    ):
        print("------------- EVENT -------------")
        print(f"event.output: {event.output}")
        if event.content and event.content.parts:
            print(f"event.content.parts[0].text: {event.content.parts[0].text}")
        elif event.content:
            print(f"event.content: {event.content}")
            
if __name__ == "__main__":
    asyncio.run(main())
