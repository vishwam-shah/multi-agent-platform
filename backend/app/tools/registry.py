from app.tools.web_search import web_search
from app.tools.code_exec import code_exec


def get_all_tools() -> list:
    return [web_search, code_exec]


def get_tool_names() -> list[str]:
    return [t.name for t in get_all_tools()]
