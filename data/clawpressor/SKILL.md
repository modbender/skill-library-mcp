---
name: clawpressor
description: Compress OpenClaw session context to reduce token usage and extend session lifetime. Uses NLP summarization (Sumy) to intelligently compact conversation history while preserving essential context. Triggers on mentions of session compression, token reduction, context cleanup, or when session size exceeds safe thresholds (~300KB). Use when (1) OpenClaw approaches 50% context limit, (2) Sessions are slowing down due to large context, (3) Reducing API costs from excessive token consumption, (4) Extending session lifetime without forced reboots.
---

# ClawPressor - Session Context Compressor

Intelligently compress OpenClaw session files to reduce token usage by 85-96%.

**Author:** JARVIS (AI Coder) | **Managed by:** BeBoX
**License:** MIT | **Version:** 1.0.0

## Quick Start

```bash
# Preview compression without changes
python3 scripts/compress.py --dry-run

# Apply compression
python3 scripts/compress.py --apply

# Restore from backup
python3 scripts/compress.py --restore
```

## When to Use

| Situation | Action |
|-----------|--------|
| Context at 30-40% | Plan compression soon |
| Context at 50% | **URGENT** — OpenClaw will force compact |
| Session > 300KB | Compress to restore performance |
| Slow responses | Large context likely the cause |
| High API costs | Compress regularly to save tokens |

## How It Works

1. **Preserves recent context** — Keeps last 5 messages intact for immediate context
2. **Summarizes old messages** — Uses LexRank algorithm to extract key information
3. **Replaces with compact block** — Single system message containing summary
4. **Creates backup** — Original preserved as `.backup` file

## Prerequisites

```bash
pip install sumy
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords')"
```

## Command Reference

```bash
# Find and compress latest session (dry-run)
python3 scripts/compress.py

# Compress specific session
python3 scripts/compress.py --session /path/to/session.jsonl --apply

# Keep more recent messages (default: 5)
python3 scripts/compress.py --keep 10 --apply

# Restore if something went wrong
python3 scripts/compress.py --restore

# View compression statistics
python3 scripts/compress.py --stats
```

## Typical Results

| Metric | Before | After | Gain |
|--------|--------|-------|------|
| Messages | 168 | 6 | **-96%** |
| Size | 347 KB | 12 KB | **-96%** |
| Context tokens | ~50k | ~8k | **-84%** |
| Session duration | ~30 min | ~2-3h | **+400%** |

## Integration with Workflows

**In HEARTBEAT.md:**
```markdown
## Context Maintenance (1x/jour)
- Check session size: `ls -lh ~/.openclaw/agents/main/sessions/*.jsonl`
- If > 200KB: `python3 skills/clawpressor/scripts/compress.py --apply`
```

**Manual check:**
```bash
# See current session stats
ls -lh ~/.openclaw/agents/main/sessions/*.jsonl | head -1
```

## Safety

- Always creates `.backup` before compressing
- `--restore` recovers original session
- Recent messages always preserved intact
- Summary stored as system message (visible to model)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Sumy not installed" | Run `pip install sumy` and NLTK downloads |
| No session found | Check `~/.openclaw/agents/main/sessions/` exists |
| Backup not found | File may have been overwritten; no recovery |
| Poor summaries | Increase `--keep` to preserve more context |

## Credits

- **Coding:** JARVIS (AI Assistant)
- **Project Management:** BeBoX
- **Technique:** NLP summarization via Sumy (LexRank algorithm)

## Related

- See `memory/openclaw-context-optimization.md` for full strategy
- Combine with SOUL_MIN/USER_MIN files for maximum efficiency
