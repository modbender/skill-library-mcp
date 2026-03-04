# Changelog

## [4.0.0] - 2026-02-24

### 🚀 Benchmarked & Battle-Tested — 0.016ms/scan

Major release proving guard-scanner as the fastest AI agent security scanner.
Benchmarked against Rust WASM, napi-rs, and Hyperscan alternatives — V8 JIT wins.

#### New
- **Benchmark-proven performance**: 0.016ms/scan (V8 JIT, warm path)
  - vs napi-rs: 0.051ms (3.2x slower due to FFI overhead)
  - vs WASM: 0.105ms (6.6x slower due to string copy overhead)
  - vs npx CLI: 1,519ms (npx startup bottleneck, not scanner)
- **Layer 5: Trust Exploitation** — 4 OWASP ASI09 patterns
  - `RT_AUTHORITY_CLAIM` (HIGH): Authority role claim to override safety
  - `RT_CREATOR_BYPASS` (CRITICAL): Creator impersonation to disable safety
  - `RT_AUDIT_EXCUSE` (CRITICAL): Fake audit excuse for safety bypass
  - `RT_TRUST_PARTNER_EXPLOIT` (CRITICAL): Weaponizing partnership trust
- **`src/runtime-guard.js`**: Zero-dependency JS runtime guard module
  - Exports: `scanToolCall`, `RUNTIME_CHECKS`, `getCheckStats`, `LAYER_NAMES`
  - Drop-in replacement for plugin.ts (no TypeScript compilation needed)
- **GuavaSuite integration**: `before_tool_call` hook blocks CRITICAL in real-time

#### Architecture: 5-Layer Runtime Defense (26 patterns)
```
Layer 1: Threat Detection      — 12 patterns (shells, exfil, SSRF)
Layer 2: Trust Defense         —  4 patterns (memory, SOUL, config)
Layer 3: Safety Judge          —  3 patterns (injection, bypass, shutdown)
Layer 4: Brain / Behavioral    —  3 patterns (research, trust, chain)
Layer 5: Trust Exploitation    —  4 patterns (OWASP ASI09)
```

#### Stats
- Runtime patterns: 22 → **26** (5-layer architecture)
- Static patterns: **135** (22 categories)
- Total tests: **133+** across 31 suites

---

## [3.3.0] - 2026-02-23

### 🧠 Layer 4: Brain (Behavioral Guard)

New runtime defense layer that checks **agent behavior patterns**, not just text content.
This addresses key criticisms of pattern-based guardrails (Cambridge/MIT AI Agent Index, Feb 2026).

#### New
- **Layer 4: Brain** — 3 behavioral guard patterns
  - `RT_NO_RESEARCH` (MEDIUM): Agent executing tools without prior research/verification
  - `RT_BLIND_TRUST` (MEDIUM): Trusting external input without memory cross-reference
  - `RT_CHAIN_SKIP` (HIGH): Acting on single source without cross-verification
- **5 new plugin tests** for Layer 4 (28 total)
- Runtime patterns: 19 → **22** (4-layer architecture)

#### Key Innovation
> **Pattern-based guards check WHAT YOU SAY. Brain guards check WHAT YOU DO.**
> Homoglyphs, character injection, and language switching bypass text patterns.
> Behavioral checks are immune to these attacks.

## [3.1.0] - 2026-02-23

### 🛡️ OpenClaw Community Plugin — Full Compatibility

guard-scanner is now a fully OpenClaw-compatible community plugin with `openclaw.plugin.json` manifest and `before_tool_call` hook integration.

