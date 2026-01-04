# Test Runner

Run tests with quick feedback loop.

**Usage**: `/run_tests [path|marker]`

- If no arguments: Run all tests with `pytest -q backend/tests --maxfail=1 -x`
- If path provided: Run specific test file (e.g., `/run_tests test_notes.py`)
- If marker provided: Run tests with marker (e.g., `/run_tests -m slow`)

**Steps**:
1. Run pytest with provided arguments or defaults
2. If tests pass, show summary
3. If tests fail, summarize failures and suggest next steps
4. Optionally run coverage if all tests pass
