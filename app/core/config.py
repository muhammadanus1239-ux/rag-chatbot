from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://raguser:ragpassword@localhost:5432/ragdb"
    )
    secret_key: str = "change-me-later"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    llm_api_key: str = ""
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_model: str = ""

    class Config:
        env_file = ".env"


settings = Settings()