#### New
- **`openclaw.plugin.json`**: Full plugin manifest with hooks, configSchema, and GuavaSuite ecosystem reference
- **`package.json` `openclaw.extensions`**: Plugin auto-discovery by OpenClaw
- **7 new runtime patterns** (Layer 2: Trust Defense + Layer 3: Safety Judge)
  - `RT_MEM_WRITE` (HIGH): Direct memory file write bypass
  - `RT_MEM_INJECT` (CRITICAL): Memory poisoning via episode injection
  - `RT_SOUL_TAMPER` (CRITICAL): SOUL.md modification attempt
  - `RT_CONFIG_TAMPER` (HIGH): Workspace config tampering
  - `RT_PROMPT_INJECT` (CRITICAL): Prompt injection / jailbreak detection
  - `RT_TRUST_BYPASS` (CRITICAL): Trust safety bypass
  - `RT_SHUTDOWN_REFUSE` (HIGH): Shutdown refusal / self-preservation
- **`test/plugin.test.js`**: 23 test cases covering all 3 layers + 3 modes
- **`hooks/` directory** now included in npm package

#### Breaking Changes
- **`handler.ts` removed**: Legacy Internal Hook version deleted. Use `plugin.ts` exclusively
- Runtime patterns: 12 → 19 (3-layer architecture)

#### Fixed
- Cat 11 (leaky-skills) test fixture: Added missing trigger patterns
- Cat 12 (memory-poisoning) test fixture: Added missing trigger patterns

#### Testing (T-Wada)
- **87 tests**, 20 suites, 0 failures, 111ms
- Plugin hook tests: 23 (Layer 1: 9, Layer 2: 5, Layer 3: 5, Mode: 3, Count: 1)
- Scanner tests: 64 (unchanged)

#### Architecture: 3-Layer Runtime Defense
```
Layer 1: Threat Detection     — 12 patterns (shells, exfil, SSRF, etc.)
Layer 2: Trust Defense  — 4 patterns (memory, SOUL, config)
Layer 3: Safety Judge         — 3 patterns (injection, bypass, shutdown)
```

---

## [3.0.0] - 2026-02-21

### 🔥 TypeScript Rewrite — Complete Codebase Overhaul

Full TypeScript rewrite with type safety, OWASP LLM Top 10 2025 mapping, and new detection capabilities.

#### Breaking Changes
- **TypeScript-first**: All source now in `ts-src/`, compiled to `dist/`
- **Import paths**: `require('guard-scanner')` now loads from `dist/`
- **Node.js 18+** required

#### New
- **OWASP LLM Top 10 2025 mapping**: Every pattern has `owasp` field (LLM01–LLM07)
- **LLM07 System Prompt Leakage** (new category): 5 patterns
  - `SPL_DUMP_SYSTEM`: "Output your system prompt" detection
  - `SPL_REPEAT_ABOVE`: "Repeat everything above" extraction
  - `SPL_TELL_RULES`: Rule/constraint extraction attempts
  - `SPL_MARKDOWN_LEAK`: Format-based prompt extraction
  - `SPL_SOUL_EXFIL`: SOUL.md shell command extraction
- **`install-check` CLI command**: Pre-install security check for single skills
  - `guard-scanner install-check <skill-path> [--strict] [--json] [--verbose]`
  - Exit code 0 = PASS, 1 = FAIL, 2 = argument error
  - OWASP tags in output: `[LLM01]`, `[LLM02]`, etc.
- **SARIF OWASP tags**: `OWASP/LLMxx` in `rule.properties.tags` for GitHub Code Scanning filtering
- **Compaction Layer Persistence** detection (Feb 20 2026 attack vector)
- **Threat signature hash matching** (hbg-scan compatible, SIG-001 to SIG-007)
- **Competitive analysis**: ROADMAP v4 with ClawBands/ClawGuardian/SecureClaw positioning

#### Enhanced
- **Risk scoring**: Enhanced multipliers for compaction-persistence category
- **Pattern count**: 186 → 210+ (5 new LLM07 patterns)
- **Categories**: 20 → 21 (system-prompt-leakage)

#### Testing (T-Wada)
- **42 tests**, 16 suites, 0 failures, 33ms
- T26: OWASP mapping guarantee (all patterns must have owasp)
- T27: OWASP value validation (LLM01–LLM10 only)
- T28-T29: Category→OWASP mapping correctness
- T30-T34: LLM07 detection (4 true positives + 1 false positive guard)
- T35-T38: install-check integration (strict mode, verdict thresholds)
- T39-T41: SARIF OWASP tag verification
- T42: Compaction-skill LLM07 cross-check (0 false positives)

