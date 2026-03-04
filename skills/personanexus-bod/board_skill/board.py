"""Board of Directors — historical figures advisory panel for PersonaNexus agents."""

from __future__ import annotations

import enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class DiscStyle(enum.StrEnum):
    """DISC primary style for a board member."""

    DOMINANCE = "dominance"
    INFLUENCE = "influence"
    STEADINESS = "steadiness"
    COMPLIANCE = "compliance"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class OceanScores(BaseModel):
    """OCEAN personality scores (0.0–1.0 normalized scale)."""

    openness: float = Field(..., ge=0.0, le=1.0)
    conscientiousness: float = Field(..., ge=0.0, le=1.0)
    extraversion: float = Field(..., ge=0.0, le=1.0)
    agreeableness: float = Field(..., ge=0.0, le=1.0)
    neuroticism: float = Field(..., ge=0.0, le=1.0)


class MemberPersonality(BaseModel):
    """Personality profile for a board member across three frameworks."""

    ocean: OceanScores
    disc_style: DiscStyle
    jungian_type: str = Field(..., pattern=r"^[EI][NS][TF][JP]$")


class BoardMember(BaseModel):
    """A single member of the advisory board."""

    id: str = Field(..., max_length=100)
    name: str = Field(..., max_length=200)
    historical_figure: str = Field(..., max_length=200)
    died: str = Field(..., max_length=50, description="e.g. '~496 BC', '180 AD', '1527'")
    board_role: str = Field(..., max_length=200)
    core_mindset: str = Field(..., max_length=500)
    modern_relevance: str = Field(..., max_length=1000)
    personality: MemberPersonality
    key_quote: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=2000)


# ---------------------------------------------------------------------------
# Top-level BoardConfig
# ---------------------------------------------------------------------------

_DEFAULT_DISCLAIMER = (
    "These are fictional interpretations inspired by public-domain historical figures. "
    "Not official representations or endorsements. Use responsibly and adapt to your context."
)


class BoardConfig(BaseModel):
    """Complete Board of Directors configuration for an agent.

    When ``enabled`` is False (the default), the board has no effect on the
    agent's personality or system prompt.  Existing YAML files without a
    ``board`` key will default to this disabled state.
    """

    enabled: bool = False
    disclaimer: str = Field(
        default=_DEFAULT_DISCLAIMER,
        max_length=2000,
    )
    board_members: list[BoardMember] = Field(default_factory=list, max_length=20)
    engagement_rules: list[str] = Field(default_factory=list, max_length=20)
    notes: str | None = Field(None, max_length=2000)


# ---------------------------------------------------------------------------
# build_persona — quick YAML-to-prompt helper
# ---------------------------------------------------------------------------


def build_persona(yaml_file: str | Path) -> str:
    """Build a system prompt from a PersonaNexus YAML file.

    This is a convenience function that loads a YAML identity file and
    produces a basic system prompt string, including board context when
    the ``board`` section is enabled.

    For full-featured compilation (Anthropic XML, OpenClaw JSON, SOUL.md,
    etc.) use :class:`board_skill.compiler.SystemPromptCompiler` instead.
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

    # --- Board integration ---
    board: dict[str, Any] = persona.get("board", {})
    if board.get("enabled", False):
        disclaimer = board.get("disclaimer", _DEFAULT_DISCLAIMER)
        system_prompt += f"\n\n{disclaimer}"

        members = board.get("board_members", [])
        if members:
            system_prompt += "\n\nYou have access to a Board of Directors for advisory input:"
            for m in members:
                if isinstance(m, dict):
                    mname = m.get("name", "Unknown")
                    role = m.get("board_role", "Advisor")
                    mindset = m.get("core_mindset", "")
                    system_prompt += f"\n- {mname} ({role}): {mindset}"

        rules = board.get("engagement_rules", [])
        if rules:
            system_prompt += "\n\nBoard engagement rules:"
            for rule in rules:
                system_prompt += f"\n- {rule}"

    return system_prompt
