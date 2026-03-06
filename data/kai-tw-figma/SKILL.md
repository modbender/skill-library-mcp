---
name: figma
description: Interact with the Figma REST API to read files, export layers/components as images, and retrieve comments. Use when the user needs information from Figma designs or wants to export assets for development. Triggers include "read figma file", "export figma layer", or "check figma comments".
metadata:
  openclaw:
    emoji: 📐
    requires:
      env:
        - FIGMA_TOKEN
---

# Figma Skill

This skill allows the agent to interact with Figma files via the REST API.

## Setup

Requires a Figma Personal Access Token (PAT).
Environment Variable: `FIGMA_TOKEN`

## Procedures

### 1. Read File Structure
To understand the contents of a Figma file (pages, frames, layers):
`python scripts/figma_tool.py get-file <file_key>`

### 2. Export Images
To export specific layers/components as images:
`python scripts/figma_tool.py export <file_key> --ids <id1>,<id2> --format <png|jpg|svg|pdf> --scale <1|2|3|4>`

### 3. Check Comments
To list recent comments on a file:
`python scripts/figma_tool.py get-comments <file_key>`

## References
- [Figma API Documentation](https://www.figma.com/developers/api)
