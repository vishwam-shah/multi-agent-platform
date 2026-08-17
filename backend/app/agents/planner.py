import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.providers import get_llm
from app.tools.registry import get_tool_names
from app.tracing.tracer import Tracer

PLANNER_SYSTEM_PROMPT = """You are a planning agent. Given a user's high-level goal, decompose it into a sequence of 2-8 concrete, actionable steps that can be executed independently by worker agents.

Available tools that worker agents can use:
{tools}

Return ONLY a valid JSON array of steps. Each step must have:
- "index": integer starting from 0
- "description": a clear, specific instruction for the worker agent
- "tools_needed": list of tool names the worker should use (from the available tools)

Example output:
[
  {{"index": 0, "description": "Search the web for the latest Python web frameworks in 2024", "tools_needed": ["web_search"]}},
  {{"index": 1, "description": "Write Python code to create a comparison table of the frameworks found", "tools_needed": ["code_exec"]}}
]

Do not include any text outside the JSON array."""


async def plan_goal(
    goal: str,
    provider: str,
    model: str,
    tracer: Tracer,
) -> list[dict]:
    llm = get_llm(provider, model)

    tools_desc = ", ".join(get_tool_names())
    system_msg = PLANNER_SYSTEM_PROMPT.format(tools=tools_desc)

    messages = [
        SystemMessage(content=system_msg),
        HumanMessage(content=f"Goal: {goal}"),
    ]

    timer = tracer.timer()
    with timer:
        response = await llm.ainvoke(messages)

    token_usage = None
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        token_usage = {
            "prompt_tokens": response.usage_metadata.get("input_tokens", 0),
            "completion_tokens": response.usage_metadata.get("output_tokens", 0),
            "total_tokens": response.usage_metadata.get("total_tokens", 0),
        }

    await tracer.log(
        "llm_call",
        provider=provider,
        model=model,
        input_data={"goal": goal, "system_prompt": system_msg},
        output_data={"response": response.content},
        token_usage=token_usage,
        duration_ms=timer.elapsed_ms,
    )

    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    return json.loads(content)
