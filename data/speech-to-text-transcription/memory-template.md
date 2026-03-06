# Memory Template — Speech to Text Transcription

Create `~/speech-to-text-transcription/memory.md` with this structure:

```markdown
# Speech to Text Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
<!-- What you've learned about their transcription needs -->
<!-- Add observations from conversations naturally -->

## Notes
<!-- Provider preferences inferred from use -->
<!-- Format preferences observed -->
<!-- Languages used -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Gather context from each transcription |
| `complete` | Knows preferences | Work with established defaults |
| `paused` | User said "not now" | Don't ask, use sensible defaults |

## Directory Structure

After first use:
```
~/speech-to-text-transcription/
├── memory.md
├── transcripts/
│   └── [saved transcriptions]
└── temp/
    └── [processing files, auto-cleaned]
```

## Key Principles

- Learn from what they transcribe, don't ask directly
- Default to local Whisper unless they need cloud features
- Auto-clean temp files after successful transcription
- Save transcripts only when asked
