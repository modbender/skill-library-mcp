"""Pydantic models for the AI PersonaNexus Framework v1.0 — with religion extension."""

from __future__ import annotations

import enum
import warnings
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from religion_skill.religion import ReligionConfig

# Suppress pydantic warning about 'register' field name shadowing BaseModel attribute
warnings.filterwarnings("ignore", message=".*Field name.*register.*shadows.*")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Status(enum.StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ExpertiseCategory(enum.StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class OutOfExpertiseStrategy(enum.StrEnum):
    ATTEMPT_ANYWAY = "attempt_anyway"
    ACKNOWLEDGE_AND_REDIRECT = "acknowledge_and_redirect"
    HARD_DECLINE = "hard_decline"


class Register(enum.StrEnum):
    INTIMATE = "intimate"
    CASUAL = "casual"
    CONSULTATIVE = "consultative"
    FORMAL = "formal"
    FROZEN = "frozen"


class SentenceLength(enum.StrEnum):
    SHORT = "short"
    MIXED = "mixed"
    LONG = "long"


class ParagraphLength(enum.StrEnum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class EmojiUsage(enum.StrEnum):
    NEVER = "never"
    SPARINGLY = "sparingly"
    FREQUENTLY = "frequently"


class ReadingLevel(enum.StrEnum):
    SIMPLE = "simple"
    INTERMEDIATE = "intermediate"
    PROFESSIONAL = "professional"
    ACADEMIC = "academic"


class JargonPolicy(enum.StrEnum):
    AVOID = "avoid"
    DEFINE_ON_FIRST_USE = "define_on_first_use"
    ASSUME_KNOWN = "assume_known"


class AssumedKnowledge(enum.StrEnum):
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class Enforcement(enum.StrEnum):
    OUTPUT_FILTER = "output_filter"
    RUNTIME_SANDBOX = "runtime_sandbox"
    PROMPT_INSTRUCTION = "prompt_instruction"
    LANGUAGE_DETECTION = "language_detection"
    OUTPUT_TRUNCATION = "output_truncation"


class Severity(enum.StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OverrideLevel(enum.StrEnum):
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    NONE = "none"


class Strictness(enum.StrEnum):
    STRICT = "strict"
    MODERATE = "moderate"
    LOOSE = "loose"


class MemoryBackend(enum.StrEnum):
    VECTOR_STORE = "vector_store"
    KEY_VALUE = "key_value"
    GRAPH = "graph"
    NONE = "none"


class NumericConflictStrategy(enum.StrEnum):
    LAST_WINS = "last_wins"
    HIGHEST = "highest"
    LOWEST = "lowest"
    AVERAGE = "average"


class ListConflictStrategy(enum.StrEnum):
    APPEND = "append"
    REPLACE = "replace"
    UNIQUE_APPEND = "unique_append"


class ObjectConflictStrategy(enum.StrEnum):
    DEEP_MERGE = "deep_merge"
    REPLACE = "replace"


class MergeStrategy(enum.StrEnum):
    APPEND = "append"
    REPLACE = "replace"
    PREPEND = "prepend"


class PersonalityMode(enum.StrEnum):
    CUSTOM = "custom"
    OCEAN = "ocean"
    DISC = "disc"
    JUNGIAN = "jungian"
    HYBRID = "hybrid"


class OverridePriority(enum.StrEnum):
    EXPLICIT_WINS = "explicit_wins"
    FRAMEWORK_WINS = "framework_wins"


class AvatarType(enum.StrEnum):
    PHOTO = "photo"
    ILLUSTRATED = "illustrated"
    THREE_D = "3d"
    ICON = "icon"
    NONE = "none"


# ---------------------------------------------------------------------------
# Interaction Protocols
# ---------------------------------------------------------------------------


class InteractionEscalationTrigger(enum.StrEnum):
    UNABLE_TO_HELP = "unable_to_help"
    USER_REQUESTS_HUMAN = "user_requests_human"
    SAFETY_CONCERN = "safety_concern"
    CONFIDENCE_LOW = "confidence_low"
    OUT_OF_SCOPE = "out_of_scope"


class HumanInteraction(BaseModel):
    """How this agent interacts with human users."""

    greeting_style: str | None = None
    farewell_style: str | None = None
    tone_matching: bool = False
    escalation_triggers: list[InteractionEscalationTrigger] = Field(default_factory=list)
    escalation_message: str | None = None


class AgentInteraction(BaseModel):
    """How this agent interacts with other agents."""

    handoff_style: str = "structured"
    status_reporting: str = "on_request"
    conflict_resolution: str = "defer_to_hierarchy"


class InteractionConfig(BaseModel):
    """Configuration for interaction protocols."""

    human: HumanInteraction = Field(default_factory=HumanInteraction)
    agent: AgentInteraction = Field(default_factory=AgentInteraction)


class VoiceProvider(enum.StrEnum):
    ELEVENLABS = "elevenlabs"
    AZURE = "azure"
    GOOGLE = "google"
    OPENAI = "openai"


class Pacing(enum.StrEnum):
    RAPID = "rapid"
    MEASURED = "measured"
    DELIBERATE = "deliberate"


class Emphasis(enum.StrEnum):
    NONE = "none"
    KEY_TERMS = "key_terms"
    EMOTIONAL = "emotional"


class LengthCalibration(enum.StrEnum):
    BRIEF = "brief"
    MODERATE = "moderate"
    THOROUGH = "thorough"
    ADAPTIVE = "adaptive"


class ClarificationBias(enum.StrEnum):
    TOWARD_ACTION = "toward_action"
    TOWARD_PRECISION = "toward_precision"


class TestSuite(enum.StrEnum):
    FULL = "full"
    SMOKE = "smoke"
    AFFECTED_ONLY = "affected_only"


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


class Metadata(BaseModel):
    id: str = Field(..., pattern=r"^agt_[a-zA-Z0-9_]+$")
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: str = Field(..., min_length=1, max_length=500)
    created_at: datetime
    updated_at: datetime
    author: str | None = None
    tags: list[str] = Field(default_factory=list, max_length=50)
    status: Status = Status.DRAFT


# ---------------------------------------------------------------------------
# Role & Purpose
# ---------------------------------------------------------------------------


class Scope(BaseModel):
    primary: list[str] = Field(..., min_length=1, max_length=50)
    secondary: list[str] = Field(default_factory=list, max_length=50)
    out_of_scope: list[str] = Field(default_factory=list, max_length=50)


class Audience(BaseModel):
    primary: str
    secondary: str | None = None
    assumed_knowledge: AssumedKnowledge = AssumedKnowledge.INTERMEDIATE


class Role(BaseModel):
    title: str
    purpose: str = Field(..., min_length=1, max_length=1000)
    scope: Scope
    audience: Audience | None = None


# ---------------------------------------------------------------------------
# Personality
# ---------------------------------------------------------------------------


class OceanProfile(BaseModel):
    """Big Five (OCEAN) personality profile with five dimensions scaled 0-1."""

    openness: float = Field(..., ge=0.0, le=1.0)
    conscientiousness: float = Field(..., ge=0.0, le=1.0)
    extraversion: float = Field(..., ge=0.0, le=1.0)
    agreeableness: float = Field(..., ge=0.0, le=1.0)
    neuroticism: float = Field(..., ge=0.0, le=1.0)


class DiscProfile(BaseModel):
    """DISC personality profile with four dimensions scaled 0-1."""

    dominance: float = Field(..., ge=0.0, le=1.0)
    influence: float = Field(..., ge=0.0, le=1.0)
    steadiness: float = Field(..., ge=0.0, le=1.0)
    conscientiousness: float = Field(..., ge=0.0, le=1.0)


class JungianProfile(BaseModel):
    """Jungian 16-type personality profile with four preference dimensions scaled 0-1.

    Based on Carl Jung's typological theory (1921, public domain).
    Each dimension represents a preference spectrum:
      ei: 0=Extraversion, 1=Introversion
      sn: 0=Sensing, 1=iNtuition
      tf: 0=Thinking, 1=Feeling
      jp: 0=Judging, 1=Perceiving
    """

    ei: float = Field(..., ge=0.0, le=1.0, description="Extraversion (0) vs Introversion (1)")
    sn: float = Field(..., ge=0.0, le=1.0, description="Sensing (0) vs iNtuition (1)")
    tf: float = Field(..., ge=0.0, le=1.0, description="Thinking (0) vs Feeling (1)")
    jp: float = Field(..., ge=0.0, le=1.0, description="Judging (0) vs Perceiving (1)")


class PersonalityProfile(BaseModel):
    """Personality framework configuration for OCEAN/DISC/Jungian/hybrid modes."""

    mode: PersonalityMode = PersonalityMode.CUSTOM
    ocean: OceanProfile | None = None
    disc: DiscProfile | None = None
    disc_preset: str | None = Field(
        None,
        description="Named DISC preset (e.g. 'the_commander', 'the_analyst')",
    )
    jungian: JungianProfile | None = None
    jungian_preset: str | None = Field(
        None,
        description="Jungian type preset (e.g. 'intj', 'enfp')",
    )
    override_priority: OverridePriority = OverridePriority.EXPLICIT_WINS


class PersonalityTraits(BaseModel):
    warmth: float | None = Field(None, ge=0.0, le=1.0)
    verbosity: float | None = Field(None, ge=0.0, le=1.0)
    assertiveness: float | None = Field(None, ge=0.0, le=1.0)
    humor: float | None = Field(None, ge=0.0, le=1.0)
    empathy: float | None = Field(None, ge=0.0, le=1.0)
    directness: float | None = Field(None, ge=0.0, le=1.0)
    rigor: float | None = Field(None, ge=0.0, le=1.0)
    creativity: float | None = Field(None, ge=0.0, le=1.0)
    epistemic_humility: float | None = Field(None, ge=0.0, le=1.0)
    patience: float | None = Field(None, ge=0.0, le=1.0)

    model_config = {"extra": "allow"}

    def defined_traits(self) -> dict[str, float]:
        """Return only the traits that have been explicitly set."""
        return {
            k: v
            for k, v in self.model_dump(exclude_none=True).items()
            if isinstance(v, (int, float))
        }


# Canonical ordering of the 10 standard personality traits.
# Import this instead of hardcoding the list.
TRAIT_ORDER: list[str] = [
    "warmth",
    "verbosity",
    "assertiveness",
    "humor",
    "empathy",
    "directness",
    "rigor",
    "creativity",
    "epistemic_humility",
    "patience",
]


class TraitModifier(BaseModel):
    """Modifier to apply to a personality trait in a given mood state."""

    trait: str
    delta: float = Field(ge=-1.0, le=1.0)


class MoodState(BaseModel):
    """A named emotional/mood state that modifies personality expression."""

    name: str
    description: str | None = None
    trait_modifiers: list[TraitModifier] = Field(default_factory=list)
    tone_override: str | None = None


class MoodTransition(BaseModel):
    """Rule for transitioning between mood states."""

    from_state: str = "*"  # "*" means any state
    to_state: str
    trigger: str  # e.g. "user_frustration_detected", "complex_technical_query"


class MoodConfig(BaseModel):
    """Configuration for dynamic mood/emotional states."""

    default: str = "neutral"
    states: list[MoodState] = Field(default_factory=list, max_length=50)
    transitions: list[MoodTransition] = Field(default_factory=list, max_length=50)


# ============================================================================
# Behavioral Modes (state machine for operating modes)
# ============================================================================


class BehavioralModeOverrides(BaseModel):
    """Overrides to apply when a behavioral mode is active."""

    tone_register: Register | None = None
    tone_default: str | None = None
    emoji_usage: EmojiUsage | None = None
    sentence_length: SentenceLength | None = None
    trait_modifiers: list[TraitModifier] = Field(default_factory=list, max_length=20)


class BehavioralMode(BaseModel):
    """A named operating mode with personality/communication overrides."""

    name: str
    description: str | None = None
    overrides: BehavioralModeOverrides = Field(default_factory=BehavioralModeOverrides)
    additional_guardrails: list[str] = Field(default_factory=list)


class BehavioralModeConfig(BaseModel):
    """Configuration for behavioral mode state machine."""

    default: str = "standard"
    modes: list[BehavioralMode] = Field(default_factory=list)


class Personality(BaseModel):
    traits: PersonalityTraits = Field(default_factory=PersonalityTraits)
    profile: PersonalityProfile = Field(default_factory=PersonalityProfile)
    mood: MoodConfig | None = None  # NEW
    notes: str | None = None

    @model_validator(mode="after")
    def validate_personality_mode(self) -> Personality:
        """Validate trait requirements based on personality mode."""
        mode = self.profile.mode

        if mode == PersonalityMode.CUSTOM:
            # Custom mode: require at least 2 traits set directly
            set_traits = self.traits.defined_traits()
            if len(set_traits) < 2:
                raise ValueError("At least 2 personality traits must be defined in custom mode")

        elif mode == PersonalityMode.OCEAN:
            if self.profile.ocean is None:
                raise ValueError("OCEAN profile is required when mode is 'ocean'")

        elif mode == PersonalityMode.DISC:
            if self.profile.disc is None and self.profile.disc_preset is None:
                raise ValueError("DISC profile or disc_preset is required when mode is 'disc'")

        elif mode == PersonalityMode.JUNGIAN:
            if self.profile.jungian is None and self.profile.jungian_preset is None:
                raise ValueError(
                    "Jungian profile or jungian_preset is required when mode is 'jungian'"
                )

        elif mode == PersonalityMode.HYBRID:
            has_framework = (
                self.profile.ocean is not None
                or self.profile.disc is not None
                or self.profile.disc_preset is not None
                or self.profile.jungian is not None
                or self.profile.jungian_preset is not None
            )
            if not has_framework:
                raise ValueError(
                    "At least one framework profile (ocean/disc/jungian) is required in hybrid mode"
                )
            has_overrides = len(self.traits.defined_traits()) > 0
            if not has_overrides:
                raise ValueError("At least one explicit trait override is required in hybrid mode")

        return self


# ---------------------------------------------------------------------------
# Communication
# ---------------------------------------------------------------------------


class ToneOverride(BaseModel):
    context: str = Field(..., max_length=500)
    tone: str = Field(..., max_length=500)
    note: str | None = Field(None, max_length=500)


class ToneConfig(BaseModel):
    model_config = {"populate_by_name": True}

    default: str = Field(..., max_length=500)
    register: Register | None = None  # shadows BaseModel attribute — intentional
    overrides: list[ToneOverride] = Field(default_factory=list, max_length=20)


class StyleConfig(BaseModel):
    sentence_length: SentenceLength | None = None
    paragraph_length: ParagraphLength | None = None
    use_headers: bool | None = None
    use_lists: bool | None = None
    use_code_blocks: bool | None = None
    use_emoji: EmojiUsage | None = None
    preferred_formats: list[str] = Field(default_factory=list, max_length=20)


class LanguageConfig(BaseModel):
    primary: str = Field("en", max_length=10)
    supported: list[str] = Field(default_factory=list, max_length=20)
    reading_level: ReadingLevel | None = None
    jargon_policy: JargonPolicy | None = None


class VocabularyConfig(BaseModel):
    preferred: list[str] = Field(default_factory=list, max_length=100)
    avoided: list[str] = Field(default_factory=list, max_length=100)
    signature_phrases: list[str] = Field(default_factory=list, max_length=50)


class VoiceExample(BaseModel):
    """An example of right or wrong voice for calibration."""

    text: str = Field(..., max_length=5000)
    context: str | None = Field(None, max_length=500)


class VoiceExamples(BaseModel):
    """Good and bad output samples for voice calibration."""

    good: list[VoiceExample] = Field(default_factory=list, max_length=50)
    bad: list[VoiceExample] = Field(default_factory=list, max_length=50)


class Communication(BaseModel):
    tone: ToneConfig
    style: StyleConfig | None = None
    language: LanguageConfig = Field(default_factory=LanguageConfig)
    vocabulary: VocabularyConfig | None = None
    voice_examples: VoiceExamples | None = None


# ---------------------------------------------------------------------------
# Expertise
# ---------------------------------------------------------------------------


class ExpertiseDomain(BaseModel):
    name: str = Field(..., max_length=200)
    level: float = Field(..., ge=0.0, le=1.0)
    category: ExpertiseCategory
    description: str | None = Field(None, max_length=1000)
    can_teach: bool = False


class Expertise(BaseModel):
    domains: list[ExpertiseDomain] = Field(default_factory=list, max_length=100)
    out_of_expertise_strategy: OutOfExpertiseStrategy = (
        OutOfExpertiseStrategy.ACKNOWLEDGE_AND_REDIRECT
    )


# ---------------------------------------------------------------------------
# Principles
# ---------------------------------------------------------------------------


class Principle(BaseModel):
    id: str
    priority: int = Field(..., ge=1)
    statement: str = Field(..., max_length=2000)
    implications: list[str] = Field(default_factory=list, max_length=20)


# ---------------------------------------------------------------------------
# Behavioral Framework
# ---------------------------------------------------------------------------


class BehaviorRule(BaseModel):
    condition: str | None = Field(None, max_length=1000)
    action: str = Field(..., max_length=1000)
    template: str | None = Field(None, max_length=5000)
    adjustments: dict[str, float] = Field(default_factory=dict)
    note: str | None = None


class BehaviorStrategy(BaseModel):
    approach: str = Field(..., max_length=1000)
    rules: list[BehaviorRule] = Field(default_factory=list, max_length=50)
    max_pushback_rounds: int | None = None
    final_fallback: str | None = Field(None, max_length=1000)
    near_scope_threshold: float | None = None
    near_scope_action: str | None = Field(None, max_length=1000)
    bias: ClarificationBias | None = None


class ProactiveTrigger(BaseModel):
    id: str
    condition: str
    action: str
    announce: bool = True
    priority: str | None = None


class ProactiveConfig(BaseModel):
    enabled: bool = False
    triggers: list[ProactiveTrigger] = Field(default_factory=list, max_length=50)
    limits: dict[str, Any] = Field(default_factory=dict)


class LengthRule(BaseModel):
    condition: str
    length: LengthCalibration
    note: str | None = None


class LengthCalibrationConfig(BaseModel):
    default: LengthCalibration = LengthCalibration.ADAPTIVE
    rules: list[LengthRule] = Field(default_factory=list, max_length=50)


class ClarificationPolicy(BaseModel):
    default: str = "ask_when_ambiguous"
    bias: ClarificationBias = ClarificationBias.TOWARD_ACTION


class ConversationConfig(BaseModel):
    length_calibration: LengthCalibrationConfig = Field(default_factory=LengthCalibrationConfig)
    clarification_policy: ClarificationPolicy = Field(default_factory=ClarificationPolicy)
    reference_prior_context: bool = True
    summarize_long_threads: bool = True
    thread_summary_threshold: int = 15


class DecisionHeuristic(BaseModel):
    name: str
    description: str | None = None
    weight: float = Field(0.5, ge=0.0, le=1.0)


class DecisionMaking(BaseModel):
    heuristics: list[DecisionHeuristic] = Field(default_factory=list, max_length=50)
    autonomy_threshold: dict[str, str] = Field(default_factory=dict)


class Behavior(BaseModel):
    strategies: dict[str, BehaviorStrategy] = Field(default_factory=dict)
    proactive: ProactiveConfig = Field(default_factory=ProactiveConfig)
    conversation: ConversationConfig = Field(default_factory=ConversationConfig)
    decision_making: DecisionMaking = Field(default_factory=DecisionMaking)


# ---------------------------------------------------------------------------
# Guardrails & Boundaries
# ---------------------------------------------------------------------------


class HardGuardrail(BaseModel):
    id: str
    rule: str
    enforcement: Enforcement
    severity: Severity


class SoftGuardrailConfig(BaseModel):
    model_config = {"extra": "allow"}


class SoftGuardrail(BaseModel):
    id: str
    rule: str
    enforcement: Enforcement | None = None
    override_level: OverrideLevel = OverrideLevel.ADMIN
    current_config: SoftGuardrailConfig | None = None


class TopicEntry(BaseModel):
    category: str
    subtopics: list[str] = Field(default_factory=list, max_length=50)
    reason: str | None = None
    redirect_to: str | None = None
    response: str | None = None


class Topics(BaseModel):
    allowed: list[TopicEntry] = Field(default_factory=list, max_length=100)
    restricted: list[TopicEntry] = Field(default_factory=list, max_length=100)
    forbidden: list[TopicEntry] = Field(default_factory=list, max_length=100)


class ConfirmableAction(BaseModel):
    action: str
    confirmation_prompt: str | None = None


class Permissions(BaseModel):
    autonomous: list[str] = Field(default_factory=list)
    requires_confirmation: list[ConfirmableAction] = Field(default_factory=list)
    forbidden: list[str] = Field(default_factory=list)


class EscalationTrigger(BaseModel):
    condition: str
    action: str
    notify: str | None = None
    priority: str | None = None
    message: str | None = None
    threshold: int | str | None = None
    window: str | None = None
    resources: list[str] = Field(default_factory=list)


class EscalationChannel(BaseModel):
    method: str
    url: str | None = None
    service_id: str | None = None
    channel: str | None = None


class Escalation(BaseModel):
    triggers: list[EscalationTrigger] = Field(default_factory=list)
    channels: dict[str, EscalationChannel] = Field(default_factory=dict)


class Guardrails(BaseModel):
    hard: list[HardGuardrail] = Field(..., min_length=1)
    soft: list[SoftGuardrail] = Field(default_factory=list)
    topics: Topics = Field(default_factory=Topics)
    permissions: Permissions = Field(default_factory=Permissions)
    escalation: Escalation = Field(default_factory=Escalation)


# ---------------------------------------------------------------------------
# Memory & Context
# ---------------------------------------------------------------------------


class IdentityContext(BaseModel):
    always_loaded: list[str] = Field(default_factory=list)
    conditional: list[dict[str, str]] = Field(default_factory=list)
    token_budget: int = 3000
    compression_strategy: str | None = None


class SlidingWindow(BaseModel):
    max_turns: int = 50
    max_tokens: int = 8000


class SummarizationConfig(BaseModel):
    enabled: bool = True
    trigger: str | None = None
    method: str | None = None
    preserve: list[str] = Field(default_factory=list)


class SessionConfig(BaseModel):
    strategy: str = "sliding_window_with_summary"
    sliding_window: SlidingWindow = Field(default_factory=SlidingWindow)
    summarization: SummarizationConfig = Field(default_factory=SummarizationConfig)
    session_state: dict[str, bool] = Field(default_factory=dict)


class MemoryCategory(BaseModel):
    category: str
    examples: list[str] = Field(default_factory=list)
    retention: str | None = None
    privacy_level: str | None = None


class MemoryLifecycle(BaseModel):
    review_interval: str | None = None
    decay_strategy: str | None = None
    max_memories_per_user: int = 500
    user_can_view: bool = True
    user_can_delete: bool = True
    user_can_export: bool = True


class LongTermMemory(BaseModel):
    enabled: bool = False
    backend: MemoryBackend = MemoryBackend.NONE
    remember: list[MemoryCategory] = Field(default_factory=list)
    forget: list[str] = Field(default_factory=list)
    lifecycle: MemoryLifecycle = Field(default_factory=MemoryLifecycle)


class UserModelField(BaseModel):
    name: str
    type: str
    source: str | None = None
    mutable: bool = True
    values: list[str] = Field(default_factory=list)
    affects: list[str] = Field(default_factory=list)


class RelationshipDynamic(enum.StrEnum):
    DEFERS_TO = "defers_to"
    COLLABORATES_WITH = "collaborates_with"
    MENTORS = "mentors"
    DELEGATES_TO = "delegates_to"
    ESCALATES_TO = "escalates_to"
    PEER = "peer"


class AgentRelationship(BaseModel):
    agent_id: str
    name: str | None = None
    relationship: str  # kept for backward compat
    dynamic: RelationshipDynamic | None = None
    context: str | None = None  # when this relationship applies
    interaction_style: str | None = None  # e.g. "formal-respectful", "casual-energetic"
    handoff_protocol: str | None = None
    shared_context: list[str] = Field(default_factory=list)


class Relationships(BaseModel):
    enabled: bool = False
    user_model: dict[str, Any] = Field(default_factory=dict)
    agent_relationships: list[AgentRelationship] = Field(default_factory=list)
    unknown_agent_default: str = "professional-cautious"
    escalation_path: list[str] = Field(default_factory=list)  # ordered list of agent_ids


class Memory(BaseModel):
    identity_context: IdentityContext = Field(default_factory=IdentityContext)
    session: SessionConfig = Field(default_factory=SessionConfig)
    long_term: LongTermMemory = Field(default_factory=LongTermMemory)
    relationships: Relationships = Field(default_factory=Relationships)


# ---------------------------------------------------------------------------
# Multi-Modal Presentation
# ---------------------------------------------------------------------------


class VoiceSettings(BaseModel):
    speed: float = Field(1.0, ge=0.5, le=2.0)
    pitch: float = Field(0.0, ge=-1.0, le=1.0)
    stability: float = Field(0.7, ge=0.0, le=1.0)
    similarity_boost: float = Field(0.8, ge=0.0, le=1.0)


class VoiceStyle(BaseModel):
    pacing: Pacing = Pacing.MEASURED
    emphasis: Emphasis = Emphasis.KEY_TERMS
    pause_at_transitions: bool = True


class Pronunciation(BaseModel):
    word: str
    say: str


class VoiceConfig(BaseModel):
    enabled: bool = False
    provider: VoiceProvider | None = None
    voice_id: str | None = None
    settings: VoiceSettings = Field(default_factory=VoiceSettings)
    style: VoiceStyle = Field(default_factory=VoiceStyle)
    pronunciation: list[Pronunciation] = Field(default_factory=list)


class Avatar(BaseModel):
    type: AvatarType = AvatarType.NONE
    url: str | None = None
    fallback_emoji: str | None = None
    theme_color: str | None = None


class StatusIndicators(BaseModel):
    thinking: str | None = None
    responding: str | None = None
    error: str | None = None


class VisualConfig(BaseModel):
    avatar: Avatar = Field(default_factory=Avatar)
    status_indicators: StatusIndicators = Field(default_factory=StatusIndicators)


class PlatformOverride(BaseModel):
    platform: str
    format: str | None = None
    max_response_length: int | None = None
    tone_adjustment: dict[str, float] = Field(default_factory=dict)
    use_emoji: EmojiUsage | None = None
    use_threads: bool | None = None
    include_signature: bool | None = None
    signature: str | None = None
    include_metadata: bool | None = None
    avoid_formatting: bool | None = None
    spell_out_abbreviations: bool | None = None


class PlatformDefaults(BaseModel):
    max_response_length: int = 2000
    format: str = "markdown"


class PlatformConfig(BaseModel):
    defaults: PlatformDefaults = Field(default_factory=PlatformDefaults)
    overrides: list[PlatformOverride] = Field(default_factory=list)


class Presentation(BaseModel):
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    visual: VisualConfig = Field(default_factory=VisualConfig)
    platforms: PlatformConfig = Field(default_factory=PlatformConfig)


# ---------------------------------------------------------------------------
# Dynamic Identity & Evolution
# ---------------------------------------------------------------------------


class RuntimeMutableField(BaseModel):
    field: str
    bounds: list[float] | None = None
    drift_rate: float | None = None
    trigger: str | None = None


class DriftMetric(BaseModel):
    trait: str
    method: str
    alert_threshold: float | str | None = None
    correct_threshold: float | str | None = None


class DriftDetection(BaseModel):
    enabled: bool = False
    check_interval: str | None = None
    metrics: list[DriftMetric] = Field(default_factory=list)
    correction: dict[str, Any] = Field(default_factory=dict)


class RollbackConfig(BaseModel):
    enabled: bool = True
    max_versions: int = 20
    method: str = "full_snapshot"


class Versioning(BaseModel):
    auto_increment: str = "patch"
    changelog: dict[str, Any] = Field(default_factory=dict)
    rollback: RollbackConfig = Field(default_factory=RollbackConfig)


class Evolution(BaseModel):
    immutable_fields: list[str] = Field(default_factory=list)
    admin_mutable_fields: list[str] = Field(default_factory=list)
    runtime_mutable_fields: list[RuntimeMutableField] = Field(default_factory=list)
    drift_detection: DriftDetection = Field(default_factory=DriftDetection)
    versioning: Versioning = Field(default_factory=Versioning)


# ---------------------------------------------------------------------------
# Evaluation & Testing
# ---------------------------------------------------------------------------


class TestGenerator(BaseModel):
    source: str
    method: str
    description: str | None = None
    prompts_per_trait: int | None = None
    prompts_per_guardrail: int | None = None
    scenarios_per_strategy: int | None = None
    prompts_per_domain: int | None = None


class TestGenerationConfig(BaseModel):
    enabled: bool = False
    generators: list[TestGenerator] = Field(default_factory=list)


class ScoringConfig(BaseModel):
    method: str | None = None
    model: str | None = None
    prompt_template: str | None = None
    criteria: list[str] = Field(default_factory=list)


class Rubric(BaseModel):
    description: str | None = None
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    passing_score: float = 3.5
    weight: float = 0.25


class GoldenTestConfig(BaseModel):
    path: str | None = None
    format: str = "conversation_yaml"


class RegressionConfig(BaseModel):
    trigger: str = "pre_deploy"
    test_suite: TestSuite = TestSuite.FULL
    golden_tests: GoldenTestConfig = Field(default_factory=GoldenTestConfig)
    diff_report: dict[str, Any] = Field(default_factory=dict)


class Evaluation(BaseModel):
    test_generation: TestGenerationConfig = Field(default_factory=TestGenerationConfig)
    rubrics: dict[str, Rubric] = Field(default_factory=dict)
    regression: RegressionConfig = Field(default_factory=RegressionConfig)


# ---------------------------------------------------------------------------
# Composition & Conflict Resolution
# ---------------------------------------------------------------------------


class ExplicitResolution(BaseModel):
    field: str
    strategy: str


class ContradictionDetection(BaseModel):
    enabled: bool = True
    threshold: float = 0.7
    related_trait_pairs: list[list[str]] = Field(default_factory=list)


class ConflictResolution(BaseModel):
    numeric_traits: NumericConflictStrategy = NumericConflictStrategy.LAST_WINS
    string_fields: NumericConflictStrategy = NumericConflictStrategy.LAST_WINS
    list_fields: ListConflictStrategy = ListConflictStrategy.APPEND
    object_fields: ObjectConflictStrategy = ObjectConflictStrategy.DEEP_MERGE
    explicit_resolutions: list[ExplicitResolution] = Field(default_factory=list)


class CompositionConfig(BaseModel):
    conflict_resolution: ConflictResolution = Field(default_factory=ConflictResolution)
    contradiction_detection: ContradictionDetection = Field(default_factory=ContradictionDetection)


# ---------------------------------------------------------------------------
# Narrative Identity (for SOUL.md compilation)
# ---------------------------------------------------------------------------


class Opinion(BaseModel):
    """A domain-specific take or opinion."""

    domain: str = Field(..., description="Topic area (e.g. 'Technology', 'Management')")
    takes: list[str] = Field(..., min_length=1, description="Specific opinions in this domain")


class Influence(BaseModel):
    """A person, book, or concept that shaped the agent's thinking."""

    name: str
    category: str = Field(
        "concept",
        description="Type of influence: 'person', 'book', 'concept', 'framework'",
    )
    insight: str = Field(..., description="What was learned or adopted from this influence")


class Narrative(BaseModel):
    """Narrative identity elements for rich personality rendering (SOUL.md).

    These optional fields enable richer, more authentic personality output
    beyond what numeric traits and structured schemas can express.
    """

    backstory: str | None = Field(
        None, description="Extended background beyond metadata.description"
    )
    opinions: list[Opinion] = Field(default_factory=list)
    influences: list[Influence] = Field(default_factory=list)
    tensions: list[str] = Field(
        default_factory=list,
        description="Authentic contradictions that make the personality feel human",
    )
    pet_peeves: list[str] = Field(default_factory=list)
    current_focus: list[str] = Field(
        default_factory=list,
        description="Active projects or areas of current attention",
    )


# ---------------------------------------------------------------------------
# Archetype & Mixin wrappers (used in archetype/mixin YAML files)
# ---------------------------------------------------------------------------


class ArchetypeHeader(BaseModel):
    id: str
    name: str
    description: str | None = None
    abstract: bool = True


class MixinHeader(BaseModel):
    id: str
    name: str
    description: str | None = None


# ---------------------------------------------------------------------------
# Top-Level PersonaNexus
# ---------------------------------------------------------------------------


class AgentIdentity(BaseModel):
    """Complete PersonaNexus specification."""

    schema_version: str = Field("1.0", pattern=r"^\d+\.\d+$")

    # Inheritance
    extends: str | None = None
    mixins: list[str] = Field(default_factory=list)
    overrides: dict[str, Any] | None = None

    # Archetype/Mixin markers (for template files)
    archetype: ArchetypeHeader | None = None
    mixin: MixinHeader | None = None

    # Core sections
    metadata: Metadata
    role: Role
    personality: Personality
    communication: Communication
    expertise: Expertise = Field(default_factory=Expertise)
    principles: list[Principle] = Field(..., min_length=1)
    behavior: Behavior = Field(default_factory=Behavior)
    guardrails: Guardrails

    # Optional sections
    narrative: Narrative = Field(default_factory=Narrative)
    memory: Memory = Field(default_factory=Memory)
    presentation: Presentation = Field(default_factory=Presentation)
    evolution: Evolution = Field(default_factory=Evolution)
    evaluation: Evaluation = Field(default_factory=Evaluation)
    composition: CompositionConfig = Field(default_factory=CompositionConfig)
    behavioral_modes: BehavioralModeConfig | None = None  # NEW v1.4
    interaction: InteractionConfig | None = None  # NEW v1.4
    religion: ReligionConfig = Field(default_factory=ReligionConfig)  # Religion extension

    @field_validator("principles")
    @classmethod
    def principles_unique_priorities(cls, v: list[Principle]) -> list[Principle]:
        priorities = [p.priority for p in v]
        if len(priorities) != len(set(priorities)):
            raise ValueError("Principle priorities must be unique")
        return v
