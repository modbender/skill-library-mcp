from typing import Optional
from pydantic import BaseModel, Field


class MagicLinkRequest(BaseModel):
    email: str = Field(..., max_length=255)


class MagicLinkResponse(BaseModel):
    success: bool
    message: str


class VerifyTokenRequest(BaseModel):
    token: str


class VerifyTokenResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    message: str
