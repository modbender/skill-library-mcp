---
name: keyswap
description: Rotate Claude Max API token for OpenClaw Anthropic profiles. Use when the user says "swap key", "rotate key", "new key", "keyswap", or provides a new `sk-ant-` token to replace the current one.
---

# Key Rotation

Rotate the Claude Max API token for both Anthropic profiles (`anthropic:jawadjarvis` and `anthropic:manual`) in OpenClaw.

## Instructions

1. If the user has not provided a token, ask for one. It must start with `sk-ant-`.
2. Run the rotation script:

```bash
bash /opt/homebrew/lib/node_modules/openclaw/skills/keyswap/scripts/keyswap.sh <token>
```

3. Report the result to the user. On success, confirm both profiles were updated and the gateway restarted. On failure, show the error output.
