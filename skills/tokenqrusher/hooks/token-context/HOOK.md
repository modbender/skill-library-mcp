---
name: token-context
description: "Filters context files based on message complexity to reduce token usage by up to 99%"
homepage: https://github.com/qsmtco/tokenQrusher
metadata: 
  openclaw: 
    emoji: "🎯"
    events: ["agent:bootstrap"]
    requires: 
      config: ["workspace.dir"]
---

# Token Context Hook

Filters which workspace files are loaded into context based on the complexity of the incoming message.

## What It Does

1. Listens for `agent:bootstrap` event
2. Extracts the user's message from the session
3. Classifies complexity (simple/standard/complex)
4. Filters `bootstrapFiles` to only include necessary files

## Complexity Levels

### Simple (99% token reduction)
Used for: greetings, acknowledgments, simple questions

Files loaded:
- SOUL.md (identity)
- IDENTITY.md (who I am)

### Standard (90% token reduction)
Used for: code writing, file operations, regular work

Files loaded:
- SOUL.md
- IDENTITY.md  
- USER.md (about the user)

### Complex (0% reduction)
Used for: architecture, design, deep analysis

Files loaded:
- ALL files (current behavior preserved)

## Configuration

Edit `config.json` in the hook directory to customize file lists.

## Requirements

- OpenClaw with hooks enabled
- Workspace directory configured

## Events

Listens to: `agent:bootstrap`
