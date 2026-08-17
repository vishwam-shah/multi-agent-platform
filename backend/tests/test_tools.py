from app.tools.code_exec import code_exec
from app.tools.registry import get_all_tools, get_tool_names


def test_code_exec_basic():
    result = code_exec.invoke({"code": "print(2 + 2)"})
    assert "4" in result


def test_code_exec_timeout():
    result = code_exec.invoke({"code": "import time; time.sleep(60)"})
    assert "timed out" in result.lower()


def test_code_exec_error():
    result = code_exec.invoke({"code": "raise ValueError('test error')"})
    assert "test error" in result


def test_registry():
    tools = get_all_tools()
    assert len(tools) == 2
    names = get_tool_names()
    assert "web_search" in names
    assert "code_exec" in names
