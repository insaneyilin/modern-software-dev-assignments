# API Documentation

**Version**: 0.1.0
**Base URL**: `http://localhost:8000`
**OpenAPI Version**: 3.1.0

## Overview

This API provides endpoints for managing notes and action items. It follows RESTful conventions and returns JSON responses.

## Table of Contents

- [Endpoints](#endpoints)
  - [Root](#root)
  - [Notes](#notes)
  - [Action Items](#action-items)
- [Schemas](#schemas)
- [Error Handling](#error-handling)

---

## Endpoints

### Root

#### `GET /`

Health check endpoint.

**Response**: `200 OK`

```bash
curl http://localhost:8000/
```

---

### Notes

#### `GET /notes/`

List all notes.

**Tags**: `notes`
**Response**: `200 OK`

**Response Schema**: Array of `NoteRead`

**Example**:
```bash
curl http://localhost:8000/notes/
```

**Response**:
```json
[
  {
    "id": 1,
    "title": "Meeting Notes",
    "content": "Discussed project timeline"
  }
]
```

---

#### `POST /notes/`

Create a new note.

**Tags**: `notes`
**Request Body**: `NoteCreate` (required)
**Response**: `201 Created`

**Response Schema**: `NoteRead`

**Example**:
```bash
curl -X POST http://localhost:8000/notes/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Note",
    "content": "This is the content"
  }'
```

**Response**:
```json
{
  "id": 2,
  "title": "New Note",
  "content": "This is the content"
}
```

**Error Responses**:
- `422 Unprocessable Entity`: Validation error

---

#### `GET /notes/search/`

Search notes by query string.

**Tags**: `notes`
**Query Parameters**:
- `q` (string, optional): Search query

**Response**: `200 OK`

**Response Schema**: Array of `NoteRead`

**Example**:
```bash
curl "http://localhost:8000/notes/search/?q=meeting"
```

**Response**:
```json
[
  {
    "id": 1,
    "title": "Meeting Notes",
    "content": "Discussed project timeline"
  }
]
```

**Error Responses**:
- `422 Unprocessable Entity`: Validation error

---

#### `GET /notes/{note_id}`

Get a specific note by ID.

**Tags**: `notes`
**Path Parameters**:
- `note_id` (integer, required): The note ID

**Response**: `200 OK`

**Response Schema**: `NoteRead`

**Example**:
```bash
curl http://localhost:8000/notes/1
```

**Response**:
```json
{
  "id": 1,
  "title": "Meeting Notes",
  "content": "Discussed project timeline"
}
```

**Error Responses**:
- `422 Unprocessable Entity`: Validation error

---

### Action Items

#### `GET /action-items/`

List all action items.

**Tags**: `action_items`
**Response**: `200 OK`

**Response Schema**: Array of `ActionItemRead`

**Example**:
```bash
curl http://localhost:8000/action-items/
```

**Response**:
```json
[
  {
    "id": 1,
    "description": "Review pull request",
    "completed": false
  }
]
```

---

#### `POST /action-items/`

Create a new action item.

**Tags**: `action_items`
**Request Body**: `ActionItemCreate` (required)
**Response**: `201 Created`

**Response Schema**: `ActionItemRead`

**Example**:
```bash
curl -X POST http://localhost:8000/action-items/ \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Write unit tests"
  }'
```

**Response**:
```json
{
  "id": 2,
  "description": "Write unit tests",
  "completed": false
}
```

**Error Responses**:
- `422 Unprocessable Entity`: Validation error

---

#### `PUT /action-items/{item_id}/complete`

Mark an action item as completed.

**Tags**: `action_items`
**Path Parameters**:
- `item_id` (integer, required): The action item ID

**Response**: `200 OK`

**Response Schema**: `ActionItemRead`

**Example**:
```bash
curl -X PUT http://localhost:8000/action-items/1/complete
```

**Response**:
```json
{
  "id": 1,
  "description": "Review pull request",
  "completed": true
}
```

**Error Responses**:
- `422 Unprocessable Entity`: Validation error

---

## Schemas

### NoteCreate

Request schema for creating a note.

**Properties**:
- `title` (string, required): The note title
- `content` (string, required): The note content

**Example**:
```json
{
  "title": "My Note",
  "content": "Note content here"
}
```

---

### NoteRead

Response schema for a note.

**Properties**:
- `id` (integer, required): The note ID
- `title` (string, required): The note title
- `content` (string, required): The note content

**Example**:
```json
{
  "id": 1,
  "title": "My Note",
  "content": "Note content here"
}
```

---

### ActionItemCreate

Request schema for creating an action item.

**Properties**:
- `description` (string, required): The action item description

**Example**:
```json
{
  "description": "Complete the task"
}
```

---

### ActionItemRead

Response schema for an action item.

**Properties**:
- `id` (integer, required): The action item ID
- `description` (string, required): The action item description
- `completed` (boolean, required): Whether the item is completed

**Example**:
```json
{
  "id": 1,
  "description": "Complete the task",
  "completed": false
}
```

---

### HTTPValidationError

Error response for validation failures.

**Properties**:
- `detail` (array of `ValidationError`): List of validation errors

**Example**:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### ValidationError

Individual validation error details.

**Properties**:
- `loc` (array of string/integer, required): Error location path
- `msg` (string, required): Error message
- `type` (string, required): Error type

---

## Error Handling

### Common HTTP Status Codes

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `422 Unprocessable Entity`: Request validation failed

### Validation Errors

When a request fails validation, the API returns a `422` status with an `HTTPValidationError` response containing details about what went wrong.

**Example Error Response**:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
