---
name: ai-writing-humanizer
description: Automatically strip AI writing patterns and stock phrases from user-facing prose before sending. Use when preparing longer texts to ensure a natural, human tone without obvious AI tells.
---

# AI Writing Humanizer

Provide a cleaned, human-sounding version of input text by removing or rewriting common AI-generated writing patterns. Load this skill automatically for any user-facing prose longer than ~150 words.

## Patterns Covered

- Overuse of hedging phrases: "At the end of the day", "It's worth noting", "It is important to remember"
- Stock transitions and signposts: "First", "Secondly", "Finally"
- Structural markers: em dashes (—), parentheses for side notes, bullet-like serial lists
- Predictable rule-of-three constructs: "X, Y, and Z" used as checklist language
- Passive voice sections flagged by "was", "were", "has been"
- Performed authenticity cues: "I hope this helps", "Let me know if you have any questions"

## Usage

1. Pass input text to `scripts/humanize.py --input text.txt --output cleaned.txt`.
2. For integrations, import `humanize_text()` from the script and apply before sending.

## Bundled Resources

- scripts/humanize.py — Python script implementing regex-based pattern removal and light rewriting
- references/signs-of-ai-writing.md — List of AI writing signs based on Wikipedia
- tests/test_humanizer.py — Regression tests to detect patterns
