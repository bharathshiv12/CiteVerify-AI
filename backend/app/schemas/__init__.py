"""
CiteVerify Pydantic Schemas Package.
Directly derived from canonical contracts in contracts/schemas/.
"""
from app.schemas.enums import (
    VerificationVerdict,
    ProcessingStatus,
    VerificationState,
    EvidenceLevel,
    RetrievalStatus,
    PipelineStage,
)
from app.schemas.error import ErrorDetail, ErrorEnvelope
from app.schemas.document import (
    Document,
    DocumentBase,
    DocumentStatusResponse,
    DocumentAnalyzeResponse,
)
from app.schemas.citation import Citation
from app.schemas.research_paper import ResearchPaper
from app.schemas.evidence import Evidence
from app.schemas.verification import Verification, ClaimReviewRequest
from app.schemas.claim import Claim, ClaimBase, ClaimListResponse
from app.schemas.report import VerificationReport

__all__ = [
    "VerificationVerdict",
    "ProcessingStatus",
    "VerificationState",
    "EvidenceLevel",
    "RetrievalStatus",
    "PipelineStage",
    "ErrorDetail",
    "ErrorEnvelope",
    "Document",
    "DocumentBase",
    "DocumentStatusResponse",
    "DocumentAnalyzeResponse",
    "Citation",
    "ResearchPaper",
    "Evidence",
    "Verification",
    "ClaimReviewRequest",
    "Claim",
    "ClaimBase",
    "ClaimListResponse",
    "VerificationReport",
]
