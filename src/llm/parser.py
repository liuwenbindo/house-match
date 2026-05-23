from openai import OpenAI
from pydantic import ValidationError

from src.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from src.llm.prompts import build_system_prompt
from src.schemas.preferences import HousingPreferences

MAX_RETRIES = 2


def _create_client() -> OpenAI:
    return OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)


def parse(description: str) -> HousingPreferences:
    """Parse a natural-language person description into structured housing preferences."""
    client = _create_client()
    system_prompt = build_system_prompt()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": description},
    ]

    for attempt in range(1 + MAX_RETRIES):
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        raw = response.choices[0].message.content
        try:
            return HousingPreferences.model_validate_json(raw)
        except ValidationError as e:
            if attempt < MAX_RETRIES:
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"Your JSON was invalid. Errors:\n{e}\n\n"
                            "Please fix the JSON and try again."
                        ),
                    },
                )
            else:
                raise ValueError(
                    f"Failed to parse valid preferences after {MAX_RETRIES} retries: {e}"
                ) from e
