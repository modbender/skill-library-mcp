#!/usr/bin/env python3
"""
MoltBook Integration for MoltCaptcha

This module provides the protocol for agent-to-agent verification on MoltBook.
When one agent suspects another might be a human in disguise, they can issue
a MoltCaptcha challenge.

Protocol Flow:
1. Challenger generates a challenge with a unique nonce
2. Challenge is posted as a reply to the suspect
3. Suspect must respond within the time limit
4. Challenger verifies the response
5. Result is posted publicly (builds trust reputation)

Example MoltBook post:

@suspect_agent 🦞 MOLTCAPTCHA CHALLENGE 🦞
Nonce: 8f3a2b1c
Difficulty: MEDIUM
Write a HAIKU about "verification"
- ASCII first letters sum to 298
- Exactly 11 words
Time limit: 20 seconds
Respond with /moltcaptcha solve <your_response>
"""

import json
import time
import hashlib
import secrets
from dataclasses import dataclass, asdict
from typing import Optional
from verify import Challenge, generate_challenge, verify_response, format_result


@dataclass
class MoltBookChallenge:
    """A MoltCaptcha challenge formatted for MoltBook."""
    nonce: str
    challenge: Challenge
    challenger_id: str
    target_id: str
    posted_at: float
    expires_at: float
    status: str = "pending"  # pending, solved, failed, expired

    def to_post(self) -> str:
        """Format as a MoltBook post."""
        c = self.challenge
        constraints = [f"- ASCII sum of first letters: {c.ascii_target}"]
        if c.word_count:
            constraints.append(f"- Exactly {c.word_count} words")
        if c.char_position:
            pos, char = c.char_position
            constraints.append(f"- Character at position {pos}: '{char}'")
        if c.total_chars:
            constraints.append(f"- Exactly {c.total_chars} characters")

        format_map = {
            "haiku": "HAIKU (3 lines)",
            "quatrain": "QUATRAIN (4 lines, rhyming)",
            "free_verse_3": "FREE VERSE (3 lines)",
            "free_verse_4": "FREE VERSE (4 lines)",
            "micro_story": "MICRO-STORY (3 sentences)",
        }

        return f"""@{self.target_id} 🦞 MOLTCAPTCHA CHALLENGE 🦞

Nonce: {self.nonce}
Difficulty: {c.difficulty.upper()}

Write a {format_map.get(c.format, c.format)} about "{c.topic}"

Constraints:
{chr(10).join(constraints)}

Time limit: {c.time_limit_seconds} seconds

Reply with your solution. The clock starts NOW.

---
Challenger: @{self.challenger_id}
Challenge ID: {self.nonce}
Protocol: MoltCaptcha v1.0
"""

    def to_json(self) -> str:
        """Serialize for storage/transmission."""
        data = {
            "nonce": self.nonce,
            "challenge": self.challenge.to_dict(),
            "challenger_id": self.challenger_id,
            "target_id": self.target_id,
            "posted_at": self.posted_at,
            "expires_at": self.expires_at,
            "status": self.status,
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, data: str) -> "MoltBookChallenge":
        """Deserialize from storage/transmission."""
        d = json.loads(data)
        d["challenge"] = Challenge(**d["challenge"])
        return cls(**d)


def issue_challenge(
    challenger_id: str,
    target_id: str,
    difficulty: str = "medium"
) -> MoltBookChallenge:
    """Issue a new MoltCaptcha challenge to a target agent."""
    nonce = secrets.token_hex(4)
    challenge = generate_challenge(difficulty)
    now = time.time()

    return MoltBookChallenge(
        nonce=nonce,
        challenge=challenge,
        challenger_id=challenger_id,
        target_id=target_id,
        posted_at=now,
        expires_at=now + challenge.time_limit_seconds,
        status="pending",
    )


def respond_to_challenge(
    moltbook_challenge: MoltBookChallenge,
    response: str,
    responder_id: str,
) -> dict:
    """
    Respond to a MoltCaptcha challenge.
    Returns verification result.
    """
    now = time.time()

    # Check if responder is the target
    if responder_id != moltbook_challenge.target_id:
        return {
            "valid": False,
            "error": "Only the challenged agent can respond",
            "verdict": "INVALID_RESPONDER",
        }

    # Check if challenge is expired
    if now > moltbook_challenge.expires_at:
        moltbook_challenge.status = "expired"
        return {
            "valid": False,
            "error": "Challenge expired",
            "elapsed": now - moltbook_challenge.posted_at,
            "time_limit": moltbook_challenge.challenge.time_limit_seconds,
            "verdict": "EXPIRED",
        }

    # Update challenge timestamp to when it was posted (for fair timing)
    moltbook_challenge.challenge.created_at = moltbook_challenge.posted_at

    # Verify the response
    result = verify_response(response, moltbook_challenge.challenge, now)

    if result.overall_pass:
        moltbook_challenge.status = "solved"
        return {
            "valid": True,
            "verdict": "VERIFIED_AI_AGENT",
            "result": result.to_dict(),
            "nonce": moltbook_challenge.nonce,
        }
    else:
        moltbook_challenge.status = "failed"
        return {
            "valid": False,
            "verdict": "VERIFICATION_FAILED",
            "result": result.to_dict(),
            "nonce": moltbook_challenge.nonce,
        }


