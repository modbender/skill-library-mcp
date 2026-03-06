# Security Policy

## Overview

**apiosk-publish** is a skill for publishing APIs on the Apiosk marketplace. It has been designed with security as a top priority.

## Security Level: Benign

This skill is rated **Benign** on the ClawHub security scale.

### What This Means

- ✅ No arbitrary code execution
- ✅ No `curl | bash` patterns
- ✅ All external requests go to verified Apiosk infrastructure
- ✅ Private keys are never sent to third parties (used locally for signing only)
- ✅ No write access outside `~/.apiosk/` directory
- ✅ All dependencies declared (`curl`, `jq`, `cast`)

## Network Access

This skill communicates **only** with:
- `https://gateway.apiosk.com` — Apiosk gateway API

All communication uses HTTPS exclusively.

## Data Access

- **Reads:** `~/.apiosk/wallet.json` (address + private key) or `~/.apiosk/wallet.txt` (address only)
- **Writes:** None (skill stores no local data)

## Wallet Security

- Wallet address is read from `~/.apiosk/wallet.json` or `~/.apiosk/wallet.txt`
- Private key may be read from `~/.apiosk/wallet.json`, `APIOSK_PRIVATE_KEY`, or `--private-key`
- Private key is only used locally to produce ECDSA signatures for gateway auth headers
- Private key is not transmitted directly to the gateway
- You retain full control of your wallet

## Required Binaries

- `curl` — HTTP requests
- `jq` — JSON parsing
- `cast` — wallet message signing for auth headers

These are standard Unix utilities and are **not** downloaded by this skill.

## API Endpoint Validation

When you register an API:
1. Gateway validates the endpoint URL is HTTPS
2. Performs a health check (HEAD/GET request)
3. Only approves if health check passes
4. Your endpoint URL is stored in the Apiosk database

**Important:** Ensure your API endpoint is secure and doesn't expose sensitive data.

## No Arbitrary Code Execution

- All scripts are simple shell scripts
- No `eval`, `source`, or dynamic code execution
- No external script downloads
- No dependency installations

## Reporting Security Issues

If you discover a security issue:

1. **DO NOT** open a public GitHub issue
2. Email: security@apiosk.com
3. We'll respond within 24 hours
4. Coordinated disclosure after fix

## Updates

This skill may receive security updates. Check the latest version on ClawHub.

---

**Last Updated:** 2026-02-26  
**Version:** 1.1.0
