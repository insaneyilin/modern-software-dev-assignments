from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, status

from ..db import list_action_items, mark_action_item_done
from ..schemas import ActionItemResponse, ActionItemUpdate, ExtractRequest, ExtractResponse
from ..services.extract import extract_action_items, extract_action_items_llm

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse, status_code=status.HTTP_201_CREATED)
def extract(request: ExtractRequest) -> ExtractResponse:
    """Extract action items from text"""
    from ..db import insert_action_items, insert_note
    
    # items = extract_action_items_llm(request.text)
    items = extract_action_items(request.text)
    
    note_id: Optional[int] = None
    if request.save_note:
        note_id = insert_note(request.text)
    
    ids = insert_action_items(items, note_id=note_id)
    
    # Fetch created action items
    all_items = list_action_items()
    created_items = [
        item for item in all_items
        if item.id in ids
    ]
    
    return ExtractResponse(note_id=note_id, items=created_items)


@router.post("/extract-llm", response_model=ExtractResponse, status_code=status.HTTP_201_CREATED)
def extract_llm(request: ExtractRequest) -> ExtractResponse:
    """Extract action items from text using LLM"""
    from ..db import insert_action_items, insert_note
    
    items = extract_action_items_llm(request.text)
    
    note_id: Optional[int] = None
    if request.save_note:
        note_id = insert_note(request.text)
    
    ids = insert_action_items(items, note_id=note_id)
    
    # Fetch created action items
    all_items = list_action_items()
    created_items = [
        item for item in all_items
        if item.id in ids
    ]
    
    return ExtractResponse(note_id=note_id, items=created_items)


@router.get("", response_model=list[ActionItemResponse])
def list_all(note_id: Optional[int] = Query(None, description="Filter by note ID")) -> list[ActionItemResponse]:
    """List all action items, optionally filtered by note_id"""
    return list_action_items(note_id=note_id)


@router.post("/{action_item_id}/done", response_model=ActionItemResponse)
def mark_done(action_item_id: int, update: ActionItemUpdate) -> ActionItemResponse:
    """Mark an action item as done or not done"""
    return mark_action_item_done(action_item_id, update.done)