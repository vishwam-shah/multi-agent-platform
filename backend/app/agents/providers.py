from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from app.config import settings


def get_llm(provider: str, model: str, temperature: float = 0.2):
    if provider == "openai":
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.openai_api_key,
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=settings.anthropic_api_key,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
