import os
import pytest
from pydantic import ValidationError

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# Tests for extract_action_items_llm

def test_extract_action_items_llm_bullet_lists():
    """Test LLM extraction with bullet point lists"""
    text = """
    Meeting notes:
    - Set up database connection
    * Implement authentication
    • Add error handling
    Some regular text here.
    """.strip()

    items = extract_action_items_llm(text)
    assert len(items) == 3
    assert "Set up database connection" in items
    assert "Implement authentication" in items
    assert "Add error handling" in items


def test_extract_action_items_llm_keyword_prefixed():
    """Test LLM extraction with keyword-prefixed lines"""
    text = """
    Action items from sprint planning:
    todo: Review pull requests
    action: Update documentation
    next: Deploy to staging
    Regular narrative text.
    """.strip()

    items = extract_action_items_llm(text)
    assert len(items) == 3
    assert "Review pull requests" in items
    assert "Update documentation" in items
    assert "Deploy to staging" in items


def test_extract_action_items_llm_empty_input():
    """Test LLM extraction with empty input"""
    text = ""
    
    items = extract_action_items_llm(text)
    assert items == []
    
    text_whitespace = "   \n\t  "
    items = extract_action_items_llm(text_whitespace)
    assert items == []


def test_extract_action_items_llm_mixed_format():
    """Test LLM extraction with mixed formats (bullets, keywords, checkboxes)"""
    text = """
    Project tasks:
    - [ ] Task one
    todo: Task two
    * Task three
    1. Task four
    action: Task five
    """.strip()

    items = extract_action_items_llm(text)
    assert len(items) == 5
    assert "Task one" in items
    assert "Task two" in items
    assert "Task three" in items
    assert "Task four" in items
    assert "Task five" in items
