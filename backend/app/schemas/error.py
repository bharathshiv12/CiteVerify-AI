"""
Error response schemas matching contracts/schemas/error.schema.json.
"""
from typing import Any, Dict
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable description of error")
    details: Dict[str, Any] = Field(default_factory=dict, description="Structured metadata")
    request_id: str = Field(..., description="Unique request tracing UUID")


class ErrorEnvelope(BaseModel):
    error: ErrorDetail

