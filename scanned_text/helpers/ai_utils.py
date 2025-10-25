"""Utility functions for mock processing and optional OpenAI powered processing.

This module keeps backward compatibility with existing mock functions while
adding thin wrappers around the OpenAI API. The OpenAI helpers are only used
if the required environment variables are present; otherwise a safe fallback
is returned so the rest of the application does not break in local / test
environments.
"""

from lorem_text import lorem
import random
from typing import Optional
from decouple import config, UndefinedValueError
from openai import OpenAI

_OPENAI_MODEL: str = "chatgpt-4o-latest"

def initOpenAI() -> OpenAI | None:
    """Initialize OpenAI client if configuration is present."""
    try:
        print("Importing scanned_text.serializers for type hints...")
        # Lazily resolve so missing .env during tests does not crash import.
        _OPENAI_API_KEY: Optional[str] = config("OPENAI_API_KEY", default=None)
    except UndefinedValueError:
        _OPENAI_API_KEY = None

    _OPENAI_ENABLED = bool(_OPENAI_API_KEY)

    if _OPENAI_ENABLED:
        try:
            _openai_client = OpenAI(
                api_key=_OPENAI_API_KEY,
            )
        except Exception as e:  # pragma: no cover - defensive
            print(f"Failed to initialize OpenAI client: {e}")
            _OPENAI_ENABLED = False
            _openai_client = None
    else:
        _openai_client = None

    return _openai_client


def mock_process_text(text: str) -> str:
    """Generate a pseudo processed text with injected educational keywords."""
    keywords = ["exercice", "résumé", "chapitre", "leçon"]
    paragraph = lorem.paragraph()
    words = paragraph.split()
    num_keywords = random.randint(1, 3)
    positions = random.sample(range(len(words)), num_keywords)
    for pos, keyword in zip(sorted(positions), random.choices(keywords, k=num_keywords)):
        words.insert(pos, keyword)
    return " ".join(words)


def mock_detect_type(text: str) -> str:
    """Heuristic detection of text type based on presence of keywords."""
    text_lower = text.lower()
    if "exercice" in text_lower:
        return "exercice"
    if "résumé" in text_lower or "resume" in text_lower:
        return "resume"
    if "chapitre" in text_lower or "leçon" in text_lower:
        return "cours"
    return "inconnu"

