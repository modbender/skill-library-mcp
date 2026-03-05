# Migration Guide: tokenQrusher v2.0.x → v2.1.0

v2.1.0 removes non-functional components. If upgrading from an earlier version, follow these steps.

---

## What Changed

**Removed components:**
- `token-model` hook (model recommendations, not operational)
- `token-usage` hook (budget tracking, advisory only)
- `token-cron` hook (optimization scheduler, not functional without usage data)
- Associated scripts and tests

**Kept components:**
- `token-context` (context filtering)
- `token-heartbeat` (heartbeat optimization)
- `token-shared` (utility functions)

**Removed CLI commands:**
- `tokenqrusher model`
- `tokenqrusher budget`
- `tokenqrusher usage`
- `tokenqrusher optimize`

---

## Step‑by‑Step Migration

1. **Disable old hooks** (optional but clean):
   ```bash
   openclaw hooks disable token-model
   openclaw hooks disable token-usage
   openclaw hooks disable token-cron
   ```

2. **Remove old hook directories** (they will no longer be used):
   ```bash
   rm -rf ~/.openclaw/hooks/token-model
   rm -rf ~/.openclaw/hooks/token-usage
   rm -rf ~/.openclaw/hooks/token-cron
   ```

3. **Update the skill**:
   ```bash
   clawhub update tokenQrusher
   # or: clawhub install tokenQrusher --force
   ```

4. **Install remaining hooks** (the `install` command now only installs the two needed hooks):
   ```bash
   tokenqrusher install --hooks
   ```

5. **Restart the gateway** to reload hook configuration:
   ```bash
   openclaw gateway restart
   ```

---

## Verification

Check that hooks are active:

```bash
openclaw hooks list
# Should show token-context and token-heartbeat as ready.
```

Run the status command:

```bash
tokenqrusher status
# Should show both hooks with ✓ ready
```

Test context recommendation:

```bash
tokenqrusher context "hello"
# Should output: Complexity: simple, files: SOUL.md, IDENTITY.md
```

---

## Configuration Files

Old configuration files can be safely deleted:
- `~/.openclaw/hooks/token-model/config.json`
- `~/.openclaw/hooks/token-usage/config.json`
- `~/.openclaw/hooks/token-cron/config.json`

State files from the removed components are also no longer created:
- `~/.openclaw/workspace/memory/usage-history.json`
- `~/.openclaw/workspace/memory/token-tracker-state.json`
- `~/.openclaw/workspace/memory/context-usage.json`

---

## Questions?

The simplified skill focuses on the features that actually influence OpenClaw behavior. If you were relying on the advisory output of `token-model` or `token-usage`, consider implementing those checks externally or manually adjusting your model selection and monitoring usage through OpenClaw's own tools.
