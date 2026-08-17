"""Per-1M-token USD pricing for supported models, used to compute live run/step cost.

Prices are (input_price_per_1m, output_price_per_1m). Update as providers change pricing.
Unknown models fall back to $0 cost rather than guessing.
"""

PRICING: dict[str, tuple[float, float]] = {
    # OpenAI
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-5": (1.25, 10.00),
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5-nano": (0.05, 0.40),
    "o3": (2.00, 8.00),
    "o3-mini": (1.10, 4.40),
    # Anthropic
    "claude-3-5-sonnet-20241022": (3.00, 15.00),
    "claude-3-5-sonnet-latest": (3.00, 15.00),
    "claude-3-5-haiku-20241022": (0.80, 4.00),
    "claude-3-opus-20240229": (15.00, 75.00),
    "claude-opus-4-20250514": (15.00, 75.00),
    "claude-sonnet-4-20250514": (3.00, 15.00),
    "claude-sonnet-4-5-20250929": (3.00, 15.00),
    "claude-haiku-4-5-20251001": (1.00, 5.00),
}


def estimate_cost(model: str | None, token_usage: dict | None) -> float:
    """Estimate USD cost for a single LLM call given its model and token usage."""
    if not model or not token_usage:
        return 0.0

    prices = PRICING.get(model)
    if prices is None:
        # Fall back to a prefix match so dated/aliased model names (e.g.
        # "gpt-4o-2024-08-06") still resolve to the base model's pricing.
        for key, val in PRICING.items():
            if model.startswith(key):
                prices = val
                break

    if prices is None:
        return 0.0

    input_price, output_price = prices
    prompt_tokens = token_usage.get("prompt_tokens") or token_usage.get("input_tokens") or 0
    completion_tokens = token_usage.get("completion_tokens") or token_usage.get("output_tokens") or 0
    return (prompt_tokens / 1_000_000) * input_price + (completion_tokens / 1_000_000) * output_price
