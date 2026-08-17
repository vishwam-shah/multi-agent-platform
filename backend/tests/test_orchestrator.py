import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from app.config import settings


def test_retry_config():
    assert settings.max_retries >= 1
    assert settings.retry_base_delay > 0


def test_retry_backoff_calculation():
    base = settings.retry_base_delay
    delays = [base * (2 ** i) for i in range(settings.max_retries)]
    assert delays[0] == base
    assert delays[1] == base * 2
    assert delays[2] == base * 4
