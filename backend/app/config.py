from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    PROJECT_NAME: str = "Skill Bridge"
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024
    allowed_exts: set = {".pdf", ".docx"}
    
    DEBUG: bool = False
    DATABASE_URL: str
    AI_SERVICE_URL: str
    model_config = SettingsConfigDict(env_file=".env")



settings = Settings()
