"""
RAG Knowledge Base for incident history and runbooks.

Uses vector similarity search to find relevant historical incidents
and operational knowledge.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import structlog
from pydantic import BaseModel, Field

from src.config.settings import get_settings

logger = structlog.get_logger()


class Incident(BaseModel):
    """Stored incident record."""

    id: str = Field(default_factory=lambda: f"INC-{uuid4().hex[:8]}")
    title: str
    description: str
    root_cause: str
    resolution: str
    metrics_affected: List[str] = Field(default_factory=list)
    services_affected: List[str] = Field(default_factory=list)
    severity: str
    duration_minutes: int
    occurred_at: datetime
    resolved_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    runbook_url: Optional[str] = None

    # Embedding for similarity search
    embedding: Optional[List[float]] = None


class Runbook(BaseModel):
    """Stored runbook."""

    id: str = Field(default_factory=lambda: f"RB-{uuid4().hex[:8]}")
    title: str
    description: str
    trigger_conditions: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    last_used: Optional[datetime] = None

    # Embedding for similarity search
    embedding: Optional[List[float]] = None


class SearchResult(BaseModel):
    """Search result with similarity score."""

    item: Union[Incident, Runbook]
    score: float
    item_type: str


class KnowledgeBase:
    """
    RAG-based knowledge base for incidents and runbooks.

    Features:
    - Vector similarity search using Qdrant
    - Incident storage and retrieval
    - Runbook management
    - Embedding generation
    """

    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        settings = get_settings()
        self.qdrant_url = qdrant_url or settings.qdrant.url
        self.collection_name = collection_name or settings.qdrant.collection_name

        self._client = None
        self._anthropic_client = None
        self._initialized = False

        # Local cache for development/fallback
        self._incidents: Dict[str, Incident] = {}
        self._runbooks: Dict[str, Runbook] = {}

    async def initialize(self) -> bool:
        """Initialize connection to Qdrant."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            self._client = QdrantClient(url=self.qdrant_url)

            # Check if collection exists
            collections = self._client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                # Create collection
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=get_settings().qdrant.embedding_dimensions,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(
                    "Created Qdrant collection",
                    collection=self.collection_name,
                )

            self._initialized = True
            logger.info("Knowledge base initialized", url=self.qdrant_url)
            return True

        except Exception as e:
            logger.warning(
                "Failed to initialize Qdrant, using local storage",
                error=str(e),
            )
            self._initialized = False
            return False

    async def add_incident(self, incident: Incident) -> str:
        """Add an incident to the knowledge base."""
        # Generate embedding
        embedding = await self._generate_embedding(
            f"{incident.title} {incident.description} {incident.root_cause} {incident.resolution}"
        )
        incident.embedding = embedding

        # Store in Qdrant if available
        if self._client and self._initialized and embedding:
            try:
                from qdrant_client.models import PointStruct

                self._client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        PointStruct(
                            id=hash(incident.id) % (2**63),
                            vector=embedding,
                            payload={
                                "type": "incident",
                                "id": incident.id,
                                "title": incident.title,
                                "description": incident.description,
                                "root_cause": incident.root_cause,
                                "resolution": incident.resolution,
                                "metrics_affected": incident.metrics_affected,
                                "services_affected": incident.services_affected,
                                "severity": incident.severity,
                                "duration_minutes": incident.duration_minutes,
                                "occurred_at": incident.occurred_at.isoformat(),
                                "tags": incident.tags,
                            },
                        )
                    ],
                )
            except Exception as e:
                logger.warning("Failed to store incident in Qdrant", error=str(e))

        # Always store in local cache
        self._incidents[incident.id] = incident

        logger.info("Added incident", id=incident.id, title=incident.title)
        return incident.id

    async def add_runbook(self, runbook: Runbook) -> str:
        """Add a runbook to the knowledge base."""
        # Generate embedding
        embedding = await self._generate_embedding(
            f"{runbook.title} {runbook.description} {' '.join(runbook.trigger_conditions)}"
        )
        runbook.embedding = embedding

        # Store in Qdrant if available
        if self._client and self._initialized and embedding:
            try:
                from qdrant_client.models import PointStruct

                self._client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        PointStruct(
                            id=hash(runbook.id) % (2**63),
                            vector=embedding,
                            payload={
                                "type": "runbook",
                                "id": runbook.id,
                                "title": runbook.title,
                                "description": runbook.description,
                                "trigger_conditions": runbook.trigger_conditions,
                                "steps": runbook.steps,
                                "tags": runbook.tags,
                            },
                        )
                    ],
                )
            except Exception as e:
                logger.warning("Failed to store runbook in Qdrant", error=str(e))

        # Always store in local cache
        self._runbooks[runbook.id] = runbook

        logger.info("Added runbook", id=runbook.id, title=runbook.title)
        return runbook.id

    async def search_similar_incidents(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.5,
    ) -> List[SearchResult]:
        """Search for similar incidents."""
        results: List[SearchResult] = []

        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        if self._client and self._initialized and query_embedding:
            try:
                search_results = self._client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    query_filter={
                        "must": [{"key": "type", "match": {"value": "incident"}}]
                    },
                    limit=limit,
                )

                for result in search_results:
                    if result.score >= min_score:
                        payload = result.payload
                        incident = Incident(
                            id=payload["id"],
                            title=payload["title"],
                            description=payload["description"],
                            root_cause=payload["root_cause"],
                            resolution=payload["resolution"],
                            metrics_affected=payload.get("metrics_affected", []),
                            services_affected=payload.get("services_affected", []),
                            severity=payload["severity"],
                            duration_minutes=payload["duration_minutes"],
                            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
                            tags=payload.get("tags", []),
                        )
                        results.append(
                            SearchResult(
                                item=incident,
                                score=result.score,
                                item_type="incident",
                            )
                        )
            except Exception as e:
                logger.warning("Qdrant search failed", error=str(e))

        # Fallback to local search if no results
        if not results:
            results = self._local_search_incidents(query, limit, min_score)

        return results

    async def search_runbooks(
        self,
        query: str,
        limit: int = 3,
        min_score: float = 0.5,
    ) -> List[SearchResult]:
        """Search for relevant runbooks."""
        results: List[SearchResult] = []

        query_embedding = await self._generate_embedding(query)

        if self._client and self._initialized and query_embedding:
            try:
                search_results = self._client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    query_filter={
                        "must": [{"key": "type", "match": {"value": "runbook"}}]
                    },
                    limit=limit,
                )

                for result in search_results:
                    if result.score >= min_score:
                        payload = result.payload
                        runbook = Runbook(
                            id=payload["id"],
                            title=payload["title"],
                            description=payload["description"],
                            trigger_conditions=payload.get("trigger_conditions", []),
                            steps=payload.get("steps", []),
                            tags=payload.get("tags", []),
                        )
                        results.append(
                            SearchResult(
                                item=runbook,
                                score=result.score,
                                item_type="runbook",
                            )
                        )
            except Exception as e:
                logger.warning("Qdrant runbook search failed", error=str(e))

        # Fallback to local search
        if not results:
            results = self._local_search_runbooks(query, limit, min_score)

        return results

    async def find_similar_to_anomaly(
        self,
        metric_name: str,
        deviation: float,
        severity: str,
        limit: int = 5,
    ) -> List[SearchResult]:
        """Find incidents similar to a given anomaly."""
        query = f"anomaly in {metric_name} with {abs(deviation):.1f} sigma deviation severity {severity}"
        return await self.search_similar_incidents(query, limit)

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text."""
        try:
            from anthropic import Anthropic

            settings = get_settings()
            if not settings.llm.api_key:
                return None

            # Note: Anthropic doesn't have an embedding API
            # In production, use OpenAI's text-embedding-3-small or similar
            # For now, return a simple hash-based pseudo-embedding for testing
            import hashlib

            # This is NOT a real embedding - just for testing
            # In production, use a proper embedding service
            hash_bytes = hashlib.sha256(text.encode()).digest()
            # Expand to embedding size using deterministic method
            import numpy as np
            np.random.seed(int.from_bytes(hash_bytes[:4], 'big'))
            embedding = np.random.randn(settings.qdrant.embedding_dimensions).tolist()
            return embedding

        except Exception as e:
            logger.warning("Embedding generation failed", error=str(e))
            return None

    def _local_search_incidents(
        self, query: str, limit: int, min_score: float
    ) -> List[SearchResult]:
        """Simple keyword-based local search fallback."""
        results: List[SearchResult] = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for incident in self._incidents.values():
            # Calculate simple relevance score
            text = f"{incident.title} {incident.description} {incident.root_cause}".lower()
            text_words = set(text.split())
            overlap = len(query_words & text_words)
            score = overlap / max(len(query_words), 1)

            if score >= min_score:
                results.append(
                    SearchResult(item=incident, score=score, item_type="incident")
                )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    def _local_search_runbooks(
        self, query: str, limit: int, min_score: float
    ) -> List[SearchResult]:
        """Simple keyword-based local search for runbooks."""
        results: List[SearchResult] = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for runbook in self._runbooks.values():
            text = f"{runbook.title} {runbook.description} {' '.join(runbook.trigger_conditions)}".lower()
            text_words = set(text.split())
            overlap = len(query_words & text_words)
            score = overlap / max(len(query_words), 1)

            if score >= min_score:
                results.append(
                    SearchResult(item=runbook, score=score, item_type="runbook")
                )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID."""
        return self._incidents.get(incident_id)

    def get_runbook(self, runbook_id: str) -> Optional[Runbook]:
        """Get runbook by ID."""
        return self._runbooks.get(runbook_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            "initialized": self._initialized,
            "qdrant_url": self.qdrant_url,
            "collection": self.collection_name,
            "incident_count": len(self._incidents),
            "runbook_count": len(self._runbooks),
        }
