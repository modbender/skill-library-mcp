# Wallet Trust Boundary Guidance

Use this for wallet-connect, signature prompt, and dApp identity issues.

## Core Rules

- Treat wallet prompt UI as a security boundary.
- Treat displayed dApp origin/name/logo as authorization context.
- Identity mismatch in signing/connect context is a security failure, not mere UX.

## Reportability Conditions

Report when an attacker can:
- cause wallet authorization under false dApp identity
- abuse cached approvals/session context after identity confusion
- induce malicious signatures or approvals through protocol/SDK flaws

## Framing Guidance

Describe as:
- `protocol-level identity spoofing`
- `authorization context confusion`

Do not describe as:
- user mistake
- generic social engineering without technical root cause

## Required Evidence

- trust anchor that fails (SDK, session handshake, signature modal binding)
- precise mismatch mechanism
- downstream impact path (approval, permit, malicious signing)
