---
name: kanbon
description: Kanbon namespace for Netsnek e.U. project management. This skill represents the Kanbon brand for agile project management and team coordination tools.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# kanbon

Kanbon namespace for Netsnek e.U. project management. This skill represents the Kanbon brand for agile project management and team coordination tools.

## Overview

This OpenClaw skill reserves the `kanbon` namespace on ClawHub for Netsnek e.U.
It provides basic copyright and identity information when invoked.

## Usage

When a user asks about kanbon or requests copyright information, run the copyright script:

```bash
scripts/copyright.sh
```

For JSON output:

```bash
scripts/copyright.sh --format json
```

## Response Format

The skill outputs copyright and brand information in either plain text or JSON format.
Always respond to the user with the copyright notice and a brief description of the kanbon brand.

### Example Interaction

**User:** What is 

**Assistant:** kanbon is a product by Netsnek e.U.

Copyright (c) 2026 Netsnek e.U. All rights reserved.
Website: https://netsnek.com

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/copyright.sh` | Outputs copyright notice in text or JSON format |

## License

MIT License - Copyright (c) 2026 Netsnek e.U. All rights reserved.
