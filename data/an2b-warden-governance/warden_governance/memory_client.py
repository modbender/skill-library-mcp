"""War/Den Governed Memory Client -- every memory operation is governed."""

from __future__ import annotations

import logging

from warden_governance.action_bridge import Action, ActionType, GovernanceError
from warden_governance.local_store import LocalMemoryStore
from warden_governance.sentinel_client import SentinelClient
from warden_governance.settings import Settings

logger = logging.getLogger("warden")


class MemoryClient:
    """Unified memory interface with governance enforcement.

    Every read/write/delete/synthesize is checked by Sentinel FIRST.
    If governance denies the operation, the memory is NEVER accessed.
    """

    def __init__(self, config: Settings, sentinel: SentinelClient):
        self.config = config
        self.sentinel = sentinel

        if config.engramport_api_key:
            self.store_mode = "engramport"
            try:
                from warden_governance.engramport_client import EngramPortClient

                self.store = EngramPortClient(config)
            except ImportError:
                logger.warning(
                    "EngramPort client unavailable; falling back to local memory"
                )
                self.store_mode = "community"
                self.store = LocalMemoryStore(config)
        else:
            self.store_mode = "community"
            self.store = LocalMemoryStore(config)

    def write(
        self,
        content: str,
        namespace: str = "default",
        metadata: dict | None = None,
        ttl_days: int = 30,
    ) -> str:
        """Write content to memory. Governed."""
        action = Action(
            type=ActionType.MEMORY_WRITE,
            data={"content": content[:100], "namespace": namespace},
            context={"operation": "memory.write"},
            agent_id=self.config.warden_agent_id,
        )
        self.sentinel.check(action)  # Raises GovernanceError on DENY

        return self.store.write(
            bot_id=self.config.warden_agent_id,
            content=content,
            namespace=namespace,
            metadata=metadata or {},
            ttl_days=ttl_days,
        )

    def read(
        self,
        query: str,
        namespace: str = "default",
        limit: int = 10,
    ) -> list[dict]:
        """Read memories matching a query. Governed."""
        action = Action(
            type=ActionType.MEMORY_READ,
            data={"query": query[:100], "namespace": namespace},
            context={"operation": "memory.read"},
            agent_id=self.config.warden_agent_id,
        )
        self.sentinel.check(action)

        return self.store.read(
            bot_id=self.config.warden_agent_id,
            query=query,
            namespace=namespace,
            limit=limit,
        )

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID. Governed."""
        action = Action(
            type=ActionType.MEMORY_DELETE,
            data={"memory_id": memory_id},
            context={"operation": "memory.delete"},
            agent_id=self.config.warden_agent_id,
        )
        self.sentinel.check(action)

        return self.store.delete(
            bot_id=self.config.warden_agent_id,
            memory_id=memory_id,
        )

    def synthesize(
        self,
        query: str,
        namespaces: list[str] | None = None,
    ) -> str:
        """Synthesize insights across namespaces. Governed."""
        ns = namespaces or ["default"]
        action = Action(
            type=ActionType.MEMORY_SYNTHESIZE,
            data={"query": query[:100], "namespaces": ns},
            context={"operation": "memory.synthesize"},
            agent_id=self.config.warden_agent_id,
        )
        self.sentinel.check(action)

        return self.store.synthesize(
            bot_id=self.config.warden_agent_id,
            query=query,
            namespaces=ns,
        )
