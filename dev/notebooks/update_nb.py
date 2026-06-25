import json

path = r"c:\Users\Home\Desktop\projetos\mark-me-down\dev\notebooks\learner-and-parser-agents-drafts.ipynb"

with open(path, "r", encoding="utf-8") as f:
    nb = json.load(f)

new_source = [
    "import sys\n",
    "from pathlib import Path\n",
    "\n",
    "PROJECT_ROOT = Path().resolve().parents[1]\n",
    "if str(PROJECT_ROOT) not in sys.path:\n",
    "    sys.path.append(str(PROJECT_ROOT))\n",
    "\n",
    "# Note: agent.py now automatically handles dotenv loading for OPENAI_API_KEY\n",
    "from agents.note_profiler.app.agent import root_agent\n",
    "import json\n",
    "from google.adk.apps import App\n",
    "from google.adk.runners import InMemoryRunner\n",
    "from google.genai import types\n",
    "\n",
    "app = App(name=\"app\", root_agent=root_agent)\n",
    "runner = InMemoryRunner(app=app)\n",
    "\n",
    "session = await runner.session_service.create_session(\n",
    "    app_name=\"app\", user_id=\"dev_user\"\n",
    ")\n",
    "\n",
    "# Draft pipeline execution to Note Profiler Agent:\n",
    "for note in templates[:1]:\n",
    "    # prepare input for the Note Profiler Agent\n",
    "    agent_input = f\"Name: {note.get('name', '')}\\nInstructions: {note.get('instructions', '')}\\nTemplate: {note.get('template_markdown', '')}\"\n",
    "    \n",
    "    print(f\"Running Note Profiler for {note.get('name')}...\")\n",
    "    enriched_profile = None\n",
    "    async for event in runner.run_async(\n",
    "        user_id=\"dev_user\",\n",
    "        session_id=session.id,\n",
    "        new_message=types.Content(role=\"user\", parts=[types.Part.from_text(text=agent_input)]),\n",
    "    ):\n",
    "        if event.output is not None:\n",
    "            enriched_profile = event.output\n",
    "            \n",
    "    # get enriched template with new keys \n",
    "    print(f\"Enriched profile for {note.get('name')}:\")\n",
    "    if enriched_profile:\n",
    "        # event.output is now the parsed Pydantic object, so we dump it properly\n",
    "        print(enriched_profile.model_dump_json(indent=2))\n",
    "    else:\n",
    "        print(\"No output was generated.\")\n",
    "    \n",
    "    print('-' * 40)\n",
    "    \n",
    "    # human check \n",
    "    # **eventually** update the note in the database with the enriched content\n"
]

# Update the last cell
if nb["cells"]:
    nb["cells"][-1]["source"] = new_source

with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
