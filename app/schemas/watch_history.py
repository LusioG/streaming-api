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
    id: int
    user_id: int
    content_id: int
    watched_at:datetime
    content: ContentPreview
    class Config:
        from_attributes = True


