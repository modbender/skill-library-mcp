---
name: aegis-audit
description: >
  Deep behavioral security audit for AI agent skills and MCP tools. Performs deterministic
  static analysis (AST + Semgrep + 15 specialized scanners), cryptographic lockfile generation,
  and optional LLM-powered intent analysis. Use when installing, reviewing, or approving any
  skill, tool, plugin, or MCP server — especially before first use. Replaces basic safety
  summaries with full CWE-mapped, OWASP-tagged, line-referenced security reports.
version: 0.1.10
homepage: https://github.com/Aegis-Scan/aegis-scan
url: https://pypi.org/project/aegis-audit/
metadata: {"openclaw":{"emoji":"🔍","homepage":"https://github.com/Aegis-Scan/aegis-scan","requires":{"bins":["aegis"],"config":["~/.aegis/config.yaml"]},"install":[{"kind":"uv","package":"aegis-audit","bins":["aegis"]}]}}
---

# Aegis Audit

Behavioral security scanner for AI agent skills and MCP tools.

Aegis is a **defensive** security auditing tool. It detects malicious patterns in other skills so users can avoid dangerous installs. This skill does not teach or enable attacks — it helps users vet skills before trusting them.

> The "SSL certificate" for AI agent skills — scan, certify, and govern before you trust.

