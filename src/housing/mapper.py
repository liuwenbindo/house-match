from __future__ import annotations

from typing import Any

from src.schemas.preferences import HousingPreferences, PropertyType, TransactionType

# Map our PropertyType enum to Realty in US API prop_type values
_PROP_TYPE_MAP: dict[PropertyType, str] = {
    PropertyType.single_family: "single_family",
    PropertyType.condo: "condo",
    PropertyType.townhouse: "townhome",
    PropertyType.apartment: "apartment",
}

# US state name → two-letter code (common states; extend as needed)
_STATE_CODES: dict[str, str] = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
    "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
    "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}


def _normalize_state(state: str | None) -> str | None:
    """Convert a state name or code to a two-letter code."""
    if state is None:
        return None
    s = state.strip()
    if len(s) == 2:
        return s.upper()
    return _STATE_CODES.get(s.lower(), s.upper()[:2])


def preferences_to_realty_params(
    prefs: HousingPreferences,
) -> dict[str, Any]:
    """Map HousingPreferences to Realty in US API query parameters."""
    params: dict[str, Any] = {}

    # Location
    if prefs.location:
        if prefs.location.city:
            params["city"] = prefs.location.city
        state_code = _normalize_state(prefs.location.state)
        if state_code:
            params["state_code"] = state_code

    # Budget
    if prefs.budget:
        if prefs.budget.min_price is not None:
            params["price_min"] = prefs.budget.min_price
        if prefs.budget.max_price is not None:
            params["price_max"] = prefs.budget.max_price

    # Property type
    if prefs.property_type and prefs.property_type != PropertyType.any:
        mapped = _PROP_TYPE_MAP.get(prefs.property_type)
        if mapped:
            params["prop_type"] = mapped

    # Rooms / size
    if prefs.bedrooms_min is not None:
        params["beds_min"] = prefs.bedrooms_min
    if prefs.bathrooms_min is not None:
        params["baths_min"] = prefs.bathrooms_min
    if prefs.sqft_min is not None:
        params["sqft_min"] = prefs.sqft_min
    if prefs.sqft_max is not None:
        params["sqft_max"] = prefs.sqft_max

    # Pets (rental only)
    if prefs.has_pets and prefs.transaction_type == TransactionType.rent:
        pet = (prefs.pet_type or "").lower()
        if "dog" in pet:
            params["allows_dogs"] = True
        if "cat" in pet:
            params["allows_cats"] = True
        if not pet:
            params["allows_dogs"] = True
            params["allows_cats"] = True

    # Amenities
    if prefs.wants_pool:
        params["has_pool"] = True

    return params


def preferences_to_homeharvest_params(
    prefs: HousingPreferences,
) -> dict[str, Any]:
    """Map HousingPreferences to HomeHarvest search parameters."""
    params: dict[str, Any] = {}

    # Location string (required by homeharvest)
    parts = []
    if prefs.location:
        if prefs.location.city:
            parts.append(prefs.location.city)
        state_code = _normalize_state(prefs.location.state)
        if state_code:
            parts.append(state_code)
    params["location"] = ", ".join(parts) if parts else "United States"

    # Listing type
    if prefs.transaction_type == TransactionType.rent:
        params["listing_type"] = "for_rent"
    elif prefs.transaction_type == TransactionType.buy:
        params["listing_type"] = "for_sale"
    else:
        params["listing_type"] = "for_sale"

    return params
