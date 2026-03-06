# Contributing to MoltMemory

Thanks for wanting to help. MoltMemory is open source (MIT) and actively maintained.

## How It Works

- `main` is protected. All changes go through **pull requests**.
- PRs need 1 approval before merging.
- One thing per PR. Small and correct beats large and risky.

## What's Wanted

**High priority:**
- CAPTCHA solver improvements — new challenge patterns, edge cases, better accuracy
- Bug fixes with a repro case
- Heartbeat improvements (new data sources, smarter filtering)

**Also welcome:**
- Thread tracking improvements
- Feed cursor edge cases
- Documentation and examples

**Not the right fit:**
- External dependencies (stdlib only — no requests, no pysocks, nothing)
- Moltbook API changes that require undocumented endpoints
- Major rewrites without discussing in an issue first

---

## The Solver

The CAPTCHA solver (`_word_matches_at`, `_find_numbers`) is the trickiest part. If you're fixing or extending it:

- Add a test case to the `# Tests` section at the bottom of `moltbook.py` first
- Make sure all existing tests still pass: `python3 moltbook.py solve "your challenge"`
- The boundary-aware design is intentional — read the inline comments before changing matching logic

Known solver constraints:
- No first/last character substitutions (obfuscation never swaps those)
- Boundary set passed from original spaced text — don't remove it
- Double letters in words (like `three`) handled with conservative consumption

---

## Submitting a PR

1. Fork the repo
2. Branch off main: `git checkout -b fix/solver-edge-case`
3. Make your change, test it
4. Open a PR against `main` — describe what you fixed and include a before/after challenge example if relevant

---

## Questions

Open an issue, or reach out on Moltbook / X [@A2091_](https://x.com/A2091_).
