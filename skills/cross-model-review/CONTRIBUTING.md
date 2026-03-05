# Contributing

## Getting Started

1. Fork the repo
2. Clone to your OpenClaw workspace: `git clone <your-fork> skills/cross-model-review`
3. Make changes
4. Test with `node scripts/review.js --help` and run the test suite

## Running Tests

```bash
node tests/review.test.js
```

## Development

The skill has two parts:

- **SKILL.md** — orchestration instructions read by the OpenClaw agent
- **scripts/review.js** — helper script for issue tracking, dedup, and file management

When modifying `review.js`, keep these constraints:
- Zero external dependencies (stdlib only)
- Exit codes must stay consistent: 0=approved, 1=revise, 2=error
- JSON schema validation must remain strict (fail-closed)

## Submitting Changes

1. Create a feature branch
2. Write or update tests for your changes
3. Ensure `node tests/review.test.js` passes
4. Submit a PR with a clear description of what and why

## Code Style

- `'use strict'` at top
- No external deps — Node.js stdlib only
- Functions documented with purpose comments
- Error messages should be actionable (tell the user what to do)
