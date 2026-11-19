"""
User settings routes for managing analysis preferences, notification flags, and thresholds.
"""
from uuid import UUID, uuid5, NAMESPACE_DNS
from typing import Optional
from fastapi import APIRouter, Depends

from app.core.dependencies import get_optional_user
from app.database.repository import AbstractRepository, get_repository
from app.schemas.user import User
from app.schemas.settings import UserSettings, UserSettingsUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])

DEFAULT_ANON_USER_ID = uuid5(NAMESPACE_DNS, "anonymous.citeverify.local")


@router.get("", response_model=UserSettings, summary="Get user preferences and verification settings")
async def get_settings(
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Returns user configuration preferences for notification, providers, and outdated thresholds.
    """
    user_id = user.id if user else DEFAULT_ANON_USER_ID
    return await repo.get_user_settings(user_id)


@router.put("", response_model=UserSettings, summary="Update user preferences")
async def update_settings(
    update_data: UserSettingsUpdate,
    user: Optional[User] = Depends(get_optional_user),
    repo: AbstractRepository = Depends(get_repository),
):
    """
    Updates preferences for the current user.
    """
    user_id = user.id if user else DEFAULT_ANON_USER_ID
    return await repo.update_user_settings(user_id, update_data)
