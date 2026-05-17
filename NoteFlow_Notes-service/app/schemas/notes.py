from datetime import datetime
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = ""


class NoteUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = ""


class NoteArchiveUpdate(BaseModel):
    is_archived: bool


class NotePinUpdate(BaseModel):
    is_pinned: bool


class NoteResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    is_archived: bool
    is_pinned: bool
    created_at: datetime
    updated_at: datetime


class CurrentUser(BaseModel):
    id: int
    username: str
    email: str
