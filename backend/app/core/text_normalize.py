"""
Text normalization — 08 §3.
Single implementation used by both the ingestion parser and the evidence validator.
All quote comparison goes through these functions.
"""

import re
import unicodedata


# Ligature replacements (03 §2)
_LIGATURES: dict[str, str] = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\ufb05": "st",
    "\ufb06": "st",
}

_LIGATURE_RE = re.compile("|".join(re.escape(k) for k in _LIGATURES))


def normalize_text(text: str) -> str:
    """Normalize text for comparison: NFKC, ligature fold, whitespace collapse, lowercase.

    Used by quote verification (04 §6) and deduplication.

    Args:
        text: Raw text from PDF or LLM output.

    Returns:
        Normalized lowercase text with collapsed whitespace.
    """
    # NFKC normalization (03 §2)
    text = unicodedata.normalize("NFKC", text)

    # Replace ligatures
    text = _LIGATURE_RE.sub(lambda m: _LIGATURES[m.group()], text)

    # Collapse whitespace (spaces, tabs, newlines)
    text = re.sub(r"\s+", " ", text).strip()

    # Lowercase for comparison
    return text.lower()


def dehyphenate(text: str) -> str:
    """Join hyphenated line breaks: 'word-\\n  continuation' → 'wordcontinuation'.

    Handles the common PDF artifact of words split across lines with a hyphen (03 §2).

    Args:
        text: Text potentially containing hyphenated line breaks.

    Returns:
        Text with hyphenated breaks joined.
    """
    return re.sub(r"(\w)-\s*\n\s*([a-z])", r"\1\2", text)


def normalize_for_quote_match(text: str) -> str:
    """Full normalization pipeline for verbatim quote matching (04 §6).

    Combines NFKC, ligature folding, dehyphenation, whitespace collapse,
    and lowercasing.

    Args:
        text: Raw text to normalize.

    Returns:
        Normalized text suitable for substring matching.
    """
    text = dehyphenate(text)
    return normalize_text(text)


def quote_in_chunk(quote: str, chunk_text: str) -> bool:
    """Check if a normalized quote is a substring of normalized chunk text (04 §6).

    Args:
        quote: The verbatim quote to verify.
        chunk_text: The chunk text to search within.

    Returns:
        True if the normalized quote is found within the normalized chunk.
    """
    norm_quote = normalize_for_quote_match(quote)
    norm_chunk = normalize_for_quote_match(chunk_text)
    return norm_quote in norm_chunk
