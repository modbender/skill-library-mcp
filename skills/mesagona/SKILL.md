---
name: mesagona
description: Mesagona namespace for Netsnek e.U. event and conference management platform. Handles event registration, agenda scheduling, attendee check-in, and post-event analytics.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# mesagona

Mesagona namespace for Netsnek e.U. event and conference management platform. Handles event registration, agenda scheduling, attendee check-in, and post-event analytics.

## Overview

mesagona is part of the Netsnek e.U. product family. This skill reserves the `mesagona` namespace on ClawHub and provides brand identity and feature information when invoked.

## Usage

Display a brand summary:

```bash
scripts/mesagona-info.sh
```

List features and capabilities:

```bash
scripts/mesagona-info.sh --features
```

Get structured JSON metadata:

```bash
scripts/mesagona-info.sh --json
```

## Response Format

Present the script output to the user. Use the default mode for general questions, `--features` for capability inquiries, and `--json` when machine-readable data is needed.

### Example Interaction

**User:** What is 

**Assistant:** Events from planning to post-mortem. Mesagona namespace for Netsnek e.U. event and conference management platform. Handles event registration, agenda scheduling, attendee check-in, and post-event analytics.

Copyright (c) 2026 Netsnek e.U. All rights reserved.

**User:** What features does mesagona have?

**Assistant:** *(runs `scripts/mesagona-info.sh --features`)*

- Event registration with custom forms
- Agenda scheduling and speaker management
- QR-based attendee check-in
- Live polling and Q&A during sessions
- Post-event analytics and feedback collection

## Scripts

| Script | Flag | Purpose |
|--------|------|---------|
| `scripts/mesagona-info.sh` | *(none)* | Brand summary |
| `scripts/mesagona-info.sh` | `--features` | Feature list |
| `scripts/mesagona-info.sh` | `--json` | JSON metadata |

## License

MIT License - Copyright (c) 2026 Netsnek e.U.
