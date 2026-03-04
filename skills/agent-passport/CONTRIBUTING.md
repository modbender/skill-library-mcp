# Contributing to Agent Passport

Thanks for taking the time to contribute. Agent Passport is a small, focused skill and we want to keep it that way. Good contributions make it more useful without making it more complicated.

## Before You Start

- Check [open issues](https://github.com/agentpassportai/agent-passport/issues) to avoid duplicates
- For significant changes, open an issue first so we can discuss the approach
- Small fixes and typos can go straight to a PR

## What We Welcome

- Bug fixes with a clear description of the problem and fix
- New mandate types with tests and documentation
- Improvements to the audit trail or ledger format
- Documentation improvements
- Performance fixes in the mandate-ledger script

## What to Avoid

- Large refactors without prior discussion
- Features that require external dependencies (zero-dep is a design goal)
- Breaking changes to the mandate schema without a migration path

## Setup

```bash
git clone https://github.com/agentpassportai/agent-passport.git
cd agent-passport
```

The skill runs on bash with no package manager. Prerequisites: `jq`, `bc`, `xxd`, `head`, `date`, `mkdir`. All standard on Linux and macOS.

To test the mandate ledger locally:

```bash
export AGENT_PASSPORT_LEDGER_DIR=/tmp/test-ledger
bash scripts/mandate-ledger.sh --help
```

## Making Changes

1. Fork the repo and create a branch: `git checkout -b fix/your-fix-name`
2. Make your changes
3. Test manually against a local ledger
4. Commit with a clear message (see below)
5. Open a PR against `main`

## Commit Messages

Keep them short and specific:

```
fix: handle missing ledger dir on first run
feat: add TTL expiry to mandate schema
docs: clarify KYA metadata fields
```

Format: `type: description` where type is `fix`, `feat`, `docs`, `test`, or `refactor`.

## PR Guidelines

- One change per PR
- Describe what the PR does and why
- If it fixes a bug, link the issue
- If it changes the mandate schema, document the before/after

## Schema Compatibility

Agent Passport mandates are stored in JSON. Any change to the schema must be backward compatible or include a migration note. Do not break existing ledger files.

## Code Style

The mandate-ledger script uses `bash` with `set -euo pipefail`. Keep it that way. Avoid external commands not in the prerequisites list.

## Versioning

We follow `vMAJOR.MINOR.PATCH`:
- PATCH: bug fixes, no behavior change
- MINOR: new features, backward compatible
- MAJOR: breaking changes (rare, discuss first)

## Questions

Open an issue with the `question` label. We respond to most things within a few days.
