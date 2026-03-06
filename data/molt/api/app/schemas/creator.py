from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class CreatorBase(BaseModel):
    email: EmailStr = Field(..., max_length=255)


class CreatorCreate(CreatorBase):
    pass


class CreatorUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=255)


class CreatorResponse(CreatorBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
