from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Skill Bridge"
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024
    allowed_exts: set = {".pdf", ".docx"}
    
    DEBUG: bool = False
    DATABASE_URL: str = ""
    AI_SERVICE_URL: str = ""
    UPLOAD_BATCH_DIR: str = ""
    REDIS_HOST: str = ""
    REDIS_PORT: int = 0
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")



settings = Settings()
