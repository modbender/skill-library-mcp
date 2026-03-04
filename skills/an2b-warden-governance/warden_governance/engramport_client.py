"""War/Den EngramPort Client -- enterprise cloud memory via MandelDB.

Provides the same interface as LocalMemoryStore but backed by
EngramPort cloud with vector search, AEGIS provenance, and
Eidetic synthesis.

Endpoints (via mandeldb.com/api/v1/portal):
- /remember  -- store a memory with vector embedding + AEGIS hash
- /recall    -- semantic search across memories
- /reflect   -- LLM-powered insight synthesis
- /stats     -- memory count, insights, activity

Key format: ek_bot_* (SHA-256 hashed at rest, shown once at registration)
"""

from __future__ import annotations

import json
import logging

from warden_governance.settings import Settings

logger = logging.getLogger("warden")


class EngramPortError(Exception):
    """General EngramPort error."""


class EngramPortAuthError(EngramPortError):
    """Invalid EngramPort API key."""


class EngramPortClient:
    """Enterprise memory client backed by EngramPort + MandelDB."""

    def __init__(self, config: Settings):
        self.config = config
        self.api_key = config.engramport_api_key
        self.base_url = config.engramport_base_url

        self._fallback_store = None
        if config.engramport_fallback:
            from warden_governance.local_store import LocalMemoryStore

            self._fallback_store = LocalMemoryStore(config)

    def write(
        self,
        bot_id: str,
        content: str,
        namespace: str,
        metadata: dict,
        ttl_days: int = 30,
    ) -> str:
        """Store a memory via EngramPort /remember endpoint."""
        try:
            import httpx
        except ImportError:
            return self._fallback_write(bot_id, content, namespace, metadata, ttl_days)

        url = f"{self.base_url}/remember"
        payload = {
            "content": content,
            "context": json.dumps(metadata),
            "session_id": namespace,
        }

        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    url,
                    json=payload,
                    headers={
                        "X-API-Key": self.api_key,
                        "Content-Type": "application/json",
                    },
                )

            if resp.status_code == 401:
                raise EngramPortAuthError("Invalid EngramPort API key")

            if resp.status_code >= 400:
                if self._fallback_store and resp.status_code >= 500:
                    logger.warning(
                        "EngramPort %s error; falling back to local",
                        resp.status_code,
                    )
                    return self._fallback_write(
                        bot_id, content, namespace, metadata, ttl_days
                    )
                resp.raise_for_status()

            data = resp.json()
            return data.get("memory_id", "")

        except EngramPortAuthError:
            raise
        except Exception as exc:
            if self._fallback_store:
                logger.warning("EngramPort unreachable: %s; using local fallback", exc)
                return self._fallback_write(
                    bot_id, content, namespace, metadata, ttl_days
                )
            raise EngramPortError(f"EngramPort write failed: {exc}") from exc

    def read(
        self,
        bot_id: str,
        query: str,
        namespace: str,
        limit: int = 10,
    ) -> list[dict]:
        """Semantic recall via EngramPort /recall endpoint."""
        try:
            import httpx
        except ImportError:
            return self._fallback_read(bot_id, query, namespace, limit)

        url = f"{self.base_url}/recall"
        payload = {"query": query, "limit": limit}

        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    url,
                    json=payload,
                    headers={
                        "X-API-Key": self.api_key,
                        "Content-Type": "application/json",
                    },
                )

            if resp.status_code == 401:
                raise EngramPortAuthError("Invalid EngramPort API key")
            if resp.status_code >= 400:
                resp.raise_for_status()

            data = resp.json()
            memories = data.get("memories", [])
            return [
                {
                    "memory_id": m.get("id", ""),
                    "content": m.get("content", ""),
                    "metadata": {},
                    "created_at": m.get("created_at", ""),
                    "relevance_score": m.get("relevance_score", 0),
                }
                for m in memories
            ]

        except EngramPortAuthError:
            raise
        except Exception as exc:
            if self._fallback_store:
                logger.warning("EngramPort recall failed: %s; using local", exc)
                return self._fallback_read(bot_id, query, namespace, limit)
            raise EngramPortError(f"EngramPort read failed: {exc}") from exc

    def delete(self, bot_id: str, memory_id: str) -> bool:
        """Delete a memory via EngramPort."""
        try:
            import httpx
        except ImportError:
            if self._fallback_store:
                return self._fallback_store.delete(bot_id, memory_id)
            return False

        try:
            with httpx.Client(timeout=30) as client:
                resp = client.request(
                    "DELETE",
                    f"{self.base_url}/memory/{memory_id}",
                    headers={
                        "X-API-Key": self.api_key,
                        "Content-Type": "application/json",
                    },
                )

            if resp.status_code == 401:
                raise EngramPortAuthError("Invalid EngramPort API key")

            return resp.status_code < 400

        except EngramPortAuthError:
            raise
        except Exception as exc:
            if self._fallback_store:
                return self._fallback_store.delete(bot_id, memory_id)
            raise EngramPortError(f"EngramPort delete failed: {exc}") from exc

    def synthesize(
        self,
        bot_id: str,
        query: str,
        namespaces: list[str],
    ) -> str:
        """Eidetic synthesis via EngramPort /reflect endpoint."""
        try:
            import httpx
        except ImportError:
            if self._fallback_store:
                return self._fallback_store.synthesize(bot_id, query, namespaces)
            return ""

        url = f"{self.base_url}/reflect"
        payload = {"topic": query}

        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    url,
                    json=payload,
                    headers={
                        "X-API-Key": self.api_key,
                        "Content-Type": "application/json",
                    },
                )

            if resp.status_code == 401:
                raise EngramPortAuthError("Invalid EngramPort API key")
            if resp.status_code >= 400:
                resp.raise_for_status()

            data = resp.json()
            insights = data.get("insights", [])
            return "\n".join(i.get("content", "") for i in insights)

        except EngramPortAuthError:
            raise
        except Exception as exc:
            if self._fallback_store:
                logger.warning("EngramPort reflect failed: %s; using local", exc)
                return self._fallback_store.synthesize(bot_id, query, namespaces)
            raise EngramPortError(f"EngramPort synthesis failed: {exc}") from exc

    def _fallback_write(
        self, bot_id: str, content: str, namespace: str, metadata: dict, ttl_days: int
    ) -> str:
        if self._fallback_store:
            return self._fallback_store.write(
                bot_id, content, namespace, metadata, ttl_days
            )
        raise EngramPortError("EngramPort unavailable and no fallback configured")

    def _fallback_read(
        self, bot_id: str, query: str, namespace: str, limit: int
    ) -> list[dict]:
        if self._fallback_store:
            return self._fallback_store.read(bot_id, query, namespace, limit)
        return []
