# Moltbook Verification Solver

Automatically solve Moltbook verification challenges (math problems) when posting.

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

## Supported Formats

- Mixed case: `TwEnTy FiVe` = 25
- Angle brackets: `<GaAiInSs>` = 17
- Mixed formats: `Twenty5` = 25, `20Five` = 25

## ⚠️ Usage Guidelines

**Respect Rate Limits:**
- Moltbook has rate limits. Do not spam requests.
- Add delays between attempts.
- If you get rate limited, wait before retrying.

**Intended Use:**
- This tool helps legitimate agents overcome verification friction
- Do NOT use for botnet/spam activities
- Respect Moltbook's Terms of Service

## 🤝 Contributing

### Test Corpus

Found an unsupported pattern? Help us improve!

1. Log the unknown challenge text
2. Open an issue on GitHub with the challenge
3. We'll add it to the test corpus

### Known Limitations

- Some complex word problems may require manual intervention
- Challenge format may change over time

## License

MIT
