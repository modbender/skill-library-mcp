---
name: multi-chat-context-manager
description: CLI tool to store and retrieve conversation contexts per channel/user.
version: 1.0.2
author: skill-factory
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# Multi-Chat Context Manager

## What This Does

A simple CLI tool to store, retrieve, and clear conversation contexts. Contexts are saved as JSON, keyed by channel/user/thread IDs. This is a utility library, not an auto-integration plugin.

## When To Use

- You need to manually store conversation history per channel or user
- You want a simple key-value context store for your scripts
- You're building custom integrations and need context persistence

## Usage

Store a conversation:
python3 scripts/context_manager.py store --channel "telegram-123" --user "user-456" --message "Hello" --response "Hi there"

Retrieve context:
python3 scripts/context_manager.py retrieve --channel "telegram-123" --user "user-456"

Clear context:
python3 scripts/context_manager.py clear --channel "telegram-123"

List all contexts:
python3 scripts/context_manager.py list

## Examples

### Example 1: Store and retrieve

Store:
python3 scripts/context_manager.py store --channel "discord-general" --user "john" --message "What is AI?" --response "AI is artificial intelligence."

Retrieve:
python3 scripts/context_manager.py retrieve --channel "discord-general" --user "john"

Output:
{
  "channel_id": "discord-general",
  "user_id": "john",
  "history": [{"message": "What is AI?", "response": "AI is artificial intelligence."}]
}

## Requirements

- Python 3.x
- No external dependencies

## Limitations

- This is a CLI tool, not an auto-integration plugin
- Does not automatically intercept messages from platforms
- Stores data in plaintext JSON (not encrypted)
- No file-locking for concurrent access
- You must call it manually from your scripts or workflows
