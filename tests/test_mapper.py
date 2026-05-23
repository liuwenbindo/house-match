from src.housing.mapper import (
    preferences_to_homeharvest_params,
    preferences_to_realty_params,
)
from src.schemas.preferences import (
    BudgetRange,
    HousingPreferences,
    LocationPreference,
    PropertyType,
    TransactionType,
)


def test_realty_params_basic():
    prefs = HousingPreferences(
        transaction_type=TransactionType.rent,
        budget=BudgetRange(max_price=2500),
        location=LocationPreference(city="Austin", state="TX"),
        bedrooms_min=2,
        property_type=PropertyType.apartment,
    )
    params = preferences_to_realty_params(prefs)
    assert params["city"] == "Austin"
    assert params["state_code"] == "TX"
    assert params["price_max"] == 2500
    assert params["beds_min"] == 2
    assert params["prop_type"] == "apartment"


def test_realty_params_pets_rental():
    prefs = HousingPreferences(
        transaction_type=TransactionType.rent,
        has_pets=True,
        pet_type="dog",
    )
    params = preferences_to_realty_params(prefs)
    assert params["allows_dogs"] is True
    assert "allows_cats" not in params


def test_realty_params_pets_not_rental():
    """Pet filters should only apply to rentals."""
    prefs = HousingPreferences(
        transaction_type=TransactionType.buy,
        has_pets=True,
        pet_type="dog",
    )
    params = preferences_to_realty_params(prefs)
    assert "allows_dogs" not in params


def test_realty_params_empty():
    prefs = HousingPreferences()
    params = preferences_to_realty_params(prefs)
    assert params == {}


def test_realty_params_state_full_name():
    prefs = HousingPreferences(
        location=LocationPreference(state="California"),
    )
    params = preferences_to_realty_params(prefs)
    assert params["state_code"] == "CA"


def test_homeharvest_params_rent():
    prefs = HousingPreferences(
        transaction_type=TransactionType.rent,
        location=LocationPreference(city="San Francisco", state="CA"),
    )
    params = preferences_to_homeharvest_params(prefs)
    assert params["location"] == "San Francisco, CA"
    assert params["listing_type"] == "for_rent"


def test_homeharvest_params_buy():
    prefs = HousingPreferences(
        transaction_type=TransactionType.buy,
        location=LocationPreference(city="Miami", state="FL"),
    )
    params = preferences_to_homeharvest_params(prefs)
    assert params["location"] == "Miami, FL"
    assert params["listing_type"] == "for_sale"


def test_homeharvest_params_no_location():
    prefs = HousingPreferences()
    params = preferences_to_homeharvest_params(prefs)
    assert params["location"] == "United States"
