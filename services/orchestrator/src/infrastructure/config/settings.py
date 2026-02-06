"""Orchestrator Service Configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Service configuration
    service_name: str = "supply-chain-orchestrator"
    service_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000

    # Agent configuration
    agent_id: str = "orchestrator-001"
    
    # Other services
    rag_agent_url: str = "http://localhost:8001"
    mcp_tool_service_url: str = "http://localhost:8002"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Logging
    log_level: str = "INFO"


settings = Settings()
