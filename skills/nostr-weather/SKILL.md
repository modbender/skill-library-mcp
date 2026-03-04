---
name: nostr-weather
description: Specialized skill for NIP-Weather IoT data, powered by nostr-nak.
---
# nostr-weather

Specialized skill for NIP-Weather IoT data.

## Dependencies
- Requires core nak commands from: `skills/nostr-nak/SKILL.md`

## Configuration
- **Metadata Kind**: `16158`
- **Readings Kind**: `4223`

## Usage
Query latest readings:
`script -q -c "nak req -k 4223 -a <pubkey> <relay> -l 1" /dev/null | cat`
