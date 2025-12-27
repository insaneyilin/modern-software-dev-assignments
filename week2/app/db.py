from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from .schemas import ActionItemResponse, NoteResponse


class DatabaseError(Exception):
    """Base exception for database operations"""
    pass


class NotFoundError(DatabaseError):
    """Raised when a requested resource is not found"""
    pass


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def ensure_data_directory_exists() -> None:
    """Ensure the data directory exists"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Context manager for database connections.
    Ensures proper cleanup and error handling.
    """
    ensure_data_directory_exists()
    connection = None
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        yield connection
        connection.commit()
    except sqlite3.Error as e:
        if connection:
            connection.rollback()
        raise DatabaseError(f"Database operation failed: {e}") from e
    finally:
        if connection:
            connection.close()


def init_db() -> None:
    """Initialize the database schema"""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
                );
                """
            )
            # Create indexes for better query performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_action_items_note_id ON action_items(note_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_action_items_done ON action_items(done)"
            )
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to initialize database: {e}") from e


def insert_note(content: str) -> int:
    """Insert a new note and return its ID"""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            return int(cursor.lastrowid)
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to insert note: {e}") from e


def list_notes() -> list[NoteResponse]:
    """List all notes"""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                NoteResponse(
                    id=row["id"],
                    content=row["content"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in rows
            ]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to list notes: {e}") from e


def get_note(note_id: int) -> Optional[NoteResponse]:
    """Get a note by ID"""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return NoteResponse(
                id=row["id"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to get note: {e}") from e


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    """Insert action items and return their IDs"""
    if not items:
        return []
    
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            ids: list[int] = []
            for item in items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                )
                ids.append(int(cursor.lastrowid))
            return ids
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to insert action items: {e}") from e


def list_action_items(note_id: Optional[int] = None) -> list[ActionItemResponse]:
    """List action items, optionally filtered by note_id"""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            rows = cursor.fetchall()
            return [
                ActionItemResponse(
                    id=row["id"],
                    note_id=row["note_id"],
                    text=row["text"],
                    done=bool(row["done"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in rows
            ]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to list action items: {e}") from e


def mark_action_item_done(action_item_id: int, done: bool) -> ActionItemResponse:
    """Mark an action item as done or not done"""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            if cursor.rowcount == 0:
                raise NotFoundError(f"Action item with id {action_item_id} not found")
            
            # Fetch the updated row
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                (action_item_id,),
            )
            row = cursor.fetchone()
            if row is None:
                raise NotFoundError(f"Action item with id {action_item_id} not found")
            
            return ActionItemResponse(
                id=row["id"],
                note_id=row["note_id"],
                text=row["text"],
                done=bool(row["done"]),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
    except NotFoundError:
        raise
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to update action item: {e}") from e