from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    PROJECT_NAME: str = "Skill Bridge"
    DEBUG: bool = False
    DATABASE_URL: str
    AI_SERVICE_URL: str
    model_config = SettingsConfigDict(env_file=".env")



settings = Settings()
