import json

from src.schemas.preferences import HousingPreferences

SYSTEM_PROMPT = """\
You are a housing preference extractor. Given a natural-language description of a person, \
extract structured housing preferences as JSON.

## Rules
- Only include fields you can confidently infer. Omit fields you cannot determine.
- Use the "reasoning" field to think step-by-step before filling in other fields.
- Infer implicit preferences:
  - "works from home" → lifestyle_notes should include "home office", consider extra bedroom
  - "has a dog" → has_pets=true, pet_type="dog", wants_yard=true is likely
  - "loves cooking" → lifestyle_notes should include "large kitchen"
  - "young professional" → likely apartment or condo, urban neighborhood
  - Monthly budget → transaction_type="rent"; large budget (>$200k) → transaction_type="buy"
- For budget: if a monthly amount is given, assume rent. If a large lump sum, assume purchase price.
- State should be a two-letter code (e.g. "CA", "NY", "TX").
- All prices are in USD.

## JSON Schema
{schema}

## Examples

### Input
"I'm a 28-year-old software engineer working remotely, living with my golden retriever. \
I'm looking to rent in Austin, Texas for under $2,500/month. I need at least 2 bedrooms \
and a yard for my dog."

### Output
{example1}

### Input
"Retired couple looking to buy a quiet condo in Florida, budget around $350,000. \
We want at least 2 bedrooms, 2 bathrooms, a pool, and close to golf courses."

### Output
{example2}
"""

_EXAMPLE_1 = {
    "reasoning": "Software engineer working remotely needs a home office. Has a golden retriever so needs pet-friendly with yard. Renting in Austin TX under $2500/mo. Needs 2+ bedrooms.",
    "transaction_type": "rent",
    "budget": {"min_price": None, "max_price": 2500},
    "location": {"city": "Austin", "state": "TX", "neighborhood_type": None},
    "property_type": "any",
    "bedrooms_min": 2,
    "has_pets": True,
    "pet_type": "dog",
    "wants_yard": True,
    "lifestyle_notes": ["home office", "pet-friendly"],
}

_EXAMPLE_2 = {
    "reasoning": "Retired couple buying a condo in Florida. Want quiet, pool, near golf. Budget $350k. 2bd/2ba minimum.",
    "transaction_type": "buy",
    "budget": {"min_price": None, "max_price": 350000},
    "location": {"city": None, "state": "FL", "neighborhood_type": "suburban"},
    "property_type": "condo",
    "bedrooms_min": 2,
    "bathrooms_min": 2,
    "wants_pool": True,
    "noise_tolerance": "quiet",
    "lifestyle_notes": ["near golf courses", "retirement-friendly"],
}


def build_system_prompt() -> str:
    schema = json.dumps(
        HousingPreferences.model_json_schema(), indent=2
    )
    return SYSTEM_PROMPT.format(
        schema=schema,
        example1=json.dumps(_EXAMPLE_1, indent=2),
        example2=json.dumps(_EXAMPLE_2, indent=2),
    )
