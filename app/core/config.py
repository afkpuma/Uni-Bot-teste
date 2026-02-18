from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    KOMMO_URL: str
    KOMMO_TOKEN: str
    MONDAY_TOKEN: str
    MONDAY_URL: str = "https://api.monday.com/v2"
    MONDAY_BOARD_ID: int = 18399984137

    # Flowise AI
    FLOWISE_API_URL: str = "http://76.13.66.202:3000/api/v1/prediction/332e1083-6c00-4dfd-92f1-87d0f9d90792"

    # Evolution API
    EVOLUTION_API_URL: str = "http://evolution_api:8080"
    EVOLUTION_API_TOKEN: str = "BatataQuente2026"
    INSTANCE_NAME: str = "UniBot"

    class Config:
        env_file = ".env"


settings = Settings()