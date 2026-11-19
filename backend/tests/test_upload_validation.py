"""
Unit and integration tests for PDF upload validation logic.
Tests rejecting empty, oversize, non-pdf extension, non-pdf MIME, and corrupt magic bytes.
"""
import pytest
from app.processors.upload_validator import validate_pdf_content
from app.core.errors import InvalidFileError, PayloadTooLargeError


def test_valid_pdf_passes_validation():
    dummy_pdf = b"%PDF-1.4\n%synthetic test content\n%%EOF"
    valid, msg = validate_pdf_content(
        filename="research_paper.pdf",
        content=dummy_pdf,
        content_type="application/pdf",
        max_size_mb=25,
    )
    assert valid is True
    assert msg == "OK"


def test_empty_file_rejected():
    with pytest.raises(InvalidFileError) as exc_info:
        validate_pdf_content(
            filename="empty.pdf",
            content=b"",
            content_type="application/pdf",
            max_size_mb=25,
        )
    assert "empty" in exc_info.value.message.lower()


def test_oversize_file_rejected():
    oversize_bytes = b"%PDF-" + b"0" * (2 * 1024 * 1024)
    with pytest.raises(PayloadTooLargeError) as exc_info:
        validate_pdf_content(
            filename="large.pdf",
            content=oversize_bytes,
            content_type="application/pdf",
            max_size_mb=1,  # 1MB limit for test
        )
    assert "exceeds" in exc_info.value.message.lower()


def test_invalid_extension_rejected():
    valid_pdf_bytes = b"%PDF-1.5 test"
    with pytest.raises(InvalidFileError) as exc_info:
        validate_pdf_content(
            filename="paper.docx",
            content=valid_pdf_bytes,
            content_type="application/pdf",
            max_size_mb=25,
        )
    assert ".pdf extension" in exc_info.value.message


def test_invalid_mime_type_rejected():
    valid_pdf_bytes = b"%PDF-1.5 test"
    with pytest.raises(InvalidFileError) as exc_info:
        validate_pdf_content(
            filename="paper.pdf",
            content=valid_pdf_bytes,
            content_type="image/png",
            max_size_mb=25,
        )
    assert "MIME type" in exc_info.value.message


def test_missing_magic_bytes_rejected():
    # File named .pdf with text content but without %PDF- magic bytes
    fake_pdf = b"NOT_A_REAL_PDF_HEADER"
    with pytest.raises(InvalidFileError) as exc_info:
        validate_pdf_content(
            filename="corrupt.pdf",
            content=fake_pdf,
            content_type="application/pdf",
            max_size_mb=25,
        )
    assert "magic bytes" in exc_info.value.message

