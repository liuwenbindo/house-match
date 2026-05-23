from __future__ import annotations

from typing import Any

from src.housing.base import HousingSource
from src.housing.mapper import preferences_to_homeharvest_params
from src.schemas.preferences import HousingPreferences


class HomeHarvestSource(HousingSource):
    """Fallback housing source using the HomeHarvest scraper (no API key needed)."""

    def search(self, preferences: HousingPreferences) -> list[dict[str, Any]]:
        try:
            from homeharvest import scrape_property
        except ImportError:
            raise ImportError(
                "homeharvest is not installed. Install it with: pip install homeharvest"
            )

        params = preferences_to_homeharvest_params(preferences)
        location = params.pop("location")
        listing_type = params.pop("listing_type", "for_sale")

        df = scrape_property(location=location, listing_type=listing_type)

        if df.empty:
            return []

        # Apply budget filter if set
        if preferences.budget:
            price_col = (
                "list_price" if "list_price" in df.columns else "price"
            )
            if price_col in df.columns:
                if preferences.budget.max_price is not None:
                    df = df[df[price_col] <= preferences.budget.max_price]
                if preferences.budget.min_price is not None:
                    df = df[df[price_col] >= preferences.budget.min_price]

        # Apply bedroom filter
        if preferences.bedrooms_min is not None and "beds" in df.columns:
            df = df[df["beds"] >= preferences.bedrooms_min]

        # Apply bathroom filter
        if preferences.bathrooms_min is not None and "baths" in df.columns:
            df = df[df["baths"] >= preferences.bathrooms_min]

        # Limit results
        df = df.head(20)

        return self._normalize(df)

    @staticmethod
    def _normalize(df: Any) -> list[dict[str, Any]]:
        """Convert DataFrame rows to flat listing dicts."""
        results = []
        for _, row in df.iterrows():
            results.append(
                {
                    "address": row.get("street", row.get("address", "")),
                    "city": row.get("city", ""),
                    "state": row.get("state", ""),
                    "zip": row.get("zip_code", row.get("zip", "")),
                    "price": row.get("list_price", row.get("price")),
                    "beds": row.get("beds"),
                    "baths": row.get("baths"),
                    "sqft": row.get("sqft"),
                    "property_type": row.get("property_type", row.get("style", "")),
                    "link": row.get("property_url", row.get("link", "")),
                }
            )
        return results
