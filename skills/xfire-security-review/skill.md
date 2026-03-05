---
name: xfire-security-review
description: "Multi-agent adversarial security review — 3 AI agents debate every finding, only real vulnerabilities survive"
version: 0.1.2
homepage: https://github.com/Har1sh-k/xfire
metadata:
  openclaw:
    emoji: "🔥"
    homepage: "https://github.com/Har1sh-k/xfire"
    requires:
      env: [ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, GITHUB_TOKEN, XFIRE_CONFIG_PATH, XFIRE_CACHE_DIR, XFIRE_AUTH_PATH]
    primaryEnv: ANTHROPIC_API_KEY
---

# xfire — Multi-Agent Adversarial Security Review

**Multiple agents. One verdict. Zero blind spots.**

xfire sends your code to 3 AI agents (Claude, Codex, Gemini) independently, then runs an adversarial debate where they cross-examine each other's findings. Only vulnerabilities that survive prosecution, defense, and a judge's ruling make the final report.

## When to Use

Invoke xfire when a user asks for any of these:

- "security review this PR"
- "find vulnerabilities in this code"
- "audit this repo for security issues"
- "run a security scan"
- "analyze this diff for security problems"
- "check this pull request for vulnerabilities"
- "code review for security"
- "pentest this codebase"
- "threat model this change"

**Do NOT use xfire for:**

- General code quality / style reviews (use a linter)
- Performance profiling
- Dependency license auditing
- Non-security functional testing

## Prerequisites

- **Python 3.11+**
- Install: `pip install xfire`
- At least one AI agent CLI or API key configured:

| Agent   | CLI tool | API key env var    |
|---------|----------|--------------------|
| Claude  | `claude` | `ANTHROPIC_API_KEY` |
| Codex   | `codex`  | `OPENAI_API_KEY`    |
| Gemini  | `gemini` | `GOOGLE_API_KEY`    |

## Setup

```bash
# Initialize config in current repo
xfire init

# Test agent connectivity
xfire test-llm

# Set up agent credentials
xfire auth login --provider claude
xfire auth login --provider codex
xfire auth login --provider gemini
```

## Commands

### Core Analysis

#### `analyze-pr` — Analyze a GitHub pull request

```bash
xfire analyze-pr --repo owner/repo --pr 123
```

| Flag | Type | Default | Env var | Description |
|------|------|---------|---------|-------------|
| `--repo` | str | *required* | — | GitHub repo in owner/repo format |
| `--pr` | int | *required* | — | PR number |
| `--github-token` | str | None | `GITHUB_TOKEN` | GitHub token |
| `--agents` | str | None | — | Comma-separated agent list (claude,codex,gemini) |
| `--skip-debate` | bool | False | — | Skip adversarial debate phase |
| `--context-depth` | str | None | — | Context depth: shallow\|medium\|deep |
| `--output` | str | None | — | Output file path |
| `--format` | str | markdown | — | Output format: markdown\|json\|sarif |
| `--post-comment` | bool | False | — | Post review as GitHub PR comment |
| `--cache-dir` | str | None | `XFIRE_CACHE_DIR` | Cache directory for context/intent persistence |
| `--verbose` | bool | False | — | Enable verbose logging |
| `--dry-run` | bool | False | — | Show what would be analyzed without calling agents |
| `--debate` | bool | False | — | Show adversarial debate transcript after the report |
| `--debug` | bool | False | — | Write full debug trace to xfire-debug-TIMESTAMP.md |
| `--silent` | bool | False | — | Suppress all output — exit code only (for git hooks) |

#### `analyze-diff` — Analyze a local diff or staged changes

```bash
xfire analyze-diff --staged --repo-dir .
xfire analyze-diff --patch changes.patch --repo-dir .
xfire analyze-diff --commit f1877d3 --repo-dir /path/to/repo
xfire analyze-diff --base main --head feature-branch
xfire analyze-diff --commit f1877d3 --thinking --repo-dir /path/to/repo
```

| Flag | Type | Default | Env var | Description |
|------|------|---------|---------|-------------|
| `--patch` | str | None | — | Path to a diff/patch file |
| `--commit` | str | None | — | Commit SHA to analyze (auto-generates patch via git show) |
| `--repo-dir` | str | . | — | Path to the repository root |
| `--staged` | bool | False | — | Analyze staged changes in the repo |
| `--base` | str | None | — | Base branch/commit for comparison |
| `--head` | str | None | — | Head branch/commit for comparison |
| `--agents` | str | None | — | Comma-separated agent list |
| `--skip-debate` | bool | False | — | Skip adversarial debate phase |
| `--context-depth` | str | None | — | Context depth: shallow\|medium\|deep |
| `--output` | str | None | — | Output file path |
| `--format` | str | markdown | — | Output format: markdown\|json\|sarif |
| `--cache-dir` | str | None | `XFIRE_CACHE_DIR` | Cache directory for context/intent persistence |
| `--thinking` | bool | False | — | Enable extended thinking/reasoning for all agents |
| `--verbose` | bool | False | — | Enable verbose logging |
| `--dry-run` | bool | False | — | Show what would be analyzed without calling agents |
| `--debate` | bool | False | — | Show adversarial debate transcript after the report |
| `--debug` | bool | False | — | Write full debug trace to xfire-debug-TIMESTAMP.md |
| `--silent` | bool | False | — | Suppress all output — exit code only (for git hooks) |

