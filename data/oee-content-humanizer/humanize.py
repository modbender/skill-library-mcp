#!/usr/bin/env python3
"""AI Content Humanizer — strips the robot out of your writing. 🐾"""

import argparse
import json
import os
import sys
import urllib.request

# ── AI tell-words (the usual suspects) ──────────────────────────────
AI_TELLS = [
    "delve", "landscape", "leverage", "it's important to note",
    "in conclusion", "game-changing", "revolutionary", "transformative",
    "tapestry", "vibrant", "bustling", "realm", "crucial", "pivotal",
    "unleash", "harness", "robust", "seamless", "cutting-edge",
    "navigate", "foster", "utilize", "facilitate", "comprehensive",
    "moreover", "furthermore", "nevertheless", "it's worth noting",
    "in today's world", "at the end of the day", "moving forward",
]

CHANNEL_GUIDES = {
    "twitter": (
        "Rewrite for Twitter/X. Max 280 characters. Punchy, direct, no fluff. "
        "Use fragments. Sound like a real person tweeting, not a brand account."
    ),
    "linkedin": (
        "Rewrite for LinkedIn. Professional but conversational — like talking to "
        "a smart colleague over coffee. Okay to use 'I'. No corporate buzzword bingo."
    ),
    "blog": (
        "Rewrite for a blog post. Longer form is fine. Vary paragraph length. "
        "Personal voice welcome — anecdotes, opinions, the occasional aside. "
        "Read it aloud; if it sounds like a textbook, try again."
    ),
    "email": (
        "Rewrite for email. Brief, clear, action-oriented. Front-load the point. "
        "Conversational but respectful. No walls of text."
    ),
    "telegram": (
        "Rewrite for Telegram. Casual, concise. Like texting a friend who's smart. "
        "Contractions, fragments, lowercase okay. Skip the formalities."
    ),
    "general": (
        "Rewrite for general use. Natural, human-sounding prose. Varies sentence "
        "length. Uses contractions. Doesn't over-explain."
    ),
}


def detect_ai_tells(text: str) -> list[str]:
    """Find AI-typical words/phrases in the text."""
    lower = text.lower()
    return [t for t in AI_TELLS if t in lower]


def build_prompt(text: str, channel: str, tells: list[str]) -> str:
    """Construct the rewrite prompt."""  # 🐾
    channel_guide = CHANNEL_GUIDES.get(channel, CHANNEL_GUIDES["general"])
    tells_note = ""
    if tells:
        tells_note = (
            f"\n\nDetected AI tells to eliminate: {', '.join(tells)}. "
            "Replace these with concrete, specific language."
        )

    return f"""You are a human editor. Your job: take AI-generated text and make it sound like a real person wrote it.

Rules:
- Kill vague qualifiers. Be specific or cut them.
- Vary sentence length. Mix short punchy sentences with longer flowing ones.
- Use contractions (it's, don't, we're) where natural.
- Fragments are fine. So are one-word sentences. Really.
- Remove filler that doesn't carry meaning.
- Keep the core message intact — don't invent new claims.
- Add natural rhythm imperfections — humans don't write in perfect parallel structure.
- No meta-commentary. Don't say "here's the rewritten version". Just output the text.
{tells_note}

Channel guidance: {channel_guide}

TEXT TO HUMANIZE:
---
{text}
---

Output ONLY the rewritten text. Nothing else."""


def call_claude(prompt: str) -> str:
    """Call Claude API directly via urllib (no deps beyond stdlib)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set in environment.", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({
        "model": "claude-haiku-4-20250414",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"API error ({e.code}): {body}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Humanize AI-generated text. 🐾",
        epilog="Pipe text in or pass as argument. Exits with human words.",
    )
    parser.add_argument("text", nargs="?", help="Text to humanize (or pipe via stdin)")
    parser.add_argument(
        "--channel", "-c",
        choices=list(CHANNEL_GUIDES.keys()),
        default="general",
        help="Target channel/platform (default: general)",
    )
    parser.add_argument(
        "--detect-only", "-d",
        action="store_true",
        help="Only detect AI tells, don't rewrite",
    )
    args = parser.parse_args()

    # Get text from arg or stdin
    if args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print("Error: provide text as argument or pipe via stdin.", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("Error: empty text.", file=sys.stderr)
        sys.exit(1)

    # Detection
    tells = detect_ai_tells(text)

    if args.detect_only:
        if tells:
            print(f"Found {len(tells)} AI tell(s): {', '.join(tells)}")
        else:
            print("No obvious AI tells detected. (Doesn't mean it's human though.)")
        sys.exit(0)

    # Show detection info on stderr so stdout stays clean  # 🐾
    if tells:
        print(f"🔍 Detected {len(tells)} AI tell(s): {', '.join(tells)}", file=sys.stderr)
    else:
        print("🔍 No keyword tells found — rewriting for style anyway.", file=sys.stderr)

    # Rewrite
    prompt = build_prompt(text, args.channel, tells)
    result = call_claude(prompt)
    print(result)


if __name__ == "__main__":
    main()  # 🐾
