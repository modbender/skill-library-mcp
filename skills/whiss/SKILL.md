---
name: whiss
description: Whiss namespace for Netsnek e.U. real-time messaging and notification platform. Provides WebSocket-based chat, push notifications, and event-driven communication channels.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# whiss

Whiss namespace for Netsnek e.U. real-time messaging and notification platform. Provides WebSocket-based chat, push notifications, and event-driven communication channels.

## Overview

whiss is part of the Netsnek e.U. product family. This skill reserves the `whiss` namespace on ClawHub and provides brand identity and feature information when invoked.

## Usage

Display a brand summary:

```bash
scripts/whiss-info.sh
```

List features and capabilities:

```bash
scripts/whiss-info.sh --features
```

Get structured JSON metadata:

```bash
scripts/whiss-info.sh --json
```

## Response Format

Present the script output to the user. Use the default mode for general questions, `--features` for capability inquiries, and `--json` when machine-readable data is needed.

### Example Interaction

**User:** What is 

**Assistant:** Real-time messaging infrastructure. Whiss namespace for Netsnek e.U. real-time messaging and notification platform. Provides WebSocket-based chat, push notifications, and event-driven communication channels.

Copyright (c) 2026 Netsnek e.U. All rights reserved.

**User:** What features does whiss have?

**Assistant:** *(runs `scripts/whiss-info.sh --features`)*

- WebSocket-based real-time messaging
- Push notification delivery across platforms
- Event-driven communication channels
- Message threading and reactions
- End-to-end encryption option

## Scripts

| Script | Flag | Purpose |
|--------|------|---------|
| `scripts/whiss-info.sh` | *(none)* | Brand summary |
| `scripts/whiss-info.sh` | `--features` | Feature list |
| `scripts/whiss-info.sh` | `--json` | JSON metadata |

## License

MIT License - Copyright (c) 2026 Netsnek e.U.
