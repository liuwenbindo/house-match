import json

from src.schemas.preferences import (
    BudgetRange,
    HousingPreferences,
    LocationPreference,
    NoiseTolerance,
    PropertyType,
    TransactionType,
)


def test_minimal_preferences():
    """All fields are optional — an empty object should validate."""
    prefs = HousingPreferences()
    assert prefs.transaction_type is None
    assert prefs.budget is None


def test_full_preferences():
    prefs = HousingPreferences(
        transaction_type=TransactionType.rent,
        budget=BudgetRange(max_price=2500),
        location=LocationPreference(city="Austin", state="TX"),
        property_type=PropertyType.apartment,
        bedrooms_min=2,
        bathrooms_min=1,
        has_pets=True,
        pet_type="dog",
        wants_yard=True,
        noise_tolerance=NoiseTolerance.quiet,
        lifestyle_notes=["home office", "large kitchen"],
    )
    assert prefs.transaction_type == TransactionType.rent
    assert prefs.budget.max_price == 2500
    assert prefs.location.city == "Austin"
    assert prefs.bedrooms_min == 2
    assert prefs.has_pets is True
    assert len(prefs.lifestyle_notes) == 2


def test_json_roundtrip():
    prefs = HousingPreferences(
        transaction_type=TransactionType.buy,
        budget=BudgetRange(min_price=200000, max_price=400000),
        location=LocationPreference(city="Miami", state="FL"),
        property_type=PropertyType.condo,
    )
    data = json.loads(prefs.model_dump_json(exclude_none=True))
    restored = HousingPreferences(**data)
    assert restored.transaction_type == TransactionType.buy
    assert restored.budget.max_price == 400000
    assert restored.location.city == "Miami"


def test_json_schema_generation():
    """Ensure we can generate a JSON schema for the LLM prompt."""
    schema = HousingPreferences.model_json_schema()
    assert "properties" in schema
    assert "transaction_type" in schema["properties"]
