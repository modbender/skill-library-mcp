# tarot_skill type definitions, aligned with tarot_game

from typing import List, Literal, TypedDict

ReadingFocus = Literal["general", "love", "career"]
SpreadType = Literal[
    "three",
    "daily",
    "single",
    "relationship",
    "career",
    "celtic_cross",
]


class CardMeanings(TypedDict):
    general: str
    love: str
    career: str


class CardMeaningsZh(TypedDict):
    upright: CardMeanings
    reversed: CardMeanings


class CardName(TypedDict):
    zh: str
    en: str


class Card(TypedDict):
    id: str
    name: CardName
    arcana: Literal["Major", "Minor"]
    image: str
    meanings: dict  # {"zh": CardMeaningsZh}


class CardPosition(TypedDict):
    card: Card
    isReversed: bool
    positionName: str


class TarotReadingRequest(TypedDict, total=False):
    spreadType: SpreadType
    question: str
    focus: ReadingFocus


class TarotReadingResult(TypedDict, total=False):
    ok: bool
    question: str
    focus: ReadingFocus
    spreadType: SpreadType
    spread: List["CardPosition"]
    summary: str
    error: str