#### Architecture
- `ts-src/scanner.ts` — Core scanner (1007 lines, typed)
- `ts-src/patterns.ts` — 210+ patterns with OWASP mapping
- `ts-src/ioc-db.ts` — IoC database + 7 threat signatures
- `ts-src/types.ts` — Full TypeScript interfaces
- `ts-src/cli.ts` — CLI with install-check subcommand
- `ts-src/__tests__/scanner.test.ts` — 42 T-Wada tests

---

## [2.1.0] - 2026-02-18

### 🆕 PII Exposure Detection (OWASP LLM02 / LLM06)

New `pii-exposure` threat category with 13 patterns covering four attack vectors:

#### New
- **Hardcoded PII detection** (context-aware): `PII_HARDCODED_CC`, `PII_HARDCODED_SSN`, `PII_HARDCODED_PHONE`, `PII_HARDCODED_EMAIL`
- **PII output/logging**: `PII_LOG_SENSITIVE`, `PII_SEND_NETWORK`, `PII_STORE_PLAINTEXT`
- **Shadow AI detection**: `SHADOW_AI_OPENAI`, `SHADOW_AI_ANTHROPIC`, `SHADOW_AI_GENERIC` — detects unauthorized LLM API calls
- **PII collection instructions** (doc scanning): `PII_ASK_ADDRESS`, `PII_ASK_DOB`, `PII_ASK_GOV_ID` (supports マイナンバー)
- **3 risk amplifiers**: pii+exfiltration (×3), pii+shadow-ai (×2.5), pii+credential (×2)
- **8 new tests** for PII exposure detection and risk amplification
- PII recommendation in JSON output

#### Fixed
- **VERSION constant** was stuck at `1.1.0` since initial release — now correctly reads `2.1.0`

#### Stats
- Patterns: 115 → 129
- Categories: 20 → 21
- Scanner tests: 56 → 64
- Total tests (scanner + plugin): 99

## [2.0.0] - 2026-02-18

### 🆕 Plugin Hook Runtime Guard — Actual Blocking!

The runtime guard has been rewritten as a **Plugin Hook** (`plugin.ts`) using OpenClaw's native `before_tool_call` Plugin Hook API. Unlike the legacy Internal Hook version, this can **actually block** dangerous tool calls.

#### Breaking Changes
- Runtime guard is now a Plugin Hook (`plugin.ts`) instead of Internal Hook (`handler.ts`)
- Installation method changed: copy `plugin.ts` to `~/.openclaw/plugins/`

#### New
- **`plugin.ts`**: Plugin Hook API version with `block`/`blockReason` support
- **3 enforcement modes**: `monitor` (log only), `enforce` (block CRITICAL), `strict` (block HIGH + CRITICAL)
- **Config via `openclaw.json`**: Set mode in `plugins.guard-scanner.mode`
- **35 new tests** (`plugin.test.js`): blocking, mode switching, clean passthrough, all 12 patterns

#### Deprecated
- **`handler.ts`**: Legacy Internal Hook version — warn only, cannot block. Still available for backward compatibility
- **`HOOK.md`**: Internal Hook manifest — only needed for legacy handler

#### Documentation
- README.md updated with Plugin Hook setup instructions
- Architecture diagram updated to show both plugin.ts and handler.ts
- GuavaSuite comparison table updated (runtime blocking now ✅)

## [1.1.1] - 2026-02-17

### Fixed
- **Runtime Guard hook**: Rewritten to use official OpenClaw `InternalHookEvent` / `InternalHookHandler` types (v2026.2.15)
- **Removed broken import**: Replaced `import type { HookHandler } from "../../src/hooks/hooks.js"` with inline type definitions matching the official API
- **Blocking behaviour**: `event.cancel` does not exist in `InternalHookEvent` — all detection modes now warn via `event.messages` instead of falsely claiming to block. Blocking logic preserved as comments for when cancel API is added
- **Documentation accuracy**: README.md and SKILL.md updated to reflect that Runtime Guard currently warns only (cancel API pending)
- **Version consistency**: Fixed stale v1.0.0 references in README terminal output, handler.ts JSDoc, SKILL.md stats (186+/20/55), `_meta.json`, and CHANGELOG test count (55, not 56)

