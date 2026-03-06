---
name: percept-speaker-id
description: Speaker identification and management for multi-person conversations.
---

# percept-speaker-id

Speaker identification and management for multi-person conversations.

## What it does

Tracks who said what in conversations. Maps anonymous speaker labels (SPEAKER_0, SPEAKER_1) to real names, maintains speaker profiles, and gates voice command authorization.

## When to use

- User asks "who said that?" or wants speaker-attributed transcripts
- User wants to configure which people can trigger voice commands
- Agent needs to know who is speaking in a multi-person conversation

## Requirements

- **percept-listen** skill installed and running
- **Omi pendant** (provides `is_user` flag for primary speaker)

## How it works

1. Omi sends transcript segments with speaker labels (SPEAKER_0, SPEAKER_1, etc.)
2. Percept resolves labels to names using the speakers registry
3. `is_user` flag from Omi identifies the pendant wearer as the primary speaker
4. Speaker profiles track first/last seen timestamps and authorization status

## Speaker registry

Located at `percept/data/speakers.json`:

```json
{
  "SPEAKER_00": {
    "name": "David",
    "is_owner": true,
    "approved": true
  },
  "SPEAKER_01": {
    "name": "Rob",
    "is_owner": false,
    "approved": true
  }
}
```

Manage via Percept dashboard (port 8960) → Settings → Speakers.

## Authorization levels

- **Owner** (`is_owner: true`): Full command access, always authorized
- **Approved** (`approved: true`): Can trigger wake word commands
- **Unknown**: Logged only, commands not executed

## Future: Voice embeddings

Planned: pyannote speaker diarization with 192-dim voice embeddings for automatic speaker recognition via cosine similarity. Currently speaker mapping is manual.

## Links

- **GitHub:** https://github.com/GetPercept/percept
