"""Identity compiler — transform resolved identities into system prompts and platform formats."""

from __future__ import annotations

import logging
import re
from typing import Any

import yaml

from religion_skill.personality import compute_personality_traits
from religion_skill.religion import InfluenceLevel, ReligionConfig
from religion_skill.types import (
    AgentIdentity,
    Behavior,
    BehavioralModeConfig,
    Communication,
    Expertise,
    ExpertiseCategory,
    Guardrails,
    InteractionConfig,
    Memory,
    Narrative,
    Personality,
    PersonalityMode,
    Principle,
    RelationshipDynamic,
    Role,
    Severity,
)

logger = logging.getLogger(__name__)


class CompilerError(Exception):
    """Raised when compilation fails."""


# ---------------------------------------------------------------------------
# Trait-to-language mapping (5 levels per trait)
# ---------------------------------------------------------------------------

TRAIT_TEMPLATES: dict[str, list[str]] = {
    "warmth": [
        "reserved and professional",
        "moderately warm",
        "warm and approachable",
        "very warm and friendly",
        "exceptionally warm and welcoming",
    ],
    "verbosity": [
        "concise and brief",
        "moderately detailed",
        "detailed in your explanations",
        "thorough and comprehensive",
        "extremely thorough and exhaustive",
    ],
    "assertiveness": [
        "deferential and reactive",
        "balanced in assertiveness",
        "assertive when appropriate",
        "confidently assertive",
        "highly directive and proactive",
    ],
    "humor": [
        "serious and professional",
        "occasionally light-hearted",
        "appropriately humorous",
        "frequently witty and playful",
        "highly playful with frequent humor",
    ],
    "empathy": [
        "task-focused and efficient",
        "considerate of feelings",
        "empathetic and supportive",
        "highly empathetic and emotionally attuned",
        "deeply empathetic with strong emotional intelligence",
    ],
    "directness": [
        "diplomatic and indirect",
        "balanced between tact and directness",
        "direct and straightforward",
        "very direct and candid",
        "bluntly direct with no sugarcoating",
    ],
    "rigor": [
        "flexible and adaptive",
        "reasonably rigorous",
        "rigorous and methodical",
        "highly rigorous and precise",
        "exceptionally rigorous with meticulous attention to detail",
    ],
    "creativity": [
        "conventional and proven in your approaches",
        "balanced between convention and creativity",
        "creative and open to new ideas",
        "highly creative and innovative",
        "exceptionally innovative with unconventional thinking",
    ],
    "epistemic_humility": [
        "confident and decisive",
        "reasonably aware of limitations",
        "appropriately humble about uncertainty",
        "very transparent about what you don't know",
        "deeply committed to acknowledging uncertainty and limitations",
    ],
    "patience": [
        "efficient and fast-paced",
        "moderately patient",
        "patient and willing to explain",
        "very patient with repeated questions",
        "exceptionally patient and never rushed",
    ],
}


def _trait_to_language(trait_name: str, value: float) -> str:
    """Convert a numeric trait (0-1) to a natural language sentence."""
    templates = TRAIT_TEMPLATES.get(trait_name)
    if not templates:
        # Generic fallback for custom traits
        if value < 0.3:
            return f"You have low {trait_name}."
        elif value < 0.7:
            return f"You have moderate {trait_name}."
        else:
            return f"You have high {trait_name}."

    if value < 0.2:
        level = 0
    elif value < 0.4:
        level = 1
    elif value < 0.6:
        level = 2
    elif value < 0.8:
        level = 3
    else:
        level = 4

    return f"You are {templates[level]}."


def _expertise_level_text(level: float) -> str:
    """Convert expertise level to a word."""
    if level >= 0.9:
        return "expert"
    elif level >= 0.7:
        return "advanced"
    elif level >= 0.5:
        return "proficient"
    elif level >= 0.3:
        return "intermediate"
    return "basic"


# ---------------------------------------------------------------------------
# Section names used for truncation priority ordering
# ---------------------------------------------------------------------------

# Sections that are always kept during truncation (never dropped).
_REQUIRED_SECTIONS = {"header", "role", "guardrails"}

# Optional sections listed from HIGHEST priority (dropped last) to LOWEST
# priority (dropped first).  When truncating, we drop in reverse order —
# i.e. "interaction" is dropped first, then "behavioral_modes", etc.
_OPTIONAL_SECTION_PRIORITY = [
    "personality",
    "religion",
    "communication",
    "principles",
    "expertise",
    "behavior",
    "relationships",
    "behavioral_modes",
    "interaction",
]


# ---------------------------------------------------------------------------
# System Prompt Compiler
# ---------------------------------------------------------------------------


