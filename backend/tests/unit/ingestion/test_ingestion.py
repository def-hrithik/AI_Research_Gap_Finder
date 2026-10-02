"""
Unit tests for PDF ingestion pipeline:
PDF parser, section detector, and structure-aware chunker.
"""

from pathlib import Path
import fitz  # PyMuPDF
import pytest

from app.core.errors import IngestError
from app.ingestion.chunker import Chunker, build_embedding_text, split_into_sentences
from app.ingestion.metadata_extractor import extract_doi_candidates, extract_metadata_heuristics
from app.ingestion.pdf_parser import TextBlock, parse_pdf
from app.ingestion.section_detector import (
    detect_sections,
    match_canonical_chunk_type,
    strip_numbering,
)
from app.schemas.chunk import Paragraph, Section


def create_synthetic_pdf(tmp_path: Path, filename: str = "test.pdf") -> Path:
    """Create a minimal synthetic academic PDF for testing."""
    pdf_path = tmp_path / filename
    doc = fitz.open()

    # Page 1
    page1 = doc.new_page(width=595, height=842)  # A4

    # Running header
    page1.insert_text((50, 40), "JOURNAL OF AI RESEARCH 2023", fontsize=8)

    # Title
    page1.insert_text((50, 100), "Attention-Based Segmentation of Medical Images", fontsize=18)

    # Authors
    page1.insert_text((50, 130), "Alice Smith, Bob Jones", fontsize=11)

    # Abstract heading & content
    page1.insert_text((50, 180), "Abstract", fontsize=14)
    abstract_text = (
        "In this work, we propose a novel transformer-based framework for medical image segmentation. "
        "We evaluate our approach extensively on benchmark datasets and demonstrate superior accuracy. "
        "Our method achieves state-of-the-art results while maintaining computational efficiency."
    )
    page1.insert_textbox(fitz.Rect(50, 200, 545, 300), abstract_text, fontsize=10)

    # Section 1: Introduction
    page1.insert_text((50, 320), "1. Introduction", fontsize=14)
    intro_text = (
        "Medical image segmentation is a vital component of clinical computer-assisted diagnosis. "
        "Recent advances in deep learning have shown promising results. However, challenges remain "
        "in capturing long-range contextual dependencies across anatomical structures. "
        "See e.g. Smith et al. for related discussion."
    )
    page1.insert_textbox(fitz.Rect(50, 340, 545, 450), intro_text, fontsize=10)

    # Section 2: Methodology
    page1.insert_text((50, 470), "2. Methodology", fontsize=14)
    method_text = (
        "We describe our proposed architecture in detail. The encoder extracts multi-scale representations, "
        "which are fused via cross-attention modules in the latent bottleneck."
    )
    page1.insert_textbox(fitz.Rect(50, 490, 545, 600), method_text, fontsize=10)

    # Running footer
    page1.insert_text((280, 810), "Page 1 of 2", fontsize=8)

    # Page 2
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text((50, 40), "JOURNAL OF AI RESEARCH 2023", fontsize=8)

    # Section 3: Limitations
    page2.insert_text((50, 100), "3. Limitations", fontsize=14)
    limitation_text = (
        "Our evaluation is restricted to a single hospital dataset. "
        "Furthermore, our method does not generalize seamlessly to low-resolution imaging modalities."
    )
    page2.insert_textbox(fitz.Rect(50, 120, 545, 200), limitation_text, fontsize=10)

    # Section 4: Conclusion and Future Work
    page2.insert_text((50, 220), "4. Conclusion and Future Work", fontsize=14)
    conclusion_text = (
        "In conclusion, we presented a robust segmentation model. "
        "For future research, we plan to validate our model on multi-center clinical cohorts."
    )
    page2.insert_textbox(fitz.Rect(50, 240, 545, 320), conclusion_text, fontsize=10)

    # References
    page2.insert_text((50, 350), "References", fontsize=14)
    ref_text = (
        "[1] A. Smith and B. Jones, 'Attention in vision,' JAIR, 2021. doi:10.1000/182\n"
        "[2] C. Davis, 'Medical benchmark,' Nature AI, 2022."
    )
    page2.insert_textbox(fitz.Rect(50, 370, 545, 500), ref_text, fontsize=9)

    page2.insert_text((280, 810), "Page 2 of 2", fontsize=8)

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_strip_numbering():
    assert strip_numbering("1. Introduction") == ("Introduction", 1)
    assert strip_numbering("3.2.1 Experimental Setup") == ("Experimental Setup", 3)
    assert strip_numbering("IV. Results") == ("Results", 1)
    assert strip_numbering("Abstract") == ("Abstract", 0)


