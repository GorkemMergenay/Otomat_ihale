from __future__ import annotations

import re

TURKISH_CHAR_MAP = str.maketrans(
    {
        "ı": "i",
        "İ": "i",
        "ğ": "g",
        "Ğ": "g",
        "ü": "u",
        "Ü": "u",
        "ş": "s",
        "Ş": "s",
        "ö": "o",
        "Ö": "o",
        "ç": "c",
        "Ç": "c",
    }
)


def normalize_text(value: str) -> str:
    normalized = value.translate(TURKISH_CHAR_MAP).lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()
