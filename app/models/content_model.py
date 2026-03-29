from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship
from app.models.content_category import content_categories

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    description = Column(String, nullable=True)

    image_url = Column(String, unique=True, index=True, nullable=False) # poster
    banner_url = Column(String, nullable=True) # imagen horizontal

    duration_minutes = Column(Integer, nullable=True)
    release_year = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


    categories = relationship("Category", secondary=content_categories, back_populates="contents")

    watch_history = relationship("History", back_populates="content")