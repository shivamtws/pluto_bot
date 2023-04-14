from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = "Goliath Chatbot API"
    open_ai: str = os.environ.get('OPENAI_API_KEY')

    class Config:
        env_file = ".env"


settings = Settings()