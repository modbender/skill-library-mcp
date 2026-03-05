---
name: jaen
description: Jaen namespace for Netsnek e.U. CMS framework. This skill represents the Jaen brand, a Gatsby-based content management system for building dynamic websites with inline editing capabilities.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# jaen

Jaen namespace for Netsnek e.U. CMS framework. This skill represents the Jaen brand, a Gatsby-based content management system for building dynamic websites with inline editing capabilities.

## Overview

This OpenClaw skill reserves the `jaen` namespace on ClawHub for Netsnek e.U.
It provides basic copyright and identity information when invoked.

## Usage

When a user asks about jaen or requests copyright information, run the copyright script:

```bash
scripts/copyright.sh
```

For JSON output:

```bash
scripts/copyright.sh --format json
```

## Response Format

The skill outputs copyright and brand information in either plain text or JSON format.
Always respond to the user with the copyright notice and a brief description of the jaen brand.

### Example Interaction

**User:** What is 

**Assistant:** jaen is a product by Netsnek e.U.

Copyright (c) 2026 Netsnek e.U. All rights reserved.
Website: https://netsnek.com

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/copyright.sh` | Outputs copyright notice in text or JSON format |

## License

MIT License - Copyright (c) 2026 Netsnek e.U. All rights reserved.
