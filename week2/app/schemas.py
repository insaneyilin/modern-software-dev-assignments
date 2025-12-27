from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    content: str = Field(..., min_length=1, description="Note content")


class NoteCreate(NoteBase):
    pass


class NoteResponse(NoteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActionItemBase(BaseModel):
    text: str = Field(..., min_length=1, description="Action item text")


class ActionItemResponse(BaseModel):
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the text as a note")


class ExtractResponse(BaseModel):
    note_id: Optional[int] = None
    items: list[ActionItemResponse]


class ActionItemUpdate(BaseModel):
    done: bool = Field(..., description="Whether the action item is done")