from pydantic_settings import BaseSettings
from functools import lru_cache
 
 
class Settings(BaseSettings):
    APP_NAME: str = "TravelApp"
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
 
    DATABASE_URL: str = "postgresql+asyncpg://postgres:14801480@localhost:5432/travel"
    REDIS_URL: str = "redis://localhost:6379/0"
 
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
 
    PINECONE_API_KEY: str = ""
    PINECONE_ENV: str = "us-east-1"
    PINECONE_INDEX: str = "travel-knowledge"
 
    AMADEUS_CLIENT_ID: str = ""
    AMADEUS_CLIENT_SECRET: str = ""
    OPENWEATHER_API_KEY: str = ""
    MAPBOX_TOKEN: str = ""
 
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
 
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@travelapp.com"
 
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = "travelapp-uploads"
    AWS_REGION: str = "eu-west-1"
 
    class Config:
        env_file = ".env"
        case_sensitive = True
 
 
@lru_cache()
def get_settings() -> Settings:
    return Settings()
 
 
settings = get_settings()