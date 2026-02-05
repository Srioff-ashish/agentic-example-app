"""ChromaDB Service for RAG functionality"""
from __future__ import annotations

import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)


class ChromaDBService:
    """Service for managing ChromaDB operations"""

    def __init__(self, persist_directory: str, collection_name: str) -> None:
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self) -> chromadb.Collection:
        """Get or create a collection"""
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Supply chain knowledge base"},
        )

    async def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> None:
        """Add documents to the collection"""
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info(f"Added {len(documents)} documents to collection")

    async def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Query the collection"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )
        logger.info(f"Query returned {len(results.get('documents', [[]])[0])} results")
        return results

    async def delete_collection(self) -> None:
        """Delete the collection"""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")

    async def count_documents(self) -> int:
        """Count documents in the collection"""
        return self.collection.count()
