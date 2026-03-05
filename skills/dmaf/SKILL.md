---
name: dmaf
description: Set up and operate DMAF (Don't Miss A Face) — automated WhatsApp photo and video backup with face recognition and Google Photos upload. Use when a user wants to: (1) install and configure DMAF from scratch on GCP, (2) set up the OpenClaw WhatsApp media sync pipeline so group photos and videos flow automatically into Google Photos, (3) add or remove people from the face recognition database, (4) trigger a manual scan or check pipeline status, (5) troubleshoot face recognition misses, upload failures, or alerting issues.
---

# DMAF Skill

DMAF watches WhatsApp groups, recognizes faces you care about in photos and videos, and backs them up to Google Photos automatically. **Setup requires an agent. After that: zero LLM tokens — the pipeline runs on a system cron + Cloud Run with no AI calls.** This skill covers setup (one-time) and day-to-day operations.

## Architecture

```
WhatsApp groups → OpenClaw (auto-download) → GCS bucket → Cloud Run Job → Google Photos
                  ~/.openclaw/media/inbound/   every 30m    hourly
```

Key facts:
- **Dedup**: Firestore; same file never processed twice (key = `sha256(gs://uri)`)
- **Videos**: Sampled at 1–2fps, early exit on first match, full clip uploaded
- **Config**: YAML stored in Secret Manager (`dmaf-config`); update with `gcloud secrets versions add`
- **Known people**: GCS bucket (`gs://your-project-known-people/`); one subdir per person

## Phase 1 — First-Time Setup

Read **[`references/setup.md`](references/setup.md)** for the full step-by-step guide.

Summary of what you'll create:
1. GCP project + required APIs
2. Service account `dmaf-runner` with IAM roles
3. Two GCS buckets: media staging + known people
4. Google Photos OAuth token → Secret Manager
5. Config YAML → Secret Manager
6. Cloud Build + Cloud Run job
7. Cloud Scheduler (hourly trigger)
8. Firestore composite indexes
9. OpenClaw media sync (system cron)

Ask the user for their **GCP project ID** before starting. All other values can be derived from that.

## Phase 2 — Day-to-Day Operations

Read **[`references/ops.md`](references/ops.md)** for full operational commands.

Common tasks:

| Task | Command summary |
|------|----------------|
| Trigger manual scan | `gcloud run jobs execute dmaf-scan --region=us-central1 --async` |
| Check scan logs | `gcloud logging read 'resource.labels.job_name="dmaf-scan"' --limit=30 --freshness=1h` |
| Add a person | Upload photos to `gs://your-project-known-people/NAME/`, then trigger scan |
| Update config | Edit config YAML, `gcloud secrets versions add dmaf-config --data-file=config.yaml` |
| Force sync now | `bash ~/.openclaw/workspace/scripts/dmaf-sync.sh` |
| Check sync log | `tail -30 /tmp/dmaf-sync.log` |

## MCP Server (bonus)

DMAF also ships an MCP server for Claude Desktop, Claude Code, and Cursor.
It wraps the same gcloud/gsutil commands as above — useful for users who
don't have OpenClaw. See [`deploy/mcp-setup.md`](../mcp-setup.md).

```bash
pip install -e ".[mcp]"
DMAF_PROJECT=your-project dmaf-mcp
```

## Installation

```bash
# Option A: Install from ClaWHub (recommended)
clawhub install dmaf

# Option B: Copy skill directly from the repo
cp -r deploy/openclaw-skill/ ~/.openclaw/skills/dmaf/
```
