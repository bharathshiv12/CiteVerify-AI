"""
Service: Citation Matcher
Links extracted factual claims to their directly associated in-text citations
and attaches resolved bibliography reference text.
"""
import re
from typing import List, Dict, Any, Union
from app.schemas.claim import Claim
from app.schemas.citation import Citation


def match_claims_to_citations(
    claims: List[Claim],
    citations: List[Citation],
    references: Dict[str, Union[str, Dict[str, Any]]],
) -> List[Claim]:
    """
    Links each claim to citations appearing within its sentence or attached char span.
    Populates reference_text for matched citations from the parsed bibliography dictionary.
    """
    for claim in claims:
        matched_citations: List[Citation] = []
        c_start, c_end = claim.char_span if claim.char_span else (0, 0)

        for cit in citations:
            if cit.page_number != claim.page_number:
                continue

            # Check if citation marker falls inside claim span or immediately adjacent (+- 15 chars)
            if cit.char_span:
                m_start, m_end = cit.char_span
                if (c_start - 5 <= m_start <= c_end + 15) or (c_start <= m_end <= c_end + 15):
                    # Attach bibliography text if available
                    _populate_reference_text(cit, references)
                    if cit not in matched_citations:
                        matched_citations.append(cit)
            elif cit.raw_marker in claim.claim_text:
                _populate_reference_text(cit, references)
                if cit not in matched_citations:
                    matched_citations.append(cit)

        claim.citations = matched_citations

    return claims


def _populate_reference_text(citation: Citation, references: Dict[str, Union[str, Dict[str, Any]]]):
    """
    Looks up bibliography reference string for citation marker.
    """
    if citation.reference_text:
        return

    # Numeric lookup
    if citation.marker_type == "NUMERIC" and citation.reference_index:
        key = str(citation.reference_index)
        if key in references:
            ref_val = references[key]
            citation.reference_text = ref_val.get("raw_text") if isinstance(ref_val, dict) else str(ref_val)
            return

    # Author-year lookup: scan references for author surname + year
    if citation.marker_type == "AUTHOR_YEAR":
        match = re.search(r"([A-Z][a-z]+).*?(\d{4})", citation.raw_marker)
        if match:
            surname = match.group(1).lower()
            year = match.group(2)
            for ref_key, ref_val in references.items():
                ref_str = ref_val.get("raw_text") if isinstance(ref_val, dict) else str(ref_val)
                ref_str_lower = ref_str.lower()
                if surname in ref_str_lower and year in ref_str_lower:
                    citation.reference_text = ref_str
                    return
