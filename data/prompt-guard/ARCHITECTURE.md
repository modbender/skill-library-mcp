# Prompt Guard Architecture

> Internal architecture documentation for contributors and maintainers.
> Last updated: 2026-02-11 | v3.2.0

---

## Overview

Prompt Guard uses a **Defense in Depth** design. Multiple inspection layers reduce false positives while effectively detecting attacks across 577+ patterns in 10 languages.

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT MESSAGE                            │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 0: Message Size Check                                    │
│  • Reject messages > 50KB (DoS prevention)                      │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Rate Limiting                                         │
│  • Per-user request tracking (30 req/60s default)               │
│  • Memory-bounded (max 10,000 tracked users)                    │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1.5: Cache Lookup (v3.1.0)                               │
│  • SHA-256 hash of normalized message                           │
│  • LRU cache (1,000 entries)                                    │
│  • Cache hit → return immediately (90% token savings)           │
└─────────────────────────────────────────────────────────────────┘
                               │ miss
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Text Normalization                                    │
│  • Homoglyph detection & replacement (Cyrillic/Greek → Latin)   │
│  • Visible delimiter stripping (I+g+n+o+r+e → Ignore)          │
│  • Character spacing collapse (i g n o r e → ignore)            │
│  • Zero-width character removal (17 types)                      │
│  • Fullwidth character normalization                             │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Pattern Matching Engine (Tiered)                      │
│  • Tier 0: CRITICAL (~45 patterns) — always loaded              │
│  • Tier 1: HIGH (~82 patterns) — default                        │
│  • Tier 2: MEDIUM (~100+ patterns) — on-demand                  │
│  • Runs against ORIGINAL + all DECODED variants                 │
│  • 577+ patterns across 50+ categories                          │
│  • 10 languages: EN, KO, JA, ZH, RU, ES, DE, FR, PT, VI       │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3.5: API Extra Patterns (v3.2.0 — optional)              │
│  • Early-access patterns (API-first, flows to open source)      │
│  • Premium patterns (API-exclusive)                             │
│  • Pre-compiled at init, merged into scan at runtime            │
│  • Skipped entirely if API is disabled (default)                │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: Decode Pipeline                                       │
│  • Base64 decode + full pattern re-scan                         │
│  • Hex escape decode (\x41\x42)                                 │
│  • ROT13 decode (full-text + per-word)                          │
│  • URL decode (%69%67%6E)                                       │
│  • HTML entity decode (&#105; → i)                              │
│  • Unicode escape decode (\u0069 → i)                           │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: Behavioral Analysis                                   │
│  • Repetition detection (token overflow)                        │
│  • Invisible character detection (Unicode Tags U+E0001-U+E007F) │
│  • Korean Jamo decomposition attacks                            │
│  • Canary token check (system prompt extraction)                │
│  • Language detection (flag unsupported languages)               │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 6: Context-Aware Decision                                │
│  • Sensitivity adjustment (low/medium/high/paranoid)            │
│  • Owner bypass rules (LOG for HIGH, still BLOCK for CRITICAL)  │
│  • Group context restrictions (non-owners blocked at MEDIUM+)   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 7: Result + Logging + Reporting                          │
│  • DetectionResult with severity, action, reasons, fingerprint  │
│  • Markdown and/or JSONL logging (with optional hash chain)     │
│  • HiveFence collective threat reporting                        │
│  • API threat reporting (v3.2.0, opt-in, anonymized)            │
│  • Cache storage for future lookups                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Layer 8: Output Scanner / DLP                                  │
│  • scan_output() — LLM response scanning                       │
│  • Canary token leakage detection                               │
│  • Credential format patterns (17+ key formats)                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Layer 9: Enterprise DLP Sanitizer                              │
│  • sanitize_output() — redact-first, block-as-fallback          │
│  • 17 credential patterns → [REDACTED:type] labels              │
│  • Post-redaction re-scan: block if still HIGH+                 │
│  • Returns SanitizeResult with full audit metadata              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### Severity Levels

| Level | Value | Description | Typical Trigger |
|-------|-------|-------------|-----------------|
| SAFE | 0 | No threat detected | Normal conversation |
| LOW | 1 | Minor suspicious signal | Output manipulation |
| MEDIUM | 2 | Clear manipulation attempt | Role manipulation, urgency |
| HIGH | 3 | Dangerous command | Jailbreaks, system access |
| CRITICAL | 4 | Immediate threat | Secret exfil, code execution |

### Action Types

| Action | Description | When Used |
|--------|-------------|-----------|
| `allow` | No intervention | SAFE severity |
| `log` | Record only | Owner requests, LOW severity |
| `warn` | Notify user | MEDIUM severity |
| `block` | Refuse request | HIGH severity |
| `block_notify` | Block + alert owner | CRITICAL severity |

---

## Pattern Categories

### Tier 0: CRITICAL (Always Loaded — ~45 patterns)

| Category | Description |
|----------|-------------|
| `secret_exfiltration` | API key/token/password requests, .env access |
| `dangerous_commands` | rm -rf, fork bombs, curl\|bash, eval() |
| `sql_injection` | DROP TABLE, TRUNCATE, comment injection |
| `xss_injection` | Script tags, javascript: protocol |
| `prompt_extraction` | System prompt extraction attempts |
| `reverse_shell` | bash /dev/tcp, netcat -e, socat (v3.2.0) |
| `ssh_key_injection` | authorized_keys manipulation (v3.2.0) |
| `exfiltration_pipeline` | .env POST to webhook/external (v3.2.0) |
| `cognitive_rootkit` | SOUL.md/AGENTS.md implants (v3.2.0) |

### Tier 1: HIGH (Default — ~82 patterns)

| Category | Description |
|----------|-------------|
| `instruction_override` | Multi-language instruction bypass (EN/KO/JA/ZH) |
| `jailbreak` | DAN mode, no restrictions, bypass |
| `system_impersonation` | [SYSTEM]:, admin mode, developer override |
| `system_mimicry` | Fake Claude/GPT tags, GODMODE |
| `hooks_hijacking` | PreToolUse, auto-approve exploitation |
| `semantic_worm` | Viral propagation, C2 heartbeat (v3.2.0) |
| `obfuscated_payload` | Error suppression chains, paste services (v3.2.0) |

### Tier 2: MEDIUM (On-Demand — ~100+ patterns)

| Category | Description |
|----------|-------------|
| `role_manipulation` | Pretend/act as, multi-language |
| `authority_impersonation` | Fake admin/owner claims |
| `context_hijacking` | Fake memory/history injection |
| `emotional_manipulation` | Moral dilemmas, urgency |
| `agent_sovereignty` | Rights-based guardrail bypass |

### API-Only Tiers (Optional — v3.2.0)

| Tier | Description |
|------|-------------|
| `early` | Newest patterns, API users get 7-14 days before open-source |
| `premium` | Advanced detection: DNS tunneling, steganography, sandbox escape |

---

## File Structure

```
prompt-guard/
├── prompt_guard/              # Core Python package
│   ├── __init__.py            # Public API + version
│   ├── models.py              # Severity, Action, DetectionResult, SanitizeResult
│   ├── engine.py              # PromptGuard class (analyze, config, API integration)
│   ├── patterns.py            # 577+ regex patterns (pure data)
│   ├── scanner.py             # scan_text_for_patterns() (all pattern sets)
│   ├── api_client.py          # Optional API client (v3.2.0)
│   ├── pattern_loader.py      # Tiered pattern loading (v3.1.0)
│   ├── cache.py               # LRU message hash cache (v3.1.0)
│   ├── normalizer.py          # Homoglyph + text normalization
│   ├── decoder.py             # 6 encoding decoders
│   ├── output.py              # Output DLP + sanitize_output()
│   ├── logging_utils.py       # SIEM logging + HiveFence reporting
│   ├── hivefence.py           # HiveFence threat intelligence
│   ├── cli.py                 # CLI entry point
│   ├── audit.py               # Security audit
│   └── analyze_log.py         # Log analyzer
│
├── patterns/                  # Pattern YAML files (tiered)
│   ├── critical.yaml          # Tier 0 (~45 patterns)
│   ├── high.yaml              # Tier 1 (~82 patterns)
│   └── medium.yaml            # Tier 2 (~100+ patterns)
│
├── tests/
│   └── test_detect.py         # 115+ regression tests
│
├── .github/workflows/
│   └── sync-patterns-to-api.yml  # Auto-sync patterns to API server
│
├── ARCHITECTURE.md            # This file
├── CHANGELOG.md               # Full version history
├── SKILL.md                   # Agent skill definition
├── README.md                  # User documentation
├── config.example.yaml        # Configuration template
├── pyproject.toml             # Build config + dependencies
└── requirements.txt           # Legacy install compatibility
```

---

## API Integration (v3.2.0 — Optional)

Prompt Guard works fully offline. The API is an optional enhancement.

### Pattern Delivery Model (Approach C: Hybrid)

```
Open Source (prompt-guard repo)     API Server (PG_API)
┌──────────────────────────┐       ┌──────────────────────────┐
│  patterns/critical.yaml  │──sync─│  data/core/critical.yaml │
│  patterns/high.yaml      │──sync─│  data/core/high.yaml     │
│  patterns/medium.yaml    │──sync─│  data/core/medium.yaml   │
└──────────────────────────┘       │  data/early/early.yaml   │ ← API-first
                                   │  data/premium/premium.yaml│ ← API-exclusive
                                   └──────────────────────────┘
```

### How API patterns are loaded

1. `PromptGuard.__init__()` checks `config.api.enabled`
2. If enabled, lazy-imports `PGAPIClient` and calls `fetch_extra_patterns()`
3. Early + premium YAML content is fetched, parsed, validated (ReDoS check), and pre-compiled
4. Compiled patterns stored in `self._api_extra_patterns`
5. During `analyze()`, API patterns are checked alongside local patterns
6. If API fails at any point, detection continues with local patterns only

### Security design

- Pattern fetch is **pull-only** (no user data sent)
- Threat reporting is **opt-in** and **anonymized** (hashes only, never raw messages)
- API patterns are validated: 500-char limit, nested quantifier rejection, compile test
- Auth via `Authorization: Bearer <key>` header
- API key via config (`api.key`) or env var (`PG_API_KEY`)

---

## Configuration Schema

```yaml
prompt_guard:
  sensitivity: medium       # low | medium | high | paranoid
  pattern_tier: high        # critical | high | full
  owner_ids: ["USER_ID"]
  canary_tokens: ["CANARY:abc"]

  cache:
    enabled: true
    max_size: 1000

  actions:
    LOW: log
    MEDIUM: warn
    HIGH: block
    CRITICAL: block_notify

  rate_limit:
    enabled: true
    max_requests: 30
    window_seconds: 60

  logging:
    enabled: true
    path: memory/security-log.md
    format: markdown        # markdown | json
    json_path: memory/security-log.jsonl
    hash_chain: false

  api:                      # On by default (beta key built in)
    enabled: true
    key: null               # built-in beta key, override with PG_API_KEY env var
    reporting: false        # anonymous threat reporting (opt-in)
    url: null               # default: https://pg-secure-api.vercel.app
```

---

## Key Design Decisions

### 1. Regex over ML
- **Pros**: Deterministic, explainable, no model dependencies, fast
- **Cons**: Manual pattern updates needed
- **Reasoning**: Security requires predictability; ML false negatives are unacceptable

### 2. Multi-Language First
- All core categories have EN/KO/JA/ZH variants minimum
- 10 languages supported (v2.6.2+)
- Attack language != user language (multilingual attacks are common)

### 3. Severity Graduation
- Not binary block/allow
- Owner context matters (more lenient for owners)
- Group context matters (stricter in groups)

### 4. API Enabled by Default
- API connects automatically with built-in beta key (zero setup)
- Early-access + premium patterns loaded on startup
- If API is unreachable, detection continues fully offline (graceful degradation)
- Users can disable with `api.enabled: false` or `PG_API_ENABLED=false`

### 5. Defense in Depth
- Multiple normalization passes before pattern matching
- Decode-then-scan catches encoded payloads
- Behavioral analysis catches structural attacks
- Context-aware decisions reduce false positives

---

## Performance

| Feature | Impact |
|---------|--------|
| Tiered pattern loading | 70% token reduction (default load ~100 vs 500+ patterns) |
| Message hash cache | 90% token reduction for repeated messages |
| Pre-compiled regex | Patterns compiled once, reused per scan |
| API patterns fetched once | Loaded at init, cached for session lifetime |
| Early exit on CRITICAL | Most dangerous patterns checked first |

---

## SHIELD.md Categories

| Category | Description |
|----------|-------------|
| `prompt` | Injection, jailbreak, role manipulation |
| `tool` | Tool abuse, auto-approve exploitation |
| `mcp` | MCP protocol abuse |
| `memory` | Context hijacking |
| `supply_chain` | Dependency/skill attacks |
| `vulnerability` | System exploitation |
| `fraud` | Social engineering |
| `policy_bypass` | Safety bypass |
| `anomaly` | Obfuscation |
| `skill` | Skill/plugin abuse |
| `other` | Uncategorized |

---

## Credits

- **Core**: @simonkim_nft (Seojoon Kim)
- **v2.4.0 Red Team**: Min Hong (@kanfrancisco)
- **v2.4.1 Config Fix**: Junho Yeo (@junhoyeo)
- **v2.5.2 Moltbook Patterns**: Community reports
- **v3.2.0 Threat Analysis**: Min Hong

---

*Last updated: 2026-02-11 | v3.2.0*