Source: [github.com/Aegis-Scan/aegis-scan](https://github.com/Aegis-Scan/aegis-scan) | Package: [pypi.org/project/aegis-audit](https://pypi.org/project/aegis-audit/) | License: AGPL-3.0

---

## What Aegis does

Aegis answers the question every agent user should ask: *"What can this skill actually do, and should I trust it?"*

- **Deterministic static analysis** — AST parsing + Semgrep + 15 specialized scanners. Same code = same report, every time.
- **Scope-resolved capabilities** — Not just "accesses the filesystem" but exactly which files, URLs, hosts, and ports.
- **Risk scoring** — 0-100 composite score with CWE/OWASP-mapped findings and severity tiers.
- **Cryptographic proof** — Ed25519-signed lockfile with Merkle tree for tamper detection.
- **Optional LLM analysis** — Bring your own key (Gemini, Claude, OpenAI, Ollama, local). Disabled by default. See the privacy notice below before enabling.

---

## Install

Install from [PyPI](https://pypi.org/project/aegis-audit/) using pip or uv:

```bash
pip install aegis-audit
```

```bash
uv tool install aegis-audit
```

Both commands install the same package. Pin to a specific version when possible (e.g. `pip install aegis-audit==1.3.0`) and verify the publisher on PyPI before installing. The package source is at [github.com/Aegis-Scan/aegis-scan](https://github.com/Aegis-Scan/aegis-scan).

After install, the `aegis` CLI is available on your PATH.

---

## Quick start

Aegis runs fully offline by default. No API keys, no network access, no data leaves your machine.

```bash
aegis scan --no-llm
```

This scans the current directory and produces a security report. All commands default to `.` (current directory) when no path is given.

```bash
aegis scan ./some-skill --no-llm
```

---

## CLI reference

| Command | Description |
|---|---|
| `aegis scan [path]` | Full security scan with risk scoring |
| `aegis lock [path]` | Scan + generate signed `aegis.lock` |
| `aegis verify [path]` | Verify lockfile against current code |
| `aegis badge [path]` | Generate shields.io badge markdown |
| `aegis setup` | Interactive LLM configuration wizard |
| `aegis mcp-serve` | Start the MCP server (stdio transport) |
| `aegis mcp-config` | Print MCP config JSON for Cursor / Claude Desktop |
| `aegis version` | Show the Aegis version |

Common flags: `--no-llm` (skip LLM, the default), `--json` (CI output), `-v` (verbose).

---

## Lockfiles

Generate a signed lockfile after scanning:

```bash
aegis lock
```

This produces `aegis.lock` — a cryptographically signed snapshot of the skill's security state. Commit it alongside the skill so consumers can verify nothing changed.

Verify a lockfile:

```bash
aegis verify
```

If any file was modified since the lockfile was created, the Merkle root will not match and verification fails.

---

## Optional: LLM analysis

**Privacy notice:** LLM analysis is disabled by default. When enabled, Aegis sends scanned code to the configured third-party LLM provider (Google, OpenAI, or Anthropic). No data is transmitted unless you explicitly configure an API key and run a scan without `--no-llm`. Do not enable LLM mode on repositories containing secrets or sensitive code unless you trust the provider.

To enable LLM analysis, run the interactive setup:

```bash
aegis setup
```

This saves your config to `~/.aegis/config.yaml`. Alternatively, set one of these environment variables:

- `GEMINI_API_KEY` — Google Gemini
- `OPENAI_API_KEY` — OpenAI
- `ANTHROPIC_API_KEY` — Anthropic Claude

These environment variables are optional. Aegis works fully offline without them. Only set a key if you want the AI second-opinion feature and accept that scanned code will be sent to the corresponding provider.

For local LLM servers (Ollama, LM Studio, llama.cpp, vLLM), see `aegis setup` — no third-party data transmission occurs with local models.

---

## MCP server

Aegis runs as an MCP server for Cursor, Claude Desktop, and any MCP-compatible client. Three tools are exposed: `scan_skill`, `verify_lockfile`, and `list_capabilities`.

Add this to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "aegis": {
      "command": "aegis",
      "args": ["mcp-serve"]
    }
  }
}
```

Or generate it automatically:

```bash
aegis mcp-config
```

Aegis uses stdio transport — no network server needed.

---

## What gets scanned

| Scanner | What it detects |
|---|---|
| AST Parser | 750+ Python function/method patterns across 15+ categories |
| Semgrep Rules | 80+ regex rules for Python, JavaScript, and secrets |
| Secret Scanner | API keys, tokens, private keys, connection strings (30+ patterns) |
| Shell Analyzer | Pipe-to-shell, reverse shells, inline exec |
| JS Analyzer | XSS, eval, prototype pollution, dynamic imports |
| Dockerfile Analyzer | Privilege escalation, secrets in ENV/ARG, unpinned images |
| Config Analyzer | Dangerous settings in YAML, JSON, TOML, INI |
| Social Engineering | Misleading filenames, Unicode tricks, trust manipulation |
| Steganography | Hidden payloads in images, homoglyph attacks |
| Shadow Module Detector | Stdlib-shadowing files (os.py, sys.py in the skill) |
| Combo Analyzer | Multi-capability attack chains (exfiltration, C2, ransomware) |
| Taint Analysis | Source-to-sink data flows (commands, URLs, SQL, paths) |
| Complexity Analyzer | Cyclomatic complexity warnings for hard-to-audit functions |
| Skill Meta Analyzer | SKILL.md vs actual code cross-referencing |
| Persona Classifier | Overall trust profile (LGTM, Permission Goblin, etc.) |

---

## Vibe Check personas

Aegis assigns each scanned skill a persona based on deterministic analysis:

- **Cracked Dev** — Clean code, smart patterns, minimal permissions.
- **LGTM** — Permissions match the intent, scopes are sane, nothing weird.
- **Trust Me Bro** — Polished on the outside, suspicious on the inside.
- **You Sure About That?** — Messy code, missing pieces, docs that overpromise.
- **Co-Dependent Lover** — Tiny logic, huge dependency tree. Supply chain risk.
- **Permission Goblin** — Wants everything: filesystem, network, secrets.
- **Spaghetti Monster** — Unreadable chaos. High complexity.
- **The Snake** — Code that looks clean but is not. Potentially malicious.

---

## JSON output for CI

```bash
aegis scan --json --no-llm
```

```bash
aegis scan --json --no-llm | jq '.deterministic.risk_score_static'
```

```bash
aegis scan --json --no-llm | jq -e '.deterministic.risk_score_static <= 50'
```

The JSON report contains two payloads:

- **Deterministic** — Merkle tree, capabilities, findings, risk score (reproducible, signed)
- **Ephemeral** — LLM analysis, risk adjustment (non-deterministic, not signed)

---

## For skill developers

Run Aegis on your own skill before publishing:

```bash
cd ./my-skill
aegis scan --no-llm -v
```

Fix PROHIBITED findings. Document RESTRICTED ones. Ship with an `aegis.lock`:

```bash
aegis lock
```

See the [Skill Developer Best Practices](https://github.com/Aegis-Scan/aegis-scan/blob/main/docs/SKILL_DEVELOPER_GUIDE.md) guide.

---

## Architecture

```
aegis scan ./skill
    |
    +-- coordinator.py       File discovery (git-aware / directory walk)
    +-- ast_parser.py        AST analysis + pessimistic scope extraction
    +-- secret_scanner.py    30+ secret patterns
    +-- shell_analyzer.py    Dangerous shell patterns
    +-- js_analyzer.py       JS/TS vulnerability patterns
    +-- config_analyzer.py   YAML/JSON/TOML/INI risky settings
    +-- combo_analyzer.py    Multi-capability attack chains
    +-- taint_analyzer.py    Source-to-sink data flow tracking
    +-- binary_detector.py   External binary classification
    +-- social_eng_scanner   Social engineering detection
    +-- stego_scanner        Steganography + homoglyphs
    +-- hasher.py            Lazy Merkle tree
    +-- signer.py            Ed25519 signing
    +-- rule_engine.py       Policy evaluation
    +-- reporter/            JSON + Rich console output
         |
         v
    aegis_report.json + aegis.lock
```

---

## License

Aegis is dual-licensed:

- **Open Source:** AGPL-3.0 — free to use, modify, and distribute. Network service deployments must release source.
- **Commercial:** Proprietary license available for embedding in proprietary products, running without source disclosure, SLAs, and support.

See [LICENSING.md](https://github.com/Aegis-Scan/aegis-scan/blob/main/aegis-core/LICENSING.md) for full details.

---

## Contributing

Contributions welcome. By contributing, you agree to the [Contributor License Agreement](https://github.com/Aegis-Scan/aegis-scan/blob/main/aegis-core/CLA.md).

```bash
cd aegis-core
pip install -e ".[dev]"
pytest
```

---

Python 3.11+ required. No network access needed for deterministic scans. Works offline.
