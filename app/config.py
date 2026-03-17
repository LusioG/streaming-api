from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # Base de datos
    database_url: str

    # Seguridad
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # API
    api_title: str = "Streaming API"
    api_version: str = "1.0"

    class Config:
        env_file = ".env"


settings = Settings()