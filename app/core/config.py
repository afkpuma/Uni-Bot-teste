from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    KOMMO_URL: str
    KOMMO_TOKEN: str
    MONDAY_TOKEN: str
    MONDAY_URL: str = "https://api.monday.com/v2"
    MONDAY_BOARD_ID: int = 18399984137

    class Config:
        env_file = ".env"


settings = Settings()