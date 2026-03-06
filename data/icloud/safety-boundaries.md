# Safety Boundaries - iCloud

This file defines non-negotiable boundaries for agent execution.

## Never Do

- Never request Apple credentials or 2FA codes in chat.
- Never run risky write operations without explicit confirmation.
- Never persist secrets in logs or memory files.
- Never claim success without read-back verification.

## Confirmation Template for Risky Actions

Before execution, state:
- target (`device_id` or exact drive path),
- operation effect,
- expected result,
- rollback note.

Then require explicit user confirmation.

## Minimum Verification Standard

- One pre-action read snapshot.
- One post-action read verification.
- One concise operation result line (success or failure cause).
