# Action Item Extractor

A FastAPI-based web application that extracts actionable items from free-form text notes. The application supports both rule-based heuristics and LLM-powered extraction using Ollama, allowing users to convert unstructured notes into organized action item checklists.

## Overview

The Action Item Extractor is designed to help users transform meeting notes, project documentation, and other text-based content into structured action items. The application provides:

- **Dual Extraction Methods**: Rule-based heuristics and LLM-powered extraction
- **Note Management**: Save and retrieve notes with timestamps
- **Action Item Tracking**: Create, list, and mark action items as done/not done
- **Web Interface**: Simple HTML frontend for easy interaction
- **RESTful API**: Well-structured API endpoints for programmatic access

## Features

- Extract action items from text using pattern matching (bullets, keywords, checkboxes)
- Extract action items using LLM via Ollama for more intelligent extraction
- Save notes to a SQLite database
- Track action items with completion status
- Filter action items by associated note
- Simple web interface for interactive use

## Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- Conda environment
- Ollama (for LLM-powered extraction)
  - Install from: https://ollama.com
  - Pull a model: `ollama pull qwen3:8b` (or another model of your choice)

## Setup

1. **Activate your conda environment**:
   ```bash
   conda activate cs146s
   ```

2. **Install dependencies** (from project root):
   ```bash
   poetry install
   ```

3. **Set up Ollama** (if using LLM extraction):
   - Install Ollama from https://ollama.com
   - Pull a model: `ollama pull qwen3:8b`
   - Ensure Ollama is running: `ollama serve`

4. **Environment Variables** (optional):
   - Create a `.env` file in the project root if you need to configure Ollama settings
   - The application uses `python-dotenv` to load environment variables

## Running the Application

From the project root directory, start the development server:

```bash
poetry run uvicorn week2.app.main:app --reload
```

The application will be available at:
- **Web Interface**: http://127.0.0.1:8000/
- **API Documentation**: http://127.0.0.1:8000/docs (FastAPI auto-generated docs)
- **Alternative API Docs**: http://127.0.0.1:8000/redoc

The `--reload` flag enables auto-reload on code changes during development.

## API Endpoints

### Notes

- **POST `/notes`** - Create a new note
  - Request body: `{"content": "Your note text here"}`
  - Returns: Created note with ID and timestamp

- **GET `/notes`** - List all notes
  - Returns: Array of all notes, ordered by ID (descending)

- **GET `/notes/{note_id}`** - Get a specific note by ID
  - Returns: Note details or 404 if not found

### Action Items

- **POST `/action-items/extract`** - Extract action items using rule-based heuristics
  - Request body: `{"text": "Your text here", "save_note": false}`
  - Returns: Extracted action items and optional note ID

- **POST `/action-items/extract-llm`** - Extract action items using LLM (Ollama)
  - Request body: `{"text": "Your text here", "save_note": false}`
  - Returns: Extracted action items and optional note ID
  - Falls back to rule-based extraction if LLM fails

- **GET `/action-items`** - List all action items
  - Query parameter: `note_id` (optional) - Filter by note ID
  - Returns: Array of action items, ordered by ID (descending)

- **POST `/action-items/{action_item_id}/done`** - Mark an action item as done/not done
  - Request body: `{"done": true}` or `{"done": false}`
  - Returns: Updated action item

### Frontend

- **GET `/`** - Serve the web interface HTML

## Database

The application uses SQLite with the database file located at `week2/data/app.db`. The database is automatically initialized on first run with the following schema:

- **notes**: Stores note content with timestamps
- **action_items**: Stores extracted action items with completion status and optional note association

## Running Tests

The test suite is located in `week2/tests/` and uses pytest. To run all tests:

```bash
# From project root
poetry run pytest week2/tests/
```

To run a specific test file:

```bash
poetry run pytest week2/tests/test_extract.py
```

To run with verbose output:

```bash
poetry run pytest week2/tests/ -v
```

### Test Coverage

The test suite includes:
- Rule-based extraction tests (bullets, checkboxes, keywords)
- LLM extraction tests (various input formats, empty input, mixed formats)
- Edge cases and error handling

## Project Structure

```
week2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application settings
│   ├── db.py                # Database operations
│   ├── schemas.py           # Pydantic models for API
│   ├── routers/
│   │   ├── notes.py         # Notes API endpoints
│   │   └── action_items.py  # Action items API endpoints
│   └── services/
│       └── extract.py       # Extraction logic (rule-based & LLM)
├── data/
│   └── app.db              # SQLite database (auto-created)
├── frontend/
│   └── index.html          # Web interface
├── tests/
│   ├── __init__.py
│   └── test_extract.py     # Unit tests for extraction
├── assignment.md           # Assignment instructions
└── README.md              # This file
```

## Extraction Methods

### Rule-Based Extraction

The rule-based method (`extract_action_items`) uses pattern matching to identify action items:
- Bullet points: `-`, `*`, `•`, numbered lists
- Keyword prefixes: `todo:`, `action:`, `next:`
- Checkbox markers: `[ ]`, `[todo]`
- Imperative sentence detection (fallback)

### LLM-Based Extraction

The LLM method (`extract_action_items_llm`) uses Ollama to intelligently extract action items:
- Uses structured output format (JSON schema)
- More flexible and context-aware than rule-based approach
- Falls back to rule-based extraction if LLM fails
- Configured to use `qwen3:8b` model by default

## Error Handling

The application includes comprehensive error handling:
- `NotFoundError`: Raised when a resource is not found (404)
- `DatabaseError`: Raised for database operation failures (500)
- `RequestValidationError`: Raised for invalid request data (422)

All errors return appropriate HTTP status codes and JSON error messages.

## Development

### Code Style

The project uses:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting (selects: E, F, I, UP, B)

### Dependencies

Key dependencies:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `pydantic`: Data validation
- `ollama`: LLM integration
- `python-dotenv`: Environment variable management
- `pytest`: Testing framework

See `pyproject.toml` for the complete dependency list.

## License

This project is part of a course assignment and is for educational purposes.

