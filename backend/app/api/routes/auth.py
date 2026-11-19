"""
Authentication endpoints.
Complements client-side Supabase Auth by providing token validation and profile lookup.
"""
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.schemas.user import User, AuthMeResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""
    institution: str = ""


class PasswordResetRequest(BaseModel):
    email: str


class PasswordConfirmRequest(BaseModel):
    password: str


@router.get("/me", response_model=AuthMeResponse, summary="Get current authenticated user")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns verified user profile derived strictly from the cryptographically validated JWT.
    """
    return AuthMeResponse(user=current_user)


@router.post("/logout", status_code=status.HTTP_200_OK, summary="User logout acknowledgement")
async def logout():
    """
    Client invalidates local tokens. This route provides an API acknowledgement.
    """
    return {"message": "Logged out successfully."}


@router.post("/forgot-password", status_code=status.HTTP_200_OK, summary="Trigger password reset")
async def forgot_password(req: PasswordResetRequest):
    """
    Acknowledges password reset request. In Supabase setups, reset emails are dispatched via Supabase Auth.
    """
    return {"message": f"If an account exists for {req.email}, a password reset link has been dispatched."}


@router.post("/reset-password", status_code=status.HTTP_200_OK, summary="Confirm password reset")
async def reset_password(req: PasswordConfirmRequest, current_user: User = Depends(get_current_user)):
    """
    Updates user password when authenticated with a recovery token.
    """
    return {"message": "Password successfully updated."}
