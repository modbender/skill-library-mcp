"""Conversation data models for the ResonanceEngine."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Speaker(Enum):
    USER = "user"
    BOT = "bot"


@dataclass
class Message:
    """A single message in a conversation."""

    text: str
    speaker: Speaker
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    @property
    def char_count(self) -> int:
        return len(self.text)

    @property
    def sentence_count(self) -> int:
        count = 0
        for char in self.text:
            if char in ".!?":
                count += 1
        return max(count, 1)

    @property
    def question_count(self) -> int:
        return self.text.count("?")


@dataclass
class Conversation:
    """A full conversation thread with analysis-ready accessors."""

    messages: list[Message] = field(default_factory=list)
    conversation_id: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    goal: Optional[str] = None  # "sale", "support", "engagement", "retention"

    def add_message(self, text: str, speaker: Speaker, **metadata) -> Message:
        msg = Message(text=text, speaker=speaker, metadata=metadata)
        self.messages.append(msg)
        return msg

    def add_user_message(self, text: str, **metadata) -> Message:
        return self.add_message(text, Speaker.USER, **metadata)

    def add_bot_message(self, text: str, **metadata) -> Message:
        return self.add_message(text, Speaker.BOT, **metadata)

    @property
    def user_messages(self) -> list[Message]:
        return [m for m in self.messages if m.speaker == Speaker.USER]

    @property
    def bot_messages(self) -> list[Message]:
        return [m for m in self.messages if m.speaker == Speaker.BOT]

    @property
    def turn_count(self) -> int:
        return len(self.messages)

    @property
    def duration(self) -> float:
        if len(self.messages) < 2:
            return 0.0
        return self.messages[-1].timestamp - self.messages[0].timestamp

    def last_n_user_messages(self, n: int) -> list[Message]:
        return self.user_messages[-n:]

    def last_n_messages(self, n: int) -> list[Message]:
        return self.messages[-n:]
