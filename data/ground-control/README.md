# 🛰️ ground-control

> Post-upgrade verification for OpenClaw. Your system's pre-flight checklist.

## The Problem

OpenClaw upgrades can silently change your configuration. A new version might reset your primary model, alter cron job schemas, or break channel routing. You won't notice until something stops working.

## The Solution

**ground-control** is a two-part system:

1. **MODEL_GROUND_TRUTH.md** — A single file that declares what your system *should* look like: which models are registered, what every cron job runs, which channels are active.

2. **post-upgrade-verify.md** — A 5-phase automated verification that compares your running system against the ground truth and auto-repairs drift.

```
┌─────────────────────────────────────────────┐
│           MODEL_GROUND_TRUTH.md             │
│         (what you WANT your system          │
│              to look like)                  │
└──────────────────┬──────────────────────────┘
                   │  compare
                   ▼
┌─────────────────────────────────────────────┐
│         OpenClaw Runtime State              │
│       (what your system ACTUALLY is)        │
└──────────────────┬──────────────────────────┘
                   │  drift?
                   ▼
              ┌────┴────┐
              │ Phase 1  │  Config Integrity    → auto-fix
              │ Phase 2  │  API Key Liveness    → report only
              │ Phase 3  │  Cron Integrity      → auto-fix
              │ Phase 4  │  Session Smoke Test  → report only
              │ Phase 5  │  Channel Liveness    → report only
              └────┬────┘
                   │
                   ▼
            📊 Verification Report
            → Discord #ops-health
            → memory/YYYY-MM-DD.md
```

## Design Philosophy

> **OpenClaw maintains itself. We only verify the result.**

- All checks use OpenClaw's native tools (`gateway config.get`, `cron list`, `sessions_spawn`, `message`)
- No external scripts, no manual curl, no bypassing the runtime
- Auto-repair for config and cron drift (Phases 1 & 3)
- Report-only for API keys and channels (Phases 2 & 5) — these need human judgment
- Ground truth is the single source of truth — change config, update ground truth

## The 5 Phases

### Phase 1: Config Integrity
Compares `gateway config.get` output against GROUND_TRUTH. Checks primary model, registered models, compaction mode, context pruning, heartbeat interval, ACP config, and channel policies. **Auto-fixes drift** via `gateway config.patch`.

### Phase 2: API Key & Provider Liveness
Tests each LLM provider by spawning a minimal `sessions_spawn` request through OpenClaw's own routing layer — not by manually curling APIs. Non-LLM providers (Brave, Notion, etc.) are tested via env-injected curl. **Reports only** — key issues need human intervention.

### Phase 3: Cron Integrity
Compares `cron list` against GROUND_TRUTH's recurring job definitions. Checks model, schedule, delivery target, and enabled status. **Auto-fixes drift** via `cron update`. Ignores one-shot (`deleteAfterRun`) jobs. Enforces the "no Opus in cron" rule.

### Phase 4: Session Smoke Test
Spawns a single isolated Flash session with a trivial task. If it responds, the session system works. **Reports only.**

### Phase 5: Channel Liveness
Sends a test message to each configured channel (Discord, WhatsApp, etc.). WhatsApp tests run in isolated sessions due to cross-context restrictions. **Reports only.**

## Setup

### 1. Create your ground truth

Copy `templates/MODEL_GROUND_TRUTH.md` to your workspace root:

```bash
cp skills/ground-control/templates/MODEL_GROUND_TRUTH.md \
   ~/.openclaw/workspace/MODEL_GROUND_TRUTH.md
```

Edit it to match your actual system. The template has comments explaining each section.

### 2. Add the sync rule to AGENTS.md

Add this block to your `AGENTS.md` so the agent reminds you to update ground truth when config changes:

```markdown
## 🔒 GROUND_TRUTH Sync Rule

**Every time config changes (model/cron/channel/acp), remind to sync `MODEL_GROUND_TRUTH.md`.**
- After modification → ask: "Want me to update GROUND_TRUTH too?"
- If yes → update immediately
- If no → log as todo in daily diary
```

### 3. Run verification

Tell your agent:

```
/verify
```

Or have it read `scripts/post-upgrade-verify.md` and execute.

### 4. Integrate into upgrade flow

See `scripts/UPGRADE_SOP.md` for the complete pre/during/post upgrade procedure.

## Report Format

```
🔍 Post-Upgrade Verification Report
📦 Version: v2026.3.2 (from v2026.3.1)
⏱️ 2026-03-02 11:34 PST

Phase 1: Config Integrity     ⚠️ AUTO-FIXED 9/9
  ❌→✅ removed stale model, updated aliases
Phase 2: Provider Liveness    ✅ 5/6
  X/Twitter: ⚠️ free tier limit
Phase 3: Cron Integrity       ✅ 17/17 recurring jobs
Phase 4: Session Smoke Test   ✅
Phase 5: Channel Liveness     ✅ Discord | ⏭️ WhatsApp

Overall: ⚠️ DEGRADED (auto-fixed)
```

## Cost

One full verification run costs ~$0.005 (Flash model for session tests + minimal API probes).

## File Structure

```
ground-control/
├── SKILL.md                          # Skill metadata
├── README.md                         # This file
├── CHANGELOG.md                      # Version history
├── templates/
│   └── MODEL_GROUND_TRUTH.md         # Ground truth template (copy to workspace)
└── scripts/
    ├── post-upgrade-verify.md        # 5-phase verification agent prompt
    └── UPGRADE_SOP.md                # Upgrade standard operating procedure
```

## Security Model

### Credential Handling

Phase 2 can test non-LLM provider API keys (Brave, Notion, etc.). The credential flow has these guardrails:

| Layer | Control |
|-------|---------|
| **Declaration** | Only env vars named in YOUR `MODEL_GROUND_TRUTH.md` → `non_llm_providers[].env_var` are read. No enumeration, no scanning. |
| **Endpoint validation** | Each provider entry requires an `allowed_domain`. Before every curl, the hostname is extracted and compared exactly. Mismatch = skip + report ❌. |
| **Transport** | HTTPS only. Credentials sent as headers only — never in URL params or POST body. |
| **Logging** | Env var values are never logged, written to memory, or included in reports. Only status codes are reported. |
| **Opt-in** | If your GROUND_TRUTH has no `non_llm_providers` section, these checks are skipped entirely. |

### Why env vars aren't declared in registry metadata

The set of API keys depends on which non-LLM providers *you* use — it varies per installation. This is analogous to Terraform declaring `variable` blocks at plan time rather than in the provider registry. The skill's metadata declares `credentials.mode: user-declared` to make this pattern explicit.

### Auto-fix Scope

Phases 1 (config) and 3 (cron) can auto-patch your runtime. Controls:
- `--dry-run` disables all auto-fix (report-only mode)
- If >3 fields need fixing, the agent pauses for human confirmation
- Every fix logs before/after values in the report
- Phases 2 and 5 are **never** auto-fixed

## License

MIT
