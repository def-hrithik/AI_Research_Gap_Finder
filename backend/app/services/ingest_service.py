"""
Ingestion Service — 03 §1–6, 06 §3, 10 Phase 2–7.
Orchestrates PDF ingestion pipeline:
Extract → Sections → Metadata → Chunk → Embed → Vector Store Upsert.
"""

from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.errors import AppError, IngestError
from app.core.ids import new_id
from app.core.logging import ctx_paper_id, ctx_project_id
from app.database import repos
from app.database.qdrant import get_vector_store
from app.database.session import get_session
from app.embeddings.embedder import get_embedder
from app.ingestion.chunker import Chunker, build_embedding_text
from app.ingestion.metadata_extractor import extract_metadata_heuristics
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.section_detector import detect_sections
from app.services.job_service import submit_job, update_job_stage

logger = logging.getLogger("rgf.services.ingest")


def start_paper_ingestion(
    project_id: str,
    paper_id: str,
    file_path: Path,
    filename: str,
    db: Session,
) -> str:
    """Create an INGEST_PAPER job and submit it to the background runner.

    Returns:
        job_id of the queued background job.
    """
    job_id = new_id("job")
    repos.create_job(
        db=db,
        job_id=job_id,
        project_id=project_id,
        paper_id=paper_id,
        job_type="INGEST_PAPER",
    )

    # Submit to thread pool
    submit_job(
        job_id,
        _run_ingest_pipeline,
        paper_id=paper_id,
        project_id=project_id,
        file_path=str(file_path),
        filename=filename,
    )

    return job_id


def _run_ingest_pipeline(
    job_id: str,
    db: Session,
    paper_id: str,
    project_id: str,
    file_path: str,
    filename: str,
) -> dict[str, Any]:
    """Execute the end-to-end ingestion pipeline in a background worker."""
    ctx_paper_id.set(paper_id)
    ctx_project_id.set(project_id)
    settings = get_settings()

    try:
        # --- Stage 1: PARSING ---
        update_job_stage(db, job_id, stage="PARSING", progress=0.15)
        repos.update_paper_status(db, paper_id, status="PARSING")

        parsed = parse_pdf(
            file_path=file_path,
            min_chars_per_page=settings.min_chars_per_page,
            max_pages=settings.max_pdf_pages,
        )

        repos.update_paper_status(
            db, paper_id, status="PARSING", page_count=parsed.page_count
        )

        # --- Stage 2: SECTIONS & METADATA ---
        update_job_stage(db, job_id, stage="METADATA", progress=0.35)

        section_result = detect_sections(parsed)
        sections = section_result.sections
        quality = section_result.quality

        meta = extract_metadata_heuristics(parsed, filename, sections)

        # Update paper with discovered metadata
        repos.update_paper_status(
            db,
            paper_id,
            status="PARSING",
            title=meta.title or Path(filename).stem,
            authors=meta.authors,
            year=meta.year,
            doi=meta.doi,
            abstract=meta.abstract,
            section_detection_quality=quality,
            metadata_confidence=meta.field_confidence.title if meta.field_confidence else 0.5,
        )

        # --- Stage 3: CHUNKING ---
        update_job_stage(db, job_id, stage="CHUNKING", progress=0.55)
        repos.update_paper_status(db, paper_id, status="CHUNKING")

        chunker = Chunker(
            target_tokens=settings.chunk_target_tokens,
            max_tokens=settings.chunk_max_tokens,
            min_tokens=settings.chunk_min_tokens,
            overlap_sentences=settings.chunk_overlap_sentences,
        )

        paper = repos.get_paper(db, paper_id)
        current_title = paper.title if paper else meta.title
        current_authors = paper.authors if paper else meta.authors
        current_year = paper.year if paper else meta.year

        chunks = chunker.chunk_paper(
            paper_id=paper_id,
            project_id=project_id,
            title=current_title,
            authors=current_authors,
            year=current_year,
            sections=sections,
        )

        # Batch insert chunks into SQLite
        chunk_dicts = [
            {
                "chunk_id": c.chunk_id,
                "paper_id": c.paper_id,
                "project_id": c.project_id,
                "chunk_index": c.chunk_index,
                "section_heading": c.section_heading,
                "chunk_type": c.chunk_type,
                "page": c.page,
                "page_end": c.page_end,
                "text": c.text,
                "token_count": c.token_count,
                "is_table": c.is_table,
                "has_future_cue": c.has_future_cue,
                "has_limitation_cue": c.has_limitation_cue,
                "embedding_model": settings.embedding_model,
                "created_at": datetime.now(timezone.utc),
            }
            for c in chunks
        ]
        repos.create_chunks_batch(db, chunk_dicts)

        # --- Stage 4: EMBEDDING ---
        update_job_stage(db, job_id, stage="EMBEDDING", progress=0.75)
        repos.update_paper_status(db, paper_id, status="EMBEDDING")

        # Build contextual embedding texts: "{title} | {chunk_type} | {section_heading}\n{text}"
        embed_texts = [
            build_embedding_text(c.title, c.chunk_type, c.section_heading, c.text)
            for c in chunks
        ]

        embedder = get_embedder()
        vectors = embedder.embed_documents(embed_texts)

        # --- Stage 5: INDEXING (Qdrant) ---
        update_job_stage(db, job_id, stage="INDEXING", progress=0.90)

        vs = get_vector_store()
        vs.upsert_chunks(chunks, vectors, source_filename=filename)

        # Mark paper as INDEXED (05 §2)
        repos.update_paper_status(db, paper_id, status="INDEXED")
        logger.info("Paper %s fully indexed with %d chunks", paper_id, len(chunks))

        # --- Stage 6: STRUCTURED ANALYSIS ---
        try:
            from app.services.analysis_service import extract_paper_analysis_heuristically
            analysis_payload = extract_paper_analysis_heuristically(paper, chunks)
            ana_id = new_id("ana")
            repos.create_analysis(
                db=db,
                analysis_id=ana_id,
                paper_id=paper_id,
                prompt_version="1.0.0",
                llm_model="heuristic-extractor",
                payload=analysis_payload,
                status="COMPLETED",
            )
            repos.update_paper_status(db, paper_id, status="ANALYZED")
            logger.info("Paper %s structured analysis completed", paper_id)
        except Exception as ana_err:
            logger.warning("Auto-analysis failed for %s (non-fatal): %s", paper_id, ana_err)

        return {
            "paper_id": paper_id,
            "chunks_count": len(chunks),
            "pages_count": parsed.page_count,
            "title": current_title,
        }

    except Exception as exc:
        logger.exception("Pipeline failed for paper %s: %s", paper_id, exc)
        code = getattr(exc, "code", "INGEST_FAILED")
        message = getattr(exc, "message", str(exc))

        # Rollback: mark paper FAILED, delete chunks and vectors
        try:
            repos.update_paper_status(
                db, paper_id, status="FAILED", error_code=code, error_message=message
            )
            repos.delete_chunks_by_paper(db, paper_id)
            vs = get_vector_store()
            vs.delete_by_paper(paper_id)
        except Exception as cleanup_err:
            logger.warning("Cleanup error during ingest rollback: %s", cleanup_err)

        raise IngestError(code=code, message=message)
