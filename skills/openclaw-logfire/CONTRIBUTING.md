# Contributing to @ultrathink/openclaw-logfire

Thanks for your interest in contributing! This guide covers how to set up, develop, test, and submit changes.

## Prerequisites

- **Node.js** >= 20
- **npm** (ships with Node.js)
- **Git** with GPG signing configured

## Setup

```bash
git clone https://github.com/Ultrathink-Solutions/openclaw-logfire
cd openclaw-logfire
npm install
```

Verify everything works:

```bash
npm run typecheck   # TypeScript strict mode
npm run lint        # ESLint 9 flat config
npm test            # Vitest
```

## Project Structure

```text
src/
  index.ts                  Plugin entry point — hook wiring and lifecycle
  config.ts                 Typed configuration with env var fallbacks
  otel.ts                   OTEL SDK initialization (Logfire OTLP HTTP)
  util.ts                   JSON serialization, truncation, secret redaction
  trace-link.ts             Logfire trace URL builder
  hooks/
    before-agent-start.ts   Root invoke_agent span creation
    before-tool-call.ts     Child execute_tool span + context propagation
    tool-result-persist.ts  Tool span close + error recording
    agent-end.ts            Agent span close + metrics emission
    message-received.ts     Channel attribution enrichment
  context/
    span-store.ts           Session -> active spans (LIFO tool stack)
    propagation.ts          W3C traceparent inject/extract
  metrics/
    genai-metrics.ts        Token usage + operation duration histograms
  events/
    inference-details.ts    Opt-in inference operation event
docs/
  worktracking/             Implementation plans and architecture docs
  guides/                   Technical guides
  fixes/                    Bug fix documentation
```

## Development Workflow

### Branch Strategy

We use branch protection on `main` with required CI checks. All changes go through pull requests.

```bash
# Create a feature branch
git checkout -b feat/my-change

# Make changes, then verify
npm run typecheck
npm run lint
npm test

# Commit with GPG signature
git commit -S -m "feat: description of change"

# Push and open PR
git push -u origin feat/my-change
gh pr create
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) with a Linear ticket suffix:

Format: `<type>: <summary> (ULT-###)`

| Prefix | Use for | Example |
|--------|---------|---------|
| `feat:` | New functionality | `feat: add webhook context extraction (ULT-123)` |
| `fix:` | Bug fixes | `fix: prevent span leak on timeout (ULT-124)` |
| `chore:` | Build, CI, config changes | `chore: update OTEL SDK to 1.31 (ULT-125)` |
| `refactor:` | Code restructuring without behavior change | `refactor: simplify span store lookup (ULT-126)` |
| `test:` | Test additions or fixes | `test: add redaction edge cases (ULT-127)` |
| `docs:` | Documentation only | `docs: update config reference (ULT-128)` |

### CI Checks

Every PR must pass on **both Node 20 and Node 22**:

1. `npm run typecheck` — TypeScript strict mode compilation
2. `npm run lint` — ESLint with typescript-eslint rules
3. `npm test` — Vitest test suite

## Writing Code

### OTEL Semantic Conventions

This plugin follows the [OTEL GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/). When adding or modifying span attributes:

- Use `gen_ai.*` namespace for standard GenAI attributes
- Use `openclaw.*` namespace for OpenClaw-specific attributes
- Reference the spec before inventing new attribute names

Key conventions:

| Attribute | Convention |
|-----------|-----------|
| `gen_ai.operation.name` | `invoke_agent` or `execute_tool` |
| `gen_ai.agent.name` | Agent identifier |
| `gen_ai.tool.name` | Tool being called |
| `gen_ai.usage.input_tokens` | Prompt token count |
| `gen_ai.usage.output_tokens` | Completion token count |
| `error.type` | Error class name |

### Span Lifecycle

Every span must be properly closed. The span store uses a LIFO (stack) discipline:

1. `before_agent_start` opens the root span
2. `before_tool_call` opens a child span (pushed to stack)
3. `tool_result_persist` closes the tool span (popped from stack)
4. `agent_end` closes the root span

If a span is opened, it **must** be closed — even on error. Use try/finally patterns.

### Error Isolation

**Plugin errors must never crash the OpenClaw host process.** Every hook handler is wrapped in try/catch at registration. If you add new hooks or modify existing ones, maintain this pattern:

```typescript
api.on('hook_name', ((event: never) => {
  try {
    handleHook(event, config);
  } catch (err) {
    api.logger.warn(`Logfire hook_name error: ${err}`);
  }
}) as (event: never) => void);
```

### Privacy Controls

The plugin has several privacy flags (`captureToolInput`, `captureToolOutput`, `captureMessageContent`, `redactSecrets`). When recording data from hook events:

- Always check the relevant config flag before recording
- Use `redactSecrets()` from `util.ts` when `config.redactSecrets` is true
- Use `truncate()` to respect `config.toolInputMaxLength`

## Writing Tests

Tests live alongside source files as `*.test.ts` (co-located pattern).

### What to Test

- **Config resolution** — defaults, env var overrides, user config merges
- **Utility functions** — serialization edge cases, truncation, redaction patterns
- **Span store** — concurrent sessions, LIFO ordering, TTL cleanup
- **Trace link generation** — URL format correctness

### What NOT to Test

- OpenTelemetry SDK internals (trust the library)
- Exact OTLP wire format (integration-test territory)
- OpenClaw hook event shapes (they're external contracts)

### Running Tests

```bash
npm test              # Single run
npm run test:watch    # Watch mode during development
```

## Local Testing with OpenClaw

To test against a real OpenClaw instance:

```bash
# Symlink into OpenClaw extensions
ln -s $(pwd) ~/.openclaw/extensions/openclaw-logfire

# Or add to openclaw.json
# "plugins": { "load": { "paths": ["./path/to/openclaw-logfire"] } }

export LOGFIRE_TOKEN="your-write-token"
openclaw restart
openclaw plugins list  # Should show "logfire" as enabled
```

## Code Review

We use [CodeRabbit](https://coderabbit.ai/) for automated AI code review. It checks:

- OTEL semantic convention compliance
- Span lifecycle correctness
- Error isolation patterns
- Privacy control adherence
- TypeScript type safety

CodeRabbit will comment on your PR automatically. Address any issues it flags before requesting human review.

## Documentation

When documenting fixes or significant changes, add files to `docs/` following the naming convention:

```text
docs/fixes/YYYY-MM-DD-short-description.md
docs/guides/YYYY-MM-DD-short-description.md
```

## Questions?

Open an issue on the [GitHub repo](https://github.com/Ultrathink-Solutions/openclaw-logfire/issues).
