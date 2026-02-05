"""MCP Tool Service Configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MCP Tool Service settings"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Service configuration
    service_name: str = "supply-chain-mcp-tool-service"
    service_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8002

    # Agent configuration
    agent_id: str = "mcp-tool-001"
    
    # Orchestrator
    orchestrator_url: str = "http://localhost:8000"
    
    # Logging
    log_level: str = "INFO"


settings = Settings()
