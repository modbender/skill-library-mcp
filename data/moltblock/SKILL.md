---
name: moltblock - Trust Layer for AI Agents
description: Verification gating for AI-generated artifacts. Policy checks and code verification to catch dangerous patterns before execution.
version: 0.11.0
metadata:
  openclaw:
    requires:
      anyBins:
        - npx
        - node
      config:
        - moltblock.json
        - ~/.moltblock/moltblock.json
    primaryEnv: OPENAI_API_KEY
    optionalEnv:
      - ANTHROPIC_API_KEY
      - GOOGLE_API_KEY
      - ZAI_API_KEY
    homepage: https://github.com/moltblock/moltblock
    install:
      - kind: node
        package: moltblock@0.11.0
        bins: [moltblock]
---

# moltblock — Trust Layer for AI Agents

## Description

Moltblock provides verification gating for AI-generated artifacts. It runs policy checks and optional code verification (via vitest) to catch dangerous patterns before they reach production.

**What moltblock does:**
- Generates code via LLM API calls, then runs policy checks against the output
- When `--test` is provided, executes vitest to verify generated code against a user-provided test file (see **Security: Test Execution** below)
- Reads its own config files (`moltblock.json`, `~/.moltblock/moltblock.json`) if present
- API keys are read from environment variables at runtime and sent only to the configured LLM provider endpoint

## When to Use

Use `moltblock` when the task involves:

- **High risk** (always verify): Destructive operations (`rm -rf`, `DROP TABLE`), privilege escalation (`sudo`, `chmod 777`), credential/key access (`.ssh/`, `id_rsa`, `.env`), system modification, raw disk writes
- **Medium risk** (verify when uncertain): Network requests (`curl`, `wget`, `fetch`), file writes, database modifications, subprocess spawning, dynamic code evaluation
- **Low risk** (skip verification): Simple text responses, math, reading public information, code that doesn't touch the filesystem or network

## Tool: moltblock

Verify a task before execution.

### Usage

```bash
npx moltblock@0.11.0 "<task description>" --provider <provider> --json
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| task | Yes | The task description to verify |
| --provider | No | LLM provider: openai, google, zai, local (auto-detected from env) |
| --model | No | Model override |
| --test | No | Path to test file (for code verification) |
| --json | No | Output structured JSON result |

### Environment Variables

Moltblock auto-detects the LLM provider from whichever API key is set. If no key is set, it falls back to a local LLM at `localhost:1234`. Set **one** of these for a cloud provider:
- `OPENAI_API_KEY` — OpenAI (primary)
- `ANTHROPIC_API_KEY` — Anthropic/Claude (optional)
- `GOOGLE_API_KEY` — Google/Gemini (optional)
- `ZAI_API_KEY` — ZAI (optional)

### Example

```bash
# Verify a task
npx moltblock@0.11.0 "implement a function that validates email addresses" --json

# Verify code with tests
npx moltblock@0.11.0 "implement a markdown-to-html converter" --test ./tests/markdown.test.ts --json
```

### Output (JSON mode)

```json
{
  "verification_passed": true,
  "verification_evidence": "All policy rules passed.",
  "authoritative_artifact": "...",
  "draft": "...",
  "critique": "...",
  "final_candidate": "..."
}
```

## Installation

Use directly with npx (recommended, no install needed):

```bash
npx moltblock@0.11.0 "your task" --json
```

Or install globally:

```bash
npm install -g moltblock@0.11.0
```

## Configuration

No configuration file is required. Moltblock auto-detects your LLM provider from environment variables and falls back to sensible defaults.

Optionally, place `moltblock.json` in your project root or `~/.moltblock/moltblock.json` to customize model bindings:

```json
{
  "agent": {
    "bindings": {
      "generator": { "backend": "google", "model": "gemini-2.0-flash" },
      "critic": { "backend": "google", "model": "gemini-2.0-flash" },
      "judge": { "backend": "google", "model": "gemini-2.0-flash" }
    }
  }
}
```

See the [full configuration docs](https://github.com/moltblock/moltblock#configuration) for policy rules and advanced options.

## Source

- Repository: [github.com/moltblock/moltblock](https://github.com/moltblock/moltblock)
- npm: [npmjs.com/package/moltblock](https://www.npmjs.com/package/moltblock)
- License: MIT

## Security: Test Execution

When `--test` is used, moltblock writes LLM-generated code to a temporary file and runs vitest against it using the user-provided test file. **This executes LLM-generated code in a Node.js process on the host machine.** Mitigations:

- The test file path must be provided explicitly by the user — moltblock does not select or generate test files
- Generated code is written to `os.tmpdir()` and cleaned up after execution
- Policy rules run **before** test execution to deny known dangerous patterns (e.g. `rm -rf`, `eval`, `child_process`, filesystem writes)
- Without `--test`, no code execution occurs — only policy checks run against the generated artifact

**Residual risk:** Policy rules are pattern-based and cannot catch all dangerous code. LLM-generated code executed via `--test` may perform arbitrary actions within the permissions of the Node.js process. Users should review generated code or run moltblock in a sandboxed environment when verifying untrusted tasks.

## Disclaimer

Moltblock reduces risk but does not eliminate it. Verification is best-effort — policy rules and LLM-based checks can miss dangerous patterns. Always review generated artifacts before executing them. The authors and contributors are not responsible for any damage, data loss, or security incidents resulting from the use of this tool. Use at your own risk.
