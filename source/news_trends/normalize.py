"""Text normalization: strip email metadata/boilerplate and fix encoding artifacts."""

from __future__ import annotations

import re
import unicodedata

# Common mojibake / smart-punctuation fixes seen in exported email digests.
_REPLACEMENTS = {
    "\u00e2\u20ac\u201c": "\u2013",  # â€“ -> –
    "\u00e2\u20ac\u201d": "\u2014",  # â€” -> —
    "\u00e2\u20ac\u2122": "\u2019",  # â€™ -> ’
    "\u00e2\u20ac\u0153": "\u201c",  # â€œ -> “
    "\u00e2\u20ac\u009d": "\u201d",  # â€<9d> -> ”
    "\u00e2\u20ac\u02dc": "\u2018",  # â€˜ -> ‘
    "\u00c2\u00a0": " ",             # Â  -> nbsp/space
    "\u00a0": " ",                   # nbsp -> space
}

_METADATA_PREFIXES = ("**From:**", "**To:**", "**Cc:**", "**Date:**", "**Folder:**", "**Message ID:**")

_FOOTER_MARKERS = (
    "sources cited:",
    "curated for",
    "sent by copilot",
    "## web source links",
    "compiled from",
    "compiled for",
)


def fix_encoding(text: str) -> str:
    for bad, good in _REPLACEMENTS.items():
        text = text.replace(bad, good)
    return unicodedata.normalize("NFC", text)


def strip_email_metadata(text: str) -> str:
    """Remove the email header block (everything up to and including the first '---')."""
    lines = text.splitlines()
    out: list[str] = []
    in_header = False
    cut = 0
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(_METADATA_PREFIXES):
            in_header = True
        if in_header and stripped == "---":
            cut = idx + 1
            break
    return "\n".join(lines[cut:]) if cut else text


def strip_footer(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        if line.strip().lstrip("*_# ").lower().startswith(_FOOTER_MARKERS):
            break
        out.append(line)
    return "\n".join(out)


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_digest(text: str) -> str:
    text = fix_encoding(text)
    text = strip_email_metadata(text)
    text = strip_footer(text)
    return normalize_whitespace(text)


def normalize_title(title: str) -> str:
    """Lowercased, punctuation-light form used for title-similarity hashing."""
    title = fix_encoding(title).lower()
    title = re.sub(r"[^a-z0-9 ]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()
