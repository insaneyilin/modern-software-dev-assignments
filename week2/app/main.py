from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import DatabaseError, NotFoundError, init_db
from .routers import action_items, notes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    settings.ensure_directories()
    try:
        init_db()
        yield
    except DatabaseError as e:
        # Log error in production
        print(f"Database initialization failed: {e}")
        raise
    # Shutdown (if needed, add cleanup here)
    # yield


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan,
)


# Exception handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database operation failed"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Serve the frontend HTML"""
    html_path = settings.FRONTEND_DIR / "index.html"
    if not html_path.exists():
        raise FileNotFoundError(f"Frontend file not found: {html_path}")
    return html_path.read_text(encoding="utf-8")


# Include routers
app.include_router(notes.router)
app.include_router(action_items.router)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.FRONTEND_DIR)), name="static")