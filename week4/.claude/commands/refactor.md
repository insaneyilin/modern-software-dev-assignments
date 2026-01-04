# Refactor Module

Safely rename or move a module with import updates.

**Usage**: `/refactor <old_path> <new_path>`

**Example**: `/refactor services/extract.py services/parser.py`

**Steps**:
1. Find all imports of the old module
2. Rename/move the file
3. Update all import statements
4. Run `make lint` to check for issues
5. Run `make test` to verify nothing broke
6. Output checklist of modified files and verification steps
