from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

#TABLA INTERMEDIA muchos a muchos contents a categories
content_categories = Table(
    "content_categories",
    Base.metadata,
    Column("content_id", Integer, ForeignKey("contents.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)