# Code Quality Check

Run formatting and linting, then tests.

**Usage**: `/quality [--fix]`

**Steps**:
1. Run `make lint` to check for issues
2. If `--fix` flag: Run `make format` to auto-fix
3. Run `make test` to ensure nothing broke
4. Summarize results and any remaining issues
