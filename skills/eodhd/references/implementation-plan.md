# EODHD Bash CLI Implementation Plan

## Goal

Deliver an open source Bash CLI and Codex skill for the public EODHD API, designed for OpenClaw agents, GitHub-hosted development, and Clawhub.ai distribution. The implementation must be stateless, secrets-safe, and easy for agents to invoke deterministically.

## Non-Goals

- No local credential store
- No user profile or host-specific config files
- No caching or background services
- No dependency on personal data, private datasets, or local artifacts
- No undocumented EODHD behavior baked into the contract

## Core Contract

- Binary name: `eodhd`
- Runtime dependencies: Bash and `curl`
- Default output: JSON to stdout
- Diagnostics: stderr
- Auth source: `EODHD_API_KEY` by default
- Secret safety: redact token values in all human-readable output paths

## Milestones

### Milestone 0: Contract and repository skeleton

Deliverables:
- `SKILL.md`
- `agents/openai.yaml`
- `.gitignore`
- initial `references/` docs

Acceptance criteria:
- The repo clearly states stateless behavior.
- The repo contains no plaintext secrets or local-machine assumptions.
- The skill description is specific enough to trigger for OpenClaw EODHD wrapper work.

### Milestone 1: CLI skeleton

Deliverables:
- `scripts/eodhd`
- `--help`
- `--version`
- base parser for global flags

Acceptance criteria:
- Running the script with no args prints usage and exits non-zero.
- Running with `--help` exits zero.
- Global flags parse before subcommand dispatch.

### Milestone 2: HTTP and auth foundation

Deliverables:
- `require_api_key`
- `build_url`
- `perform_request`
- `redact_sensitive_text`

Acceptance criteria:
- `EODHD_API_KEY` is required unless an explicit override is provided.
- Query strings are encoded safely enough for documented parameters.
- Any token in logs, dry-run output, or traces is replaced with `***REDACTED***`.
- HTTP failures produce a consistent stderr shape.

### Milestone 3: MVP commands

Deliverables:
- `eod SYMBOL`
- `fundamentals SYMBOL`
- `real-time SYMBOL`
- `search QUERY`
- `exchanges`
- `raw PATH`

Acceptance criteria:
- Each command maps directly to a documented EODHD endpoint.
- `raw PATH` can reach newly added endpoints without code changes.
- Shared flags such as `--from`, `--to`, `--fmt`, and `--query key=value` work consistently.

### Milestone 4: Security sanity and observability

Deliverables:
- `--dry-run`
- `--verbose`
- sanitized error and request tracing
- redaction tests

Acceptance criteria:
- No raw token appears in stdout, stderr, or test fixtures.
- `--dry-run` shows the effective request shape without disclosing the token.
- Verbose mode remains safe if copied into issue reports or CI logs.

### Milestone 5: Tests and CI

Deliverables:
- `shellcheck` config or CI invocation
- `shfmt` config or CI invocation
- smoke tests for parser, URL generation, and redaction
- GitHub Actions workflow

Acceptance criteria:
- CI passes on a clean checkout.
- Smoke tests do not require a real EODHD token.
- Linting fails on unsafe shell patterns or malformed scripts.

### Milestone 6: Distribution hardening

Deliverables:
- final skill metadata
- example prompts
- versioning strategy
- release notes template or tag-based release workflow

Acceptance criteria:
- The repo is publishable to Clawhub.ai without embedding user secrets.
- Version tags correspond to skill and CLI behavior changes.
- Public examples use placeholders or documented demo values only.

## Security Requirements

### Secret handling

- Prefer OpenClaw secret injection into `EODHD_API_KEY`.
- Treat `api_token` as sensitive wherever it appears.
- Never echo the token in help text, examples, traces, or failure messages.
- Avoid shell constructs that leak arguments through xtrace or process listings when alternatives exist.

### Logging and output

- Redact exact token matches and obvious `api_token=...` patterns.
- Sanitize copied curl commands before printing them.
- Keep verbose logs off by default.
- Do not serialize environment dumps in CI failures.

### Repo hygiene

- Add `.env`, `*.local`, temp files, and coverage artifacts to `.gitignore`.
- Do not commit captured API responses if they contain account-specific details.
- Use placeholder symbols and placeholder secrets in docs and tests.

## Suggested exit semantics

- `0`: success
- `2`: usage or argument error
- `3`: missing auth
- `4`: transport or HTTP failure
- `5`: response parse or normalization failure

Keep this stable once published so agents can reason about failures.

## Test matrix

- No args
- `--help`
- missing `EODHD_API_KEY`
- masked `--dry-run`
- command-to-endpoint mapping
- repeated `--query key=value`
- invalid subcommand
- HTTP 401 and 404 handling

## Recommended implementation order

1. Create the repo skeleton and skill metadata.
2. Implement the parser and common helpers.
3. Add redaction before adding verbose or dry-run features.
4. Ship the MVP commands.
5. Add CI and smoke tests.
6. Expand the command surface only after the contract is stable.
