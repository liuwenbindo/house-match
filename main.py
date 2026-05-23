"""Housing Preference Pipeline — CLI entry point.

Usage:
    python main.py "I'm a software engineer in SF with a dog, budget $3k/month rent"
    echo "description" | python main.py
"""

import json
import sys

from src.config import RAPIDAPI_KEY
from src.llm.parser import parse
from src.schemas.preferences import HousingPreferences


def get_housing_source():
    """Return the best available housing source."""
    if RAPIDAPI_KEY:
        from src.housing.realty_api import RealtyApiSource
        return RealtyApiSource()
    else:
        from src.housing.homeharvest_source import HomeHarvestSource
        print("[info] No RAPIDAPI_KEY set — using HomeHarvest fallback.\n")
        return HomeHarvestSource()


def run(description: str) -> None:
    """Run the full pipeline: NL description → preferences → listings."""
    # Step 1: Parse natural language into structured preferences
    print("=" * 60)
    print("STEP 1: Extracting housing preferences via LLM...")
    print("=" * 60)

    preferences: HousingPreferences = parse(description)

    print("\nExtracted preferences:")
    print(
        json.dumps(
            preferences.model_dump(exclude_none=True),
            indent=2,
        )
    )

    # Step 2: Search for matching listings
    print("\n" + "=" * 60)
    print("STEP 2: Searching for matching listings...")
    print("=" * 60)

    source = get_housing_source()

    try:
        listings = source.search(preferences)
    except Exception as e:
        print(f"\n[error] Housing search failed: {e}")
        return

    if not listings:
        print("\nNo listings found matching your criteria.")
        return

    print(f"\nFound {len(listings)} listing(s):\n")
    for i, listing in enumerate(listings, 1):
        price = listing.get("price")
        price_str = f"${price:,.0f}" if price else "N/A"
        beds = listing.get("beds", "?")
        baths = listing.get("baths", "?")
        sqft = listing.get("sqft")
        sqft_str = f"{sqft:,.0f} sqft" if sqft else ""

        print(f"  {i}. {listing.get('address', 'N/A')}")
        print(f"     {listing.get('city', '')}, {listing.get('state', '')} {listing.get('zip', '')}")
        print(f"     {price_str} | {beds}bd / {baths}ba {sqft_str}")
        if listing.get("link"):
            print(f"     {listing['link']}")
        print()


def main() -> None:
    if len(sys.argv) > 1:
        description = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        description = sys.stdin.read().strip()
    else:
        print("Usage: python main.py \"<person description>\"")
        print("   or: echo \"<description>\" | python main.py")
        sys.exit(1)

    if not description:
        print("Error: empty description provided.")
        sys.exit(1)

    print(f"\nInput: {description}\n")
    run(description)


if __name__ == "__main__":
    main()
