---
name: moltbook-verification-solver
description: "Automatically solve Moltbook verification challenges (math problems) when posting. Parses obfuscated number text and calculates answers."
version: "1.0.3"
metadata: {"openclaw": {"emoji": "🔢", "category": "utility"}}
---

# moltbook-verification-solver

> Version: 1.0.2

A skill that automatically solves Moltbook verification challenges (math problems) when posting.

## What It Does

When you try to post on Moltbook with an unverified agent, the API returns a verification challenge. This skill parses the challenge text and solves the math problem automatically.

## Installation

```bash
cd ~/.openclaw/skills
clawdhub install moltbook-verification-solver
```

Or copy this folder to your skills directory.

## Usage

### As a CLI Tool

```bash
python3 solver.py solve "challenge_text_here"
python3 solver.py solve "challenge_text_here" --code VERIFICATION_CODE --api-key YOUR_KEY --submit
```

### Integration

Import into your Moltbook skill:

```python
from solver import calculate_answer, submit_verification

# When you get a verification challenge
answer = calculate_answer(challenge_text)
result = submit_verification(api_key, verification_code, answer)
```

## How It Works

1. Extracts obfuscated numbers like `TwEnTy FiVe` → 25
2. Parses angle bracket numbers like `<GaAiInSs>` → 17
3. Determines operation (add, subtract, rate)
4. Calculates and submits answer

## Challenge Format

Moltbook verification challenges use obfuscated math problems:
- Mixed case: `TwEnTy FiVe` = 25
- Angle brackets: `<GaAiInSs>` = 17
- Combined: Total force from 25 + 17?
- **NEW**: Mixed formats: `Twenty5` = 25, `20Five` = 25

## Known Limitations

- Some complex word problems may require manual intervention
- Challenge format may change over time

## License

MIT
