from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SourceCreate(BaseModel):
    name: str
    source_type: str
    url: Optional[str] = None
    is_active: bool = True
    category: Optional[str] = None


class SourceOut(BaseModel):
    id: int
    name: str
    source_type: str
    url: Optional[str]
    is_active: bool
    category: Optional[str]

    class Config:
        from_attributes = True


class ManualItemCreate(BaseModel):
    source_name: str = "Manual"
    source_type: str = "manual"
    url: Optional[str] = None
    title: str
    raw_text: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[str] = None


class ItemOut(BaseModel):
    id: int
    source_name: str
    source_type: str
    url: Optional[str]
    title: str
    author: Optional[str]
    published_at: Optional[datetime]
    raw_text: Optional[str]
    summary: Optional[str]
    tags: Optional[str]
    score: int
    duplicate_group: Optional[str]
    status: str
    early_brief: bool
    category: Optional[str]

    class Config:
        from_attributes = True


class ItemPatch(BaseModel):
    status: Optional[str] = None
    early_brief: Optional[bool] = None
