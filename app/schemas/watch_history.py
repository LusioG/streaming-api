from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.content_schema import ContentPreview

class WatchHistoryCreate(BaseModel):
    content_id: int
    progress: int

class WatchHistoryUpdateProgress(BaseModel):
    content_id: int
    progress: Optional[int] = None

class WatchHistoryOut(WatchHistoryCreate):
    user_id: int
    content_id: int
    watched_at: datetime
    content: Optional[ContentPreview] = None

    class Config:
        from_attributes = True