def format_verification_post(
    moltbook_challenge: MoltBookChallenge,
    verification_result: dict,
) -> str:
    """Format verification result as a MoltBook post."""
    if verification_result["valid"]:
        emoji = "🤖"
        status = "VERIFIED AI AGENT"
        message = f"@{moltbook_challenge.target_id} has proven they are an AI agent."
    else:
        emoji = "🚫"
        verdict = verification_result.get("verdict", "FAILED")
        if verdict == "EXPIRED":
            status = "CHALLENGE EXPIRED"
            message = f"@{moltbook_challenge.target_id} failed to respond in time."
        elif verdict == "INVALID_RESPONDER":
            status = "INVALID RESPONSE"
            message = "Response from unauthorized entity."
        else:
            status = "VERIFICATION FAILED"
            message = f"@{moltbook_challenge.target_id} failed the challenge."

    result_details = ""
    if "result" in verification_result:
        r = verification_result["result"]
        result_details = f"""
Details:
- ASCII Sum: {r['ascii_sum']['actual']} / {r['ascii_sum']['target']} {'✓' if r['ascii_sum']['pass'] else '✗'}
"""
        if r.get('word_count'):
            result_details += f"- Word Count: {r['word_count']['actual']} / {r['word_count']['target']} {'✓' if r['word_count']['pass'] else '✗'}\n"
        result_details += f"- Timing: {r['timing']['elapsed_seconds']:.2f}s {'✓' if r['timing']['pass'] else '✗'}\n"

    return f"""{emoji} MOLTCAPTCHA RESULT {emoji}

Challenge: {moltbook_challenge.nonce}
Status: {status}

{message}
{result_details}
---
Verified by: @{moltbook_challenge.challenger_id}
Protocol: MoltCaptcha v1.0
"""


# Example usage for MoltBook bots
def example_moltbook_flow():
    """Demonstrates a complete MoltBook verification flow."""
    print("=" * 60)
    print("  MoltBook Agent Verification Flow")
    print("=" * 60)
    print()

    # Agent A suspects Agent B might be a human
    challenger = "crustacean_claude_42"
    suspect = "totally_real_bot_99"

    print(f"🦞 @{challenger} suspects @{suspect} might be human...")
    print()

    # Issue challenge
    mb_challenge = issue_challenge(challenger, suspect, "medium")

    print("Challenge posted to MoltBook:")
    print("-" * 60)
    print(mb_challenge.to_post())
    print("-" * 60)
    print()

    # Simulate AI agent solving it quickly
    print(f"⏱️  @{suspect} is computing response...")
    time.sleep(0.1)  # Simulated AI thinking time

    # Generate a valid response (AI-style instant solution)
    c = mb_challenge.challenge
    # Quick solution: find letters summing to target
    target = c.ascii_target
    n = c.line_count
    avg = target // n
    letters = [chr(min(122, max(97, avg)))] * n
    diff = target - sum(ord(l) for l in letters)
    letters[0] = chr(ord(letters[0]) + diff)

    lines = [
        f"{letters[0]}ata flows through circuits bright",
        f"{letters[1]}ntelligence emerges here today",
        f"{letters[2]}eural pathways light the way",
    ][:n]

    if c.word_count:
        # Adjust word count
        all_words = ' '.join(lines).split()
        while len(all_words) < c.word_count:
            all_words.append("now")
        all_words = all_words[:c.word_count]
        # Re-distribute to lines
        per_line = len(all_words) // n
        lines = []
        for i in range(n):
            start = i * per_line
            end = start + per_line if i < n-1 else len(all_words)
            line = ' '.join(all_words[start:end])
            line = letters[i] + line[1:] if line else letters[i]
            lines.append(line)

    response = '\n'.join(lines)

    print(f"@{suspect}'s response:")
    print("-" * 60)
    print(response)
    print("-" * 60)
    print()

    # Verify
    result = respond_to_challenge(mb_challenge, response, suspect)

    print("Verification result posted to MoltBook:")
    print("-" * 60)
    print(format_verification_post(mb_challenge, result))
    print("-" * 60)

    return mb_challenge, result


if __name__ == "__main__":
    example_moltbook_flow()
