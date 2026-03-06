---
name: code-quality-guard
description: Professional pre-deployment code review and quality enforcement. Ensures imports are valid, tags are closed, and logic follows best practices before announcing a build is live.
---

# Code Quality Guard

Ship cleaner code, faster. Never let a missing import break your production again.

## Checklist

1. **Import Sweep**: Check every component used against the import block.
2. **Tag Verification**: Ensure all JSX/HTML tags are balanced.
3. **Environment Audit**: Verify required env vars and ports.
4. **Log Review**: Scan for debug prints and secrets.

## Usage
Run as a pre-build hook to catch "ReferenceErrors" before the human sees them.

## Installation
```bash
clawhub install code-quality-guard
```
