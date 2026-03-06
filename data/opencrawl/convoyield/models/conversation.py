"""
Conversation state models — the living representation of a yield-bearing conversation.

Every conversation is treated as a financial instrument with:
- A current "price" (engagement level)
- A "yield" (value extracted so far)
- "Momentum" (direction and velocity of value flow)
- "Volatility" (unpredictability of user behavior)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Speaker(Enum):
    USER = "user"
    BOT = "bot"


class ConversationPhase(Enum):
    """Like market phases — each requires a different strategy."""
    OPENING = "opening"           # First contact — high uncertainty, high potential
    DISCOVERY = "discovery"       # Learning about the user — data acquisition phase
    ENGAGEMENT = "engagement"     # Active value exchange — the meat of the conversation
    NEGOTIATION = "negotiation"   # User is considering an action — critical moment
    CLOSING = "closing"           # Wrapping up — last chance for value extraction
    POST_CLOSE = "post_close"     # After primary goal — bonus yield territory


@dataclass
class Turn:
    """A single conversational exchange."""
    speaker: Speaker
    text: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    @property
    def has_question(self) -> bool:
        return "?" in self.text

    @property
    def exclamation_density(self) -> float:
        if not self.text:
            return 0.0
        return self.text.count("!") / len(self.text)

    @property
    def caps_ratio(self) -> float:
        alpha = [c for c in self.text if c.isalpha()]
        if not alpha:
            return 0.0
        return sum(1 for c in alpha if c.isupper()) / len(alpha)


@dataclass
class ConversationState:
    """
    The full state of a yield-bearing conversation.

    This is the central object that all engines read from and write to.
    Think of it as the "order book" for the conversation.
    """
    turns: list[Turn] = field(default_factory=list)
    phase: ConversationPhase = ConversationPhase.OPENING
    accumulated_yield: float = 0.0
    micro_conversions_captured: list[str] = field(default_factory=list)
    active_plays: list[str] = field(default_factory=list)
    sentiment_history: list[float] = field(default_factory=list)
    momentum_history: list[float] = field(default_factory=list)
    session_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def add_turn(self, speaker: Speaker, text: str, **kwargs) -> Turn:
        turn = Turn(speaker=speaker, text=text, **kwargs)
        self.turns.append(turn)
        self._update_phase()
        return turn

    def _update_phase(self):
        """Auto-detect conversation phase based on turn count and patterns."""
        n = len(self.turns)
        user_turns = [t for t in self.turns if t.speaker == Speaker.USER]

        if n <= 2:
            self.phase = ConversationPhase.OPENING
        elif n <= 5:
            self.phase = ConversationPhase.DISCOVERY
        elif any(self._has_closing_signal(t.text) for t in self.turns[-2:]):
            self.phase = ConversationPhase.CLOSING
        elif any(self._has_negotiation_signal(t.text) for t in user_turns[-2:]):
            self.phase = ConversationPhase.NEGOTIATION
        else:
            self.phase = ConversationPhase.ENGAGEMENT

    @staticmethod
    def _has_closing_signal(text: str) -> bool:
        closing_patterns = [
            "thank", "bye", "goodbye", "that's all", "that is all",
            "nothing else", "i'm good", "im good", "talk later",
            "gotta go", "have to go", "ttyl",
        ]
        lower = text.lower()
        return any(p in lower for p in closing_patterns)

    @staticmethod
    def _has_negotiation_signal(text: str) -> bool:
        negotiation_patterns = [
            "how much", "price", "cost", "discount", "deal",
            "cheaper", "afford", "budget", "compare", "alternative",
            "competitor", "vs", "versus", "worth it", "roi",
            "free trial", "guarantee", "refund",
        ]
        lower = text.lower()
        return any(p in lower for p in negotiation_patterns)

    @property
    def turn_count(self) -> int:
        return len(self.turns)

    @property
    def user_turns(self) -> list[Turn]:
        return [t for t in self.turns if t.speaker == Speaker.USER]

    @property
    def bot_turns(self) -> list[Turn]:
        return [t for t in self.turns if t.speaker == Speaker.BOT]

    @property
    def last_user_turn(self) -> Optional[Turn]:
        user_turns = self.user_turns
        return user_turns[-1] if user_turns else None

    @property
    def avg_user_message_length(self) -> float:
        user_turns = self.user_turns
        if not user_turns:
            return 0.0
        return sum(t.word_count for t in user_turns) / len(user_turns)

    @property
    def conversation_duration(self) -> float:
        if len(self.turns) < 2:
            return 0.0
        return self.turns[-1].timestamp - self.turns[0].timestamp

    @property
    def response_velocity(self) -> float:
        """Average time between turns — faster = more engaged."""
        if len(self.turns) < 2:
            return 0.0
        gaps = []
        for i in range(1, len(self.turns)):
            gap = self.turns[i].timestamp - self.turns[i - 1].timestamp
            if gap > 0:
                gaps.append(gap)
        return sum(gaps) / len(gaps) if gaps else 0.0
