"""Shared helpers: slugs, hashing, and date extraction."""

from __future__ import annotations

import hashlib
import re
from datetime import date

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

_DATE_RE = re.compile(
    r"\b(" + "|".join(_MONTHS) + r")\.?\s+(\d{1,2})(?:\s*[\u2013\u2014-]\s*\d{1,2})?,?\s+(\d{4})\b",
    re.IGNORECASE,
)

MONTH_NAME_RE = re.compile(r"\b(" + "|".join(_MONTHS) + r")\b", re.IGNORECASE)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def short_hash(text: str, length: int = 16) -> str:
    return sha256(text)[:length]


def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:max_len].strip("-")


def extract_date(text: str, fallback: date | None = None) -> date | None:
    """Extract the first 'Month D, YYYY' date from text; fall back if none."""
    match = _DATE_RE.search(text)
    if not match:
        return fallback
    month = _MONTHS[match.group(1).lower()]
    day = int(match.group(2))
    year = int(match.group(3))
    try:
        return date(year, month, day)
    except ValueError:
        return fallback


def iso(d: date | None) -> str | None:
    return d.isoformat() if d else None
