# CLAUDE.md

## Project Overview

- **Backend**: FastAPI + SQLite (SQLAlchemy)
- **Frontend**: Static HTML/JS/CSS
- **Testing**: pytest
- **Code Quality**: black + ruff (pre-commit)

## Project Structure

```
backend/app/
├── main.py          # FastAPI entry point
├── db.py            # Database setup, sessions, seed loading
├── models.py        # SQLAlchemy models (Note, ActionItem)
├── schemas.py       # Pydantic request/response schemas
├── routers/         # API endpoints (notes.py, action_items.py)
└── services/        # Business logic (extract.py)
backend/tests/       # pytest test suite
frontend/            # Static UI files
data/                # SQLite DB (app.db) + seed.sql
docs/TASKS.md        # Agent-driven workflow tasks
```

## Key Entry Points

- **App**: `backend/app/main.py` - FastAPI app, routers, static files
- **Routers**: `backend/app/routers/notes.py`, `action_items.py`
- **Models**: `backend/app/models.py` - Note (id, title, content), ActionItem (id, description, completed)
- **Database**: `backend/app/db.py` - SQLite at `./data/app.db`, seed from `data/seed.sql`
- **Tests**: `backend/tests/test_*.py`

## `make` Commands

```bash
make run      # Start server (http://localhost:8000)
make test     # Run pytest
make format   # black + ruff --fix
make lint     # ruff check
make seed     # Apply seed data
```

## Development Workflow

### Adding Endpoints
1. Write failing test → Implement endpoint → Run tests → Format/lint
2. Update schemas if needed, update frontend if UI change

### Code Quality
- **black**: Formatter (88 char line length)
- **ruff**: Linter with auto-fix
- **pre-commit**: Auto-runs black + ruff (install with `pre-commit install`)
- Always run `make test && make lint` before committing

### Safe Commands
✅ `make run`, `make test`, `make format`, `make lint`, `pytest`, `black .`, `ruff check . --fix`

### Avoid
❌ Direct database file manipulation, skipping pre-commit hooks

## Database Patterns

```python
# In routes (dependency injection)
from fastapi import Depends
from .db import get_db

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    # Use db
    pass

# In services (context manager)
from .db import get_session
with get_session() as session:
    # Use session
    pass
```

## Environment Variables

- `DATABASE_PATH`: SQLite path (default: `./data/app.db`)
- `HOST`, `PORT`: Server config (defaults: `127.0.0.1:8000`)

## Tasks

See `docs/TASKS.md` for enhancement ideas (search, CRUD, validation, etc.)

## Notes

- Use type hints
- Follow FastAPI patterns (dependencies, Pydantic schemas)
- Write tests for new features
- Keep code formatted and linted
