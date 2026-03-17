from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.category_schema import CategoryOut


class ContentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    categories: list[int] = Field(default_factory=list)


class ContentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    categories: Optional[list[int]] = None


class ContentOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None

    categories: list[CategoryOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ContentPreview(BaseModel):
    id: int
    name: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True