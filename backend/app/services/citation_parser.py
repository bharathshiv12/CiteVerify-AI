"""
Service: Citation Parser
Parses in-text citation markers (numeric ranges and author-year) and bibliography references.
"""
import re
from typing import Dict, List, Tuple, Any, Optional
from uuid import UUID, uuid4

from app.schemas.citation import Citation


NUMERIC_CITATION_PATTERN = re.compile(r"\[(?:\s*\d+(?:\s*[-–—]\s*\d+)?\s*(?:,\s*\d+(?:\s*[-–—]\s*\d+)?)*\s*)\]")
AUTHOR_YEAR_PATTERN = re.compile(
    r"\((?:[A-Z][A-Za-z\u00C0-\u024F\s\.-]+(?:et\s+al\.?|and\s+[A-Z][A-Za-z\u00C0-\u024F\s\.-]+)?,\s*\d{4}[a-z]?(?:;\s*[A-Z][A-Za-z\u00C0-\u024F\s\.-]+(?:et\s+al\.?|and\s+[A-Z][A-Za-z\u00C0-\u024F\s\.-]+)?,\s*\d{4}[a-z]?)*)\)"
)
DOI_PATTERN = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b")
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+")
YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")

BIBLIOGRAPHY_HEADERS = [
    re.compile(r"\n\s*(?:REFERENCES|References|BIBLIOGRAPHY|Bibliography|LITERATURE CITED)\s*\n"),
    re.compile(r"\n\s*\d*\.?\s*(?:REFERENCES|References)\s*\n"),
]


def expand_numeric_range(marker_content: str) -> List[int]:
    """
    Expands strings like '1-3, 5' into [1, 2, 3, 5].
    """
    indices: List[int] = []
    clean = marker_content.strip("[]").strip()
    parts = clean.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        range_match = re.split(r"[-–—]", part)
        if len(range_match) == 2:
            try:
                start = int(range_match[0].strip())
                end = int(range_match[1].strip())
                if 0 < start <= end and (end - start) < 50:
                    indices.extend(range(start, end + 1))
                else:
                    indices.append(start)
            except ValueError:
                pass
        else:
            try:
                indices.append(int(part))
            except ValueError:
                pass
    return sorted(list(set(indices)))


def parse_in_text_citations(pages: List[Dict[str, Any]], document_id: UUID) -> List[Citation]:
    """
    Extracts all in-text citation markers across pages with exact page numbers and character spans.
    """
    citations: List[Citation] = []

    for page in pages:
        page_num = page["page_number"]
        text = page["text"]

        # 1. Numeric citations [1], [1-3], [1, 2]
        for match in NUMERIC_CITATION_PATTERN.finditer(text):
            raw_marker = match.group(0)
            char_span = [match.start(), match.end()]
            expanded = expand_numeric_range(raw_marker)
            primary_index = expanded[0] if expanded else None

            citations.append(
                Citation(
                    id=uuid4(),
                    document_id=document_id,
                    raw_marker=raw_marker,
                    marker_type="NUMERIC",
                    page_number=page_num,
                    char_span=char_span,
                    reference_index=primary_index,
                )
            )

        # 2. Author-year citations (Smith et al., 2020)
        for match in AUTHOR_YEAR_PATTERN.finditer(text):
            raw_marker = match.group(0)
            char_span = [match.start(), match.end()]

            citations.append(
                Citation(
                    id=uuid4(),
                    document_id=document_id,
                    raw_marker=raw_marker,
                    marker_type="AUTHOR_YEAR",
                    page_number=page_num,
                    char_span=char_span,
                )
            )

    return citations


def parse_bibliography_references(pages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Extracts bibliographic entries from the References section.
    Returns mapping of key (e.g. '1' or 'smith2020') -> reference metadata dictionary.
    """
    # Combine full text from all pages
    full_text = "\n".join(p["text"] for p in pages)
    ref_start_idx = -1

    for pattern in BIBLIOGRAPHY_HEADERS:
        match = pattern.search(full_text)
        if match:
            ref_start_idx = match.end()
            break

    if ref_start_idx == -1:
        # Fallback: check last 20% of text
        idx = full_text.rfind("References")
        if idx != -1:
            ref_start_idx = idx + len("References")

    if ref_start_idx == -1:
        return {}

    bib_text = full_text[ref_start_idx:]
    lines = [line.strip() for line in bib_text.split("\n") if line.strip()]

    # Group into reference items
    ref_entries: Dict[str, Dict[str, Any]] = {}
    current_key = None
    current_lines: List[str] = []

    numbered_entry_pattern = re.compile(r"^\[?(\d+)\]?[\.\s]+(.*)")

    for line in lines:
        match = numbered_entry_pattern.match(line)
        if match:
            if current_key and current_lines:
                raw_ref = " ".join(current_lines)
                ref_entries[current_key] = _parse_single_reference(current_key, raw_ref)
            current_key = match.group(1)
            current_lines = [match.group(2)]
        elif current_key is not None:
            current_lines.append(line)
        else:
            # Unnumbered author-year entry or initial line
            year_match = YEAR_PATTERN.search(line)
            if year_match and len(line) > 30:
                if current_lines:
                    raw_ref = " ".join(current_lines)
                    k = f"ref_{len(ref_entries) + 1}"
                    ref_entries[k] = _parse_single_reference(k, raw_ref)
                current_lines = [line]
                current_key = f"ref_{len(ref_entries) + 1}"
            elif current_lines:
                current_lines.append(line)

    if current_key and current_lines:
        raw_ref = " ".join(current_lines)
        ref_entries[current_key] = _parse_single_reference(current_key, raw_ref)

    return ref_entries


def _parse_single_reference(key: str, raw_reference: str) -> Dict[str, Any]:
    """
    Extracts title, authors, year, DOI, URL from raw reference text.
    """
    doi_match = DOI_PATTERN.search(raw_reference)
    doi = doi_match.group(1).rstrip(".") if doi_match else None

    url_match = URL_PATTERN.search(raw_reference)
    url = url_match.group(0).rstrip(".") if url_match else None

    year_match = YEAR_PATTERN.search(raw_reference)
    year = int(year_match.group(1)) if year_match else None

    # Title & author extraction heuristics
    authors = []
    title = raw_reference

    # Try splitting by quotes or periods
    quoted_title = re.search(r'["“]([^"”]+)["”]', raw_reference)
    if quoted_title:
        title = quoted_title.group(1)
    else:
        parts = raw_reference.split(". ")
        if len(parts) >= 3:
            # Typical format: Authors. (Year). Title. Venue.
            authors_str = parts[0]
            authors = [a.strip() for a in re.split(r",|\sand\s|&", authors_str) if a.strip()]
            title = parts[1] if len(parts[1]) > 10 else parts[2]

    return {
        "key": key,
        "raw_text": raw_reference,
        "title": title.strip(),
        "authors": authors[:5],
        "year": year,
        "doi": doi,
        "url": url,
    }


def parse_citations_and_references(
    pages: List[Dict[str, Any]],
    document_id: UUID,
) -> Tuple[List[Citation], Dict[str, Dict[str, Any]]]:
    """
    Combines in-text citation parsing and bibliography reference extraction.
    Links matched reference text to numeric in-text citations.
    """
    citations = parse_in_text_citations(pages, document_id)
    references = parse_bibliography_references(pages)

    # Attach reference text to matching numeric citations
    for cit in citations:
        if cit.marker_type == "NUMERIC" and cit.reference_index:
            ref_key = str(cit.reference_index)
            if ref_key in references:
                ref_info = references[ref_key]
                cit.reference_text = ref_info.get("raw_text")

    return citations, references
