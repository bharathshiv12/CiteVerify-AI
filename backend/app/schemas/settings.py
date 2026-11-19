"""
User settings schemas.
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class UserSettings(BaseModel):
    user_id: Optional[UUID] = None
    notify_analysis_done: bool = True
    notify_human_review_needed: bool = True
    preferred_research_provider: str = "ALL"  # ALL | CROSSREF | OPENALEX | EUROPE_PMC
    strict_numeric_comparison: bool = True
    auto_flag_outdated_years: int = Field(default=10, ge=1, le=50)
    allow_external_ai_evaluation: bool = False


class UserSettingsUpdate(BaseModel):
    notify_analysis_done: Optional[bool] = None
    notify_human_review_needed: Optional[bool] = None
    preferred_research_provider: Optional[str] = None
    strict_numeric_comparison: Optional[bool] = None
    auto_flag_outdated_years: Optional[int] = Field(default=None, ge=1, le=50)
    allow_external_ai_evaluation: Optional[bool] = None
