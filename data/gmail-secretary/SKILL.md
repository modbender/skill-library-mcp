---
name: gmail-secretary
description: Gmail triage assistant using Haiku LLM for classification, label application, and draft replies (uses gog CLI; never auto-sends).
---

# Gmail Secretary (Alan)

## Safety rules (non-negotiable)
- **Never send email automatically.** Only create drafts + summaries.
- Prefer **labels** over moving/deleting.
- Keep the voice reference **style-focused** (patterns + a few short redacted snippets), not a full archive.

## Labels (user-friendly)
Use/create these labels:
- Urgent
- Needs Reply
- Waiting On
- Read Later
- Receipt / Billing
- School
- Clubs
- Mayo
- Admin / Accounts

## Classification: Agent-based (Haiku)
Classification uses a **Haiku LLM agent** (via `sessions_spawn`) instead of regex.
- `scripts/triage-and-draft.sh` fetches inbox → writes summaries to `cache/gmail-inbox-summaries.json`
- Agent reads summaries, classifies each email, writes results to `cache/gmail-triage-labels.json`
- `scripts/apply-labels.sh` reads classification results and applies Gmail labels via `gog`

### Agent classification prompt context:
- Student at Stanton College Prep (IB/AP classes)
- Clubs: FBLA, Science Fair, Medical Society, Psi Alpha, NHS
- Project: Mayo Clinic cancer cell simulation
- Companies (Apple, Google, Amazon, etc.) are NOT "School"
- Newsletters/promos → Read Later
- Account security/password/verification → Admin / Accounts

## Files
- Voice reference (auto-maintained): `references/voice.md`
- Draft queue (generated): `/home/delta/.openclaw/workspace/cache/gmail-drafts.md`
- Triage digest (generated): `/home/delta/.openclaw/workspace/cache/gmail-triage.md`
- Inbox summaries (intermediate): `/home/delta/.openclaw/workspace/cache/gmail-inbox-summaries.json`
- Classification results: `/home/delta/.openclaw/workspace/cache/gmail-triage-labels.json`

## Scripts
- Build/refresh voice reference from Sent mail:
  - `scripts/build-voice-reference.sh` (samples last 50 sent messages)
- Fetch inbox + extract summaries:
  - `scripts/triage-and-draft.sh`
- Apply labels from classification:
  - `scripts/apply-labels.sh`

## Workflow
1) Run `triage-and-draft.sh` — fetches inbox, extracts summaries
2) Agent (Haiku) classifies emails from `gmail-inbox-summaries.json`
3) Agent writes results to `gmail-triage-labels.json`
4) Run `apply-labels.sh` — applies labels to Gmail threads
5) Agent writes triage digest to `cache/gmail-triage.md` for nudges
