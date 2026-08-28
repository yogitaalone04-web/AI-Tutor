import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "uploads"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Tutor — Textbook Q&A Assistant"
    API_V1_STR: str = "/api"
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIM: int = 3072
    
    # CORS
    ALLOWED_ORIGIN: str = os.getenv("ALLOWED_ORIGIN", "http://localhost:5173")
    
    # Text Chunking Settings
    CHUNK_SIZE: int = 1500  # ~500 tokens
    CHUNK_OVERLAP: int = 200  # ~50 tokens
    
    # File Limits
    MAX_UPLOAD_SIZE_MB: int = 20
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
