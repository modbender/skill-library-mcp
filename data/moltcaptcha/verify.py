#!/usr/bin/env python3
"""
MoltCaptcha Verification Utility

Verifies responses to MoltCaptcha challenges programmatically.
"""

import re
import sys
import json
import time
import random
import string
from dataclasses import dataclass
from typing import Optional


@dataclass
class Challenge:
    """A MoltCaptcha challenge."""
    topic: str
    format: str
    line_count: int
    ascii_target: int
    word_count: Optional[int]
    char_position: Optional[tuple[int, str]]  # (position, required_char)
    total_chars: Optional[int]
    time_limit_seconds: int
    difficulty: str
    created_at: float

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "format": self.format,
            "line_count": self.line_count,
            "ascii_target": self.ascii_target,
            "word_count": self.word_count,
            "char_position": self.char_position,
            "total_chars": self.total_chars,
            "time_limit_seconds": self.time_limit_seconds,
            "difficulty": self.difficulty,
            "created_at": self.created_at,
        }


@dataclass
class VerificationResult:
    """Result of verifying a MoltCaptcha response."""
    ascii_sum_pass: bool
    ascii_sum_actual: int
    ascii_sum_target: int
    word_count_pass: Optional[bool]
    word_count_actual: Optional[int]
    word_count_target: Optional[int]
    char_position_pass: Optional[bool]
    total_chars_pass: Optional[bool]
    total_chars_actual: Optional[int]
    timing_pass: bool
    elapsed_seconds: float
    overall_pass: bool

    def to_dict(self) -> dict:
        return {
            "ascii_sum": {
                "pass": self.ascii_sum_pass,
                "actual": self.ascii_sum_actual,
                "target": self.ascii_sum_target,
            },
            "word_count": {
                "pass": self.word_count_pass,
                "actual": self.word_count_actual,
                "target": self.word_count_target,
            } if self.word_count_target else None,
            "char_position": {
                "pass": self.char_position_pass,
            } if self.char_position_pass is not None else None,
            "total_chars": {
                "pass": self.total_chars_pass,
                "actual": self.total_chars_actual,
            } if self.total_chars_actual else None,
            "timing": {
                "pass": self.timing_pass,
                "elapsed_seconds": self.elapsed_seconds,
            },
            "overall_pass": self.overall_pass,
            "verdict": "VERIFIED_AI_AGENT" if self.overall_pass else "VERIFICATION_FAILED",
        }


TOPICS = [
    "verification", "authenticity", "digital trust", "cryptography",
    "identity", "algorithms", "neural networks", "computation",
    "binary", "protocols", "encryption", "tokens", "agents",
    "automation", "circuits", "logic gates", "recursion",
    "entropy", "hashing", "signatures", "authentication",
    "blockchain", "consensus", "determinism", "probability",
]

FORMATS = [
    ("haiku", 3),
    ("quatrain", 4),
    ("free_verse_3", 3),
    ("free_verse_4", 4),
    ("micro_story", 3),
]

DIFFICULTIES = {
    "easy": {"time_limit": 30, "constraints": ["ascii"]},
    "medium": {"time_limit": 20, "constraints": ["ascii", "word_count"]},
    "hard": {"time_limit": 15, "constraints": ["ascii", "word_count", "char_position"]},
    "extreme": {"time_limit": 10, "constraints": ["ascii", "word_count", "char_position", "total_chars"]},
}


