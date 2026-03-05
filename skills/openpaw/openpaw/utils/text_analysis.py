"""Zero-cost text analysis utilities. No APIs. No ML models. Pure Python."""

from __future__ import annotations

import re
import math

# Hedging / uncertainty language
HEDGE_WORDS = frozenset({
    "maybe", "perhaps", "possibly", "might", "could", "somewhat",
    "i think", "i guess", "i suppose", "not sure", "not certain",
    "kind of", "sort of", "a bit", "a little", "probably",
    "it depends", "hard to say", "i wonder", "im not sure",
    "don't know", "dont know", "uncertain", "unsure",
})

# Commitment / decision language
COMMIT_WORDS = frozenset({
    "yes", "absolutely", "definitely", "let's do it", "lets do it",
    "i want", "i need", "sign me up", "count me in", "deal",
    "agreed", "for sure", "perfect", "exactly", "i'll take",
    "ill take", "sounds good", "let's go", "lets go", "ready",
    "i'm in", "im in", "sold", "done", "great", "love it",
    "do it", "proceed", "confirm", "buy", "purchase", "subscribe",
})

# Objection / resistance language
OBJECTION_WORDS = frozenset({
    "but", "however", "although", "expensive", "costly", "too much",
    "not worth", "i don't think", "i dont think", "concerned",
    "worried", "risk", "risky", "problem", "issue", "complicated",
    "difficult", "hard", "can't", "cant", "won't", "wont",
    "no thanks", "not interested", "pass", "skip", "later",
    "think about it", "need time", "not now", "too fast",
})

# Positive emotional language
POSITIVE_WORDS = frozenset({
    "amazing", "awesome", "great", "excellent", "fantastic",
    "wonderful", "love", "like", "enjoy", "happy", "excited",
    "impressed", "beautiful", "brilliant", "cool", "nice",
    "thank", "thanks", "appreciate", "helpful", "good",
})

# Negative emotional language
NEGATIVE_WORDS = frozenset({
    "bad", "terrible", "awful", "horrible", "hate", "dislike",
    "angry", "frustrated", "annoyed", "disappointed", "confused",
    "lost", "stuck", "broken", "wrong", "fail", "failed",
    "useless", "waste", "boring", "slow", "ugly", "stupid",
})

# Urgency language
URGENCY_WORDS = frozenset({
    "asap", "urgent", "immediately", "now", "quickly", "fast",
    "hurry", "rush", "deadline", "today", "right away",
    "as soon as possible", "critical", "emergency",
})


class TextAnalyzer:
    """Pure-Python text analysis engine. Zero dependencies. Zero API costs."""

    @staticmethod
    def word_count(text: str) -> int:
        return len(text.split())

    @staticmethod
    def sentence_count(text: str) -> int:
        count = sum(1 for c in text if c in ".!?")
        return max(count, 1)

    @staticmethod
    def question_count(text: str) -> int:
        return text.count("?")

    @staticmethod
    def exclamation_count(text: str) -> int:
        return text.count("!")

    @staticmethod
    def avg_word_length(text: str) -> float:
        words = text.split()
        if not words:
            return 0.0
        return sum(len(w) for w in words) / len(words)

    @staticmethod
    def caps_ratio(text: str) -> float:
        alpha_chars = [c for c in text if c.isalpha()]
        if not alpha_chars:
            return 0.0
        return sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)

    @staticmethod
    def lexical_diversity(text: str) -> float:
        words = text.lower().split()
        if not words:
            return 0.0
        return len(set(words)) / len(words)

    @staticmethod
    def phrase_density(text: str, phrase_set: frozenset) -> float:
        text_lower = text.lower()
        words = text_lower.split()
        if not words:
            return 0.0
        matches = 0
        for phrase in phrase_set:
            if " " in phrase:
                if phrase in text_lower:
                    matches += len(phrase.split())
            else:
                matches += words.count(phrase)
        return min(matches / len(words), 1.0)

    @staticmethod
    def hedge_density(text: str) -> float:
        return TextAnalyzer.phrase_density(text, HEDGE_WORDS)

    @staticmethod
    def commit_density(text: str) -> float:
        return TextAnalyzer.phrase_density(text, COMMIT_WORDS)

    @staticmethod
    def objection_density(text: str) -> float:
        return TextAnalyzer.phrase_density(text, OBJECTION_WORDS)

    @staticmethod
    def positive_density(text: str) -> float:
        return TextAnalyzer.phrase_density(text, POSITIVE_WORDS)

    @staticmethod
    def negative_density(text: str) -> float:
        return TextAnalyzer.phrase_density(text, NEGATIVE_WORDS)

    @staticmethod
    def urgency_density(text: str) -> float:
        return TextAnalyzer.phrase_density(text, URGENCY_WORDS)

    @staticmethod
    def sentiment_score(text: str) -> float:
        """Simple sentiment: -1 (negative) to +1 (positive)."""
        pos = TextAnalyzer.positive_density(text)
        neg = TextAnalyzer.negative_density(text)
        total = pos + neg
        if total == 0:
            return 0.0
        return (pos - neg) / total

    @staticmethod
    def formality_score(text: str) -> float:
        """0 (casual) to 1 (formal). Based on word length, contractions, slang markers."""
        words = text.split()
        if not words:
            return 0.5

        avg_len = sum(len(w) for w in words) / len(words)
        has_contractions = bool(re.search(r"\b\w+'\w+\b", text))
        has_emoji = bool(re.search(r"[^\w\s,.\-!?;:\"'()@#$%^&*+=<>/\\|`~\[\]{}]", text))

        score = min(avg_len / 8.0, 1.0)  # Longer words = more formal
        if has_contractions:
            score -= 0.15
        if has_emoji:
            score -= 0.2

        return max(0.0, min(1.0, score))

    @staticmethod
    def compute_trajectory(values: list[float]) -> float:
        """Compute trend direction from a list of values. Returns -1 to 1."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        # Simple linear regression slope
        x_mean = (n - 1) / 2.0
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        # Normalize to -1 to 1 range using tanh
        return math.tanh(slope * 2)

    @staticmethod
    def mirror_score(text_a: str, text_b: str) -> float:
        """How much text_b mirrors text_a's style. 0-1."""
        if not text_a or not text_b:
            return 0.0

        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a or not words_b:
            return 0.0

        # Vocabulary overlap
        overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)

        # Length similarity
        len_ratio = min(len(text_a), len(text_b)) / max(len(text_a), len(text_b), 1)

        # Formality similarity
        form_diff = abs(
            TextAnalyzer.formality_score(text_a) - TextAnalyzer.formality_score(text_b)
        )

        return (overlap * 0.4 + len_ratio * 0.3 + (1 - form_diff) * 0.3)
