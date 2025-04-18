from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str  = os.getenv("OPENAI_API_KEY") 
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "chatgpt_clone"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
