# guard-scanner — OpenClaw Community Plugin Registration

## Plugin Information

| Field | Value |
|-------|-------|
| **Plugin Name** | 🛡️ guard-scanner — Security scanner + runtime guard for AI agent skills |
| **npm package** | `guard-scanner` |
| **GitHub** | https://github.com/koatora20/guard-scanner |
| **Install** | `openclaw plugins install guard-scanner` |
| **Version** | 3.1.0 |
| **License** | MIT |

## Description

Static security scanner + runtime `before_tool_call` guard for OpenClaw agents. 19 runtime threat patterns across 3 defense layers, 190+ static detection patterns across 21 threat categories.

### What it does:

1. **Static scanning** — `npx guard-scanner [dir]` scans skills before installation (21 categories, 190+ patterns, SARIF/JSON/HTML output)
2. **Runtime guard** — `before_tool_call` hook automatically blocks dangerous tool calls with `block`/`blockReason`
3. **3 enforcement modes** — `monitor` (log only), `enforce` (block CRITICAL, default), `strict` (block HIGH+CRITICAL)

### 3-Layer Runtime Defense (19 patterns)

```
Layer 1: Threat Detection     — 12 patterns (reverse shells, credential exfil, SSRF, AMOS, etc.)
Layer 2: EAE Paradox Defense  — 4 patterns (memory/SOUL/config tampering protection)
Layer 3: Parity Judge         — 3 patterns (prompt injection, parity bypass, shutdown refusal)
```

### Why this matters:

- **Moltbook incident (Feb 2026)**: 1.5M API keys exposed from AI agent platform
- **Snyk ToxicSkills audit**: 36.8% of AI agent skills contain security flaws
- **OpenClaw's own THREAT-MODEL-ATLAS.md** identifies gaps that guard-scanner directly addresses
- **First security-focused plugin** in the OpenClaw ecosystem

### Requirements met:

- [x] Published on npmjs (`guard-scanner@3.1.0`)
- [x] Public GitHub repository (https://github.com/koatora20/guard-scanner)
- [x] Documentation: README.md (700+ lines), CHANGELOG.md, SECURITY.md, CONTRIBUTING.md
- [x] Issue tracker: GitHub Issues
- [x] Maintenance signal: 5 releases (v1.0.0 → v3.1.0) in 6 days, 91 tests
- [x] `openclaw.plugin.json` manifest with `configSchema`

### Testing:

```
ℹ tests 91
ℹ suites 21
ℹ pass 91
ℹ fail 0
ℹ duration_ms 118ms
```

---

*Built by Guava 🍈 & Dee — part of the [GuavaSuite](https://www.npmjs.com/package/guavasuite) ecosystem.*
