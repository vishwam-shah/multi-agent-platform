from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

from app.agents.providers import get_llm
from app.tools.registry import get_all_tools
from app.tracing.tracer import Tracer

WORKER_SYSTEM_PROMPT = """You are a worker agent executing a specific step in a multi-step plan.

You have access to tools. Use them as needed to complete the task.
Be thorough and return a clear, detailed result.

Previous step results (memory):
{memory}

Complete the assigned task and return your findings/results clearly."""


async def execute_step(
    step_description: str,
    memory_context: dict[str, dict],
    provider: str,
    model: str,
    tracer: Tracer,
) -> str:
    llm = get_llm(provider, model)
    tools = get_all_tools()

    memory_str = ""
    if memory_context:
        for key, val in memory_context.items():
            memory_str += f"\n- {key}: {val.get('result', str(val))}"
    else:
        memory_str = "No previous results yet."

    agent = create_agent(
        llm,
        tools=tools,
        system_prompt=WORKER_SYSTEM_PROMPT.format(memory=memory_str),
    )

    timer = tracer.timer()
    with timer, get_usage_metadata_callback() as usage_cb:
        result = await agent.ainvoke({"messages": [HumanMessage(content=step_description)]})

    messages = result.get("messages", [])
    output_text = messages[-1].content if messages else ""

    # The agent loop can make multiple LLM calls per step (tool-calling loop);
    # sum usage across every model invoked so cost tracking covers the whole step.
    token_usage = None
    if usage_cb.usage_metadata:
        totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        for model_usage in usage_cb.usage_metadata.values():
            totals["prompt_tokens"] += model_usage.get("input_tokens", 0)
            totals["completion_tokens"] += model_usage.get("output_tokens", 0)
            totals["total_tokens"] += model_usage.get("total_tokens", 0)
        token_usage = totals

    await tracer.log(
        "agent_decision",
        provider=provider,
        model=model,
        input_data={"step": step_description, "memory_keys": list(memory_context.keys())},
        output_data={"result": output_text},
        token_usage=token_usage,
        duration_ms=timer.elapsed_ms,
    )

    return output_text
