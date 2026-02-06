"""RAG Agent Configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """RAG Agent settings"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Service configuration
    service_name: str = "supply-chain-rag-agent"
    service_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8001

    # Agent configuration
    agent_id: str = "rag-agent-001"
    
    # ChromaDB configuration
    chroma_db_path: str = "./data/chromadb"
    chroma_collection_name: str = "supply_chain_docs"
    
    # Orchestrator
    orchestrator_url: str = "http://localhost:8000"
    
    # Logging
    log_level: str = "INFO"


settings = Settings()
