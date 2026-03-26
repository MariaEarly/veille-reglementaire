from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # rss, email, web, manual
    url = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("Item", back_populates="source")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    source_name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)
    url = Column(String(1000), nullable=True)
    title = Column(String(1000), nullable=False)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True)
    raw_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    tags = Column(String(1000), nullable=True)
    score = Column(Integer, default=0)
    duplicate_group = Column(String(255), nullable=True)
    status = Column(String(50), default="new")
    early_brief = Column(Boolean, default=False)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("Source", back_populates="items")
