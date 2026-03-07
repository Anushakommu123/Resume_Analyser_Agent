"""
Configuration settings for the Testing Agents application.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "testing_agents"
    test_cases_collection: str = "test_cases"
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4-turbo-preview"
    
    # Vector Search Configuration
    vector_dimension: int = 1536  # OpenAI text-embedding-3-small dimension
    top_k_results: int = 5  # Number of similar test cases to retrieve
    
    # Application Configuration
    app_name: str = "Testing Agents API"
    debug: bool = False
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

