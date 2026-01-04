# Add New Endpoint

Follow TDD workflow to add a new API endpoint.

**Usage**: `/add-endpoint <router> <method> <path> [description]`

**Example**: `/add-endpoint notes PUT /notes/{id} "Update note by ID"`

**Steps**:
1. Write failing test in appropriate `backend/tests/test_*.py`
2. Implement endpoint in `backend/app/routers/*.py`
3. Update schemas in `backend/app/schemas.py` if needed
4. Run tests to verify
5. Format and lint code
6. Summarize changes and next steps (e.g., frontend update)
