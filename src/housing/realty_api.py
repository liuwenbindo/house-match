from __future__ import annotations

from typing import Any

import httpx

from src.config import RAPIDAPI_KEY
from src.housing.base import HousingSource
from src.housing.mapper import preferences_to_realty_params
from src.schemas.preferences import HousingPreferences, TransactionType

_HOST = "realty-in-us.p.rapidapi.com"
_SALE_URL = f"https://{_HOST}/properties/v3/list"
_RENTAL_URL = f"https://{_HOST}/properties/v3/list"


class RealtyApiSource(HousingSource):
    """Housing source using the RapidAPI 'Realty in US' API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or RAPIDAPI_KEY
        if not self.api_key:
            raise ValueError(
                "RAPIDAPI_KEY is required for RealtyApiSource. "
                "Set it in .env or pass it directly."
            )

    def search(self, preferences: HousingPreferences) -> list[dict[str, Any]]:
        params = preferences_to_realty_params(preferences)

        # Determine endpoint based on transaction type
        is_rental = preferences.transaction_type == TransactionType.rent

        # Build the request payload for the v3 list endpoint
        payload: dict[str, Any] = {
            "limit": 20,
            "offset": 0,
            "status": ["for_rent"] if is_rental else ["for_sale"],
        }

        if "city" in params or "state_code" in params:
            payload["city"] = params.get("city", "")
            payload["state_code"] = params.get("state_code", "")

        if "price_min" in params or "price_max" in params:
            price_filter: dict[str, Any] = {}
            if "price_min" in params:
                price_filter["min"] = params["price_min"]
            if "price_max" in params:
                price_filter["max"] = params["price_max"]
            if is_rental:
                payload["list_price"] = price_filter
            else:
                payload["list_price"] = price_filter

        if "beds_min" in params:
            payload["beds_min"] = params["beds_min"]
        if "baths_min" in params:
            payload["baths_min"] = params["baths_min"]
        if "sqft_min" in params or "sqft_max" in params:
            sqft_filter: dict[str, Any] = {}
            if "sqft_min" in params:
                sqft_filter["min"] = params["sqft_min"]
            if "sqft_max" in params:
                sqft_filter["max"] = params["sqft_max"]
            payload["sqft"] = sqft_filter
        if "prop_type" in params:
            payload["type"] = [params["prop_type"]]

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": _HOST,
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=30) as client:
            resp = client.post(_SALE_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        return self._normalize(data)

    @staticmethod
    def _normalize(data: dict[str, Any]) -> list[dict[str, Any]]:
        """Normalize API response into a flat list of listing dicts."""
        results = []
        properties = (
            data.get("data", {}).get("home_search", {}).get("results", [])
        )
        for prop in properties:
            location = prop.get("location", {})
            address = location.get("address", {})
            description = prop.get("description", {})
            results.append(
                {
                    "address": address.get("line", ""),
                    "city": address.get("city", ""),
                    "state": address.get("state_code", ""),
                    "zip": address.get("postal_code", ""),
                    "price": prop.get("list_price"),
                    "beds": description.get("beds"),
                    "baths": description.get("baths"),
                    "sqft": description.get("sqft"),
                    "property_type": description.get("type", ""),
                    "link": prop.get("permalink", ""),
                }
            )
        return results
