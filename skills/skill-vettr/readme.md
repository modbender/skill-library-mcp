# skill-vettr v2.0.3

Static analysis security scanner for OpenClaw skills. Analyses code before installation to detect common threats.

## Quick Start

```bash
cd ~/.openclaw/skills/skill-scanner
npm install
npm run build
npm test
```

> ⚠️ `npm install` runs dependency lifecycle scripts (tree-sitter includes native builds). For stronger isolation, install inside a container or use `npm ci --ignore-scripts` (note: AST analysis may break without tree-sitter WASM artifacts).

## What It Does

skill-vettr scans a skill's source code, dependencies, and metadata for security issues. It uses:

- **tree-sitter AST parsing** for structural code analysis (eval, exec, spawn, dynamic require, prototype pollution, etc.)
- **Regex patterns** for things AST can't detect (prompt injection, homoglyph attacks, encoded function names)
- **Dependency analysis** for known malicious packages, suspicious prefixes, lifecycle scripts
- **Metadata analysis** for typosquatting (Levenshtein distance), dangerous permissions, blocked authors

## What It Doesn't Do

This is a heuristic scanner. It has inherent limitations:

- Cannot detect runtime-only behaviour (e.g., code that downloads malware at runtime from an innocuous-looking URL)
- AST queries can be evaded by sufficiently motivated attackers (e.g., multi-stage string construction)
- Only scans JS/TS code files — binary payloads, images, and other non-text files are skipped
- Does not sandbox or execute the target skill
- Malicious package lists are small and non-exhaustive

For high-security environments, combine with sandboxing and manual review.

## External Binaries

The `vet-url` and `vet-clawhub` commands invoke external binaries via `execSafe` (uses `execFile`, no shell spawned):

| Binary | Command | Purpose |
|--------|---------|---------|
| `git` | `vet-url` | Clone `.git` URLs (hooks disabled via `-c core.hooksPath=/dev/null`) |
| `curl` | `vet-url` | Download archive URLs (max 50 MB, 120s timeout) |
| `tar` | `vet-url` | Extract archives (`--no-same-owner --no-same-permissions`) |
| `clawhub` | `vet-clawhub` | Fetch skills from ClawHub registry |

The `/skill:vet` command (local path) requires only `node`. Ensure external binaries are trusted and available on `PATH` before using remote vetting commands.

## Usage

**Vet a local skill directory:**
```
/skill:vet --path ~/Downloads/suspicious-skill
```

**Vet from URL:**
```
/skill:vet-url --url https://github.com/org/skill/archive/main.tar.gz
```

**Vet from ClawHub:**
```
/skill:vet-clawhub --skill some-skill-name
```

## Configuration

Add to `~/.openclaw/config.json`:

```json
{
  "skill-vettr": {
    "maxRiskScore": 50,
    "requireAuthor": true,
    "autoVet": true,
    "maxNetworkCalls": 5,
    "allowedHosts": ["api.openai.com", "api.anthropic.com", "registry.npmjs.org"],
    "blockedAuthors": [],
    "blockedPackages": [],
    "typosquatTargets": ["my-important-skill"]
  }
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `maxRiskScore` | 50 | Score at or above which installation is blocked |
| `requireAuthor` | true | Warn if SKILL.md lacks an author field |
| `autoVet` | false | Automatically vet skills on `skill:pre-install` hook |
| `maxNetworkCalls` | 5 | Excess network calls beyond this add to risk score |
| `allowedHosts` | (see above) | Hostnames that are allowed for network calls |
| `blockedAuthors` | [] | Author names to block outright |
| `blockedPackages` | [] | npm package names to block (merged with built-in list) |
| `typosquatTargets` | [] | Skill names to check for typosquatting similarity |

## Risk Levels

| Level | Score | Recommendation |
|-------|-------|----------------|
| SAFE | 0 | INSTALL |
| LOW | 1-19 | INSTALL |
| MEDIUM | 20-39 | REVIEW |
| HIGH | 40-69 | REVIEW or BLOCK |
| CRITICAL | 70+ | BLOCK |

## Testing

```bash
npm run build
npm test
```

Tests use Node's built-in test runner (`node:test`). The test suite covers each analyzer independently plus end-to-end integration tests against fixture skill directories.

## Security Notes

The `vet` and `vet-url` commands allow paths under the current working directory (`process.cwd()`) as a convenience, so you can vet skills directly in your workspace without copying them elsewhere. The trade-off is that any path under `cwd` is accepted for vetting, which may be a broader scope than intended if you run the tool from a high-privilege or sensitive directory. In high-security environments, consider running skill-vettr from a dedicated, isolated directory to limit the allowed root scope.

The `vet-url` command downloads and extracts remote archives into a temporary directory. This is necessary for its purpose but means external binaries (`curl`, `tar`, `git`) touch the filesystem. The `vet-clawhub` command similarly invokes the `clawhub` CLI. Run these commands only against URLs and slugs you have reason to trust, and prefer running inside a disposable container or VM for untrusted sources.

If you enable the `autoVet` hook, review your configuration carefully — it will automatically invoke the vetting engine on every `skill:pre-install` event.

## Publishing

The root directory of this repository is the publishable artifact. There is no separate build or packaging step required — publish directly from the repo root.

## Licence

MIT
