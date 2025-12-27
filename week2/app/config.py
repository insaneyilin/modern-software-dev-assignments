from __future__ import annotations

from pathlib import Path


class Settings:
    """Application settings"""
    
    BASE_DIR: Path = Path(__file__).resolve().parents[1]
    DATA_DIR: Path = BASE_DIR / "data"
    DB_PATH: Path = DATA_DIR / "app.db"
    FRONTEND_DIR: Path = BASE_DIR / "frontend"
    
    # API settings
    API_TITLE: str = "Action Item Extractor"
    API_VERSION: str = "1.0.0"
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()