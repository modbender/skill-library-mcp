from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ContinuityRepository(Protocol):
    def migrate(self) -> bool: ...

    def get_soul_card(self, agent_id: str) -> Any | None: ...

    def get_mission_ticket(self, agent_id: str) -> Any | None: ...


@runtime_checkable
class ContinuityPacketBuilder(Protocol):
    def build_packet(self, agent_id: str) -> Any: ...
