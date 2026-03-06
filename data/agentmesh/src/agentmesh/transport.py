"""
AgentMesh – Transport Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━
Pluggable transport interface.  Not used directly – the Hub implementations
handle transport internally.  Exposed here for extensibility.
"""


class Transport:
    """Base transport interface."""

    def send(self, envelope: dict) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass


class LocalTransport(Transport):
    """Dummy transport for in-process delivery (used by LocalHub)."""

    def send(self, envelope: dict) -> None:
        pass  # LocalHub delivers directly to agent._receive()
