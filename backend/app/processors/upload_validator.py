"""
Validation logic for uploaded academic PDFs.
Enforces: non-empty, file size limit, .pdf extension, application/pdf MIME, and %PDF- magic bytes.
"""
from typing import Tuple
from app.core.errors import InvalidFileError, PayloadTooLargeError

PDF_MAGIC_BYTES = b"%PDF-"


def validate_pdf_content(
    filename: str,
    content: bytes,
    content_type: str,
    max_size_mb: int = 25,
) -> Tuple[bool, str]:
    """
    Validates uploaded file against PDF requirements.
    Returns (True, "OK") or raises specific AppException.
    """
    # 1. Check non-empty
    if not content or len(content) == 0:
        raise InvalidFileError(
            message="The uploaded file is empty (0 bytes).",
            details={"filename": filename, "size_bytes": 0},
        )

    # 2. Check maximum size
    max_bytes = max_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise PayloadTooLargeError(
            message=f"File exceeds maximum allowed upload size of {max_size_mb}MB.",
            details={"filename": filename, "file_size_bytes": len(content), "max_allowed_bytes": max_bytes},
        )

    # 3. Check file extension
    if not filename.lower().endswith(".pdf"):
        raise InvalidFileError(
            message="File must have a .pdf extension.",
            details={"filename": filename},
        )

    # 4. Check MIME type (allow standard application/pdf and x-pdf)
    valid_mimes = ["application/pdf", "application/x-pdf"]
    if content_type and content_type.lower() not in valid_mimes:
        raise InvalidFileError(
            message=f"Invalid MIME type '{content_type}'. Must be 'application/pdf'.",
            details={"content_type": content_type},
        )

    # 5. Check magic bytes (%PDF-)
    if not content.startswith(PDF_MAGIC_BYTES):
        prefix_hex = content[:8].hex() if len(content) >= 8 else content.hex()
        raise InvalidFileError(
            message="File does not contain valid PDF header magic bytes (%PDF-).",
            details={"prefix_hex": prefix_hex},
        )

    return True, "OK"