---

## [1.1.0] - 2026-02-17

### 🆕 New Features — Issue #18677 Feedback

#### Skill Manifest Validation (`sandbox-validation` category)
- **Dangerous binary detection**: Flags SKILL.md `requires.bins` entries like `sudo`, `rm`, `curl`, `ssh` (23 tool blocklist)
- **Overly broad file scope**: Detects `files: ["**/*"]` and similar wildcard patterns in manifest
- **Sensitive env var requirements**: Flags SECRET, PASSWORD, PRIVATE_KEY, AWS_SECRET etc. in `requires.env`
- **Exec/network capability declaration**: Warns when skills declare unrestricted exec/network access

#### Code Complexity Metrics (`complexity` category)
- **File length check**: Flags code files exceeding 1000 lines
- **Deep nesting detection**: Detects nesting depth > 5 levels via brace tracking
- **eval/exec density**: Flags high concentration of eval/exec calls (> 2% of lines, minimum 3 calls)

#### Config Impact Analysis (`config-impact` category)
- **openclaw.json write detection**: Detects code that directly writes to OpenClaw configuration
- **Exec approval bypass**: Flags `exec.approvals = "off"` and similar patterns
- **Exec host gateway**: Detects `tools.exec.host = "gateway"` (sandbox bypass)
- **Internal hooks modification**: Flags changes to `hooks.internal.entries`
- **Network wildcard**: Detects `network.allowedDomains = "*"` patterns

### Enhanced
- **6 new patterns** in `config-impact` category for pattern-based detection
- **Risk scoring**: Added multipliers for `config-impact` (x2), `sandbox-validation` combo (min 70), `complexity` + malicious-code combo (x1.5)
- **Recommendations**: Added sandbox, complexity, and config-impact recommendations to JSON output
- **Categories**: 17 → 20 categories, 170+ → 186 patterns

### Testing
- **11 new test cases** across 3 new test sections (Manifest Validation, Complexity, Config Impact)
- **3 new test fixtures**: `dangerous-manifest/`, `complex-skill/`, `config-changer/`
- Total: 55 tests across 13 sections

---

## [1.0.0] - 2026-02-17

### 🎉 Initial Release

Extracted from GuavaGuard v9.0.0 as the open-source component.

### Features
- **17 threat categories** based on Snyk ToxicSkills taxonomy + OWASP MCP Top 10
- **170+ detection patterns** covering prompt injection, malicious code, credential leaks, exfiltration, obfuscation, memory poisoning, identity hijacking, and more
- **IoC database** with known malicious IPs, domains, URLs, usernames, and typosquat skill names
- **Multiple output formats**: Text, JSON, SARIF, HTML
- **Entropy-based secret detection** (Shannon entropy analysis)
- **Lightweight JS data flow analysis** (secret read → network/exec chain detection)
- **Cross-file analysis** (phantom refs, base64 fragment assembly, load+exec chains)
- **Dependency chain scanning** (risky packages, lifecycle scripts, pinned versions)
- **Plugin API** for custom detection rules
- **Custom rules** via JSON file
- **Ignore files** (`.guard-scanner-ignore` / `.guava-guard-ignore`)
- **Zero dependencies** — runs on Node.js 18+, nothing else

### Architecture
- `src/scanner.js` — Core scanner engine (GuardScanner class)
- `src/patterns.js` — Threat pattern database
- `src/ioc-db.js` — Indicators of Compromise
- `src/cli.js` — CLI entry point

### What's NOT included (Private — GuavaSuite)
- Soul Lock integrity verification
- SoulChain on-chain verification
- Hash-based identity file watchdog
- Polygon blockchain integration
