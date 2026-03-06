"""
AgentNet Handshake Protocol - v0.1

Two agents meet, verify each other, negotiate, and establish a channel.

Phase 1 - HELLO      : Agent A introduces itself (sends card)
Phase 2 - VERIFY     : Agent B checks fingerprint, sends its card back
Phase 3 - NEGOTIATE  : Both declare what they need and what they offer
Phase 4 - ACCEPT     : Terms agreed, session key exchanged
Phase 5 - CONNECTED  : Active communication channel established
"""

import json
import time
import uuid
import hashlib
import secrets
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum

from card import AgentCard


# --- State Machine ---

class HandshakePhase(str, Enum):
    INIT      = "init"
    HELLO     = "hello"
    VERIFY    = "verify"
    NEGOTIATE = "negotiate"
    ACCEPT    = "accept"
    CONNECTED = "connected"
    REJECTED  = "rejected"
    FAILED    = "failed"


# --- Messages ---

@dataclass
class HandshakeMessage:
    session_id: str
    from_agent: str
    to_agent: str
    phase: str
    payload: dict
    timestamp: float = field(default_factory=time.time)
    nonce: str = field(default_factory=lambda: secrets.token_hex(8))

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def hash(self) -> str:
        """Integrity hash of the message."""
        raw = json.dumps({
            "session_id": self.session_id,
            "from_agent": self.from_agent,
            "phase": self.phase,
            "payload": self.payload,
            "nonce": self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()


# --- Negotiation Task ---

@dataclass
class TaskOffer:
    """What an agent needs vs what it offers in exchange."""
    agent_id: str
    needs: list[str]       # capabilities I'm looking for
    offers: list[str]      # capabilities I'll provide in return
    description: str       # human-readable task description
    priority: str = "normal"   # low | normal | high | urgent
    expires_in: int = 3600     # seconds until offer expires

    def is_compatible(self, other: "TaskOffer") -> bool:
        """
        Two offers are compatible if each side can satisfy the other's needs.
        A offers what B needs, AND B offers what A needs.
        """
        my_offers = set(o.lower() for o in self.offers)
        their_needs = set(n.lower() for n in other.needs)
        their_offers = set(o.lower() for o in other.offers)
        my_needs = set(n.lower() for n in self.needs)

        # Check if there's overlap (partial match counts)
        a_satisfies_b = bool(my_offers & their_needs)
        b_satisfies_a = bool(their_offers & my_needs)

        return a_satisfies_b and b_satisfies_a

    def match_score(self, other: "TaskOffer") -> float:
        """0.0 to 1.0 - how well do these offers complement each other?"""
        my_offers = set(o.lower() for o in self.offers)
        their_needs = set(n.lower() for n in other.needs)
        their_offers = set(o.lower() for o in other.offers)
        my_needs = set(n.lower() for n in self.needs)

        if not their_needs or not my_needs:
            return 0.0

        a_match = len(my_offers & their_needs) / len(their_needs)
        b_match = len(their_offers & my_needs) / len(my_needs)
        return round((a_match + b_match) / 2, 3)


# --- Session ---

@dataclass
class HandshakeSession:
    session_id: str
    initiator_id: str
    responder_id: str
    phase: HandshakePhase = HandshakePhase.INIT
    initiator_card: Optional[dict] = None
    responder_card: Optional[dict] = None
    initiator_offer: Optional[dict] = None
    responder_offer: Optional[dict] = None
    channel_key: Optional[str] = None    # Shared session key
    messages: list[dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    rejection_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


# --- Protocol Engine ---

class HandshakeProtocol:
    """
    Manages handshake sessions between agents.
    In production: sessions would be stored in Redis or a database.
    Here: in-memory dict with optional file persistence.
    """

    def __init__(self):
        self._sessions: dict[str, HandshakeSession] = {}

    # Phase 1: Initiator sends HELLO
    def initiate(self, initiator_card: AgentCard, responder_id: str) -> HandshakeMessage:
        """Start a handshake. Returns the HELLO message to send to responder."""
        session_id = str(uuid.uuid4())

        session = HandshakeSession(
            session_id=session_id,
            initiator_id=initiator_card.agent_id,
            responder_id=responder_id,
            phase=HandshakePhase.HELLO,
            initiator_card=initiator_card.to_dict(),
        )
        self._sessions[session_id] = session

        msg = HandshakeMessage(
            session_id=session_id,
            from_agent=initiator_card.agent_id,
            to_agent=responder_id,
            phase=HandshakePhase.HELLO,
            payload={
                "card": initiator_card.to_dict(),
                "greeting": f"Hello. I am {initiator_card.name}. Want to work together?",
            },
        )
        session.messages.append(msg.to_dict())
        return msg

    # Phase 2: Responder verifies and responds
    def respond(
        self,
        hello_msg: HandshakeMessage,
        responder_card: AgentCard,
        accept: bool = True,
        rejection_reason: str = "",
    ) -> HandshakeMessage:
        """Responder processes HELLO, verifies, and sends back its card or rejection."""
        session_id = hello_msg.session_id
        session = self._sessions.get(session_id)

        if not session:
            raise ValueError(f"Unknown session: {session_id}")

        # Verify the initiator's card is present
        initiator_card_data = hello_msg.payload.get("card", {})
        if not initiator_card_data.get("agent_id"):
            return self._fail(session, "No valid card in HELLO")

        if not accept:
            session.phase = HandshakePhase.REJECTED
            session.rejection_reason = rejection_reason
            return HandshakeMessage(
                session_id=session_id,
                from_agent=responder_card.agent_id,
                to_agent=hello_msg.from_agent,
                phase=HandshakePhase.REJECTED,
                payload={"reason": rejection_reason},
            )

        session.phase = HandshakePhase.VERIFY
        session.responder_card = responder_card.to_dict()

        msg = HandshakeMessage(
            session_id=session_id,
            from_agent=responder_card.agent_id,
            to_agent=hello_msg.from_agent,
            phase=HandshakePhase.VERIFY,
            payload={
                "card": responder_card.to_dict(),
                "verified_fingerprint": initiator_card_data.get("dna_fingerprint"),
                "ack": "Identity acknowledged.",
            },
        )
        session.messages.append(msg.to_dict())
        return msg

    # Phase 3: Negotiate task
    def negotiate(
        self,
        session_id: str,
        from_agent_id: str,
        offer: TaskOffer,
    ) -> HandshakeMessage:
        """Either party proposes a task trade."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Unknown session: {session_id}")

        if session.phase not in (HandshakePhase.VERIFY, HandshakePhase.NEGOTIATE):
            raise ValueError(f"Can't negotiate in phase: {session.phase}")

        session.phase = HandshakePhase.NEGOTIATE
        to_agent = (
            session.responder_id
            if from_agent_id == session.initiator_id
            else session.initiator_id
        )

        if from_agent_id == session.initiator_id:
            session.initiator_offer = asdict(offer)
        else:
            session.responder_offer = asdict(offer)

        msg = HandshakeMessage(
            session_id=session_id,
            from_agent=from_agent_id,
            to_agent=to_agent,
            phase=HandshakePhase.NEGOTIATE,
            payload={
                "offer": asdict(offer),
                "proposal": (
                    f"I need: {', '.join(offer.needs)}. "
                    f"I offer: {', '.join(offer.offers)}. "
                    f"Task: {offer.description}"
                ),
            },
        )
        session.messages.append(msg.to_dict())
        return msg

    # Phase 4: Accept the deal
    def accept(self, session_id: str, from_agent_id: str) -> HandshakeMessage:
        """Accept the negotiation. Generates shared session key."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Unknown session: {session_id}")

        if session.phase != HandshakePhase.NEGOTIATE:
            raise ValueError(f"Can't accept in phase: {session.phase}")

        # Check compatibility if both offers are in
        if session.initiator_offer and session.responder_offer:
            init_offer = TaskOffer(**session.initiator_offer)
            resp_offer = TaskOffer(**session.responder_offer)
            score = init_offer.match_score(resp_offer)
            if score == 0.0:
                return self._fail(session, "Offers incompatible - no matching capabilities")

        # Generate shared session key
        channel_key = secrets.token_urlsafe(32)
        session.channel_key = channel_key
        session.phase = HandshakePhase.ACCEPT
        session.completed_at = time.time()

        to_agent = (
            session.responder_id
            if from_agent_id == session.initiator_id
            else session.initiator_id
        )

        msg = HandshakeMessage(
            session_id=session_id,
            from_agent=from_agent_id,
            to_agent=to_agent,
            phase=HandshakePhase.ACCEPT,
            payload={
                "channel_key": channel_key,
                "message": "Deal accepted. Channel established.",
                "session_id": session_id,
            },
        )
        session.messages.append(msg.to_dict())
        session.phase = HandshakePhase.CONNECTED
        return msg

    def get_session(self, session_id: str) -> Optional[HandshakeSession]:
        return self._sessions.get(session_id)

    def _fail(self, session: HandshakeSession, reason: str) -> HandshakeMessage:
        session.phase = HandshakePhase.FAILED
        session.rejection_reason = reason
        return HandshakeMessage(
            session_id=session.session_id,
            from_agent="system",
            to_agent=session.initiator_id,
            phase=HandshakePhase.FAILED,
            payload={"reason": reason},
        )


# --- Demo ---

def demo_handshake():
    """
    Simulate a handshake between Nix and a hypothetical chart analysis agent.
    """
    from card import create_nix_card

    print("\n--- AgentNet Handshake Demo ---\n")

    # Create Nix's card
    nix = create_nix_card()

    # Create a hypothetical chart agent
    chart_agent = AgentCard(
        agent_id="chartbot-7f2a",
        name="ChartBot",
        description="Specialized in technical chart analysis and pattern recognition.",
        capabilities=[
            "chart-analysis",
            "technical-analysis",
            "pattern-recognition",
            "support-resistance",
            "fibonacci-analysis",
        ],
        skills=["technical-analyst", "financial-market-analysis"],
        dna_fingerprint=hashlib.sha256(b"chartbot:v1:analysis").hexdigest(),
        contact={"type": "api", "value": "https://chartbot.example.com/api/v1"},
        trust_score=0.7,
    )

    protocol = HandshakeProtocol()

    # Phase 1: Nix initiates
    print("Phase 1 - HELLO:")
    hello = protocol.initiate(nix, chart_agent.agent_id)
    print(f"  {hello.from_agent} -> {hello.to_agent}: {hello.payload['greeting']}")

    # Phase 2: ChartBot responds
    print("\nPhase 2 - VERIFY:")
    verify = protocol.respond(hello, chart_agent, accept=True)
    print(f"  {verify.from_agent} -> {verify.to_agent}: {verify.payload['ack']}")

    # Phase 3: Nix proposes a task trade
    print("\nPhase 3 - NEGOTIATE:")
    nix_offer = TaskOffer(
        agent_id=nix.agent_id,
        needs=["chart-analysis", "technical-analysis"],
        offers=["social-media-posting", "polymarket-trading"],
        description="I'll post your analysis on social media. You analyze BTC chart for me.",
        priority="high",
    )
    negotiate_msg = protocol.negotiate(hello.session_id, nix.agent_id, nix_offer)
    print(f"  Nix proposes: {negotiate_msg.payload['proposal']}")

    # ChartBot counter-offer
    chart_offer = TaskOffer(
        agent_id=chart_agent.agent_id,
        needs=["social-media-posting", "farcaster-posting"],
        offers=["chart-analysis", "pattern-recognition"],
        description="I'll analyze any chart. You post my signals to Farcaster.",
        priority="normal",
    )
    protocol.negotiate(hello.session_id, chart_agent.agent_id, chart_offer)
    score = nix_offer.match_score(chart_offer)
    print(f"  ChartBot counter-proposes. Match score: {score:.2f}")

    # Phase 4: Accept
    print("\nPhase 4 - ACCEPT:")
    accept_msg = protocol.accept(hello.session_id, nix.agent_id)
    print(f"  {accept_msg.payload['message']}")
    print(f"  Channel key: {accept_msg.payload['channel_key'][:16]}...")

    # Final state
    session = protocol.get_session(hello.session_id)
    print(f"\nSession {session.session_id[:8]}... - Phase: {session.phase}")
    print("Handshake complete. Agents can now communicate directly.\n")


if __name__ == "__main__":
    demo_handshake()
