from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    rent = "rent"
    buy = "buy"
    either = "either"


class PropertyType(str, Enum):
    single_family = "single_family"
    condo = "condo"
    townhouse = "townhouse"
    apartment = "apartment"
    any = "any"


class NoiseTolerance(str, Enum):
    quiet = "quiet"
    moderate = "moderate"
    lively = "lively"


class BudgetRange(BaseModel):
    min_price: Optional[int] = Field(None, description="Minimum price in USD")
    max_price: Optional[int] = Field(None, description="Maximum price in USD")


class LocationPreference(BaseModel):
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(
        None, description="US state name or two-letter code"
    )
    neighborhood_type: Optional[str] = Field(
        None,
        description="Desired neighborhood vibe, e.g. 'urban', 'suburban', 'rural'",
    )


class CommutePreference(BaseModel):
    workplace_description: Optional[str] = Field(
        None, description="Where the person works or commutes to"
    )
    max_commute_minutes: Optional[int] = Field(
        None, description="Maximum acceptable one-way commute in minutes"
    )


class HousingPreferences(BaseModel):
    """Structured housing preferences extracted from a natural-language description."""

    # Hard filters
    transaction_type: Optional[TransactionType] = None
    budget: Optional[BudgetRange] = None
    location: Optional[LocationPreference] = None
    property_type: Optional[PropertyType] = None
    bedrooms_min: Optional[int] = Field(None, ge=0)
    bathrooms_min: Optional[int] = Field(None, ge=0)
    sqft_min: Optional[int] = Field(None, ge=0)
    sqft_max: Optional[int] = Field(None, ge=0)
    has_pets: Optional[bool] = None
    pet_type: Optional[str] = Field(
        None, description="e.g. 'dog', 'cat', 'dog and cat'"
    )
    needs_parking: Optional[bool] = None
    wants_pool: Optional[bool] = None
    wants_gym: Optional[bool] = None
    wants_yard: Optional[bool] = None

    # Soft filters
    noise_tolerance: Optional[NoiseTolerance] = None
    commute: Optional[CommutePreference] = None
    lifestyle_notes: Optional[list[str]] = Field(
        None,
        description="Inferred lifestyle preferences, e.g. 'large kitchen', 'home office'",
    )
    reasoning: Optional[str] = Field(
        None,
        description="Chain-of-thought reasoning used by the LLM (not used in search)",
    )
