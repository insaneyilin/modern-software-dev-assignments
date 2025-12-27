from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import Response

from ..db import NotFoundError, get_note, insert_note, list_notes
from ..schemas import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate) -> NoteResponse:
    """Create a new note"""
    note_id = insert_note(note.content)
    created_note = get_note(note_id)
    if created_note is None:
        raise NotFoundError(f"Note with id {note_id} not found after creation")
    return created_note


@router.get("", response_model=list[NoteResponse])
def list_all_notes() -> list[NoteResponse]:
    """List all notes"""
    return list_notes()


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """Get a single note by ID"""
    note = get_note(note_id)
    if note is None:
        raise NotFoundError(f"Note with id {note_id} not found")
    return note