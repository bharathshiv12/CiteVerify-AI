"""
Dashboard routes providing aggregate analytics, verification counts, and activity feeds.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_optional_user
from app.database.repository import AbstractRepository, get_repository
from app.schemas.user import User
from app.schemas.dashboard import DashboardStats, DashboardActivity

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats, summary="Get dashboard verification metrics")
async def get_dashboard_stats(
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Returns high-level verification metrics, document counts, and reliability scores.
    """
    user_id = user.id if user else None
    return await repo.get_dashboard_stats(user_id=user_id)


@router.get("/activity", response_model=List[DashboardActivity], summary="Get recent activity events")
async def get_dashboard_activity(
    limit: int = Query(10, ge=1, le=50),
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Returns recent document processing and verification activity events.
    """
    user_id = user.id if user else None
    return await repo.get_dashboard_activity(user_id=user_id, limit=limit)
