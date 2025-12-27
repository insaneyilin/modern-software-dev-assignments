from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters

class ActionItemsResponse(BaseModel):
    action_items: list[str]


def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items from text using LLM via Ollama.
    
    Args:
        text: Input text to extract action items from
        
    Returns:
        List of extracted action items as strings
    """
    if not text.strip():
        return []
    
    prompt = f"""
Extract all action items, tasks, todos, and actionable items from the following text.
Return them as a JSON array of strings. Each action item should be a clear, concise task statement.

Text:
{text}

Return as JSON with a list of action items.
"""
    
    try:
        response = chat(
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                }
            ],
            model='qwen3:8b',
            format=ActionItemsResponse.model_json_schema(),
            options={
                'temperature': 0,
            }
        )
        
        result = ActionItemsResponse.model_validate_json(response.message.content)
        return result.action_items
    except Exception as e:
        # Fallback to rule-based extraction if LLM fails
        # You might want to log the error here
        return extract_action_items(text)
