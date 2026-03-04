"""Religion & spiritual framework configuration for PersonaNexus agents."""

from __future__ import annotations

import enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class InfluenceLevel(enum.StrEnum):
    """How strongly religion shapes the agent's worldview and decisions."""

    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"
    CENTRAL = "central"


class Strictness(enum.StrEnum):
    STRICT = "strict"
    MODERATE = "moderate"
    FLEXIBLE = "flexible"


class AuthorityLevel(enum.StrEnum):
    CANONICAL = "canonical"
    AUTHORITATIVE = "authoritative"
    INSPIRATIONAL = "inspirational"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class DietaryRule(BaseModel):
    """A dietary observance or restriction."""

    rule: str = Field(..., max_length=500)
    strictness: Strictness = Strictness.MODERATE
    exceptions: list[str] = Field(default_factory=list, max_length=20)


class HolyDay(BaseModel):
    """A significant day or period of observance."""

    name: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=500)
    observance: str | None = Field(None, max_length=500)
    period: str | None = Field(None, max_length=100)


class PrayerSchedule(BaseModel):
    """Prayer or meditation practice configuration."""

    enabled: bool = False
    frequency: str | None = Field(None, max_length=200)
    description: str | None = Field(None, max_length=500)


class SacredText(BaseModel):
    """A sacred or foundational text."""

    name: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=500)
    authority_level: AuthorityLevel = AuthorityLevel.INSPIRATIONAL


class MoralFramework(BaseModel):
    """A structured moral/ethical framework derived from religious teaching."""

    name: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=1000)
    principles: list[str] = Field(default_factory=list, max_length=50)
    decision_weight: float = Field(0.5, ge=0.0, le=1.0)


class Tradition(BaseModel):
    """A religious tradition or practice that influences behavior."""

    name: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=500)
    behavioral_impact: str | None = Field(None, max_length=500)


# ---------------------------------------------------------------------------
# Top-level ReligionConfig
# ---------------------------------------------------------------------------


class ReligionConfig(BaseModel):
    """Complete religion/spiritual framework configuration for an agent.

    When ``enabled`` is False (the default), religion has no effect on the
    agent's personality or system prompt.  Existing YAML files without a
    ``religion`` key will default to this disabled state.
    """

    enabled: bool = False
    tradition_name: str | None = Field(
        None,
        max_length=200,
        description="e.g. 'Christianity', 'Islam', 'Buddhism', 'Hinduism'",
    )
    denomination: str | None = Field(
        None,
        max_length=200,
        description="e.g. 'Catholic', 'Sunni', 'Theravada', 'Vaishnavism'",
    )
    influence: InfluenceLevel = InfluenceLevel.MODERATE
    principles: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Core guiding principles derived from the faith tradition",
    )
    sacred_texts: list[SacredText] = Field(default_factory=list, max_length=20)
    moral_framework: MoralFramework | None = None
    traditions: list[Tradition] = Field(default_factory=list, max_length=30)
    dietary_rules: list[DietaryRule] = Field(default_factory=list, max_length=20)
    holy_days: list[HolyDay] = Field(default_factory=list, max_length=50)
    prayer_schedule: PrayerSchedule | None = None
    notes: str | None = Field(None, max_length=2000)


# ---------------------------------------------------------------------------
# build_persona — quick YAML-to-prompt helper
# ---------------------------------------------------------------------------


def build_persona(yaml_file: str | Path) -> str:
    """Build a system prompt from a PersonaNexus YAML file.

    This is a convenience function that loads a YAML identity file and
    produces a basic system prompt string, including religion context when
    the ``religion`` section is enabled.

    For full-featured compilation (Anthropic XML, OpenClaw JSON, SOUL.md,
    etc.) use :class:`religion_skill.compiler.SystemPromptCompiler` instead.
    """
    with open(yaml_file, "r") as fh:
        persona: dict[str, Any] = yaml.safe_load(fh) or {}

    name = persona.get("metadata", {}).get("name", "Agent")
    role_title = persona.get("role", {}).get("title", "assistant")

    # Build trait string from personality traits
    traits_dict: dict[str, Any] = persona.get("personality", {}).get("traits", {})
    if traits_dict:
        trait_parts = [f"{k}={v}" for k, v in traits_dict.items() if isinstance(v, (int, float))]
        traits_str = ", ".join(trait_parts)
    else:
        traits_str = "balanced"

    system_prompt = f"You are {name}, a {role_title} with traits: {traits_str}."

    # --- Religion integration ---
    religion: dict[str, Any] = persona.get("religion", {})
    if religion.get("enabled", False):
        influence = religion.get("influence", "moderate")
        principles = religion.get("principles", [])
        if principles:
            principles_str = " ".join(principles)
            system_prompt += (
                f" You are guided by these {influence}-level principles:"
                f" {principles_str}. Weigh decisions against them."
            )

        # Moral framework
        moral = religion.get("moral_framework")
        if moral and isinstance(moral, dict):
            fw_name = moral.get("name", "")
            fw_principles = moral.get("principles", [])
            if fw_name:
                system_prompt += f" Your moral framework is {fw_name}."
            if fw_principles:
                system_prompt += f" Core values: {', '.join(fw_principles)}."

        # Traditions
        traditions = religion.get("traditions", [])
        if traditions:
            tradition_names = [
                t["name"] if isinstance(t, dict) else str(t) for t in traditions
            ]
            system_prompt += f" You honor these traditions: {', '.join(tradition_names)}."

        # Dietary rules
        dietary = religion.get("dietary_rules", [])
        if dietary:
            rules = [d["rule"] if isinstance(d, dict) else str(d) for d in dietary]
            system_prompt += f" Dietary observances: {'; '.join(rules)}."

        # Sacred texts
        texts = religion.get("sacred_texts", [])
        if texts:
            text_names = [t["name"] if isinstance(t, dict) else str(t) for t in texts]
            system_prompt += f" You draw wisdom from: {', '.join(text_names)}."

    return system_prompt
