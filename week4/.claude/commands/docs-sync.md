# API Documentation Sync

Sync API documentation with OpenAPI schema.

**Usage**: `/docs-sync`

**Steps**:
1. Fetch `/openapi.json` from running server (or read from file)
2. Compare with existing `docs/API.md` (create if missing)
3. Update `docs/API.md` with current endpoints, schemas, and examples
4. List any route deltas or missing documentation
5. Output diff-like summary and TODOs