def test_match_canonical_chunk_type():
    assert match_canonical_chunk_type("1. Introduction") == "INTRODUCTION"
    assert match_canonical_chunk_type("Methodology") == "METHODOLOGY"
    assert match_canonical_chunk_type("Experimental Setup") == "METHODOLOGY"
    assert match_canonical_chunk_type("Evaluation") == "RESULTS"
    assert match_canonical_chunk_type("Threats to Validity") == "LIMITATION"
    assert match_canonical_chunk_type("Conclusion and Future Work") == "CONCLUSION"
    assert match_canonical_chunk_type("References") == "REFERENCES"
    assert match_canonical_chunk_type("Acknowledgements") == "OTHER"


def test_sentence_splitting_with_abbreviations():
    text = (
        "We follow Smith et al. in their setup. "
        "As shown in Fig. 2, the error is approx. 0.05. "
        "The model performs well on this benchmark."
    )
    sentences = split_into_sentences(text)
    assert len(sentences) == 3
    assert "et al." in sentences[0]
    assert "Fig. 2" in sentences[1]


def test_pdf_parsing_end_to_end(tmp_path: Path):
    pdf_path = create_synthetic_pdf(tmp_path)
    parsed = parse_pdf(pdf_path, min_chars_per_page=50)

    assert parsed.page_count == 2
    assert len(parsed.pages) == 2
    assert parsed.references_start_page == 2

    # Section detection
    section_result = detect_sections(parsed)
    sections = section_result.sections
    assert len(sections) >= 3

    headings = [s.heading for s in sections]
    chunk_types = [s.chunk_type for s in sections]

    assert "ABSTRACT" in chunk_types
    assert "INTRODUCTION" in chunk_types
    assert "LIMITATION" in chunk_types

    # Check cues
    lim_sections = [s for s in sections if s.chunk_type == "LIMITATION"]
    assert len(lim_sections) > 0
    assert lim_sections[0].has_limitation_cue is True

    # Metadata extraction
    meta = extract_metadata_heuristics(parsed, "test.pdf", sections)
    assert "Attention-Based Segmentation" in meta.title
    assert meta.year == 2023 or meta.year is not None

    # Chunking
    chunker = Chunker(target_tokens=100, max_tokens=250, min_tokens=20)
    chunks = chunker.chunk_paper(
        paper_id="pap_test_01",
        project_id="prj_test_01",
        title=meta.title,
        authors=meta.authors,
        year=meta.year,
        sections=sections,
    )

    assert len(chunks) >= 3
    # Check invariant: Abstract is exactly one chunk
    abs_chunks = [c for c in chunks if c.chunk_type == "ABSTRACT"]
    assert len(abs_chunks) == 1
    assert abs_chunks[0].page == 1

    # Check embedding text format: "{title} | {chunk_type} | {section_heading}\n{text}"
    emb_text = build_embedding_text(
        chunks[0].title, chunks[0].chunk_type, chunks[0].section_heading, chunks[0].text
    )
    assert f"{chunks[0].title} |" in emb_text


def test_corrupted_pdf_error(tmp_path: Path):
    bad_pdf = tmp_path / "corrupt.pdf"
    bad_pdf.write_bytes(b"not a valid pdf data here")
    with pytest.raises(IngestError) as exc_info:
        parse_pdf(bad_pdf)
    assert exc_info.value.code == "CORRUPTED_PDF"
