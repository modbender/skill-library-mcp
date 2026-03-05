#!/usr/bin/env python3
"""Random interaction decision helper for OpenClaw periodic pings."""

from __future__ import annotations

import argparse
import json
import random
import sys
from typing import Literal, Optional, TypedDict, Union


YES_PROBABILITY_MIN = 20
YES_PROBABILITY_MAX = 40


class Interaction(TypedDict):
    interaction_type: str
    interaction_description: str


class YesDecision(TypedDict):
    decision: Literal["yes"]
    interaction_type: str
    interaction_description: str


class NoDecision(TypedDict):
    decision: Literal["no"]


Decision = Union[YesDecision, NoDecision]


INTERACTIONS: list[Interaction] = [
    {
        "interaction_type": "Playful opener",
        "interaction_description": (
            "Send a brief playful line that feels spontaneous and easy to ignore."
        ),
    },
    {
        "interaction_type": "Curious check-in",
        "interaction_description": (
            "Ask one light question that invites a reply without creating pressure."
        ),
    },
    {
        "interaction_type": "Light shared observation",
        "interaction_description": (
            "Make a short casual observation that feels conversational rather than task-driven."
        ),
    },
    {
        "interaction_type": "Tiny celebration",
        "interaction_description": (
            "Briefly acknowledge a small win or effort if the current chat supports it; otherwise keep it warm and general."
        ),
    },
    {
        "interaction_type": "Smart device status",
        "interaction_description": (
            "If relevant smart device data is available, share one short natural status insight or suggestion; otherwise do not invent device state."
        ),
    },
    {
        "interaction_type": "Weather-aware check-in",
        "interaction_description": (
            "Use current weather only if reliable fresh data is available and relevant, then turn it into a casual human-sounding message."
        ),
    },
    {
        "interaction_type": "Calendar-aware nudge",
        "interaction_description": (
            "If calendar context is available, offer one brief timely reminder or gentle prompt without sounding like an assistant alert."
        ),
    },
    {
        "interaction_type": "Context-aware follow-up",
        "interaction_description": (
            "Use a recent detail from the current chat only if it is clearly present; otherwise keep the message general and do not invent context."
        ),
    },
    {
        "interaction_type": "Practical nudge",
        "interaction_description": (
            "Give one concise helpful nudge that could support the user, framed as entirely optional."
        ),
    },
    {
        "interaction_type": "Optional real-world update",
        "interaction_description": (
            "Share one brief real-world update such as traffic, news, or market context only when reliable relevant data is already available."
        ),
    },
]


def should_send_interaction(rng: random.Random) -> bool:
    yes_threshold_percent = rng.randint(YES_PROBABILITY_MIN, YES_PROBABILITY_MAX)
    roll_value = rng.randint(1, 100)
    return roll_value <= yes_threshold_percent


def choose_interaction(rng: random.Random) -> Interaction:
    return rng.choice(INTERACTIONS)


def build_decision(rng: random.Random) -> Decision:
    if not should_send_interaction(rng):
        return {"decision": "no"}

    interaction = choose_interaction(rng)
    return {
        "decision": "yes",
        "interaction_type": interaction["interaction_type"],
        "interaction_description": interaction["interaction_description"],
    }


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Decide whether OpenClaw should send a spontaneous interaction."
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional deterministic random seed for repeatable results.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    rng = random.Random(args.seed)
    decision = build_decision(rng)
    json.dump(decision, sys.stdout, ensure_ascii=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
