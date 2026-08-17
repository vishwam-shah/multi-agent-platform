from langchain_core.tools import tool

from app.config import settings


@tool
def web_search(query: str) -> str:
    """Search the web for information on a given query. Returns a summary of the top results."""
    from tavily import TavilyClient

    client = TavilyClient(api_key=settings.tavily_api_key)
    response = client.search(query=query, max_results=5)

    results = []
    for r in response.get("results", []):
        results.append(f"**{r['title']}**\n{r['url']}\n{r['content']}\n")

    return "\n---\n".join(results) if results else "No results found."
