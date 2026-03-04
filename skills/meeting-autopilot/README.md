# ✈️ Meeting Autopilot

**Turn meeting transcripts into operational outputs — not summaries, but action items, decisions, follow-up emails, and ticket drafts.**

One transcript in, ready-to-send emails out.

## Install

```bash
clawhub install meeting-autopilot
```

## What It Does

Paste or point it at a meeting transcript (VTT, SRT, or plain text). Meeting Autopilot runs a multi-pass LLM analysis and produces:

| Output | What You Get |
|--------|-------------|
| ✅ **Decisions** | What was decided, by whom, with rationale |
| 📋 **Action Items** | Owner, deadline, priority — ready for your task tracker |
| 📧 **Follow-Up Emails** | Professional, ready-to-send email drafts |
| 🎫 **Ticket Drafts** | Jira/Linear/GitHub-ready issue descriptions |
| ❓ **Open Questions** | What's still unresolved |
| 🅿️ **Parking Lot** | What was deferred for later |

### The WOW Moment: Follow-Up Emails

Other tools give you bullet points. Meeting Autopilot gives you a complete follow-up email you can copy, paste, and send. Professional tone, proper formatting, includes all the context.

### Example Output

```
## ✈️ Meeting Autopilot Report

**Sprint Planning — Week 7**
📅 February 15, 2026 at 14:30
👥 Participants: Sarah, Mike, Priya, James

## 📊 Overview
| Category        | Count |
|-----------------|------:|
| ✅ Decisions     |     3 |
| 📋 Action Items  |     7 |
| ❓ Open Questions |     2 |

## 📋 Action Items
| # | Action                              | Owner | Deadline   | Status |
|:-:|-------------------------------------|-------|------------|:------:|
| 1 | Set up PostgreSQL staging instance  | Mike  | Friday     | ⬜ Open |
| 2 | Draft API migration plan            | Priya | Next Tues  | ⬜ Open |
| 3 | Schedule security review            | Sarah | This week  | ⬜ Open |

## 📧 Follow-Up Email
**Subject:** Sprint Planning Follow-Up — 3 Decisions, 7 Action Items

Hi team,

Thanks for a productive sprint planning session. Here's what we agreed on...
```

## Usage

Just ask:

> "Process this meeting transcript"  
> "Extract action items from my meeting"  
> "Here's our standup transcript, give me the follow-up email"

Or run directly:

```bash
# From a file
bash scripts/meeting-autopilot.sh meeting.vtt --title "Sprint Planning"

# From clipboard (macOS)
pbpaste | bash scripts/meeting-autopilot.sh - --title "Team Sync"

# Save report to file
bash scripts/meeting-autopilot.sh meeting.txt --title "Board Meeting" --output ./reports
```

## Supported Formats

| Format | Source | Speaker Labels |
|--------|--------|:--------------:|
| **VTT** (WebVTT) | Zoom, Google Meet, Teams | ✅ Yes |
| **SRT** (SubRip) | Otter.ai, video editors | ⚠️ Sometimes |
| **TXT** (Plain text) | Manual notes, any source | ✅ If formatted as `Speaker: text` |

Format is auto-detected. Force with `--format vtt|srt|txt` if needed.

## Requirements

- **bash**, **jq**, **python3**, **curl** (typically pre-installed on macOS/Linux)
- **ANTHROPIC_API_KEY** or **OPENAI_API_KEY** environment variable

No audio transcription in v1 — bring your own transcript from Zoom, Otter, Google Meet, or any other source.

## How It Works

Meeting Autopilot uses a **multi-pass extraction pipeline**:

1. **Parse** — Normalize VTT/SRT/TXT into structured segments with speaker labels and timestamps
2. **Extract** — LLM identifies every decision, action item, question, and key point
3. **Generate** — LLM produces professional email drafts and ticket descriptions
4. **Report** — Everything formatted as beautiful, screenshot-ready Markdown

## OpenClaw Discord v2 Ready

Compatible with OpenClaw Discord channel behavior documented for v2026.2.14+:
- Compact first response with meeting outcome highlights
- Component-style quick actions when available (`Show Action Items`, `Show Follow-Up Email Draft`, `Show Ticket Drafts`)
- Numbered-list fallback when components are unavailable

## Cross-Meeting Tracking

Every processed meeting is stored locally at `~/.meeting-autopilot/history/` as JSON. This is the foundation for v1.1's cross-meeting tracking: "Did Bob follow through on last week's action items?"

## Safety

- Transcript content is sent to the configured LLM API (Anthropic or OpenAI) for processing
- No data is sent anywhere else — no telemetry, no tracking
- History is stored locally on your machine only
- All inputs are validated and safely handled (no eval, no injection)
- See [SECURITY.md](SECURITY.md) for the full security model

## FAQ

**Q: Can it transcribe audio/video?**  
A: Not in v1. Use Zoom/Meet/Teams built-in transcription, Otter.ai, or `whisper.cpp` — then feed the transcript to Meeting Autopilot.

**Q: What if my transcript doesn't have speaker labels?**  
A: It still works! Action items won't have owners attributed, but everything else works. For best results, use VTT format with speaker names.

**Q: How long can the transcript be?**  
A: Depends on your LLM's context window. Claude handles ~150K tokens (hours of transcript). GPT-4o handles ~128K tokens. Typical 1-hour meetings are well within limits.

**Q: Does it work offline?**  
A: No — it requires an LLM API call. A local LLM option is planned for v1.1.

---

<sub>Powered by Anvil AI ✈️ | [Report an issue](https://github.com/cacheforge-ai/cacheforge-skills/issues)</sub>
