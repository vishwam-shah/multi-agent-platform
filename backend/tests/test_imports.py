"""Import-smoke tests. langchain has broken these modules across major version
bumps before (AgentExecutor/create_tool_calling_agent removed in langchain 1.x)
with no other test catching it, since execute_step is otherwise only exercised
by real LLM calls. Importing every agent module here fails fast in CI instead.
"""


def test_worker_module_imports():
    from app.agents import worker  # noqa: F401


def test_orchestrator_module_imports():
    from app.agents import orchestrator  # noqa: F401


def test_planner_module_imports():
    from app.agents import planner  # noqa: F401


def test_main_app_imports():
    from app.main import app

    assert app is not None