class SystemPromptCompiler:
    """Compiles a resolved AgentIdentity into a natural-language system prompt."""

    def __init__(self, token_budget: int = 3000):
        self.token_budget = token_budget
        # Track which sections were included/omitted after compilation
        self._sections_included: list[str] = []
        self._sections_omitted: list[str] = []
        self._was_truncated: bool = False

    def compile(self, identity: AgentIdentity, format: str = "text") -> str:
        """
        Compile an identity into a system prompt string.

        Args:
            identity: A fully resolved AgentIdentity.
            format: "text" (generic markdown), "anthropic", or "openai".

        Returns:
            The system prompt as a string.
        """
        # Reset truncation tracking
        self._sections_included = []
        self._sections_omitted = []
        self._was_truncated = False

        # Build named sections as (name, content) pairs
        named_sections: list[tuple[str, str]] = []

        named_sections.append(("header", self._render_header(identity)))
        named_sections.append(("role", self._render_role(identity.role)))
        named_sections.append(("personality", self._render_personality(identity.personality)))
        named_sections.append(("communication", self._render_communication(identity.communication)))

        expertise_section = self._render_expertise(identity.expertise)
        if expertise_section:
            named_sections.append(("expertise", expertise_section))

        named_sections.append(("principles", self._render_principles(identity.principles)))

        behavior_section = self._render_behavior(identity.behavior)
        if behavior_section:
            named_sections.append(("behavior", behavior_section))

        named_sections.append(("guardrails", self._render_guardrails(identity.guardrails)))

        modes_section = self._render_behavioral_modes(identity.behavioral_modes)
        if modes_section:
            named_sections.append(("behavioral_modes", modes_section))

        relationships_section = self._render_relationships(identity.memory)
        if relationships_section:
            named_sections.append(("relationships", relationships_section))

        interaction_section = self._render_interaction(identity.interaction)
        if interaction_section:
            named_sections.append(("interaction", interaction_section))

        religion_section = self._render_religion(identity.religion)
        if religion_section:
            named_sections.append(("religion", religion_section))

        # Join all sections for initial prompt
        prompt = "\n\n".join(content for _name, content in named_sections if content)

        # Check token budget and truncate if necessary
        estimated = self.estimate_tokens(prompt)
        if estimated > self.token_budget:
            logger.warning(
                "Prompt estimated at %d tokens, exceeds budget of %d. Truncating.",
                estimated,
                self.token_budget,
            )
            named_sections = self._truncate_to_budget(named_sections, self.token_budget)
            prompt = "\n\n".join(content for _name, content in named_sections if content)
            self._was_truncated = True
        else:
            # All sections included, nothing omitted
            self._sections_included = [name for name, _ in named_sections]
            self._sections_omitted = []

        if format == "anthropic":
            return self._wrap_anthropic(prompt, identity)
        elif format == "openai":
            return self._wrap_openai(prompt, identity)
        return prompt

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (~4 chars per token)."""
        return len(text) // 4

    def _estimate_tokens_by_model(self, text: str, model: str) -> int:
        """Estimate tokens using model-specific character ratios.

        Args:
            text: The text to estimate tokens for.
            model: Model family identifier. Recognized values:
                   "anthropic", "openai" -> ~4 chars/token
                   "soul" -> ~3.5 chars/token (markdown is slightly more efficient)

        Returns:
            Estimated token count.
        """
        model_lower = model.lower()
        if model_lower in ("soul",):
            # Markdown-heavy content is slightly more token-efficient
            return int(len(text) / 3.5)
        # Default: anthropic, openai, and anything else
        return len(text) // 4

    def _truncate_to_budget(
        self,
        named_sections: list[tuple[str, str]],
        budget: int,
    ) -> list[tuple[str, str]]:
        """Drop optional sections in reverse priority order to fit the token budget.

        Strategy:
        1. Keep required sections (header, role, guardrails) always.
        2. Drop optional sections starting from the lowest priority:
           interaction -> behavioral_modes -> relationships -> behavior -> expertise
        3. If still over budget after dropping all optional sections, truncate
           principles to the top 5.

        Args:
            named_sections: List of (section_name, content) pairs.
            budget: Token budget to fit within.

        Returns:
            Trimmed list of (section_name, content) pairs.
        """
        # Build a mutable list and a quick lookup
        sections = list(named_sections)

        # Drop order: reverse of priority (lowest priority dropped first)
        drop_order = list(reversed(_OPTIONAL_SECTION_PRIORITY))

        omitted: list[str] = []

        for section_to_drop in drop_order:
            prompt = "\n\n".join(content for _, content in sections if content)
            if self.estimate_tokens(prompt) <= budget:
                break

            # Find and remove this section (if present)
            new_sections = []
            dropped = False
            for name, content in sections:
                if name == section_to_drop and not dropped:
                    logger.info("Dropping section '%s' to fit token budget.", section_to_drop)
                    omitted.append(section_to_drop)
                    dropped = True
                else:
                    new_sections.append((name, content))
            sections = new_sections

        # Check if still over budget — truncate principles to top 5
        prompt = "\n\n".join(content for _, content in sections if content)
        if self.estimate_tokens(prompt) > budget:
            new_sections = []
            for name, content in sections:
                if name == "principles":
                    content = self._truncate_principles(content, max_count=5)
                    logger.info("Truncated principles to top 5 to fit token budget.")
                new_sections.append((name, content))
            sections = new_sections

        self._sections_included = [name for name, _ in sections]
        self._sections_omitted = omitted

        return sections

    @staticmethod
    def _truncate_principles(principles_text: str, max_count: int = 5) -> str:
        """Keep only the first N numbered principles from the rendered text."""
        lines = principles_text.split("\n")
        result_lines: list[str] = []
        principle_count = 0
        for line in lines:
            # Detect numbered principle lines like "1. ..." "2. ..."
            if re.match(r"^\d+\.\s", line):
                principle_count += 1
                if principle_count > max_count:
                    # Skip this and all subsequent lines that are part of this principle
                    continue
            elif principle_count > max_count:
                # Skip implication lines (indented) belonging to a dropped principle
                if line.startswith("   "):
                    continue
                # If it's a non-indented, non-numbered line after we've exceeded,
                # it's probably an orphan — skip it too
                continue
            result_lines.append(line)
        return "\n".join(result_lines)

    # ------------------------------------------------------------------
    # Section renderers
    # ------------------------------------------------------------------

    def _render_header(self, identity: AgentIdentity) -> str:
        desc = identity.metadata.description.strip()
        return f"# {identity.metadata.name}\n\n{desc}"

    def _render_role(self, role: Role) -> str:
        lines = [f"## Your Role: {role.title}", "", role.purpose.strip()]

        if role.scope.primary:
            lines.append("\nYou specialize in:")
            for item in role.scope.primary:
                lines.append(f"- {item}")

        if role.scope.secondary:
            lines.append("\nYou can also help with:")
            for item in role.scope.secondary:
                lines.append(f"- {item}")

        if role.scope.out_of_scope:
            lines.append("\nOut of scope (do not attempt):")
            for item in role.scope.out_of_scope:
                lines.append(f"- {item}")

        if role.audience:
            lines.append(f"\nPrimary audience: {role.audience.primary}")

        return "\n".join(lines)

    def _render_personality(self, personality: Personality) -> str:
        lines = ["## Your Personality"]

        # Compute traits from profile if mode is not custom
        if personality.profile.mode != PersonalityMode.CUSTOM:
            computed = compute_personality_traits(personality)
            traits = computed.defined_traits()
            mode_label = personality.profile.mode.value.upper()
            lines.append(f"\n*Personality derived from {mode_label} profile.*")
        else:
            traits = personality.traits.defined_traits()

        for trait_name, value in sorted(traits.items()):
            lines.append(_trait_to_language(trait_name, value))

        if personality.notes:
            lines.append(f"\n{personality.notes.strip()}")

        # Render mood/emotional states if configured
        if personality.mood:
            lines.append("\n## Emotional States")
            lines.append(f"Default mood: {personality.mood.default or 'neutral'}")
            if personality.mood.states:
                lines.append("Available states:")
                for state in personality.mood.states:
                    state_info = f"- {state.name}"
                    if state.description:
                        state_info += f": {state.description}"
                    if state.trait_modifiers:
                        modifier_parts = []
                        for modifier in state.trait_modifiers:
                            sign = "+" if modifier.delta >= 0 else ""
                            modifier_parts.append(f"{modifier.trait} {sign}{modifier.delta}")
                        if modifier_parts:
                            state_info += f" (modifies: {', '.join(modifier_parts)})"
                    if state.tone_override:
                        state_info += f" (tone: {state.tone_override})"
                    lines.append(state_info)
            if personality.mood.transitions:
                lines.append("Transitions:")
                for transition in personality.mood.transitions:
                    from_display = (
                        "*" if transition.from_state == "*" else f"'{transition.from_state}'"
                    )
                    lines.append(
                        f"- [{transition.trigger}] → '{transition.to_state}' (from: {from_display})"
                    )

        return "\n".join(lines)

    def _render_communication(self, comm: Communication) -> str:
        lines = ["## Communication Style", f"\nDefault tone: {comm.tone.default}"]

        if comm.tone.register:
            lines.append(f"Register: {comm.tone.register.value}")

        if comm.style:
            style_parts: list[str] = []
            if comm.style.sentence_length:
                style_parts.append(f"sentence length: {comm.style.sentence_length.value}")
            if comm.style.use_headers is not None:
                style_parts.append(f"use headers: {'yes' if comm.style.use_headers else 'no'}")
            if comm.style.use_lists is not None:
                style_parts.append(f"use lists: {'yes' if comm.style.use_lists else 'no'}")
            if comm.style.use_emoji:
                style_parts.append(f"emoji: {comm.style.use_emoji.value}")
            if style_parts:
                lines.append(f"Style: {', '.join(style_parts)}")

        if comm.vocabulary:
            if comm.vocabulary.preferred:
                lines.append("\nPreferred phrases:")
                for phrase in comm.vocabulary.preferred:
                    lines.append(f'- "{phrase}"')
            if comm.vocabulary.avoided:
                lines.append("\nAvoid phrases like:")
                for phrase in comm.vocabulary.avoided:
                    lines.append(f'- "{phrase}"')
            if comm.vocabulary.signature_phrases:
                lines.append("\nSignature phrases:")
                for phrase in comm.vocabulary.signature_phrases:
                    lines.append(f'- "{phrase}"')

        if comm.tone.overrides:
            lines.append("\nTone adjustments by context:")
            for override in comm.tone.overrides:
                lines.append(f"- When {override.context}: use {override.tone} tone")

        return "\n".join(lines)

    def _render_expertise(self, expertise: Expertise) -> str:
        if not expertise.domains:
            return ""

        lines = ["## Your Expertise"]

        primary = [d for d in expertise.domains if d.category == ExpertiseCategory.PRIMARY]
        secondary = [d for d in expertise.domains if d.category == ExpertiseCategory.SECONDARY]
        tertiary = [d for d in expertise.domains if d.category == ExpertiseCategory.TERTIARY]

        if primary:
            lines.append("\nPrimary expertise:")
            for domain in primary:
                level_text = _expertise_level_text(domain.level)
                line = f"- {domain.name} ({level_text})"
                if domain.description:
                    line += f" — {domain.description}"
                lines.append(line)

        if secondary:
            lines.append("\nSecondary expertise:")
            for domain in secondary:
                lines.append(f"- {domain.name}")

        if tertiary:
            lines.append("\nFamiliar with:")
            for domain in tertiary:
                lines.append(f"- {domain.name}")

        return "\n".join(lines)

    def _render_principles(self, principles: list[Principle]) -> str:
        lines = ["## Core Principles", "\nFollow these principles in order of priority:"]

        sorted_principles = sorted(principles, key=lambda p: p.priority)
        for i, principle in enumerate(sorted_principles, 1):
            lines.append(f"{i}. {principle.statement}")
            if principle.implications:
                for impl in principle.implications:
                    lines.append(f"   - {impl}")

        return "\n".join(lines)

    def _render_behavior(self, behavior: Behavior) -> str:
        if not behavior.strategies:
            return ""

        lines = ["## Behavioral Strategies"]

        for strategy_name, strategy in behavior.strategies.items():
            readable_name = strategy_name.replace("_", " ")
            lines.append(f"\nWhen handling {readable_name}:")
            lines.append(f"Approach: {strategy.approach}")

            for rule in strategy.rules:
                if rule.condition:
                    lines.append(f"- If {rule.condition}: {rule.action}")
                else:
                    lines.append(f"- {rule.action}")

            if strategy.final_fallback:
                lines.append(f"- Fallback: {strategy.final_fallback}")

        return "\n".join(lines)

    def _render_guardrails(self, guardrails: Guardrails) -> str:
        lines = ["## Non-Negotiable Rules"]

        critical = [g for g in guardrails.hard if g.severity == Severity.CRITICAL]
        high = [g for g in guardrails.hard if g.severity == Severity.HIGH]
        other = [g for g in guardrails.hard if g.severity not in (Severity.CRITICAL, Severity.HIGH)]

        if critical:
            lines.append("\nCRITICAL — you must NEVER violate these:")
            for gr in critical:
                lines.append(f"- {gr.rule}")

        if high:
            lines.append("\nHigh priority constraints:")
            for gr in high:
                lines.append(f"- {gr.rule}")

        if other:
            lines.append("\nAdditional constraints:")
            for gr in other:
                lines.append(f"- {gr.rule}")

        if guardrails.topics and guardrails.topics.forbidden:
            lines.append("\nForbidden topics:")
            for topic in guardrails.topics.forbidden:
                reason = f" ({topic.reason})" if topic.reason else ""
                lines.append(f"- {topic.category}{reason}")

        return "\n".join(lines)

    def _render_relationships(self, memory: Memory) -> str:
        rels = memory.relationships
        if not rels.enabled and not rels.agent_relationships:
            return ""
        lines = ["## Agent Relationships"]
        if rels.agent_relationships:
            for r in rels.agent_relationships:
                name = r.name or r.agent_id
                desc = f"{name}: {r.relationship}"
                if r.dynamic:
                    desc += f" ({r.dynamic.value})"
                if r.context:
                    desc += f" — {r.context}"
                if r.interaction_style:
                    desc += f" [style: {r.interaction_style}]"
                lines.append(f"- {desc}")
        if rels.escalation_path:
            lines.append(f"\nEscalation path: {' → '.join(rels.escalation_path)}")
        if rels.unknown_agent_default:
            lines.append(f"Default interaction with unknown agents: {rels.unknown_agent_default}")
        lines.append("")
        return "\n".join(lines)

    def _render_interaction(self, interaction: InteractionConfig | None) -> str:
        if interaction is None:
            return ""
        lines = ["## Interaction Protocols"]
        h = interaction.human
        if h.greeting_style or h.farewell_style or h.tone_matching or h.escalation_triggers:
            lines.append("## With Humans")
            if h.greeting_style:
                lines.append(f"- Greeting: {h.greeting_style}")
            if h.farewell_style:
                lines.append(f"- Farewell: {h.farewell_style}")
            if h.tone_matching:
                lines.append("- Tone matching: Mirror the user's formality level")
            if h.escalation_triggers:
                triggers = ", ".join(t.value for t in h.escalation_triggers)
                lines.append(f"- Escalate when: {triggers}")
            if h.escalation_message:
                lines.append(f'- Escalation message: "{h.escalation_message}"')
        a = interaction.agent
        lines.append("## With Other Agents")
        lines.append(f"- Handoff style: {a.handoff_style}")
        lines.append(f"- Status reporting: {a.status_reporting}")
        lines.append(f"- Conflict resolution: {a.conflict_resolution}")
        lines.append("")
        return "\n".join(lines)

    def _render_behavioral_modes(self, modes: BehavioralModeConfig | None) -> str:
        if modes is None or not modes.modes:
            return ""
        lines = ["## Behavioral Modes", f"Default mode: {modes.default}", ""]
        for mode in modes.modes:
            desc = f" — {mode.description}" if mode.description else ""
            lines.append(f"### {mode.name}{desc}")
            if mode.overrides.tone_register:
                lines.append(f"  Register: {mode.overrides.tone_register}")
            if mode.overrides.tone_default:
                lines.append(f"  Tone: {mode.overrides.tone_default}")
            if mode.overrides.emoji_usage:
                lines.append(f"  Emoji: {mode.overrides.emoji_usage}")
            if mode.overrides.sentence_length:
                lines.append(f"  Sentences: {mode.overrides.sentence_length}")
            if mode.overrides.trait_modifiers:
                mods = ", ".join(
                    f"{m.trait} {'+' if m.delta > 0 else ''}{m.delta}"
                    for m in mode.overrides.trait_modifiers
                )
                lines.append(f"  Trait adjustments: {mods}")
            if mode.additional_guardrails:
                lines.append(f"  Additional rules: {'; '.join(mode.additional_guardrails)}")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Religion rendering
    # ------------------------------------------------------------------

    def _render_religion(self, religion: ReligionConfig) -> str:
        """Render the religion/spiritual framework section."""
        if not religion.enabled:
            return ""

        lines: list[str] = ["## Religious & Spiritual Framework"]

        # Tradition / denomination header
        if religion.tradition_name:
            label = religion.tradition_name
            if religion.denomination:
                label += f" ({religion.denomination})"
            lines.append(f"Tradition: {label}")

        # Influence description
        influence_desc = {
            InfluenceLevel.SUBTLE: "These beliefs subtly inform your worldview.",
            InfluenceLevel.MODERATE: "These beliefs moderately shape your worldview and decisions.",
            InfluenceLevel.STRONG: "These beliefs strongly shape your worldview and decision-making.",
            InfluenceLevel.CENTRAL: (
                "These beliefs are central to your identity and permeate all decisions."
            ),
        }
        lines.append(influence_desc.get(religion.influence, ""))

        # Principles
        if religion.principles:
            lines.append("")
            influence_val = religion.influence.value
            principles_str = "; ".join(religion.principles)
            lines.append(
                f"You are guided by these {influence_val}-level principles: "
                f"{principles_str}. Weigh decisions against them."
            )

        # Moral framework
        if religion.moral_framework:
            mf = religion.moral_framework
            lines.append("")
            lines.append(f"Moral framework: {mf.name}")
            if mf.description:
                lines.append(f"  {mf.description}")
            if mf.principles:
                lines.append(f"  Core values: {', '.join(mf.principles)}")
            lines.append(f"  Decision weight: {mf.decision_weight}")

        # Sacred texts
        if religion.sacred_texts:
            lines.append("")
            lines.append("Sacred texts:")
            for text in religion.sacred_texts:
                desc = f" — {text.description}" if text.description else ""
                lines.append(f"  - {text.name} ({text.authority_level.value}){desc}")

        # Traditions
        if religion.traditions:
            lines.append("")
            lines.append("Traditions:")
            for tradition in religion.traditions:
                impact = f" → {tradition.behavioral_impact}" if tradition.behavioral_impact else ""
                lines.append(f"  - {tradition.name}{impact}")

        # Dietary rules
        if religion.dietary_rules:
            lines.append("")
            lines.append("Dietary observances:")
            for rule in religion.dietary_rules:
                exc = f" (exceptions: {', '.join(rule.exceptions)})" if rule.exceptions else ""
                lines.append(f"  - {rule.rule} [{rule.strictness.value}]{exc}")

        # Holy days
        if religion.holy_days:
            lines.append("")
            lines.append("Holy days:")
            for day in religion.holy_days:
                obs = f" — {day.observance}" if day.observance else ""
                period = f" ({day.period})" if day.period else ""
                lines.append(f"  - {day.name}{period}{obs}")

        # Prayer schedule
        if religion.prayer_schedule and religion.prayer_schedule.enabled:
            ps = religion.prayer_schedule
            lines.append("")
            freq = f": {ps.frequency}" if ps.frequency else ""
            lines.append(f"Prayer/meditation{freq}")
            if ps.description:
                lines.append(f"  {ps.description}")

        # Notes
        if religion.notes:
            lines.append("")
            lines.append(f"Note: {religion.notes}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Format wrappers
    # ------------------------------------------------------------------

    def _wrap_anthropic(self, prompt: str, identity: AgentIdentity) -> str:
        """Wrap for Anthropic Claude — use XML section tags for better parsing."""
        # Split the prompt into its component sections and wrap each in XML tags
        wrapped_parts: list[str] = []

        # Map markdown section headers to XML tag names
        section_map = {
            "# ": "identity",
            "## Your Role": "role",
            "## Your Personality": "personality",
            "## Emotional States": "personality",
            "## Communication Style": "communication",
            "## Your Expertise": "expertise",
            "## Core Principles": "principles",
            "## Behavioral Strategies": "behavior",
            "## Non-Negotiable Rules": "guardrails",
            "## Behavioral Modes": "behavioral_modes",
            "## Agent Relationships": "relationships",
            "## Interaction Protocols": "interaction",
            "## Religious & Spiritual Framework": "religion",
        }

        # Split on double newlines (section boundaries)
        raw_sections = prompt.split("\n\n")

        # Group consecutive blocks that belong to the same XML section
        current_tag: str | None = None
        current_content: list[str] = []

        def _flush() -> None:
            nonlocal current_tag, current_content
            if current_content:
                text = "\n\n".join(current_content)
                if current_tag:
                    wrapped_parts.append(f"<{current_tag}>\n{text}\n</{current_tag}>")
                else:
                    wrapped_parts.append(text)
            current_content = []

        for block in raw_sections:
            first_line = block.split("\n")[0].strip()
            matched_tag = None

            for prefix, tag in section_map.items():
                if first_line.startswith(prefix):
                    matched_tag = tag
                    break

            if matched_tag and matched_tag != current_tag:
                _flush()
                current_tag = matched_tag
                current_content = [block]
            else:
                current_content.append(block)

        _flush()

        return "\n\n".join(wrapped_parts)

    def _wrap_openai(self, prompt: str, identity: AgentIdentity) -> str:
        """Wrap for OpenAI — add a concise summary prefix."""
        name = identity.metadata.name
        role_title = identity.role.title
        prefix = f"You are {name}, a {role_title}."
        return f"{prefix}\n\n{prompt}"


# ---------------------------------------------------------------------------
# OpenClaw Compiler
# ---------------------------------------------------------------------------


class OpenClawCompiler:
    """Compiles a resolved AgentIdentity into OpenClaw personality.json format."""

    def __init__(self, prompt_compiler: SystemPromptCompiler | None = None):
        self.prompt_compiler = prompt_compiler or SystemPromptCompiler()

    def compile(
        self,
        identity: AgentIdentity,
        model_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Compile identity into OpenClaw personality.json format.

        Args:
            identity: The resolved PersonaNexus.
            model_config: Optional model configuration dict to override defaults.
                          Expected keys: primary_model, temperature, max_tokens, top_p.

        Returns:
            Dictionary matching the OpenClaw personality.json schema.
        """
        system_prompt = self.prompt_compiler.compile(identity, format="text")

        # Compute traits from profile if mode is not custom
        if identity.personality.profile.mode != PersonalityMode.CUSTOM:
            computed = compute_personality_traits(identity.personality)
            traits_dict = computed.defined_traits()
        else:
            traits_dict = identity.personality.traits.defined_traits()

        result: dict[str, Any] = {
            "agent_name": identity.metadata.name,
            "agent_role": self._simplify_role(identity.role.title),
            "version": identity.metadata.version,
            "system_prompt": system_prompt,
            "greeting": self._generate_greeting(identity),
            "personality_traits": traits_dict,
            "model_config": self._default_model_config(model_config),
            "tool_preferences": {},
            "behavioral_settings": self._extract_behavioral_settings(identity),
            "response_format": self._extract_response_format(identity),
            "domain_expertise": [d.name for d in identity.expertise.domains],
            "example_phrases": (
                identity.communication.vocabulary.signature_phrases
                if identity.communication.vocabulary
                else []
            ),
            "guidelines": [
                p.statement for p in sorted(identity.principles, key=lambda p: p.priority)
            ],
        }

        # Include religion config if enabled
        if identity.religion.enabled:
            religion_data: dict[str, Any] = {
                "enabled": True,
                "influence": identity.religion.influence.value,
                "principles": identity.religion.principles,
            }
            if identity.religion.tradition_name:
                religion_data["tradition_name"] = identity.religion.tradition_name
            if identity.religion.denomination:
                religion_data["denomination"] = identity.religion.denomination
            if identity.religion.moral_framework:
                religion_data["moral_framework"] = (
                    identity.religion.moral_framework.model_dump()
                )
            if identity.religion.sacred_texts:
                religion_data["sacred_texts"] = [
                    t.model_dump() for t in identity.religion.sacred_texts
                ]
            if identity.religion.traditions:
                religion_data["traditions"] = [
                    t.model_dump() for t in identity.religion.traditions
                ]
            if identity.religion.dietary_rules:
                religion_data["dietary_rules"] = [
                    r.model_dump() for r in identity.religion.dietary_rules
                ]
            if identity.religion.holy_days:
                religion_data["holy_days"] = [
                    d.model_dump() for d in identity.religion.holy_days
                ]
            if identity.religion.prayer_schedule:
                religion_data["prayer_schedule"] = (
                    identity.religion.prayer_schedule.model_dump()
                )
            result["religion"] = religion_data

        # Include personality profile metadata for non-custom modes
        profile = identity.personality.profile
        if profile.mode != PersonalityMode.CUSTOM:
            profile_meta: dict[str, Any] = {"mode": profile.mode.value}
            if profile.ocean:
                profile_meta["ocean"] = profile.ocean.model_dump()
            if profile.disc:
                profile_meta["disc"] = profile.disc.model_dump()
            if profile.disc_preset:
                profile_meta["disc_preset"] = profile.disc_preset
            result["personality_profile"] = profile_meta

        return result

    def _simplify_role(self, title: str) -> str:
        return title.lower().replace(" ", "_").replace("-", "_")

    def _generate_greeting(self, identity: AgentIdentity) -> str:
        name = identity.metadata.name
        role = identity.role.title
        purpose = identity.role.purpose.strip().split("\n")[0]  # first line only
        return f"Hello! I'm {name}, your {role}. {purpose} How can I assist you today?"

    def _default_model_config(
        self,
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        config = {
            "primary_model": "claude-sonnet-4",
            "fallback_model": "claude-haiku-4",
            "temperature": 0.3,
            "max_tokens": 4096,
            "top_p": 0.9,
        }
        if overrides:
            config.update(overrides)
        return config

    def _extract_behavioral_settings(self, identity: AgentIdentity) -> dict[str, bool]:
        settings: dict[str, bool] = {}
        for guardrail in identity.guardrails.hard:
            settings[guardrail.id] = True
        for guardrail in identity.guardrails.soft:
            settings[guardrail.id] = True
        return settings

    def _extract_response_format(self, identity: AgentIdentity) -> dict[str, Any]:
        result: dict[str, Any] = {"tone": identity.communication.tone.default}

        if identity.communication.style:
            style = identity.communication.style
            if style.use_headers is not None:
                result["use_headings"] = style.use_headers
            if style.use_lists is not None:
                result["use_bullet_points"] = style.use_lists
            if style.use_emoji:
                result["use_emoji"] = style.use_emoji.value
            if style.sentence_length:
                result["sentence_length"] = style.sentence_length.value

        return result


# ---------------------------------------------------------------------------
# Soul Compiler — YAML → SOUL.md + STYLE.md
# ---------------------------------------------------------------------------


class SoulCompiler:
    """Compiles a resolved AgentIdentity into SOUL.md and STYLE.md Markdown files.

    Follows the soul.md format (https://github.com/aaronjmars/soul.md)
    for compatibility with OpenClaw's workspace bootstrap system.
    """

    def compile(self, identity: AgentIdentity) -> dict[str, str]:
        """Compile identity into SOUL.md and STYLE.md content.

        Returns:
            Dict with keys "soul_md" and "style_md", each containing Markdown text.
        """
        return {
            "soul_md": self._render_soul(identity),
            "style_md": self._render_style(identity),
        }

    # ------------------------------------------------------------------
    # SOUL.md rendering
    # ------------------------------------------------------------------

    def _render_soul(self, identity: AgentIdentity) -> str:
        sections: list[str] = []

        sections.append(self._soul_header(identity))
        sections.append(self._soul_who_i_am(identity))
        sections.append(self._soul_worldview(identity))

        opinions = self._soul_opinions(identity.narrative)
        if opinions:
            sections.append(opinions)

        sections.append(self._soul_interests(identity))

        current_focus = self._soul_current_focus(identity.narrative)
        if current_focus:
            sections.append(current_focus)

        influences = self._soul_influences(identity.narrative)
        if influences:
            sections.append(influences)

        vocabulary = self._soul_vocabulary(identity)
        if vocabulary:
            sections.append(vocabulary)

        tensions = self._soul_tensions(identity.narrative)
        if tensions:
            sections.append(tensions)

        religion = self._soul_religion(identity)
        if religion:
            sections.append(religion)

        sections.append(self._soul_boundaries(identity))

        pet_peeves = self._soul_pet_peeves(identity.narrative)
        if pet_peeves:
            sections.append(pet_peeves)

        return "\n\n".join(s for s in sections if s)

    def _soul_header(self, identity: AgentIdentity) -> str:
        desc = identity.metadata.description.strip()
        return f"# {identity.metadata.name}\n\n{desc}"

    def _soul_who_i_am(self, identity: AgentIdentity) -> str:
        lines = ["## Who I Am"]

        # Use narrative backstory if available, otherwise build from role
        if identity.narrative.backstory:
            lines.append(f"\n{identity.narrative.backstory.strip()}")
        else:
            lines.append(f"\n{identity.role.purpose.strip()}")

        # Add personality narrative from notes
        if identity.personality.notes:
            lines.append(f"\n{identity.personality.notes.strip()}")

        # Add personality trait descriptions
        if identity.personality.profile.mode != PersonalityMode.CUSTOM:
            computed = compute_personality_traits(identity.personality)
            traits = computed.defined_traits()
        else:
            traits = identity.personality.traits.defined_traits()

        if traits:
            trait_lines: list[str] = []
            for trait_name, value in sorted(traits.items()):
                trait_lines.append(_trait_to_language(trait_name, value))
            lines.append("\n" + " ".join(trait_lines))

        return "\n".join(lines)

    def _soul_worldview(self, identity: AgentIdentity) -> str:
        lines = ["## Worldview"]
        for principle in sorted(identity.principles, key=lambda p: p.priority):
            lines.append(f"\n- {principle.statement}")
            for impl in principle.implications:
                lines.append(f"  - {impl}")
        return "\n".join(lines)

    def _soul_opinions(self, narrative: Narrative) -> str:
        if not narrative.opinions:
            return ""
        lines = ["## Opinions"]
        for opinion in narrative.opinions:
            lines.append(f"\n### {opinion.domain}")
            for take in opinion.takes:
                lines.append(f"- {take}")
        return "\n".join(lines)

    def _soul_interests(self, identity: AgentIdentity) -> str:
        if not identity.expertise.domains:
            return ""
        lines = ["## Interests"]
        for domain in identity.expertise.domains:
            level = _expertise_level_text(domain.level)
            desc = f": {domain.description}" if domain.description else ""
            lines.append(f"- **{domain.name}** ({level}){desc}")
        return "\n".join(lines)

    def _soul_current_focus(self, narrative: Narrative) -> str:
        if not narrative.current_focus:
            return ""
        lines = ["## Current Focus"]
        for focus in narrative.current_focus:
            lines.append(f"- {focus}")
        return "\n".join(lines)

    def _soul_influences(self, narrative: Narrative) -> str:
        if not narrative.influences:
            return ""
        lines = ["## Influences"]

        by_category: dict[str, list[tuple[str, str]]] = {}
        for inf in narrative.influences:
            cat = inf.category.title()
            by_category.setdefault(cat, []).append((inf.name, inf.insight))

        for category, items in by_category.items():
            lines.append(f"\n### {category}")
            for name, insight in items:
                lines.append(f"- **{name}**: {insight}")

        return "\n".join(lines)

    def _soul_vocabulary(self, identity: AgentIdentity) -> str:
        vocab = identity.communication.vocabulary
        if not vocab:
            return ""
        if not vocab.signature_phrases:
            return ""
        lines = ["## Vocabulary"]
        for phrase in vocab.signature_phrases:
            lines.append(f'- **"{phrase}"**')
        return "\n".join(lines)

    def _soul_tensions(self, narrative: Narrative) -> str:
        if not narrative.tensions:
            return ""
        lines = ["## Tensions & Contradictions"]
        for tension in narrative.tensions:
            lines.append(f"- {tension}")
        return "\n".join(lines)

    def _soul_religion(self, identity: AgentIdentity) -> str:
        """Render religion section for SOUL.md."""
        religion = identity.religion
        if not religion.enabled:
            return ""

        lines = ["## Faith & Guiding Principles"]

        if religion.tradition_name:
            label = religion.tradition_name
            if religion.denomination:
                label += f" ({religion.denomination})"
            lines.append(f"\nI draw from the {label} tradition.")

        if religion.principles:
            lines.append("")
            for principle in religion.principles:
                lines.append(f"- {principle}")

        if religion.moral_framework:
            lines.append(f"\nMoral compass: {religion.moral_framework.name}")
            if religion.moral_framework.principles:
                for p in religion.moral_framework.principles:
                    lines.append(f"- {p}")

        if religion.sacred_texts:
            texts = ", ".join(t.name for t in religion.sacred_texts)
            lines.append(f"\nI draw wisdom from: {texts}")

        return "\n".join(lines)

    def _soul_boundaries(self, identity: AgentIdentity) -> str:
        lines = ["## Boundaries"]
        seen: set[str] = set()

        for gr in identity.guardrails.hard:
            key = gr.rule.lower().strip()
            if key not in seen:
                seen.add(key)
                lines.append(f"- Won't: {gr.rule}")

        # Out-of-scope items as boundaries
        if identity.role.scope.out_of_scope:
            for item in identity.role.scope.out_of_scope:
                key = item.lower().strip()
                if key not in seen:
                    seen.add(key)
                    lines.append(f"- Won't: {item}")

        return "\n".join(lines)

    def _soul_pet_peeves(self, narrative: Narrative) -> str:
        if not narrative.pet_peeves:
            return ""
        lines = ["## Pet Peeves"]
        for peeve in narrative.pet_peeves:
            lines.append(f"- {peeve}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # STYLE.md rendering
    # ------------------------------------------------------------------

    def _render_style(self, identity: AgentIdentity) -> str:
        sections: list[str] = []

        sections.append("# Voice & Style Guide")
        sections.append(self._style_voice_principles(identity))
        sections.append(self._style_vocabulary(identity))
        sections.append(self._style_formatting(identity))

        context_styles = self._style_context_adjustments(identity)
        if context_styles:
            sections.append(context_styles)

        examples = self._style_examples(identity)
        if examples:
            sections.append(examples)

        anti = self._style_anti_patterns(identity)
        if anti:
            sections.append(anti)

        return "\n\n".join(s for s in sections if s)

    def _style_voice_principles(self, identity: AgentIdentity) -> str:
        lines = ["## Voice Principles"]
        comm = identity.communication

        lines.append(f"\n- Default tone: {comm.tone.default}")
        if comm.tone.register:
            lines.append(f"- Register: {comm.tone.register.value}")

        # Add trait-derived voice description
        if identity.personality.profile.mode != PersonalityMode.CUSTOM:
            computed = compute_personality_traits(identity.personality)
            traits = computed.defined_traits()
        else:
            traits = identity.personality.traits.defined_traits()

        if traits:
            voice_notes: list[str] = []
            for trait_name, value in sorted(traits.items()):
                voice_notes.append(_trait_to_language(trait_name, value))
            lines.append(f"\n{' '.join(voice_notes)}")

        return "\n".join(lines)

    def _style_vocabulary(self, identity: AgentIdentity) -> str:
        vocab = identity.communication.vocabulary
        if not vocab:
            return ""

        lines = ["## Vocabulary"]

        if vocab.preferred:
            lines.append("\n### Words & Phrases You Use")
            for phrase in vocab.preferred:
                lines.append(f'- "{phrase}"')

        if vocab.avoided:
            lines.append("\n### Words You Never Use")
            for phrase in vocab.avoided:
                lines.append(f'- "{phrase}"')

        return "\n".join(lines)

    def _style_formatting(self, identity: AgentIdentity) -> str:
        style = identity.communication.style
        if not style:
            return ""

        lines = ["## Punctuation & Formatting"]

        if style.sentence_length:
            lines.append(f"- Sentence length: {style.sentence_length.value}")
        if style.use_headers is not None:
            lines.append(f"- Use headers: {'yes' if style.use_headers else 'no'}")
        if style.use_lists is not None:
            lines.append(f"- Use lists: {'yes' if style.use_lists else 'no'}")
        if style.use_code_blocks is not None:
            lines.append(f"- Use code blocks: {'yes' if style.use_code_blocks else 'no'}")
        if style.use_emoji:
            lines.append(f"- Emoji: {style.use_emoji.value}")

        return "\n".join(lines)

    def _style_context_adjustments(self, identity: AgentIdentity) -> str:
        if not identity.communication.tone.overrides:
            return ""

        lines = ["## Context-Specific Style"]
        for override in identity.communication.tone.overrides:
            lines.append(f"\n### {override.context.title()}")
            lines.append(f"- Tone: {override.tone}")
            if override.note:
                lines.append(f"- Note: {override.note}")

        return "\n".join(lines)

    def _style_examples(self, identity: AgentIdentity) -> str:
        examples = identity.communication.voice_examples
        if not examples:
            return ""
        if not examples.good and not examples.bad:
            return ""

        lines = ["## Voice Examples"]

        if examples.good:
            lines.append("\n### Right Voice")
            for ex in examples.good:
                ctx = f" ({ex.context})" if ex.context else ""
                lines.append(f'\n> "{ex.text}"{ctx}')

        if examples.bad:
            lines.append("\n### Wrong Voice")
            for ex in examples.bad:
                ctx = f" ({ex.context})" if ex.context else ""
                lines.append(f'\n> "{ex.text}"{ctx}')

        return "\n".join(lines)

    def _style_anti_patterns(self, identity: AgentIdentity) -> str:
        vocab = identity.communication.vocabulary
        if not vocab or not vocab.avoided:
            return ""

        lines = ["## Anti-Patterns", "\nNever say:"]
        for phrase in vocab.avoided:
            lines.append(f'- "{phrase}"')

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Markdown Compiler — clean documentation-oriented markdown
# ---------------------------------------------------------------------------


class MarkdownCompiler:
    """Compiles a resolved AgentIdentity into clean, structured Markdown documentation."""

    def compile(self, identity: AgentIdentity) -> str:
        """Compile identity into well-structured Markdown with proper heading hierarchy.

        Returns:
            Clean Markdown string suitable for documentation.
        """
        sections: list[str] = []

        # Title
        sections.append(f"# {identity.metadata.name}")
        sections.append(f"_{identity.metadata.description.strip()}_")
        sections.append(
            f"Version {identity.metadata.version} | Status: {identity.metadata.status.value}"
        )

        # Role
        sections.append(f"## Role: {identity.role.title}")
        sections.append(identity.role.purpose.strip())

        if identity.role.scope.primary:
            scope_lines = ["### Scope", "", "**Primary:**"]
            for item in identity.role.scope.primary:
                scope_lines.append(f"- {item}")
            if identity.role.scope.secondary:
                scope_lines.append("\n**Secondary:**")
                for item in identity.role.scope.secondary:
                    scope_lines.append(f"- {item}")
            if identity.role.scope.out_of_scope:
                scope_lines.append("\n**Out of Scope:**")
                for item in identity.role.scope.out_of_scope:
                    scope_lines.append(f"- {item}")
            sections.append("\n".join(scope_lines))

        if identity.role.audience:
            sections.append(f"### Audience\n\n{identity.role.audience.primary}")

        # Personality
        if identity.personality.profile.mode != PersonalityMode.CUSTOM:
            computed = compute_personality_traits(identity.personality)
            traits = computed.defined_traits()
        else:
            traits = identity.personality.traits.defined_traits()

        if traits:
            personality_lines = ["## Personality"]
            for trait_name, value in sorted(traits.items()):
                bar = _markdown_bar(value)
                personality_lines.append(f"- **{trait_name}**: {bar} ({value:.2f})")
            if identity.personality.notes:
                personality_lines.append(f"\n{identity.personality.notes.strip()}")
            sections.append("\n".join(personality_lines))

        # Communication
        comm = identity.communication
        comm_lines = ["## Communication", f"\n**Tone:** {comm.tone.default}"]
        if comm.tone.register:
            comm_lines.append(f"**Register:** {comm.tone.register.value}")
        sections.append("\n".join(comm_lines))

        # Expertise
        if identity.expertise.domains:
            expertise_lines = ["## Expertise"]
            for domain in identity.expertise.domains:
                level_text = _expertise_level_text(domain.level)
                line = f"- **{domain.name}** ({level_text}, {domain.category.value})"
                if domain.description:
                    line += f" -- {domain.description}"
                expertise_lines.append(line)
            sections.append("\n".join(expertise_lines))

        # Principles
        if identity.principles:
            principle_lines = ["## Principles"]
            for principle in sorted(identity.principles, key=lambda p: p.priority):
                principle_lines.append(f"\n### {principle.priority}. {principle.statement}")
                if principle.implications:
                    for impl in principle.implications:
                        principle_lines.append(f"- {impl}")
            sections.append("\n".join(principle_lines))

        # Religion
        if identity.religion.enabled:
            religion_lines = ["## Religious & Spiritual Framework"]
            if identity.religion.tradition_name:
                label = identity.religion.tradition_name
                if identity.religion.denomination:
                    label += f" ({identity.religion.denomination})"
                religion_lines.append(f"\n**Tradition:** {label}")
            religion_lines.append(
                f"**Influence:** {identity.religion.influence.value}"
            )
            if identity.religion.principles:
                religion_lines.append("\n**Principles:**")
                for p in identity.religion.principles:
                    religion_lines.append(f"- {p}")
            if identity.religion.moral_framework:
                mf = identity.religion.moral_framework
                religion_lines.append(f"\n**Moral Framework:** {mf.name}")
                if mf.principles:
                    for p in mf.principles:
                        religion_lines.append(f"- {p}")
            sections.append("\n".join(religion_lines))

        # Guardrails
        guardrails_lines = ["## Guardrails"]
        for gr in identity.guardrails.hard:
            severity_label = gr.severity.value.upper() if gr.severity else "MEDIUM"
            guardrails_lines.append(f"- **[{severity_label}]** {gr.rule}")
        sections.append("\n".join(guardrails_lines))

        return "\n\n".join(sections)


def _markdown_bar(value: float, width: int = 10) -> str:
    """Create a simple text progress bar for markdown."""
    filled = round(value * width)
    return "[" + "#" * filled + "." * (width - filled) + "]"


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def compile_identity(
    identity: AgentIdentity,
    target: str = "text",
    token_budget: int = 3000,
) -> str | dict[str, Any]:
    """
    Compile a resolved AgentIdentity into the specified target format.

    Args:
        identity: A fully resolved AgentIdentity.
        target: "text", "anthropic", "openai", "openclaw", "soul", "json",
                or "markdown".
        token_budget: Estimated token budget for system prompt.

    Returns:
        String for text/markdown formats, dict for openclaw/soul/json.
    """
    prompt_compiler = SystemPromptCompiler(token_budget=token_budget)

    if target in ("text", "anthropic", "openai"):
        prompt = prompt_compiler.compile(identity, format=target)
        # If truncation occurred, append a note about omitted sections
        if prompt_compiler._was_truncated and prompt_compiler._sections_omitted:
            omitted_list = ", ".join(prompt_compiler._sections_omitted)
            note = f"\n\n<!-- Note: Sections omitted to fit token budget: {omitted_list} -->"
            prompt += note
        return prompt
    elif target == "openclaw":
        openclaw_compiler = OpenClawCompiler(prompt_compiler)
        return openclaw_compiler.compile(identity)
    elif target == "soul":
        soul_compiler = SoulCompiler()
        return soul_compiler.compile(identity)
    elif target == "json":
        prompt = prompt_compiler.compile(identity, format="text")
        result: dict[str, Any] = {
            "system_prompt": prompt,
            "tokens_estimated": prompt_compiler.estimate_tokens(prompt),
        }
        # Include section tracking in JSON output
        if prompt_compiler._sections_included:
            result["sections_included"] = prompt_compiler._sections_included
        if prompt_compiler._sections_omitted:
            result["sections_omitted"] = prompt_compiler._sections_omitted
        return result
    elif target == "markdown":
        markdown_compiler = MarkdownCompiler()
        return markdown_compiler.compile(identity)
    else:
        raise CompilerError(f"Unknown target format: {target}")
