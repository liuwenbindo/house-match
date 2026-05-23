from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.schemas.preferences import HousingPreferences


class HousingSource(ABC):
    """Abstract interface for housing listing sources."""

    @abstractmethod
    def search(self, preferences: HousingPreferences) -> list[dict[str, Any]]:
        """Search for listings matching the given preferences.

        Returns a list of dicts, each representing a listing with at minimum:
        - address, city, state
        - price
        - beds, baths, sqft (when available)
        """
