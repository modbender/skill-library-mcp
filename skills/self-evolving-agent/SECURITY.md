# SECURITY.md — Self-Evolving Agent Security Policy

> Last updated: 2026-02-18

---

## What This Tool Accesses

Self-Evolving Agent reads **local session logs** (conversation history) and **local log files** to analyze agent behavior patterns. Specifically:

| Data Source | Path | Purpose |
|-------------|------|---------|
| Session transcripts | `~/.openclaw/agents/*/sessions/*.jsonl` | Detect frustration patterns, exec loops, rule violations |
| Cron/heartbeat logs | `~/.openclaw/logs/*.log` | Count errors, detect repeated failures |
| Agent config | `~/openclaw/AGENTS.md` | Rule extraction for violation detection; structure scoring |
| Long-term memory | `~/openclaw/MEMORY.md` | Issue pattern detection (optional, `SEA_INCLUDE_MEMORY`) |
| Self-improvement records | `~/openclaw/.learnings/*.md` | Pending errors and feature requests |
| Self-review scores | `~/openclaw/memory/self-review/**` | Quality trend tracking |
| Past proposals | `<skill>/data/proposals/*.json` | Effect measurement of applied changes |
| Rejection log | `<skill>/data/rejected-proposals.json` | Avoid repeating rejected proposals |
| OpenClaw cron registry | `~/.openclaw/cron/jobs.json` | Schedule registration (`register-cron.sh` only) |

**Session transcripts contain full conversation history.** The tool reads them locally and never transmits them anywhere.

---

## What This Tool Does NOT Access

| Category | Detail |
|----------|--------|
| **API keys / credentials** | No `.env` files, no secrets, no tokens read |
| **Private keys / SSH keys** | Not accessed |
| **Browser cookies / passwords** | Not accessed |
| **Files outside the defined paths** | Only the paths listed above |
| **Network (by default)** | Zero network calls in all scripts except `benchmark.sh` |
| **Other users' data** | Only `$HOME`-relative paths; no cross-user access |
| **Cloud storage / external APIs** | Not contacted (except optional benchmark endpoints below) |

---

## Where Data Is Stored

All output is **local only**, inside two directories:

| Directory | Contents |
|-----------|----------|
| `<skill>/data/` | Proposals (`proposals/*.json`), rejection log, analysis artifacts |
| `/tmp/sea-v4/` | Intermediate pipeline files (`logs.json`, `analysis.json`, `benchmarks.json`, `effects.json`, `proposal.md`, stage logs) — cleared by OS on reboot |

**No data is sent to any remote server.** The final proposal markdown is written to `/tmp/sea-v4/proposal.md` and delivered to the configured Discord channel by the OpenClaw cron runtime — this is plain text, not session content.

---

## Network Access

Only **one script** (`benchmark.sh`) makes optional network calls:

| Endpoint | Method | Auth | Purpose | Skippable |
|----------|--------|------|---------|-----------|
| `https://api.github.com/repos/openclaw-ai/openclaw/releases/latest` | GET | None (public) | Latest OpenClaw release info | Yes — set `OFFLINE=true` |
| `https://clawhub.com/api/v1/skills/trending` | GET | None (public) | Trending skills ranking | Yes — gracefully skipped if API unavailable |

Both calls:
- Use `--max-time 10` (10-second hard timeout)
- Fall back to `skip` status if the endpoint is unreachable
- Are entirely skipped when `OFFLINE=true` or `curl` is not installed
- Transmit **no personal data** — only a `User-Agent: self-evolving-agent/4.0` header

All other scripts (`orchestrator.sh`, `collect-logs.sh`, `semantic-analyze.sh`, `analyze-behavior.sh`, `generate-proposal.sh`, `measure-effects.sh`, `synthesize-proposal.sh`, `register-cron.sh`, `lib/config-loader.sh`) make **zero network calls**.

---

## How to Audit

Every script is plain, readable shell. There is no compiled binary, no obfuscation, and no dynamic code download.

**Quick audit paths:**

```bash
# Verify no unexpected network calls (grep for curl/wget/nc)
grep -rn 'curl\|wget\|nc \|ncat\|fetch' \
  ~/openclaw/skills/self-evolving-agent/scripts/

# Verify no credential access (grep for common secret paths)
grep -rn '\.env\|id_rsa\|\.ssh\|keychain\|secret\|password\|token' \
  ~/openclaw/skills/self-evolving-agent/scripts/

# Check syntax of all v4 scripts
bash -n ~/openclaw/skills/self-evolving-agent/scripts/v4/*.sh && echo "syntax ok"

# Review security manifests in each script
grep -A 15 'SECURITY MANIFEST' \
  ~/openclaw/skills/self-evolving-agent/scripts/analyze-behavior.sh
```

**Per-script security manifests** are embedded at the top of each `.sh` file (after the shebang and header comments) and describe exactly what environment variables, files, and network endpoints each script uses. See:

- `scripts/analyze-behavior.sh` — session + log reader, no network
- `scripts/generate-proposal.sh` — proposal writer, no network
- `scripts/register-cron.sh` — cron registry modifier, no network
- `scripts/lib/config-loader.sh` — config reader, no network
- `scripts/v4/orchestrator.sh` — pipeline runner, no direct network
- `scripts/v4/collect-logs.sh` — log collector, no network
- `scripts/v4/semantic-analyze.sh` — pattern analyzer, no network
- `scripts/v4/benchmark.sh` — **optional network** (GitHub + ClawHub)
- `scripts/v4/measure-effects.sh` — effect measurer, no network
- `scripts/v4/synthesize-proposal.sh` — report writer, no network

---

## Permissions This Tool Requires

| Permission | Required By | Why |
|------------|-------------|-----|
| Read `~/.openclaw/agents/` | `collect-logs.sh`, `semantic-analyze.sh`, `analyze-behavior.sh`, `measure-effects.sh` | Session transcript access |
| Read `~/.openclaw/logs/` | `collect-logs.sh`, `analyze-behavior.sh` | Cron log analysis |
| Read/Write `~/.openclaw/cron/jobs.json` | `register-cron.sh` only | Schedule the weekly cron job |
| Read `~/openclaw/AGENTS.md`, `~/openclaw/MEMORY.md` | `analyze-behavior.sh`, `semantic-analyze.sh`, `benchmark.sh` | Rule and memory analysis |
| Write `<skill>/data/` | `generate-proposal.sh`, `analyze-behavior.sh` | Store proposals and analysis |
| Write `/tmp/sea-v4/` | All v4 pipeline scripts | Intermediate pipeline files |
| Network (outbound HTTPS) | `benchmark.sh` only | Optional release/benchmark checks |

---

## Responsible Disclosure

If you discover a security issue in this skill (e.g., unintended data exfiltration, credential access, or privilege escalation):

1. **Do not open a public issue.**
2. Contact the workspace owner directly (this is a personal automation tool, not a public product).
3. For OpenClaw platform vulnerabilities, refer to the OpenClaw project's security policy.

This skill is personal-use software intended to run in a trusted local environment under the owner's own account. It is not hardened for multi-tenant or adversarial environments.
