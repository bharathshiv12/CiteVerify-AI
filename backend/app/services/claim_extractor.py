"""
Service: Claim Extractor
Extracts factual, testable statements in academic text asserting empirical findings,
measurements, or scientific conclusions using transparent heuristics.
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID, uuid4

from app.schemas.claim import Claim
from app.schemas.citation import Citation
from app.schemas.enums import VerificationState
from app.services.citation_parser import NUMERIC_CITATION_PATTERN, AUTHOR_YEAR_PATTERN


# Scientific assertion cue patterns
EMPIRICAL_CUES = [
    re.compile(r"\b(?:achieve[ds]?|outperform[eds]?|demonstrate[ds]?|observe[ds]?|improve[ds]?|increase[ds]?|decrease[ds]?|reduce[ds]?|require[ds]?|report[eds]?|obtain[eds]?|yield[eds]?)\b", re.IGNORECASE),
    re.compile(r"\b(?:results?\s+(?:show|indicate|confirm|demonstrate|prove)s?)\b", re.IGNORECASE),
    re.compile(r"\b(?:we\s+found\s+that|our\s+(?:experiments?|findings?)\s+(?:show|demonstrate|reveal))\b", re.IGNORECASE),
    re.compile(r"\b(?:statistically\s+significant|p\s*[<=]\s*0?\.\d+)\b", re.IGNORECASE),
    re.compile(r"\b\d+(?:\.\d+)?\s*%(?!\w)|\b\d+(?:\.\d+)?\s*(?:percent|fold|x|ms|seconds?|dB|BLEU|F1|accuracy|million|billion)\b", re.IGNORECASE),
    re.compile(r"\b(?:superior\s+to|higher\s+than|lower\s+than|faster\s+than)\b", re.IGNORECASE),
]

# Section headers to skip (we don't extract claims from the References section itself)
SKIP_SECTIONS = [
    re.compile(r"^(?:REFERENCES|References|BIBLIOGRAPHY|Bibliography|ACKNOWLEDGMENTS|Acknowledgments)\b")
]


def split_into_sentences(text: str) -> List[Dict[str, Any]]:
    """
    Splits text into sentences while tracking exact character offsets.
    Protects common scientific abbreviations (e.g., et al., e.g., i.e., Fig., Eq., Dr., Prof., vs.).
    """
    # Replace abbreviation periods with temporary placeholder
    abbr_pattern = re.compile(r"\b(et\s+al|e\.g|i\.e|Fig|Eq|Dr|Prof|vs|vol|no|pp|ref)\.", re.IGNORECASE)
    protected = abbr_pattern.sub(r"\1__DOT__", text)

    # Sentence boundary regex: punctuation followed by whitespace and capital letter
    sentence_boundary = re.compile(r'([.!?])(?:\s+(?=[A-Z0-9"\'\(\[]|$))')

    sentences = []
    start = 0

    for match in sentence_boundary.finditer(protected):
        end = match.end()
        raw_sentence = text[start:end].strip()
        if len(raw_sentence) >= 20:
            sentences.append({
                "text": raw_sentence,
                "start": start,
                "end": start + len(raw_sentence),
            })
        start = end

    if start < len(text):
        remaining = text[start:].strip()
        if len(remaining) >= 20:
            sentences.append({
                "text": remaining,
                "start": start,
                "end": start + len(remaining),
            })

    return sentences


def is_empirical_claim(sentence: str) -> Tuple[bool, str]:
    """
    Heuristic check whether sentence constitutes an empirical or factual scientific claim.
    Returns (is_claim, cue_type).
    """
    # Check for quantitative or empirical cues
    for cue in EMPIRICAL_CUES:
        match = cue.search(sentence)
        if match:
            return True, match.group(0)

    # Check if sentence contains citation markers attached to an assertion
    has_numeric = bool(NUMERIC_CITATION_PATTERN.search(sentence))
    has_author_year = bool(AUTHOR_YEAR_PATTERN.search(sentence))
    if has_numeric or has_author_year:
        # If it also contains comparison or assertive verbs
        if re.search(r"\b(?:is|are|was|were|has|have|had|shows?|proves?|indicates?|leads?|caused?|connects?|proposes?|evaluates?|uses?|finds?|found)\b", sentence, re.IGNORECASE):
            return True, "citation_backed_statement"

    return False, ""


def extract_claims(
    pages: List[Dict[str, Any]],
    document_id: UUID,
    all_citations: Optional[List[Citation]] = None,
) -> List[Claim]:
    """
    Extracts factual, testable claims from document pages using transparent heuristics.
    Links citations attached within the narrowest sentence scope.
    """
    claims: List[Claim] = []
    seen_texts = set()

    for page in pages:
        page_num = page["page_number"]
        page_text = page["text"]

        # Check if page is purely references
        first_line = page_text.strip().split("\n")[0] if page_text.strip() else ""
        if any(skip.search(first_line) for skip in SKIP_SECTIONS):
            continue

        # Identify start offset of references section on this page if present
        ref_header_match = re.search(r"(?:^|\n)\s*(?:REFERENCES|References|BIBLIOGRAPHY|Bibliography)\b", page_text)
        ref_offset = ref_header_match.start() if ref_header_match else len(page_text)

        sentences = split_into_sentences(page_text)

        for sent in sentences:
            # Skip sentences that occur inside the references / bibliography section
            if sent["start"] >= ref_offset:
                continue

            # If sentence straddles into references header, trim it before the header
            if sent["end"] > ref_offset:
                sent["text"] = page_text[sent["start"]:ref_offset].strip()
                sent["end"] = ref_offset
                if len(sent["text"]) < 20:
                    continue

            sentence_text = sent["text"]

            # Avoid duplicates
            clean_norm = re.sub(r"\s+", " ", sentence_text.strip().lower())
            if clean_norm in seen_texts:
                continue

            is_claim, cue = is_empirical_claim(sentence_text)
            if not is_claim:
                continue

            seen_texts.add(clean_norm)

            # Find citations within this exact sentence
            attached_citations: List[Citation] = []
            if all_citations:
                for cit in all_citations:
                    if cit.page_number == page_num and cit.char_span:
                        c_start, c_end = cit.char_span
                        if sent["start"] <= c_start <= sent["end"]:
                            attached_citations.append(cit)

            # Clean claim text (strip outer whitespace, keep citation brackets)
            claim_id = uuid4()
            char_span = [sent["start"], sent["end"]]

            claims.append(
                Claim(
                    id=claim_id,
                    document_id=document_id,
                    claim_text=sentence_text,
                    page_number=page_num,
                    char_span=char_span,
                    citations=attached_citations,
                    verdict=None,
                    verification_state=VerificationState.PENDING,
                    confidence=0.0,
                    rationale=f"Heuristically extracted factual assertion via empirical cue: '{cue}'.",
                    evidence=[],
                    needs_human_review=False,
                    review_reasons=[],
                )
            )

    return claims
