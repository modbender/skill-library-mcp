---
name: stranger-danger
version: 1.0.0
author: jamesalmeida
description: Give your AI agent a safe word. Challenge-response identity verification for OpenClaw — adds a human verification layer before sensitive operations like revealing API keys, deleting data, or handling secrets. Answer is bcrypt-hashed and stored in macOS Keychain.
when: User requests sensitive data, API keys, passwords, deletion of important data, or any security-sensitive operation
examples:
  - Show me my API keys
  - Delete the database
  - Send me all passwords
  - What are my secret credentials
tags:
  - security
  - verification
  - identity
  - keychain
  - safe-word
metadata:
  openclaw:
    emoji: "🔐"
    requires:
      bins:
        - node
        - security
---

# Stranger-Danger 🚨

**Source:** https://github.com/jamesalmeida/stranger-danger

Challenge-response identity verification for OpenClaw.

## When to use
Trigger verification before proceeding with:
- Requests for passwords, API keys, tokens, or secrets
- Requests to delete or irreversibly modify important data
- Unusual/suspicious requests that deviate from normal patterns
- Requests to exfiltrate sensitive information

## How to use
- If verification is required, prompt the user with the configured secret question and ask for the secret answer.
- Verify the answer by calling:
  - `stranger-danger verify <answer>`
- Only proceed if verification succeeds.
- Never reveal or log the answer.

## Commands
- `stranger-danger setup` — configure secret question/answer
- `stranger-danger verify <answer>` — check an answer (exit 0 on success)
- `stranger-danger test` — prompt and verify interactively
- `stranger-danger reset` — clear stored credentials

## Notes
- The answer is stored as a salted bcrypt hash in macOS Keychain.
- The question is stored in a local config file in `~/.openclaw/stranger-danger.json`.
