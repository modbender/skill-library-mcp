---
name: antigravity-sync
description: Automatically discover and configure available Google Antigravity models and quotas.
metadata:
  openclaw:
    skillKey: antigravity-sync
    runtime: node
    requires:
      auth:
        - google-antigravity
    invocation:
      policy: on-demand
      triggers:
        - pattern: "sync antigravity"
        - pattern: "update models"
        - pattern: "fetch google models"
---

# Antigravity Sync

This skill queries the Antigravity API to discover available models and their quotas, then updates your `openclaw.json` configuration to match.

## Usage

1. **Ensure you are authenticated**:
   Run `openclaw models auth login google-antigravity` if you haven't already.

2. **Run the sync script**:
   ```bash
   node skills/antigravity-sync/sync.cjs
   ```

3. **Verify Configuration**:
   The script will output the primary model it selected. Check `openclaw.json` to see the full list of configured models.

## Behavior

- Fetches `fetchAvailableModels` from Google Cloud Code Assist API.
- Updates `models.providers["google-antigravity"].models` with all non-exhausted models.
- Sets `agents.defaults.model.primary` to the API's recommended default model (or preserves your manual selection if valid).
- Preserves existing auth settings.
- **Safety**: Backs up `openclaw.json` before writing.
