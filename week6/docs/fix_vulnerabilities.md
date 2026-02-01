# Security Vulnerability Fixes Report

This document details the security vulnerabilities identified by Semgrep and the fixes applied to mitigate them.

## Summary

- **Total Issues Fixed**: 2 critical vulnerabilities
- **Files Modified**: `backend/app/routers/notes.py`
- **Test Status**: ✅ All tests passing after fixes

---

## Issue 1: SQL Injection in unsafe_search Endpoint

### Location
- **File**: `backend/app/routers/notes.py`
- **Lines**: 69-93 (specifically line 71-79 for the vulnerable SQL query)

### Semgrep Rule/Category
- **Rule**: SQL Injection with FastAPI / SQL Injection with aiosqlite via fastapi
- **Category**: CWE-89: SQL Injection

### Risk Description
The `unsafe_search` endpoint used f-string formatting to directly interpolate user input (`q` parameter) into a raw SQL query. This allowed attackers to inject malicious SQL statements, potentially:
- Extracting sensitive data from the database
- Modifying or deleting data
- Bypassing authentication/authorization
- Executing arbitrary SQL commands

**Example Attack**: A malicious user could send `q=' OR '1'='1` to bypass the WHERE clause and retrieve all notes, or use `q='; DROP TABLE notes; --` to delete the entire notes table.

### Fix Applied

**Before (Vulnerable Code)**:
```python
sql = text(
    f"""
    SELECT id, title, content, created_at, updated_at
    FROM notes
    WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
    ORDER BY created_at DESC
    LIMIT 50
    """
)
rows = db.execute(sql).all()
```

**After (Secure Code)**:
```python
sql = text(
    """
    SELECT id, title, content, created_at, updated_at
    FROM notes
    WHERE title LIKE :pattern OR content LIKE :pattern
    ORDER BY created_at DESC
    LIMIT 50
    """
)
pattern = f"%{q}%"
rows = db.execute(sql, {"pattern": pattern}).all()
```

### Changes Made
1. Removed f-string formatting from the SQL query
2. Used parameterized query with named parameter `:pattern`
3. Passed user input as a parameter dictionary to `db.execute()`
4. Constructed the LIKE pattern separately before passing to the query

### Why This Mitigates the Issue
Parameterized queries (also called prepared statements) separate SQL code from user data. The database driver treats the parameter values as pure data, not executable SQL code. This means:
- Special SQL characters in user input are automatically escaped
- The SQL structure cannot be altered by user input
- Injection attacks are prevented at the database driver level

The database engine knows that `:pattern` is a placeholder for data, not SQL syntax, so even if a user sends `' OR '1'='1`, it will be treated as a literal string to search for, not as SQL logic.

---

## Issue 2: Code Injection in debug/eval Endpoint

### Location
- **File**: `backend/app/routers/notes.py`
- **Lines**: 102-105 (specifically line 104)

### Semgrep Rule/Category
- **Rule**: Code Injection with FastAPI
- **Category**: CWE-94: Code Injection

### Risk Description
The `/debug/eval` endpoint used Python's `eval()` function to execute arbitrary expressions provided by users. This is extremely dangerous because:
- Attackers can execute arbitrary Python code on the server
- Full system compromise is possible
- Attackers can read sensitive files, environment variables, or secrets
- Attackers can modify data, install backdoors, or pivot to other systems
- The application process privileges are fully available to the attacker

**Example Attack**: A malicious user could send `expr=__import__('os').system('rm -rf /')` to delete files, or `expr=open('/etc/passwd').read()` to read sensitive system files.

### Fix Applied

**Before (Vulnerable Code)**:
```python
@router.get("/debug/eval")
def debug_eval(expr: str) -> dict[str, str]:
    result = str(eval(expr))  # noqa: S307
    return {"result": result}
```

**After (Secure Code)**:
```python
@router.get("/debug/eval")
def debug_eval(expr: str) -> dict[str, str]:
    # Removed eval() to prevent code injection vulnerability
    # This endpoint is disabled for security reasons
    raise HTTPException(
        status_code=501,
        detail="This endpoint has been disabled due to security concerns. Use safe alternatives for expression evaluation."
    )
    return {"result": ""}
```

### Changes Made
1. Completely removed the `eval()` call
2. Replaced functionality with an HTTP 501 (Not Implemented) error
3. Added clear error message explaining the security concern
4. Kept the endpoint structure intact to avoid breaking API contracts

### Why This Mitigates the Issue
The only safe way to handle `eval()` is to not use it at all. By disabling the endpoint:
- No user input can be executed as code
- The attack surface is completely eliminated
- The application clearly communicates that this functionality is unavailable

**Alternative Approaches** (not implemented, but recommended for production):
- If expression evaluation is truly needed, use a safe sandboxed parser like `ast.literal_eval()` (only for literals)
- Implement a whitelist of allowed operations
- Use a domain-specific language (DSL) with limited, safe operations
- Remove the endpoint entirely if it's only for debugging

---

## Issues Not Fixed (False Positives or Non-Issues)

### SQL Injection in action_items.py:33 and notes.py:33
**Status**: No fix needed - False positive

**Analysis**:
Lines 33 in both files use SQLAlchemy ORM with proper parameterized queries:
```python
rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
```

The `stmt` object is built using SQLAlchemy's query builder API, which automatically parameterizes all values. The `skip` and `limit` parameters are integers validated by FastAPI's type system and Pydantic, making SQL injection impossible. Semgrep likely flagged this due to the presence of `.execute()` but this is a false positive.

### SQL Injection with SQLAlchemy in notes.py:72
**Status**: Fixed as part of Issue 1

**Analysis**:
This was the same vulnerability as Issue 1 (the `unsafe_search` endpoint). The line number reference (72) pointed to the SQL query construction that was fixed by implementing parameterized queries.

---

## Verification

### Tests
All existing tests pass after the fixes:
```bash
$ make test
3 passed, 13 warnings in 0.04s
```

### Manual Testing
1. **SQL Injection Fix**: The `unsafe_search` endpoint now safely handles special characters:
   - Input: `q=' OR '1'='1` → Returns only notes matching the literal string, not all notes
   - Input: `q='; DROP TABLE notes; --` → Safely searches for this string, doesn't execute SQL

2. **Code Injection Fix**: The `/debug/eval` endpoint now returns HTTP 501:
   - Any request to `/notes/debug/eval?expr=...` returns an error message
   - No code execution occurs

### Code Quality
```bash
$ make format
$ make lint
# No errors reported
```

---

## Recommendations

1. **Remove Debug Endpoints**: The `/debug/*` endpoints should be removed entirely in production or protected behind authentication and feature flags.

2. **Security Scanning**: Continue using Semgrep or similar tools in CI/CD pipelines to catch vulnerabilities early.

3. **Input Validation**: While parameterized queries prevent SQL injection, consider additional input validation for business logic (e.g., max length, allowed characters).

4. **Code Review**: Require security-focused code reviews for any endpoints that handle user input or execute queries.

5. **Principle of Least Privilege**: Ensure the database user has minimal necessary permissions to limit damage from potential future vulnerabilities.

---

## AI Coding Tool Usage

All fixes were implemented using Claude Code (Claude Sonnet 4.5) with the following workflow:
1. Read and analyzed the vulnerable code
2. Applied security best practices for each vulnerability type
3. Verified fixes with automated tests
4. Generated this comprehensive report

The AI tool helped identify the exact nature of each vulnerability and apply industry-standard mitigation techniques efficiently.
