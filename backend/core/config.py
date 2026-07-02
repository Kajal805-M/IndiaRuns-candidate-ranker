import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Intelligent Candidate Discovery Platform"
    API_V1_STR: str = "/api/v1"
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./candidates.db")
    
settings = Settings()
