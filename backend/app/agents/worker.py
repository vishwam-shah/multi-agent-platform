from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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

    prompt = ChatPromptTemplate.from_messages([
        ("system", WORKER_SYSTEM_PROMPT.format(memory=memory_str)),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, max_iterations=10, verbose=False)

    timer = tracer.timer()
    with timer:
        result = await executor.ainvoke({"input": step_description})

    output_text = result.get("output", "")

    await tracer.log(
        "agent_decision",
        provider=provider,
        model=model,
        input_data={"step": step_description, "memory_keys": list(memory_context.keys())},
        output_data={"result": output_text},
        duration_ms=timer.elapsed_ms,
    )

    return output_text
