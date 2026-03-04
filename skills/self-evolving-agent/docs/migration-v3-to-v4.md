# Migration Guide: v3 → v4

This guide is for users running v3 (the `analyze-behavior.sh` + `generate-proposal.sh` architecture) who want to upgrade to v4 (the multi-stage orchestrator pipeline).

---

## What Changed

### Architecture

| Area | v3 | v4 |
|---|---|---|
| Entry point | `scripts/analyze-behavior.sh` | `scripts/v4/orchestrator.sh` |
| Analysis | Monolithic Python inside `analyze-behavior.sh` | Separate stages: `collect-logs.sh` → `semantic-analyze.sh` → `benchmark.sh` → `measure-effects.sh` → `synthesize-proposal.sh` |
| Delivery | `generate-proposal.sh` (Discord only) | `deliver.sh` (Discord, Slack, Telegram, Webhook) |
| Cron message | calls `generate-proposal.sh` | calls `scripts/v4/orchestrator.sh` |
| Temp files | `/tmp/self-evolving-analysis.json` (single file) | `/tmp/sea-v4/` directory (per-stage files) |

### Config Format

`config.yaml` changed the `complaint_patterns` field from a flat list to a language-separated structure:

**v3 (flat list):**
```yaml
analysis:
  complaint_patterns:
    - "다시"
    - "아까"
    - "you forgot"
    - "again?"
```

**v4 (ko/en structure with auto-detect):**
```yaml
analysis:
  complaint_patterns:
    ko:
      - "말했잖아"
      - "왜 또"
      - "다시 또"
    en:
      - "you forgot"
      - "how many times"
      - "still not working"
    auto_detect: true   # Detects language from session content automatically
```

### Cron Registration

v3 registered a cron that ran `generate-proposal.sh`. v4 updates the cron message to call `orchestrator.sh`:

**v3 cron message:**
```
bash ~/openclaw/skills/self-evolving-agent/scripts/generate-proposal.sh
```

**v4 cron message:**
```
bash ~/openclaw/skills/self-evolving-agent/scripts/v4/orchestrator.sh 2>/dev/null || echo '분석 실패'

위 스크립트 실행 결과를 그대로 출력하세요.
⛔ message 도구 호출 절대 금지. 텍스트 출력만.
```

### New `delivery` Section

v4 adds a `delivery` block to `config.yaml` for multi-platform output:

```yaml
delivery:
  platform: "discord"   # discord | slack | telegram | webhook

  slack:
    webhook_url: ""
  telegram:
    bot_token: ""
    chat_id: ""
  webhook:
    url: ""
    method: "POST"
```

---

## Step-by-Step Migration

### Step 1 — Back Up Your Proposal Data

```bash
cp -r ~/openclaw/skills/self-evolving-agent/data/proposals/ \
       ~/openclaw/skills/self-evolving-agent/data/proposals.v3-backup/
```

Also back up your current `config.yaml`:

```bash
cp ~/openclaw/skills/self-evolving-agent/config.yaml \
   ~/openclaw/skills/self-evolving-agent/config.yaml.v3-backup
```

### Step 2 — Update config.yaml

Open your `config.yaml` and update the `complaint_patterns` section.

**Find:**
```yaml
  complaint_patterns:
    - "다시"
    - "you forgot"
    # ... your patterns
```

**Replace with:**
```yaml
  complaint_patterns:
    ko:
      - "말했잖아"
      - "했잖아"
      - "이미 말했"
      - "왜 또"
      - "다시 또"
      - "다시 해야"
      - "몇 번"
      - "또?"
      - "저번에도"
      - "왜 자꾸"
      - "또 그러네"
      - "안 되잖아"
      - "물어보지 말고"
      - "전부 다 해줘"
    en:
      - "you forgot"
      - "again?"
      - "same mistake"
      - "stop doing that"
      - "how many times"
      - "wrong again"
      - "you already"
      - "I told you"
      - "still broken"
      - "not what I asked"
      - "still not working"
      - "told you"
      - "as I said"
    auto_detect: true
```

> **Tip:** Copy your custom patterns from the backup. Put Korean patterns under `ko:` and English under `en:`. If you used mixed patterns, split them by language.

Also **add** the `delivery` block at the end of your `config.yaml` if it's missing:

```yaml
delivery:
  platform: "discord"

  discord:
    channel_id: ""   # Your Discord channel ID (same as cron.discord_channel)

  slack:
    webhook_url: ""
  telegram:
    bot_token: ""
    chat_id: ""
  webhook:
    url: ""
    method: "POST"
    headers:
      Content-Type: "application/json"
```

### Step 3 — Re-Register the Cron

The v4 cron calls `orchestrator.sh` instead of `generate-proposal.sh`. Update it:

