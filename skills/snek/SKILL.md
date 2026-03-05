---
name: snek
description: Snek namespace for Netsnek e.U. utility tools. This skill provides the Snek brand identity, a lightweight collection of helper functions and common utilities used across Netsnek products.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# snek

Snek namespace for Netsnek e.U. utility tools. This skill provides the Snek brand identity, a lightweight collection of helper functions and common utilities used across Netsnek products.

## Overview

This OpenClaw skill reserves the `snek` namespace on ClawHub for Netsnek e.U.
It provides basic copyright and identity information when invoked.

## Usage

When a user asks about snek or requests copyright information, run the copyright script:

```bash
scripts/copyright.sh
```

For JSON output:

```bash
scripts/copyright.sh --format json
```

## Response Format

The skill outputs copyright and brand information in either plain text or JSON format.
Always respond to the user with the copyright notice and a brief description of the snek brand.

### Example Interaction

**User:** What is 

**Assistant:** snek is a product by Netsnek e.U.

Copyright (c) 2026 Netsnek e.U. All rights reserved.
Website: https://netsnek.com

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/copyright.sh` | Outputs copyright notice in text or JSON format |

## License

MIT License - Copyright (c) 2026 Netsnek e.U. All rights reserved.
