from config import REFACTOR_CONSERVATIVE, STYLE_ADAPTIVE
from agents.prompt_builder import build_system_prompt, build_prompt_messages

def test_build_system_prompt():
    prompt = build_system_prompt(REFACTOR_CONSERVATIVE, STYLE_ADAPTIVE)
    assert "Mark-me-down" in prompt
    assert "REFACTOR MODE: CONSERVATIVE" in prompt
    assert "STYLE: ADAPTIVE" in prompt

def test_build_prompt_messages():
    raw_text = "Hello world note"
    messages = build_prompt_messages(raw_text, REFACTOR_CONSERVATIVE, STYLE_ADAPTIVE)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "REFACTOR MODE: CONSERVATIVE" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "Hello world note" in messages[1]["content"]
