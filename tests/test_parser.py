"""Tests for LLM parser. Requires a running LLM (e.g. Ollama) to pass."""

import pytest

from src.schemas.preferences import HousingPreferences, TransactionType


@pytest.fixture
def parse_fn():
    """Import parse lazily so tests can be collected even without LLM running."""
    from src.llm.parser import parse
    return parse


@pytest.mark.skipif(
    True,
    reason="Requires a running LLM server; run manually with: pytest tests/test_parser.py -k test_parse --no-header -rN",
)
class TestLLMParser:
    def test_parse_renter(self, parse_fn):
        result = parse_fn(
            "I'm a 28-year-old software engineer working remotely in Austin, TX. "
            "I have a golden retriever and need at least 2 bedrooms. Budget is $2,500/month."
        )
        assert isinstance(result, HousingPreferences)
        assert result.transaction_type == TransactionType.rent
        assert result.has_pets is True
        assert result.location is not None
        assert result.location.state in ("TX", "Texas")

    def test_parse_buyer(self, parse_fn):
        result = parse_fn(
            "Retired couple looking to buy a quiet condo in Florida, "
            "budget around $350,000. We want 2 bedrooms and a pool."
        )
        assert isinstance(result, HousingPreferences)
        assert result.transaction_type == TransactionType.buy
        assert result.wants_pool is True
