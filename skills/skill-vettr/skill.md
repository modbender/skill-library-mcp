---
name: skill-vettr
version: "2.0.3"
author: britrik
description: Static analysis security scanner for third-party OpenClaw skills. Detects eval/spawn risks, malicious dependencies, typosquatting, and prompt injection patterns before installation. Use when vetting skills from ClawHub or untrusted sources.
tags: ["security", "scanner", "vetting", "analysis", "static-analysis"]
emoji: "🛡️"
metadata:
  openclaw:
    requires:
      bins: ["node", "git", "curl", "tar", "clawhub"]
      env: []
    install:
      command: "npm install"
      artifacts:
        - "node_modules/tree-sitter-javascript/tree-sitter-javascript.wasm"
        - "node_modules/tree-sitter-typescript/tree-sitter-typescript.wasm"
        - "node_modules/web-tree-sitter/web-tree-sitter.wasm"
      safety: >
        npm install runs dependency lifecycle scripts. tree-sitter packages
        use hasInstallScript for native/WASM builds. For isolation, run
        npm ci --ignore-scripts inside a container, then manually verify
        .wasm artifacts exist.
    notes: >
      Requires .wasm files from node_modules at runtime.
      git/curl/tar are used by vet-url to download and extract remote archives.
      clawhub CLI is used by vet-clawhub to fetch skills from the registry.
      Only the /skill:vet command (local path) needs no external binaries beyond node.
---

# skill-vettr v2.0.3

Security scanner for third-party OpenClaw skills. Analyses source code, dependencies, and metadata before installation using tree-sitter AST parsing and regex pattern matching.

## Installation

```bash
npm install
```

This installs all Node.js dependencies, including tree-sitter `.wasm` grammar files required at runtime for AST-based analysis. The `.wasm` files are located in `node_modules` and must be present for the skill to function.

> ⚠️ **Install safety:** `npm install` runs dependency lifecycle scripts, which can execute arbitrary code. For stronger isolation, run `npm ci --ignore-scripts` — but note that tree-sitter native/WASM artifacts may not build, breaking AST analysis. Prefer installing inside a container or VM when possible.

## External Binaries

The `vet-url` and `vet-clawhub` commands invoke external binaries via `execSafe` (which uses `execFile` — no shell is spawned). Only the following commands are permitted:

| Binary | Used By | Purpose |
|--------|---------|---------|
| `git` | `vet-url` | Clone `.git` URLs (with hooks disabled) |
| `curl` | `vet-url` | Download archive URLs |
| `tar` | `vet-url` | Extract downloaded archives |
| `clawhub` | `vet-clawhub` | Fetch skills from ClawHub registry |

The `/skill:vet` command (local path vetting) requires only `node` and no external binaries.

## Commands

- `/skill:vet --path <directory>` — Vet a local skill directory
- `/skill:vet-url --url <https://...>` — Download and vet from URL
- `/skill:vet-clawhub --skill <slug>` — Fetch and vet from ClawHub

## Detection Categories

| Category | Method | Examples |
|----------|--------|----------|
| Code execution | AST | eval(), new Function(), vm.runInThisContext() |
| Shell injection | AST | exec(), execSync(), spawn("bash"), child_process imports |
| Dynamic require | AST | require(variable), require(templateString) |
| Prototype pollution | AST | __proto__ assignment |
| Prompt injection | Regex | Instruction override patterns, control tokens (in string literals) |
| Homoglyph attacks | Regex | Cyrillic/Greek lookalike characters in identifiers |
| Encoded names | Regex | Unicode/hex-escaped "eval", "exec" |
| Credential paths | Regex | Cloud and SSH credential directory references, system credential store access |
| Network calls | AST | fetch() with literal URLs (checked against allowlist) |
| Malicious deps | Config | Known bad packages, lifecycle scripts, git/http deps |
| Typosquatting | Levenshtein | Skill names within edit distance 2 of targets |
| Dangerous permissions | Config | shell:exec, credentials:read in SKILL.md |

## Limitations

> ⚠️ **This is a heuristic scanner with inherent limitations. It cannot guarantee safety.**

- **Static analysis only** — Cannot detect runtime behaviour (e.g., code that fetches malware after install)
- **Evasion possible** — Sophisticated obfuscation or multi-stage string construction can evade detection
- **JS/TS only** — Binary payloads, images, and non-text files are skipped
- **Limited network detection** — Only detects `fetch()` with literal URL strings; misses axios, http module, dynamic URLs
- **No sandboxing** — Does not execute or isolate target code
- **Comment scanning** — Prompt injection detection scans string literals, not comments
- **Filesystem scope** — `vet-url` downloads and extracts remote archives into a temp directory; `vet` accepts paths under `os.tmpdir()`, `~/.openclaw`, and `~/Downloads` by default. Set `allowCwd: true` in config to also permit `process.cwd()` (see Configuration below)
- **External binary trust** — `vet-url` and `vet-clawhub` invoke `git`, `curl`, `tar`, and `clawhub` via `execFile`. These binaries must be trusted and present on `PATH`

For high-security environments, combine with sandboxing, network isolation, and manual source review. Run inside a disposable container when vetting untrusted URLs.

## Configuration

### `allowCwd`

By default, `process.cwd()` is **not** included in the set of allowed vetting roots. The default allowed roots are:

- `os.tmpdir()`
- `~/.openclaw`
- `~/Downloads`

To allow vetting paths under the current working directory, set `allowCwd: true` in your vetting config:

```json
{
  "allowCwd": true
}
```

> ⚠️ **Security implication:** Enabling `allowCwd` means the scanner will accept any path under the directory you launched it from. If you run from `/` or `$HOME`, this effectively grants access to your entire filesystem. Only enable this when running from a scoped project directory or inside a container.

## `.vettrignore`

Place a `.vettrignore` file in the root of the skill directory being scanned to exclude files or directories from analysis. This is useful for excluding test fixtures that contain deliberate malicious patterns.

### Format

- One glob pattern per line
- Lines starting with `#` are comments
- Empty lines are ignored
- Patterns ending with `/` match entire directories
- `*` matches any sequence of non-separator characters
- `**` matches any sequence including path separators (recursive)
- `?` matches a single non-separator character

### Example

```
# Exclude test fixtures containing deliberate prompt injection vectors
test/fixtures/

# Exclude generated files
dist/
*.min.js
```

If the `.vettrignore` file is unreadable or contains invalid UTF-8, the engine logs an INFO-level warning and proceeds with a full scan.