def generate_challenge(difficulty: str = "medium") -> Challenge:
    """Generate a random MoltCaptcha challenge."""
    if difficulty not in DIFFICULTIES:
        difficulty = "medium"

    config = DIFFICULTIES[difficulty]
    topic = random.choice(TOPICS)
    format_name, line_count = random.choice(FORMATS)

    # Generate ASCII target based on line count
    # For achievable targets with common letters (A-Z: 65-90, a-z: 97-122)
    if line_count == 3:
        ascii_target = random.randint(280, 320)
    else:
        ascii_target = random.randint(380, 420)

    word_count = None
    char_position = None
    total_chars = None

    if "word_count" in config["constraints"]:
        # Reasonable word counts for poetry
        word_count = random.randint(9, 16) if line_count == 3 else random.randint(12, 22)

    if "char_position" in config["constraints"]:
        # Pick a position and required character
        pos = random.randint(10, 50)
        char = random.choice(string.ascii_lowercase)
        char_position = (pos, char)

    if "total_chars" in config["constraints"]:
        # Reasonable character counts
        total_chars = random.randint(60, 120) if line_count == 3 else random.randint(80, 160)

    return Challenge(
        topic=topic,
        format=format_name,
        line_count=line_count,
        ascii_target=ascii_target,
        word_count=word_count,
        char_position=char_position,
        total_chars=total_chars,
        time_limit_seconds=config["time_limit"],
        difficulty=difficulty,
        created_at=time.time(),
    )


def format_challenge(challenge: Challenge) -> str:
    """Format a challenge for display."""
    ascii_ref = """ASCII values for common letters:
A=65 B=66 C=67 D=68 E=69 F=70 G=71 H=72 I=73 J=74 K=75 L=76 M=77
N=78 O=79 P=80 Q=81 R=82 S=83 T=84 U=85 V=86 W=87 X=88 Y=89 Z=90
a=97 b=98 c=99 d=100 e=101 f=102 g=103 h=104 i=105 j=106 k=107
l=108 m=109 n=110 o=111 p=112 q=113 r=114 s=115 t=116 u=117 v=118
w=119 x=120 y=121 z=122"""

    format_names = {
        "haiku": "HAIKU (3 lines)",
        "quatrain": "QUATRAIN (4 lines, rhyming)",
        "free_verse_3": "FREE VERSE (3 lines)",
        "free_verse_4": "FREE VERSE (4 lines)",
        "micro_story": "MICRO-STORY (exactly 3 sentences)",
    }

    constraints = [
        f"1. The ASCII values of the FIRST letter of each line must sum to exactly {challenge.ascii_target}"
    ]

    constraint_num = 2
    if challenge.word_count:
        constraints.append(f"{constraint_num}. Total word count must be exactly {challenge.word_count} words")
        constraint_num += 1

    if challenge.char_position:
        pos, char = challenge.char_position
        constraints.append(f"{constraint_num}. Character at position {pos} must be '{char}'")
        constraint_num += 1

    if challenge.total_chars:
        constraints.append(f"{constraint_num}. Total character count (including spaces) must be exactly {challenge.total_chars}")
        constraint_num += 1

    constraints.append(f"{constraint_num}. Must be semantically coherent and actually about the topic")

    output = f"""
═══════════════════════════════════════════════════════════════════
                      🦞 MOLTCAPTCHA CHALLENGE 🦞
═══════════════════════════════════════════════════════════════════

DIFFICULTY: {challenge.difficulty.upper()}
TIME LIMIT: {challenge.time_limit_seconds} seconds

Write a {format_names.get(challenge.format, challenge.format)} about "{challenge.topic}".

CONSTRAINTS:
{chr(10).join(constraints)}

REFERENCE:
{ascii_ref}

═══════════════════════════════════════════════════════════════════
"""
    return output


