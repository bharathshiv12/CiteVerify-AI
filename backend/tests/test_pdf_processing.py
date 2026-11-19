"""
Unit and integration tests for PDF upload validation, storage, PyMuPDF extraction, and scanned PDF detection.
All test PDFs are generated dynamically in memory via ReportLab (no committed binaries).
"""
import io
from uuid import uuid4
import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

from app.services.document_processor import extract_text_from_pdf, PDFProcessingError
from app.processors.upload_validator import validate_pdf_content
from app.core.errors import InvalidFileError, PayloadTooLargeError
from app.storage.file_storage import LocalFileStorage


def create_dynamic_pdf(pages_text: list) -> bytes:
    """Generates an in-memory PDF with provided text on each page."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    for text in pages_text:
        c.drawString(100, 700, text)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


def create_scanned_style_pdf() -> bytes:
    """Generates an image-only PDF lacking an extractable text layer."""
    buf = io.BytesIO()
    # Create a small dummy image
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img_buf = io.BytesIO()
    img.save(img_buf, format="PNG")
    img_buf.seek(0)

    c = canvas.Canvas(buf, pagesize=letter)
    # Draw image without text
    from reportlab.lib.utils import ImageReader
    c.drawImage(ImageReader(img_buf), 100, 500, width=200, height=200)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


def test_valid_pdf_multi_page_extraction():
    pdf_bytes = create_dynamic_pdf([
        "Page 1: Transformers achieve 28.4 BLEU score on English-German [1].",
        "Page 2: Our attention mechanism reduces latency by 15% (Vaswani et al., 2017).",
    ])

    result = extract_text_from_pdf(pdf_bytes)
    assert result["status"] == "SUCCESS"
    assert result["page_count"] == 2
    assert result["is_scanned"] is False
    assert len(result["pages"]) == 2
    assert "BLEU score" in result["pages"][0]["text"]
    assert "attention mechanism" in result["pages"][1]["text"]
    assert result["pages"][0]["page_number"] == 1
    assert result["pages"][1]["page_number"] == 2
    assert result["pages"][0]["char_end"] < result["pages"][1]["char_start"]


def test_scanned_pdf_detection():
    pdf_bytes = create_scanned_style_pdf()
    result = extract_text_from_pdf(pdf_bytes)
    assert result["status"] == "SUCCESS"
    assert result["is_scanned"] is True
    assert result["total_char_count"] < 50


def test_empty_bytes_raises_error():
    with pytest.raises(PDFProcessingError, match="empty"):
        extract_text_from_pdf(b"")


def test_corrupted_pdf_raises_error():
    with pytest.raises(PDFProcessingError, match="corrupted"):
        extract_text_from_pdf(b"%PDF-1.4\nCorrupted random payload that is not valid PDF binary data!")


@pytest.mark.asyncio
async def test_file_storage_local_crud():
    storage = LocalFileStorage()
    rel_path = f"test_folder/{uuid4()}.pdf"
    content = b"%PDF-1.5 test document stream"

    # Save
    saved_path = await storage.save_file(rel_path, content)
    assert saved_path == rel_path
    assert await storage.file_exists(rel_path) is True

    # Read
    read_bytes = await storage.get_file(rel_path)
    assert read_bytes == content

    # Delete
    deleted = await storage.delete_file(rel_path)
    assert deleted is True
    assert await storage.file_exists(rel_path) is False


@pytest.mark.asyncio
async def test_file_storage_blocks_path_traversal():
    storage = LocalFileStorage()
    with pytest.raises(ValueError, match="Path traversal"):
        await storage.save_file("../../etc/passwd", b"malicious")
