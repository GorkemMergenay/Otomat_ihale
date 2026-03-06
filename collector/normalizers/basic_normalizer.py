from __future__ import annotations

from classifier.text_utils import normalize_text


def normalize_title(value: str) -> str:
    return normalize_text(value)
