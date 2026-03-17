from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class History(Base):
    __tablename__ = "history"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    content_id = Column(Integer, ForeignKey("contents.id"), primary_key=True)
    progress = Column(Integer)  # segundos vistos
    
    watched_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watch_history")
    content = relationship("Content", back_populates="watch_history")