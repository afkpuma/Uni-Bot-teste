from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    KOMMO_URL: str
    KOMMO_TOKEN: str
    MONDAY_TOKEN: str
    MONDAY_URL: str = "https://api.monday.com/v2"
    MONDAY_BOARD_ID: int = 18399984137

    # Flowise AI
    FLOWISE_API_URL: str

    # Evolution API
    EVOLUTION_API_URL: str
    EVOLUTION_API_TOKEN: str
    INSTANCE_NAME: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()