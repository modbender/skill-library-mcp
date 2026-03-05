# Self-Review Skill

Automatically review agent output quality before sending to user.

- Checks: clarity, conciseness, actionability, structure
- Simple rule-based engine (no API cost)
- Exit code 0 = approved, 1 = needs improvement

## Usage

Pipe output to reviewer:

```bash
echo "Your response text" | node skills/self-review/index.js
```

Or integrate into agent pipeline (AGENTS.md step 6).

## Configuration

Edit `skills/self-review/index.js` to adjust thresholds.

## Advanced

For LLM-based review, see `self-review-llm` skill (separate package).

---

Author: dvinci达芬奇 (self-evolved)
Version: 1.0.0
Tags: quality, automation, token-optimization