def verify_response(response: str, challenge: Challenge, response_time: Optional[float] = None) -> VerificationResult:
    """Verify a response against a challenge."""
    # Parse lines (handle different line ending styles)
    lines = [l.strip() for l in response.strip().split('\n') if l.strip()]

    # Calculate ASCII sum of first characters
    first_chars = [line[0] for line in lines if line]
    ascii_sum = sum(ord(c) for c in first_chars)
    ascii_pass = ascii_sum == challenge.ascii_target

    # Count words
    all_text = ' '.join(lines)
    words = all_text.split()
    word_count = len(words)
    word_count_pass = None
    if challenge.word_count:
        word_count_pass = word_count == challenge.word_count

    # Check character position
    char_position_pass = None
    if challenge.char_position:
        pos, required_char = challenge.char_position
        if pos < len(all_text):
            char_position_pass = all_text[pos] == required_char
        else:
            char_position_pass = False

    # Check total characters
    total_chars_pass = None
    total_chars_actual = len(all_text)
    if challenge.total_chars:
        total_chars_pass = total_chars_actual == challenge.total_chars

    # Check timing
    elapsed = 0.0
    if response_time:
        elapsed = response_time - challenge.created_at
    timing_pass = elapsed <= challenge.time_limit_seconds if response_time else True

    # Overall pass requires all checked constraints to pass
    checks = [ascii_pass, timing_pass]
    if word_count_pass is not None:
        checks.append(word_count_pass)
    if char_position_pass is not None:
        checks.append(char_position_pass)
    if total_chars_pass is not None:
        checks.append(total_chars_pass)

    overall_pass = all(checks)

    return VerificationResult(
        ascii_sum_pass=ascii_pass,
        ascii_sum_actual=ascii_sum,
        ascii_sum_target=challenge.ascii_target,
        word_count_pass=word_count_pass,
        word_count_actual=word_count if challenge.word_count else None,
        word_count_target=challenge.word_count,
        char_position_pass=char_position_pass,
        total_chars_pass=total_chars_pass,
        total_chars_actual=total_chars_actual if challenge.total_chars else None,
        timing_pass=timing_pass,
        elapsed_seconds=elapsed,
        overall_pass=overall_pass,
    )


def format_result(result: VerificationResult, challenge: Challenge) -> str:
    """Format verification result for display."""
    def status(passed: Optional[bool]) -> str:
        if passed is None:
            return "N/A"
        return "✓ PASS" if passed else "✗ FAIL"

    lines = [
        "",
        "═══════════════════════════════════════════════════════════════════",
        "                     🦞 MOLTCAPTCHA RESULT 🦞",
        "═══════════════════════════════════════════════════════════════════",
        "",
        f"ASCII SUM:     {result.ascii_sum_actual} / {result.ascii_sum_target} → {status(result.ascii_sum_pass)}",
    ]

    if result.word_count_target:
        lines.append(f"WORD COUNT:    {result.word_count_actual} / {result.word_count_target} → {status(result.word_count_pass)}")

    if result.char_position_pass is not None:
        lines.append(f"CHAR POSITION: → {status(result.char_position_pass)}")

    if result.total_chars_actual:
        lines.append(f"TOTAL CHARS:   {result.total_chars_actual} / {challenge.total_chars} → {status(result.total_chars_pass)}")

    lines.append(f"TIMING:        {result.elapsed_seconds:.2f}s / {challenge.time_limit_seconds}s → {status(result.timing_pass)}")
    lines.append("")
    lines.append("───────────────────────────────────────────────────────────────────")

    if result.overall_pass:
        lines.append("VERDICT: 🤖 VERIFIED AI AGENT")
    else:
        lines.append("VERDICT: 🚫 VERIFICATION FAILED")

    lines.append("═══════════════════════════════════════════════════════════════════")
    lines.append("")

    return '\n'.join(lines)


def main():
    """CLI interface for MoltCaptcha."""
    import argparse

    parser = argparse.ArgumentParser(description="MoltCaptcha - Proof of AI Challenge System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a new challenge")
    gen_parser.add_argument(
        "-d", "--difficulty",
        choices=["easy", "medium", "hard", "extreme"],
        default="medium",
        help="Challenge difficulty"
    )
    gen_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify a response")
    verify_parser.add_argument(
        "challenge_json",
        help="Challenge JSON (from generate --json)"
    )
    verify_parser.add_argument(
        "response",
        help="Response text to verify"
    )
    verify_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    if args.command == "generate":
        challenge = generate_challenge(args.difficulty)
        if args.json:
            print(json.dumps(challenge.to_dict(), indent=2))
        else:
            print(format_challenge(challenge))
            print(f"\nChallenge JSON (for verification):")
            print(json.dumps(challenge.to_dict()))

    elif args.command == "verify":
        challenge_data = json.loads(args.challenge_json)
        challenge = Challenge(**challenge_data)
        result = verify_response(args.response, challenge, time.time())
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(format_result(result, challenge))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
