"""
Signal Extraction Layer.

Reads 15+ invisible micro-signals from conversation messages.
Pure algorithmic — zero API calls, zero ML models.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from openpaw.models.conversation import Conversation, Message, Speaker
from openpaw.utils.text_analysis import TextAnalyzer


@dataclass
class ConversationSignals:
    """All extracted signals from a conversation at a point in time."""

    # --- Engagement Signals ---
    message_length_trajectory: float = 0.0   # -1 to 1: shrinking vs growing
    question_density: float = 0.0            # 0 to 1: how many questions user asks
    response_elaboration: float = 0.0        # 0 to 1: how detailed are responses
    topic_persistence: float = 0.0           # 0 to 1: staying on vs drifting off topic
    exclamation_energy: float = 0.0          # 0 to 1: emotional energy markers

    # --- Trust Signals ---
    hedge_ratio: float = 0.0                 # 0 to 1: uncertainty language
    personal_disclosure: float = 0.0         # 0 to 1: sharing personal info
    formality_drift: float = 0.0             # -1 to 1: becoming more/less formal
    mirror_behavior: float = 0.0             # 0 to 1: copying bot's language
    positive_sentiment_trend: float = 0.0    # -1 to 1: sentiment trajectory

    # --- Decision Signals ---
    commitment_language: float = 0.0         # 0 to 1: decision/buy words
    objection_frequency: float = 0.0         # 0 to 1: resistance markers
    specificity_increase: float = 0.0        # -1 to 1: getting more specific
    urgency_markers: float = 0.0             # 0 to 1: time pressure language
    action_language: float = 0.0             # 0 to 1: "do", "make", "start" words

    # --- Style Signals ---
    avg_sentence_length: float = 0.0         # raw average
    vocabulary_complexity: float = 0.0       # 0 to 1: lexical diversity
    formality_level: float = 0.0             # 0 to 1: casual vs formal
    caps_usage: float = 0.0                  # 0 to 1: shouting/emphasis

    # --- Derived Signals ---
    momentum: float = 0.0                    # -1 to 1: overall direction
    volatility: float = 0.0                  # 0 to 1: how erratic the signals are

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


# Words that indicate personal disclosure
PERSONAL_MARKERS = frozenset({
    "i", "my", "me", "mine", "myself", "we", "our",
    "i'm", "im", "i've", "ive", "i'll", "ill",
    "personally", "honestly", "truthfully", "between us",
})

# Words indicating action/doing orientation
ACTION_WORDS = frozenset({
    "do", "make", "start", "begin", "create", "build", "launch",
    "run", "execute", "implement", "deploy", "try", "test",
    "send", "submit", "order", "book", "schedule", "set up",
})


class SignalExtractor:
    """Extracts behavioral micro-signals from conversation history."""

    def __init__(self):
        self._analyzer = TextAnalyzer()

    def extract(self, conversation: Conversation) -> ConversationSignals:
        """Extract all signals from the current conversation state."""
        signals = ConversationSignals()
        user_msgs = conversation.user_messages
        bot_msgs = conversation.bot_messages

        if not user_msgs:
            return signals

        # --- Engagement Signals ---
        signals.message_length_trajectory = self._message_length_trajectory(user_msgs)
        signals.question_density = self._question_density(user_msgs)
        signals.response_elaboration = self._response_elaboration(user_msgs)
        signals.topic_persistence = self._topic_persistence(user_msgs)
        signals.exclamation_energy = self._exclamation_energy(user_msgs)

        # --- Trust Signals ---
        signals.hedge_ratio = self._hedge_ratio(user_msgs)
        signals.personal_disclosure = self._personal_disclosure(user_msgs)
        signals.formality_drift = self._formality_drift(user_msgs)
        signals.mirror_behavior = self._mirror_behavior(user_msgs, bot_msgs)
        signals.positive_sentiment_trend = self._sentiment_trend(user_msgs)

        # --- Decision Signals ---
        signals.commitment_language = self._commitment_language(user_msgs)
        signals.objection_frequency = self._objection_frequency(user_msgs)
        signals.specificity_increase = self._specificity_increase(user_msgs)
        signals.urgency_markers = self._urgency_markers(user_msgs)
        signals.action_language = self._action_language(user_msgs)

        # --- Style Signals ---
        latest = user_msgs[-1]
        signals.avg_sentence_length = latest.word_count / max(latest.sentence_count, 1)
        signals.vocabulary_complexity = self._analyzer.lexical_diversity(latest.text)
        signals.formality_level = self._analyzer.formality_score(latest.text)
        signals.caps_usage = self._analyzer.caps_ratio(latest.text)

        # --- Derived Signals ---
        signals.momentum = self._compute_momentum(signals)
        signals.volatility = self._compute_volatility(user_msgs)

        return signals

    # ---- Engagement Signal Methods ----

    def _message_length_trajectory(self, msgs: list[Message]) -> float:
        if len(msgs) < 2:
            return 0.0
        lengths = [m.word_count for m in msgs[-6:]]  # Last 6 messages
        return self._analyzer.compute_trajectory(lengths)

    def _question_density(self, msgs: list[Message]) -> float:
        recent = msgs[-3:]
        total_sentences = sum(m.sentence_count for m in recent)
        total_questions = sum(m.question_count for m in recent)
        if total_sentences == 0:
            return 0.0
        return min(total_questions / total_sentences, 1.0)

    def _response_elaboration(self, msgs: list[Message]) -> float:
        recent = msgs[-3:]
        avg_words = sum(m.word_count for m in recent) / len(recent)
        # Normalize: 1-5 words = low, 5-20 = medium, 20+ = high
        return min(avg_words / 30.0, 1.0)

    def _topic_persistence(self, msgs: list[Message]) -> float:
        if len(msgs) < 2:
            return 1.0
        # Measure word overlap between consecutive messages
        overlaps = []
        for i in range(max(0, len(msgs) - 4), len(msgs) - 1):
            words_a = set(msgs[i].text.lower().split())
            words_b = set(msgs[i + 1].text.lower().split())
            if words_a and words_b:
                overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)
                overlaps.append(overlap)
        return sum(overlaps) / max(len(overlaps), 1)

    def _exclamation_energy(self, msgs: list[Message]) -> float:
        recent = msgs[-3:]
        total = sum(self._analyzer.exclamation_count(m.text) for m in recent)
        return min(total / 5.0, 1.0)

    # ---- Trust Signal Methods ----

    def _hedge_ratio(self, msgs: list[Message]) -> float:
        recent = msgs[-3:]
        total = sum(self._analyzer.hedge_density(m.text) for m in recent)
        return min(total / len(recent), 1.0)

    def _personal_disclosure(self, msgs: list[Message]) -> float:
        recent = msgs[-3:]
        total_words = sum(m.word_count for m in recent)
        if total_words == 0:
            return 0.0
        personal_count = 0
        for msg in recent:
            words = msg.text.lower().split()
            personal_count += sum(1 for w in words if w in PERSONAL_MARKERS)
        return min(personal_count / total_words, 1.0)

    def _formality_drift(self, msgs: list[Message]) -> float:
        if len(msgs) < 2:
            return 0.0
        scores = [self._analyzer.formality_score(m.text) for m in msgs[-5:]]
        return self._analyzer.compute_trajectory(scores)

    def _mirror_behavior(
        self, user_msgs: list[Message], bot_msgs: list[Message]
    ) -> float:
        if not user_msgs or not bot_msgs:
            return 0.0
        # Check if user mirrors bot's most recent style
        latest_user = user_msgs[-1]
        latest_bot = bot_msgs[-1]
        return self._analyzer.mirror_score(latest_bot.text, latest_user.text)

    def _sentiment_trend(self, msgs: list[Message]) -> float:
        if len(msgs) < 2:
            return 0.0
        sentiments = [self._analyzer.sentiment_score(m.text) for m in msgs[-5:]]
        return self._analyzer.compute_trajectory(sentiments)

    # ---- Decision Signal Methods ----

    def _commitment_language(self, msgs: list[Message]) -> float:
        recent = msgs[-3:]
        total = sum(self._analyzer.commit_density(m.text) for m in recent)
        return min(total / len(recent) * 3, 1.0)  # Amplify — commitment is rare

    def _objection_frequency(self, msgs: list[Message]) -> float:
        recent = msgs[-3:]
        total = sum(self._analyzer.objection_density(m.text) for m in recent)
        return min(total / len(recent), 1.0)

    def _specificity_increase(self, msgs: list[Message]) -> float:
        if len(msgs) < 2:
            return 0.0
        # Longer avg word length = more specific/technical
        avg_lengths = [self._analyzer.avg_word_length(m.text) for m in msgs[-5:]]
        return self._analyzer.compute_trajectory(avg_lengths)

    def _urgency_markers(self, msgs: list[Message]) -> float:
        recent = msgs[-3:]
        total = sum(self._analyzer.urgency_density(m.text) for m in recent)
        return min(total / len(recent) * 3, 1.0)

    def _action_language(self, msgs: list[Message]) -> float:
        recent = msgs[-3:]
        total_words = sum(m.word_count for m in recent)
        if total_words == 0:
            return 0.0
        action_count = 0
        for msg in recent:
            words = msg.text.lower().split()
            action_count += sum(1 for w in words if w in ACTION_WORDS)
        return min(action_count / total_words * 5, 1.0)

    # ---- Derived Signal Methods ----

    def _compute_momentum(self, signals: ConversationSignals) -> float:
        """Overall conversation momentum from -1 (dying) to +1 (accelerating)."""
        positive = (
            signals.message_length_trajectory * 0.15
            + signals.response_elaboration * 0.10
            + signals.commitment_language * 0.25
            + signals.positive_sentiment_trend * 0.15
            + signals.action_language * 0.10
            + signals.personal_disclosure * 0.10
        )
        negative = (
            signals.hedge_ratio * 0.15
            + signals.objection_frequency * 0.25
        )
        return max(-1.0, min(1.0, (positive - negative) * 2))

    def _compute_volatility(self, msgs: list[Message]) -> float:
        """How erratic the conversation is. 0 = stable, 1 = highly volatile."""
        if len(msgs) < 3:
            return 0.0
        sentiments = [self._analyzer.sentiment_score(m.text) for m in msgs[-6:]]
        if len(sentiments) < 2:
            return 0.0
        diffs = [abs(sentiments[i] - sentiments[i - 1]) for i in range(1, len(sentiments))]
        avg_diff = sum(diffs) / len(diffs)
        return min(avg_diff * 2, 1.0)
