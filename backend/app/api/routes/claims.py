"""
Claim-level routes for inspecting details and submitting human reviews.
"""
from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.errors import NotFoundError
from app.database.repository import AbstractRepository, get_repository
from app.schemas.claim import Claim, ClaimPatchRequest
from app.schemas.verification import ClaimReviewRequest

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.get("/{claim_id}", response_model=Claim)
async def get_claim(
    claim_id: UUID,
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Returns single claim details including attached citations and evidence passages.
    """
    claim = await repo.get_claim(claim_id)
    if not claim:
        raise NotFoundError(resource="Claim", identifier=str(claim_id))
    return claim


@router.post("/{claim_id}/review", response_model=Claim)
async def review_claim(
    claim_id: UUID,
    review_req: ClaimReviewRequest,
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Applies human reviewer verdict, notes, and records review history.
    """
    claim = await repo.get_claim(claim_id)
    if not claim:
        raise NotFoundError(resource="Claim", identifier=str(claim_id))

    updated = await repo.record_human_review(
        claim_id=claim_id,
        reviewer_name=review_req.reviewer_name,
        updated_verdict=review_req.updated_verdict,
        notes=review_req.notes,
    )
    return updated


@router.patch("/{claim_id}", response_model=Claim, summary="Patch claim text and span")
async def patch_claim(
    claim_id: UUID,
    patch_req: ClaimPatchRequest,
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Updates the text boundary and content of an extracted claim (Resolves Gap 3).
    """
    claim = await repo.get_claim(claim_id)
    if not claim:
        raise NotFoundError(resource="Claim", identifier=str(claim_id))

    updated = await repo.patch_claim(
        claim_id=claim_id,
        claim_text=patch_req.claim_text,
        char_span=patch_req.char_span,
    )
    if not updated:
        raise NotFoundError(resource="Claim", identifier=str(claim_id))
    return updated


