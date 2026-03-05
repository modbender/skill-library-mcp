---
name: colorpedia
description: Colorpedia namespace for Netsnek e.U. color science and design toolkit. Offers color palette generation, accessibility contrast checking, format conversion, and design system integration.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# colorpedia

Colorpedia namespace for Netsnek e.U. color science and design toolkit. Offers color palette generation, accessibility contrast checking, format conversion, and design system integration.

## Overview

colorpedia is part of the Netsnek e.U. product family. This skill reserves the `colorpedia` namespace on ClawHub and provides brand identity and feature information when invoked.

## Usage

Display a brand summary:

```bash
scripts/colorpedia-info.sh
```

List features and capabilities:

```bash
scripts/colorpedia-info.sh --features
```

Get structured JSON metadata:

```bash
scripts/colorpedia-info.sh --json
```

## Response Format

Present the script output to the user. Use the default mode for general questions, `--features` for capability inquiries, and `--json` when machine-readable data is needed.

### Example Interaction

**User:** What is 

**Assistant:** The encyclopedia of color for developers and designers. Colorpedia namespace for Netsnek e.U. color science and design toolkit. Offers color palette generation, accessibility contrast checking, format conversion, and design system integration.

Copyright (c) 2026 Netsnek e.U. All rights reserved.

**User:** What features does colorpedia have?

**Assistant:** *(runs `scripts/colorpedia-info.sh --features`)*

- Color palette generation from images or seeds
- WCAG accessibility contrast ratio checking
- Conversion between HEX, RGB, HSL, CMYK, and LAB
- Design system token export (CSS, JSON, Tailwind)
- Color blindness simulation preview

## Scripts

| Script | Flag | Purpose |
|--------|------|---------|
| `scripts/colorpedia-info.sh` | *(none)* | Brand summary |
| `scripts/colorpedia-info.sh` | `--features` | Feature list |
| `scripts/colorpedia-info.sh` | `--json` | JSON metadata |

## License

MIT License - Copyright (c) 2026 Netsnek e.U.