#### `code-review` — Full codebase security audit

```bash
xfire code-review /path/to/repo
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `repo_dir` (argument) | str | . | Path to the repository root |
| `--agents` | str | None | Comma-separated: claude,codex,gemini |
| `--skip-debate` | bool | False | Skip adversarial debate phase |
| `--max-files` | int | 150 | Maximum number of source files to scan |
| `--thinking` | bool | False | Enable extended thinking/reasoning for all agents |
| `--format` | str | markdown | Output format: markdown\|json\|sarif |
| `--output` | str | None | Output file path |
| `--verbose` | bool | False | Enable verbose logging |
| `--dry-run` | bool | False | Show what would be analyzed without calling agents |
| `--debate` | bool | False | Show adversarial debate transcript after the report |
| `--debug` | bool | False | Write full debug trace to xfire-debug-TIMESTAMP.md |
| `--silent` | bool | False | Suppress all output — exit code only (for git hooks) |

#### `scan` — Baseline-aware incremental scan

```bash
xfire scan . --base main --head feature-branch
xfire scan . --since-last-scan
xfire scan . --last 5
xfire scan . --range abc123~1..abc123
xfire scan . --since 2026-01-01
xfire scan . --diff changes.patch
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `repo_dir` (argument) | str | . | Path to the repository root |
| `--base` | str | None | Base branch/commit (use with --head) |
| `--head` | str | None | Head branch/commit (use with --base) |
| `--range` | str | None | Commit range e.g. abc123~1..abc123 |
| `--diff` | str | None | Path to a .patch file |
| `--since-last-scan` | bool | False | Scan all commits since last scan |
| `--since` | str | None | All commits since date (YYYY-MM-DD) |
| `--last` | int | None | Last N commits |
| `--agents` | str | None | Comma-separated: claude,codex,gemini |
| `--skip-debate` | bool | False | Skip adversarial debate phase |
| `--context-depth` | str | None | Context depth: shallow\|medium\|deep |
| `--format` | str | markdown | Output format: markdown\|json\|sarif |
| `--output` | str | None | Output file path |
| `--verbose` | bool | False | Enable verbose logging |
| `--dry-run` | bool | False | Show what would be analyzed without calling agents |

#### `baseline` — Build persistent repo baseline context

```bash
xfire baseline /path/to/repo
xfire baseline . --force
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `repo_dir` (argument) | str | . | Path to the repository root |
| `--force` | bool | False | Rebuild baseline even if one already exists |
| `--verbose` | bool | False | Enable verbose logging |

### Output

#### `report` — Re-generate a report from saved JSON results

```bash
xfire report --input xfire-results.json --format sarif
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--input` | str | *required* | Path to an xfire JSON results file |
| `--format` | str | markdown | Output format: markdown\|json\|sarif |
| `--output` | str | None | Output file path |

#### `debates` — Replay adversarial debate transcripts

```bash
xfire debates --input xfire-results.json
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--input` | str | *required* | Path to an xfire JSON results file |

### Setup & Diagnostics

#### `init` — Initialize xfire configuration

```bash
xfire init
```

Creates `.xfire/config.yaml` in the current directory. No flags.

#### `config-check` — Validate configuration

```bash
xfire config-check --repo-dir .
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--repo-dir` | str | . | Path to the repository root |

#### `test-llm` — Test agent connectivity

```bash
xfire test-llm
xfire test-llm --agents claude --mode api
xfire test-llm --thinking --prompt "What is 2+2?"
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--repo-dir` | str | . | Path to the repository root |
| `--agents` | str | None | Comma-separated agent list to test (default: all enabled) |
| `--timeout` | int | 30 | Timeout in seconds per agent |
| `--mode` | str | None | Override mode for all agents: cli or api |
| `--prompt` | str | None | Custom test prompt to send to each agent |
| `--thinking` | bool | False | Enable extended thinking/reasoning for the test |

#### `auth login` — Set up agent credentials

```bash
xfire auth login --provider claude
xfire auth login --provider codex
xfire auth login --provider gemini
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--provider` / `-p` | str | *required* | Provider to authenticate: codex\|gemini\|claude |
| `--token` | str | None | Claude setup-token value (--provider claude only) |

#### `auth status` — Show credential status

```bash
xfire auth status
```

No flags. Displays a table of all provider credential statuses.

### Demo

#### `demo` — Run fixture or UI demo scenarios

```bash
xfire demo --ui
xfire demo --ui --scenario both_accept
xfire demo --fixture auth_bypass_regression
```

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--fixture` | str | "" | Fixture name (e.g., auth_bypass_regression) |
| `--ui` | bool | False | Run synthetic UI demo scenarios (no LLM calls) |
| `--scenario` | str | "" | Run one UI scenario: both_accept\|judge_questions\|defender_wins |
| `--format` | str | markdown | Output format: markdown\|json\|sarif |
| `--verbose` | bool | False | Enable verbose logging |

