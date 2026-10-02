"""
File operations and validation — 03 §2, 06 §1.7, 08 §14.
Streaming file upload validation, size caps, magic bytes, hashing, and storage.
"""

import hashlib
from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile

from app.config import get_settings
from app.core.errors import (
    DuplicatePaperError,
    FileTooLargeError,
    ProjectPaperLimitError,
    UnsupportedMediaTypeError,
)
from app.database import repos
from app.database.session import get_session

PDF_MAGIC = b"%PDF-"
CHUNK_SIZE = 64 * 1024  # 64 KB streaming buffer


def validate_pdf_header(header: bytes) -> bool:
    """Validate that the file begins with the PDF magic bytes."""
    return header.startswith(PDF_MAGIC)


async def save_uploaded_pdf(
    upload_file: UploadFile,
    paper_id: str,
    project_id: str,
) -> tuple[Path, str, int]:
    """Validate and stream an uploaded PDF to disk.

    Enforces:
    - Content type (must be application/pdf or application/x-pdf)
    - Magic bytes (%PDF-)
    - Size cap (max_upload_mb from settings, enforced while streaming)
    - Project paper limit (max_papers_per_project)
    - Per-project sha256 uniqueness (no duplicate papers)

    Args:
        upload_file: FastAPI UploadFile from the request.
        paper_id: Unique paper ID.
        project_id: Target project ID.

    Returns:
        tuple of (saved_file_path, sha256_hex, total_bytes).

    Raises:
        UnsupportedMediaTypeError: If content type or magic bytes are invalid.
        FileTooLargeError: If file exceeds size cap.
        ProjectPaperLimitError: If project already has max papers.
        DuplicatePaperError: If same sha256 exists in project.
    """
    settings = get_settings()

    # 1. Content type check
    content_type = upload_file.content_type or ""
    if content_type.lower() not in ("application/pdf", "application/x-pdf", "binary/octet-stream"):
        # We allow binary/octet-stream if filename ends with .pdf, but check magic bytes strictly
        if not (upload_file.filename and upload_file.filename.lower().endswith(".pdf")):
            raise UnsupportedMediaTypeError()

    # 2. Check project paper count limit
    db = get_session()
    try:
        current_count = repos.count_papers_in_project(db, project_id)
        if current_count >= settings.max_papers_per_project:
            raise ProjectPaperLimitError(settings.max_papers_per_project)
    finally:
        db.close()

    # 3. Stream to disk while checking magic bytes, size cap, and computing sha256
    max_bytes = settings.max_upload_mb * 1024 * 1024
    uploads_dir = settings.uploads_path
    uploads_dir.mkdir(parents=True, exist_ok=True)
    target_path = uploads_dir / f"{paper_id}.pdf"

    hasher = hashlib.sha256()
    total_bytes = 0
    header_checked = False

    try:
        with open(target_path, "wb") as out_file:
            while True:
                chunk = await upload_file.read(CHUNK_SIZE)
                if not chunk:
                    break

                if not header_checked:
                    if not validate_pdf_header(chunk[:5]):
                        raise UnsupportedMediaTypeError()
                    header_checked = True

                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    raise FileTooLargeError(settings.max_upload_mb)

                hasher.update(chunk)
                out_file.write(chunk)

        if not header_checked:
            # File was completely empty
            raise UnsupportedMediaTypeError()

    except Exception:
        # Clean up partial file on validation error or disk error
        if target_path.exists():
            target_path.unlink(missing_ok=True)
        raise

    sha256_hex = hasher.hexdigest()

    # 4. Check duplicate in project
    db = get_session()
    try:
        existing = repos.get_paper_by_sha256(db, project_id, sha256_hex)
        if existing:
            # Clean up file since it's a duplicate
            target_path.unlink(missing_ok=True)
            raise DuplicatePaperError(existing.paper_id)
    finally:
        db.close()

    return target_path, sha256_hex, total_bytes


def get_paper_file_path(paper_id: str) -> Path | None:
    """Get the path to a stored paper PDF file, or None if it doesn't exist."""
    settings = get_settings()
    path = settings.uploads_path / f"{paper_id}.pdf"
    return path if path.exists() else None


def delete_paper_file(paper_id: str) -> bool:
    """Delete a stored paper PDF file."""
    path = get_paper_file_path(paper_id)
    if path and path.exists():
        path.unlink(missing_ok=True)
        return True
    return False
