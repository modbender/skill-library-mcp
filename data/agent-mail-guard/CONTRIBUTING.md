# Contributing to AgentMailGuard

Thanks for your interest in making AI agents safer. Here's how to contribute.

## Quick Start

```bash
git clone https://github.com/DiscoDaddy/agent-mail-guard.git
cd agent-mail-guard
python3 -m pytest -v  # run tests first
```

Zero dependencies — Python 3.11+ stdlib only. Keep it that way.

## Adding New Features

### New injection patterns
1. Add the pattern/regex to `sanitize_core.py`
2. Add tests in `test_sanitizer.py` proving detection works
3. Update the attack vectors table in `README.md`

### New sanitization functions
1. Add to `sanitize_core.py` with a clear docstring
2. Wire into the pipeline in `sanitize_text()` (order matters — see the pipeline comment)
3. Add a flag string for detection
4. Tests are mandatory — no PR merges without them

### Calendar-specific changes
- `cal_sanitizer.py` for calendar event processing
- `test_cal_sanitizer.py` for calendar tests

## Rules

- **Zero dependencies.** Don't add pip packages. Stdlib only.
- **Every feature needs tests.** No exceptions.
- **All 98+ tests must pass** before submitting a PR.
- **Security-focused PRs get priority** — new bypass vectors, edge cases, hardening.
- **Keep it lean.** This is a sanitizer, not a framework. If it doesn't strip, detect, or classify, it probably doesn't belong here.

## Running Tests

```bash
# Full suite
python3 -m pytest -v

# Email tests only
python3 -m pytest test_sanitizer.py -v

# Calendar tests only
python3 -m pytest test_cal_sanitizer.py -v

# Single test
python3 -m pytest test_sanitizer.py -k "test_homoglyph" -v
```

## PR Process

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-pattern`)
3. Make your changes + add tests
4. Run the full test suite
5. Submit a PR with a clear description of what you added and why

## Ideas Welcome

Open an issue if you've found a bypass vector, have a feature idea, or want to discuss architecture. Even if you don't have code, vulnerability reports are valuable.

## Code of Conduct

Be helpful. Be constructive. We're all trying to make AI agents less exploitable.
