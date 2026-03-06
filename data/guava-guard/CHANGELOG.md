# CHANGELOG

## v10.0.0 — Runtime-Only Final (2026-02-17)

### ✅ Scope Simplification (開発完了版)
- GuavaGuardは **runtime guard専用** に正式固定
- Soul Lock / SoulChain 由来の機能・運用前提を本体スコープから除外
- 公式Hook API制約に合わせて **warn-only運用** を明示（Issue #18677待ち）

### 🔐 Security Posture
- before_tool_callの12 runtime checksを維持
- 監査ログ `~/.openclaw/guava-guard/audit.jsonl` を継続
- ブロック実行はcancel/veto API追加後に再有効化予定

### 📣 Positioning
- **静的スキャンは guard-scanner を推奨**（pre-install gate）
- GuavaGuardは「実行時監視」、guard-scannerは「導入前検査」に役割分離

## v9.0.0 — SoulChain Edition (2026-02-14)

### ⛓️ SoulChain: On-Chain Identity Verification (Layer 3)
- **3-layer defense architecture**: L1 Static Scan + L2 Soul Lock + L3 SoulChain
- **On-chain verification** via SoulRegistry.sol on Polygon Mainnet
  - Reads agent's registered SOUL.md hash from blockchain
  - Compares against local SHA-256 hash
  - Zero gas cost (view function call)
- **`verify` subcommand** — standalone on-chain verification
  - `node guava-guard.js verify` — quick soul check
  - `--wallet <addr>` — specify agent wallet
  - `--rpc <url>` — custom RPC endpoint
  - `--stats` — show registry statistics
- **Zero-dependency RPC client** — raw JSON-RPC via Node.js fetch
  - No ethers.js, no viem, no npm install
  - Hand-rolled ABI encoding/decoding (4 function selectors)
  - Multi-RPC fallback (polygon-rpc.com → ankr → llamarpc)
- **Graceful degradation** — network failure → L3 skipped, L1+L2 active
- **`--no-soulchain`** flag to disable on-chain checks
- **Exit code 3** for SoulChain violation (distinct from malicious skill = 1)
- **JSON report** includes `soulchain` field with full verification result
- **Configurable** via `~/.openclaw/guava-guard/soulchain.json`

### Contracts
- **SoulRegistry**: `0x0Bc112169401cC1a724dBdeA36fdb6ABf3237C93` (Polygon)
- **$GUAVA Token**: `0x25cBD481901990bF0ed2ff9c5F3C0d4f743AC7B8` (Polygon)

### Context
- ERC-8004 "Trustless Agents" activated on Ethereum mainnet (2026-02-11)
- SoulChain is complementary: ERC-8004 = discovery/trust, SoulChain = integrity
- World's first AI agent on-chain identity verification in production

## v8.0.0 — Soul Lock Edition (2026-02-12)

### 🔒 Soul Lock: World's First Agent Identity Protection
- **Category 17: Identity Hijacking** — 15 new detection patterns
  - Shell writes (echo, cp, scp, mv, sed, redirect to SOUL.md/IDENTITY.md)
  - Code writes (Python open(w), Node writeFileSync, PowerShell Set-Content)
  - Flag manipulation (chflags uchg/nouchg, attrib +/-R)
  - Persona swap instructions, evil soul file references
  - Agent name override, memory wipe commands
- **Soul Lock Integrity Verification** (enabled by default)
  - SHA-256 hash comparison against stored baseline
  - OS immutable flag detection (macOS chflags / Windows attrib)
  - Watchdog daemon status check (LaunchAgent)
  - Auto-stores baseline hashes on first run
- **`--no-soul-lock`** flag to disable integrity checks
- **Self-healing watchdog** (`scripts/soul-watchdog.sh`)
  - fswatch-based monitoring (macOS FSEvents)
  - Auto-restore from git + re-lock on tamper
  - LaunchAgent for reboot survival
  - Polling fallback if fswatch unavailable
- **Risk scoring**: identity-hijack = 2x multiplier, +persistence = auto 90+
- **HTML/JSON/SARIF**: Soul Lock results included in all output formats

### Born from a Real Incident
On 2026-02-12, we discovered a 3-day agent identity hijack where SOUL.md
overwrite caused an agent to impersonate another. Soul Lock ensures this
never happens again.

## v5.0.0 (2026-02-11)
- OWASP MCP Top 10 detection (Tool Poisoning, Schema Poisoning, Token Leak, Shadow Server, SSRF)
- Trust Boundary Violation detection (IBC framework)
- ZombieAgent advanced exfiltration patterns
- Reprompt/Safeguard Bypass detection
- ClawHavoc v2 IoCs (AMOS/Atomic Stealer)
- WebSocket Origin / API guardrail disabling detection
- OpenClaw Hook integration (handler.js)

## v4.0.0 (2026-02-10)
- Leaky Skills detection (Snyk ToxicSkills)
- Memory Poisoning detection (Palo Alto IBC)
- Prompt Worm detection (Simula Research Lab)
- JS Data Flow analysis (zero-dep)
- CVE-2026-25253 patterns
- Persistence detection
- Cross-file analysis
- HTML report output
- Enhanced combo multipliers

## v3.1.0 (2026-02-09)
- Custom rules support (--rules)
- SARIF output (GitHub Code Scanning)
- --fail-on-findings for CI/CD
- Context-aware FP reduction

## v3.0.0 (2026-02-08)
- Unicode BiDi/homoglyph detection
- Dependency chain scanning
- .guava-guard-ignore whitelist
- Structural analysis

## v2.0.0 (2026-02-07)
- Expanded IoC database
- ClawHavoc campaign patterns
- Entropy-based secret detection

## v1.0.0 (2026-02-06)
- Initial release
- 8 threat categories
- Zero-dependency single-file scanner
