from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parent.parent.parent.parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    
    # app settings
    app_name: str = "CloudDeck"
    app_env: str = "Development"
    debug: bool = True



    # Security
    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7



    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"



    # Ollama
    ollama_url: str = "http://host.windows.internal:11434"
    ollama_model: str = "mistral"



    # CORS - who is allowed to call our API
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]



# This is the singleton -- one instance shared across the entire app
settings = Settings()