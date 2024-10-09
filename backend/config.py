from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

load_dotenv(env_path)

class Settings(BaseSettings):
    APP_NAME: str = "AI-Powered Project Management System"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./test.db"
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    class Config:
        env_file = env_path
        env_file_encoding = 'utf-8'

settings = Settings()

print("Debug information:")
print(f"Current directory: {current_dir}")
print(f".env file path: {env_path}")
print(f".env file exists: {os.path.exists(env_path)}")
print(f"GROQ_API_KEY from settings: {'Set' if settings.GROQ_API_KEY else 'Not set'}")
print(f"GROQ_API_KEY from os.environ: {'Set' if os.environ.get('GROQ_API_KEY') else 'Not set'}")


if settings.GROQ_API_KEY is None:
    print("Warning: GROQ_API_KEY is not set in settings. Attempting to get it from os.environ.")
    settings.GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

if settings.GROQ_API_KEY is None:
    print("Warning: GROQ_API_KEY is not set. Some features may not work properly.")
else:
    print("GROQ_API_KEY is set successfully.")