---
name: nostr-plantr
description: Specialized skill for Plantr IoT data (Kind 34419 and 4171).
---
# nostr-plantr

Specialized skill for Plantr IoT data (Kind 34419 and 4171).

## Dependencies
- Requires core nak commands from: `skills/nostr-nak/SKILL.md`

## Configuration
- **Plant Pot Kind**: `34419`
- **Activity Log Kind**: `4171`

## Usage
Query watering history:
`script -q -c "nak req -k 4171 <relay> -l 20" /dev/null | cat`
