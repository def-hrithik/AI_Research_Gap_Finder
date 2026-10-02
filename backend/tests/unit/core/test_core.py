"""
Tests for core modules.
"""
import pytest

from app.core.ids import new_id, chunk_id
from app.core.text_normalize import (
    normalize_text,
    dehyphenate,
    normalize_for_quote_match,
    quote_in_chunk,
)
from app.core.constants import NOT_STATED, INSUFFICIENT_EVIDENCE_MESSAGE


class TestIds:
    """Test ID generation — 05 §1."""

    def test_new_id_has_prefix(self):
        """new_id generates '{prefix}_{8hex}'."""
        result = new_id("gap")
        assert result.startswith("gap_")
        assert len(result) == 4 + 8  # prefix + underscore + 8 hex chars

    def test_new_id_unique(self):
        """Two calls produce different IDs."""
        a = new_id("prj")
        b = new_id("prj")
        assert a != b

    def test_chunk_id_format(self):
        """chunk_id is deterministic: 'chk_{paper_id}_{index:04d}'."""
        result = chunk_id("pap_a1b2c3d4", 14)
        assert result == "chk_pap_a1b2c3d4_0014"

    def test_chunk_id_zero_padded(self):
        result = chunk_id("pap_ff00aa11", 0)
        assert result == "chk_pap_ff00aa11_0000"

    def test_chunk_id_large_index(self):
        result = chunk_id("pap_ff00aa11", 9999)
        assert result == "chk_pap_ff00aa11_9999"


class TestTextNormalize:
    """Test text normalization — 08 §3, 04 §6."""

    def test_nfkc_normalization(self):
        """NFKC normalizes unicode characters."""
        text = "ﬁne ﬂow"
        result = normalize_text(text)
        assert "fi" in result
        assert "fl" in result

    def test_whitespace_collapse(self):
        """Multiple spaces, tabs, newlines → single space."""
        text = "hello   world\n\ttab"
        result = normalize_text(text)
        assert result == "hello world tab"

    def test_lowercase(self):
        result = normalize_text("Hello WORLD")
        assert result == "hello world"

    def test_dehyphenate(self):
        """Join hyphenated line breaks."""
        text = "evalu-\n  ation"
        result = dehyphenate(text)
        assert "evaluation" in result

    def test_dehyphenate_preserves_regular_hyphens(self):
        """Don't break regular hyphenated words."""
        text = "state-of-the-art"
        result = dehyphenate(text)
        assert result == "state-of-the-art"

    def test_quote_in_chunk_basic(self):
        """Quote found in chunk text after normalization."""
        chunk = "Our evaluation is restricted to a single hospital dataset from Rao et al."
        quote = "evaluation is restricted to a single hospital dataset"
        assert quote_in_chunk(quote, chunk)

    def test_quote_in_chunk_case_insensitive(self):
        chunk = "CNN-based method achieves SOTA results"
        quote = "cnn-based method achieves sota results"
        assert quote_in_chunk(quote, chunk)

    def test_quote_in_chunk_with_ligatures(self):
        chunk = "the ﬁrst ﬁnding shows eﬃcacy"
        quote = "the first finding shows efficacy"
        assert quote_in_chunk(quote, chunk)

    def test_quote_not_in_chunk(self):
        chunk = "This paper studies transformers."
        quote = "CNN architecture performs well"
        assert not quote_in_chunk(quote, chunk)


class TestConstants:
    """Test constant values match the docs."""

    def test_not_stated(self):
        assert NOT_STATED == "Not explicitly stated in the provided paper."

    def test_insufficient_evidence_message(self):
        assert "Insufficient evidence" in INSUFFICIENT_EVIDENCE_MESSAGE
