from app.pricing import estimate_cost


def test_estimate_cost_known_model():
    cost = estimate_cost("gpt-4o", {"prompt_tokens": 1_000_000, "completion_tokens": 1_000_000})
    assert cost == 12.50


def test_estimate_cost_dated_alias_prefix_match():
    cost = estimate_cost("gpt-4o-2024-08-06", {"prompt_tokens": 1_000_000, "completion_tokens": 0})
    assert cost == 2.50


def test_estimate_cost_unknown_model_is_zero():
    assert estimate_cost("some-future-model", {"prompt_tokens": 1000, "completion_tokens": 1000}) == 0.0


def test_estimate_cost_missing_usage_is_zero():
    assert estimate_cost("gpt-4o", None) == 0.0
    assert estimate_cost(None, {"prompt_tokens": 1000}) == 0.0
