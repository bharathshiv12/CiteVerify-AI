"""
Service: Document Processor
Extracts raw text per page using PyMuPDF, determines page counts,
calculates character offsets, and detects scanned/image-only PDFs.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
import pymupdf  # PyMuPDF


class PDFProcessingError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def extract_text_from_pdf(pdf_bytes: bytes, document_id: Optional[UUID] = None) -> Dict[str, Any]:
    """
    Extracts text per page from PDF bytes using PyMuPDF.
    Detects encrypted, corrupted, empty, and scanned PDFs.
    Honesty rule: No OCR is claimed or executed.
    """
    if not pdf_bytes or len(pdf_bytes) == 0:
        raise PDFProcessingError("EMPTY_FILE", "Uploaded PDF file is completely empty (0 bytes).")

    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise PDFProcessingError("CORRUPTED_PDF", f"Failed to parse PDF binary. File is corrupted: {e}")

    try:
        # Check password protection
        if doc.is_encrypted:
            raise PDFProcessingError("PASSWORD_PROTECTED", "PDF is password-protected or encrypted.")

        page_count = len(doc)
        if page_count == 0:
            raise PDFProcessingError("EMPTY_DOCUMENT", "PDF contains zero pages.")

        pages_data: List[Dict[str, Any]] = []
        total_text_length = 0
        total_images = 0
        current_offset = 0

        for page_idx in range(page_count):
            page_num = page_idx + 1
            page = doc[page_idx]

            page_text = page.get_text("text") or ""
            # Clean null characters if any
            page_text = page_text.replace("\x00", "")
            char_count = len(page_text)

            # Count embedded images for scanned detection
            image_list = page.get_images(full=True)
            total_images += len(image_list)

            start_offset = current_offset
            end_offset = current_offset + char_count

            pages_data.append({
                "page_number": page_num,
                "text": page_text,
                "char_count": char_count,
                "char_start": start_offset,
                "char_end": end_offset,
            })

            current_offset = end_offset + 1  # 1 for newline separator between pages
            total_text_length += char_count

        # Scanned heuristic:
        # If document has pages, average extracted text is less than 50 chars per page,
        # but contains images, it is likely a scanned/image PDF lacking an OCR text layer.
        avg_chars_per_page = total_text_length / max(page_count, 1)
        is_scanned = bool(avg_chars_per_page < 50 and total_images > 0)
        # Even without images, if text is virtually 0 on a multi-page document
        if avg_chars_per_page < 10:
            is_scanned = True

        full_text = "\n".join(p["text"] for p in pages_data)

        return {
            "page_count": page_count,
            "pages": pages_data,
            "full_text": full_text,
            "is_scanned": is_scanned,
            "total_char_count": total_text_length,
            "status": "SUCCESS",
            "error": None,
        }
    finally:
        doc.close()