## Configuration

xfire looks for `.xfire/config.yaml` in the repo root (override with `XFIRE_CONFIG_PATH`).

Priority: CLI flags > environment variables > config.yaml > defaults.

```yaml
repo:
  purpose: ""                          # describe what your app does
  intended_capabilities: []            # expected capabilities
  sensitive_paths:                     # paths that get extra scrutiny
    - auth/
    - payments/
    - migrations/

analysis:
  context_depth: deep                  # shallow | medium | deep
  max_related_files: 20
  include_test_files: true

agents:
  claude:
    enabled: true
    mode: cli                          # cli | api
    cli_command: claude
    model: claude-sonnet-4-20250514
    api_key_env: ANTHROPIC_API_KEY
    timeout: 600
  codex:
    enabled: true
    mode: cli
    cli_command: codex
    model: o3-mini
    api_key_env: OPENAI_API_KEY
    timeout: 300
  gemini:
    enabled: true
    mode: cli
    cli_command: gemini
    model: gemini-2.5-pro
    api_key_env: GOOGLE_API_KEY
    timeout: 300

  debate:
    role_assignment: evidence          # evidence | rotate | fixed
    fixed_roles:
      prosecutor: claude
      defense: codex
      judge: gemini
    defense_preference: [codex, claude, gemini]
    judge_preference: [codex, gemini, claude]
    max_rounds: 2
    require_evidence_citations: true
    min_agents_for_debate: 2

  skills:
    code_navigation: true
    data_flow_tracing: true
    git_archeology: true
    config_analysis: true
    dependency_analysis: true
    test_coverage_check: true

severity_gate:
  fail_on: high                        # minimum severity to fail CI
  min_confidence: 0.7
  require_debate: true

suppressions: []

fast_model:
  provider: claude
  model: claude-haiku-4-5-20251001
  api_key_env: ANTHROPIC_API_KEY
  cli_command: claude
  cli_args: [--output-format, json]
  timeout: 60
```

## Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| Markdown | `--format markdown` | Human-readable report (default) |
| JSON | `--format json` | Machine-readable structured data |
| SARIF | `--format sarif` | Static Analysis Results Interchange Format for CI tooling |

## CI/CD Integration

### GitHub Actions

```yaml
name: xfire Security Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  security-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - run: pip install xfire

      - name: Run xfire security review
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
        run: |
          xfire analyze-pr \
            --repo ${{ github.repository }} \
            --pr ${{ github.event.pull_request.number }} \
            --format sarif \
            --output results.sarif \
            --silent

      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

## How It Works

1. **Context Building** — parses the diff/PR/repo and collects related files, git history, configs, and dependency data
2. **Intent Inference** — uses a fast model (Haiku) to understand the repo's purpose, trust boundaries, and security controls
3. **Independent Review** — sends the context to each enabled agent (Claude, Codex, Gemini) in parallel
4. **Finding Extraction** — normalizes all agent responses into structured findings with severity, confidence, and CWE tags
5. **Adversarial Debate** — each finding goes through a prosecution → defense → judge pipeline where agents argue for/against its validity
6. **Verdict & Deduplication** — the judge issues a final ruling; findings are deduplicated and merged across agents
7. **Report Generation** — produces the final report in markdown, JSON, or SARIF format with severity gating for CI

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes (for Claude API mode) | Anthropic API key for Claude |
| `OPENAI_API_KEY` | For Codex API mode | OpenAI API key for Codex |
| `GOOGLE_API_KEY` | For Gemini API mode | Google API key for Gemini |
| `GITHUB_TOKEN` | For `analyze-pr` | GitHub personal access token |
| `XFIRE_CONFIG_PATH` | No | Override path to config.yaml |
| `XFIRE_CACHE_DIR` | No | Cache directory for context/intent persistence across runs |
| `XFIRE_AUTH_PATH` | No | Override path to auth.json credential store |

## Limitations

- Requires at least one AI agent (Claude, Codex, or Gemini) to be configured and reachable
- CLI mode requires the agent CLI tools to be installed and on PATH
- Does not replace manual penetration testing or formal security audits
- Findings depend on AI model capabilities and may include false positives or miss subtle vulnerabilities
- Large repositories may hit agent context limits; use `--max-files` to constrain scope
- Does not scan binary files, compiled artifacts, or container images
- Debate quality improves with more agents — single-agent mode skips the adversarial phase
