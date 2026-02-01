from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Expense Tracker"
    DATABASE_URL: str = "sqlite+aiosqlite:///./expenses.db"
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "pdf"}
    TESSERACT_LANG: str = "fra+eng"
    
    class Config:
        env_file = ".env"

settings = Settings()
settings.UPLOAD_DIR.mkdir(exist_ok=True)