```bash
cd ~/openclaw/skills/self-evolving-agent

# Remove the old v3 cron entry
bash scripts/register-cron.sh --remove

# Register the new v4 cron (reads schedule/channel from config.yaml)
bash scripts/register-cron.sh
```

If you want to verify the update without removing first:

```bash
bash scripts/register-cron.sh --update
```

> **Note:** `register-cron.sh` now reads `cron.schedule`, `cron.model`, `cron.discord_channel`, and `cron.agent_id` from `config.yaml`. Make sure these are set before running.

### Step 4 — Verify the Pipeline

Run the orchestrator manually to check all stages work:

```bash
# Dry run (no LLM calls, fast)
DRY_RUN=true VERBOSE=true \
  bash ~/openclaw/skills/self-evolving-agent/scripts/v4/orchestrator.sh
```

Expected output in verbose mode:
```
[SEA-v4 HH:MM:SS] === SEA v4.0 오케스트레이터 시작 (sea-v4-YYYYMMDD-HHMMSS) ===
[SEA-v4 HH:MM:SS] 스테이지 시작: collect_logs
[SEA-v4 HH:MM:SS] 스테이지 완료: collect_logs (Xs)
[SEA-v4 HH:MM:SS] 스테이지 시작: semantic_analyze
...
[SEA-v4 HH:MM:SS] 스테이지 완료: synthesize (Xs)
[SEA-v4 HH:MM:SS] 완료: Xs | 에러: 0건
```

If a stage shows `failed`, check the log:
```bash
cat /tmp/sea-v4/stage-<name>.log
```

---

## Breaking Changes

| # | What broke | How to fix |
|---|---|---|
| 1 | `complaint_patterns` is now a dict (`ko`/`en` keys), not a flat list | Restructure your patterns as shown in Step 2 |
| 2 | Cron calls `orchestrator.sh`, not `generate-proposal.sh` | Re-register cron with `--remove` + fresh register |
| 3 | Temp output is `/tmp/sea-v4/` (was `/tmp/self-evolving-analysis.json`) | Update any custom scripts that read from the old path |
| 4 | `delivery` config block is now required for non-Discord platforms | Add the `delivery:` section to config.yaml |
| 5 | `scripts/generate-proposal.sh` is no longer the main entry point | Use `scripts/v4/orchestrator.sh` instead |

---

## FAQ

### Will my old proposals still work?

**Yes.** `measure-effects.sh` reads both the old `data/proposals/*.json` format and the new format. Your historical proposals will still be picked up for effect measurement — the script is backwards-compatible.

### My custom `complaint_patterns` — do I lose them?

**No.** Just copy them from your `config.yaml.v3-backup` into the appropriate `ko:` or `en:` section.

### Can I keep running `analyze-behavior.sh` directly?

**Yes, for now.** The v3 scripts still exist and still work. But they won't produce the richer multi-stage output, effect measurement, or multi-platform delivery that v4 provides. The old scripts are not actively maintained going forward.

### Do I need to re-run `make install` or copy files again?

**No.** The v4 scripts are already in place under `scripts/v4/`. The migration is just config + cron re-registration.

### The cron ran but I got "분석 실패" in Discord. What now?

Run manually with `VERBOSE=true` to see which stage failed:

```bash
VERBOSE=true bash ~/openclaw/skills/self-evolving-agent/scripts/v4/orchestrator.sh
```

Then check the specific stage log:

```bash
ls /tmp/sea-v4/stage-*.log
cat /tmp/sea-v4/stage-collect_logs.log   # example
```

### I use Slack / Telegram, not Discord. What do I do?

Set `delivery.platform` in `config.yaml` to your platform and fill in the relevant credentials (`slack.webhook_url`, `telegram.bot_token` + `telegram.chat_id`). The `deliver.sh` script handles those platforms. Discord uses OpenClaw's native cron delivery and doesn't need `deliver.sh`.

### What's the minimum bash version for v4?

bash 3.2 (macOS default). The orchestrator deliberately avoids `declare -A` and other bash 4+ features.

---

## Rollback

If v4 doesn't work for you, roll back:

```bash
# Restore config
cp config.yaml.v3-backup config.yaml

# Re-register v3 cron manually
# (open ~/.openclaw/cron/jobs.json and restore the v3 cron message)
```

Or remove the cron and re-add it pointing to `generate-proposal.sh`:

```bash
bash scripts/register-cron.sh --remove
# Then manually edit ~/.openclaw/cron/jobs.json to add the v3 message
```

---

*Have a migration issue? Open a [bug report](https://github.com/ramsbaby/self-evolving-agent/issues/new?template=bug_report.yml) and include your OS, bash version, and the output of `VERBOSE=true bash scripts/v4/orchestrator.sh`.*
