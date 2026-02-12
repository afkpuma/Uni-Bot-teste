from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    KOMMO_URL: str
    KOMMO_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()