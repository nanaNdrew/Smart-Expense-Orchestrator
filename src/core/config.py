from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    APP_NAME: str = "Smart Expense Orchestrator"
    DEBUG: bool = False
    
    DATABASE_URL: str
    REDIS_URL: str
    OPENAI_API_KEY: str
    
    # Optional settings for task management or rate limiting could go here.
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
