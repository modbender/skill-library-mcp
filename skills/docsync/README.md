# DocSync

**Auto-generate docs from code. Detect drift. Keep docs alive.**

DocSync is an [OpenClaw](https://openclaw.sh) skill that generates documentation from your codebase and keeps it in sync with code changes — enforced via git hooks.

## Why DocSync?

Documentation rots. Every team knows it. DocSync fixes this by:

1. **Analyzing your code** with tree-sitter (40+ languages)
2. **Generating structured docs** from functions, classes, types, and exports
3. **Detecting drift** when code changes but docs don't
4. **Blocking commits** with stale docs (via git pre-commit hooks)
5. **Auto-regenerating** stale documentation on demand

## Quick Start

### Install via ClawHub

```bash
clawhub install docsync
```

### Generate docs (Free — no license needed)

```
> Generate docs for src/api/
```

OpenClaw will run `docsync generate src/api/` and produce markdown documentation for every source file.

### Set up drift detection (Pro — $29/user/month)

```
> Install DocSync git hooks
```

Now every commit is checked for documentation drift. If you add a new function without documenting it, the commit is blocked with a helpful message.

### Auto-fix stale docs (Pro)

```
> Fix my stale documentation
```

DocSync regenerates docs for any files with detected drift.

## Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | One-shot doc generation for files and directories |
| **Pro** | $29/user/mo | Git hooks, drift detection, auto-fix, multi-language |
| **Team** | $49/user/mo | + Onboarding guides, architecture docs, custom templates |
| **Enterprise** | $79/user/mo | + SSO, audit logs, compliance reports, SLA |

**Get your license:** [docsync.pages.dev/pricing](https://docsync.pages.dev/pricing)

## Supported Languages

TypeScript, JavaScript, Python, Rust, Go, Java, C, C++, Ruby, PHP, C#, Swift, Kotlin

## How It Works

### Code Analysis

DocSync uses **tree-sitter** for accurate, incremental AST parsing. When tree-sitter isn't available, it falls back to regex-based extraction (less accurate but functional).

Extracted symbols include:
- Functions and methods (with signatures)
- Classes, structs, and interfaces
- Type aliases and enums
- Module exports

### Drift Detection

On each commit, DocSync:
1. Parses staged source files
2. Extracts all symbols
3. Checks if each symbol appears in corresponding documentation
4. Compares file modification times (source vs. docs)
5. Reports: undocumented symbols (critical), stale docs (warning), up-to-date (info)

### Git Hooks

Uses **lefthook** for fast, parallel git hook execution. The pre-commit hook:
- Only analyzes files being committed (not the whole repo)
- Runs in parallel with other hooks
- Can be skipped with `git commit --no-verify`

## Configuration

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "docsync": {
        "enabled": true,
        "apiKey": "YOUR_LICENSE_KEY",
        "config": {
          "outputDir": "docs",
          "excludePatterns": ["**/test/**", "**/node_modules/**"],
          "driftThreshold": "warning",
          "autoFix": false
        }
      }
    }
  }
}
```

## FOSS Stack

DocSync is built entirely on open-source tools:

- **[tree-sitter](https://tree-sitter.github.io/)** — Multi-language AST parsing (MIT)
- **[lefthook](https://github.com/evilmartians/lefthook)** — Git hooks manager (MIT)
- **[difftastic](https://difftastic.wilfred.me.uk/)** — Structural diff tool (MIT)

## Privacy

- **All processing happens locally** — your code never leaves your machine
- **License validation is offline** — no phone-home, no telemetry
- **No external API calls** — works in air-gapped environments

## Support

- Docs: [docsync.pages.dev/docs](https://docsync.pages.dev/docs)
- Issues: [github.com/docsync/docsync/issues](https://github.com/docsync/docsync/issues)
- Email: support@docsync.pages.dev

## License

DocSync skill code is MIT licensed. Premium features require a commercial license key.
