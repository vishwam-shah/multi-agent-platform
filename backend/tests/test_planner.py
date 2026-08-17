import json
import pytest


def test_planner_prompt_format():
    from app.agents.planner import PLANNER_SYSTEM_PROMPT
    from app.tools.registry import get_tool_names

    tools_desc = ", ".join(get_tool_names())
    prompt = PLANNER_SYSTEM_PROMPT.format(tools=tools_desc)
    assert "web_search" in prompt
    assert "code_exec" in prompt
    assert "JSON array" in prompt
