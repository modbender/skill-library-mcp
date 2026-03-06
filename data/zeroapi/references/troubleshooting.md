# Troubleshooting

## Gateway crashes with "No API provider registered for api: undefined"

**Cause**: The `api` field is missing from a custom provider.

**Fix**: Add the correct `api` field:
- OpenAI Codex (in `openclaw.json`): `"api": "openai-responses"`
- Kimi (in `openclaw.json`): `"api": "openai-completions"`
- Google Gemini (in per-agent `models.json` ONLY): `"api": "google-gemini-cli"`

Do NOT use `"api": "google-generative-ai"` for subscription OAuth — that type sends auth via `x-goog-api-key` header which rejects OAuth tokens. Use `"google-gemini-cli"` instead.

## Google Gemini returns "API key not valid" with subscription

**Cause**: Gemini provider is using the wrong API type.

Two possible causes:
1. Provider is in `openclaw.json` with `"api": "google-generative-ai"` — move it to per-agent `models.json` with `"api": "google-gemini-cli"` instead.
2. Provider has a `baseUrl` set — remove it entirely. The `google-gemini-cli` stream function has the correct endpoint hardcoded.

See `references/provider-config.md` for the correct setup.

## Model shows `missing` in `openclaw models status`

**Cause**: The model ID does not match the provider's catalog.

For `gemini-2.5-flash-lite`: use the ID **without** `-preview` suffix (the `-preview` alias was deprecated Aug 2025). The model may show as `configured,missing` because OpenClaw's catalog hasn't added it yet (issue #10284, PR #10984 pending) — but it still works for API calls. The `normalizeGoogleModelId()` function only normalizes Gemini 3 model IDs — Gemini 2.5 IDs must match exactly.

## Codex stops working (401 Unauthorized)

**Cause**: The Codex OAuth token has expired and auto-refresh failed. This can happen if the refresh token itself expired (typically after 10+ days without use).

**Fix**: Guide the user through the OAuth flow described in `references/oauth-setup.md`. Use the tmux method to run `openclaw onboard --auth-choice openai-codex`, extract the URL, send it to the user, and paste back the redirect URL.

OpenClaw 2026.2.6+ auto-refreshes tokens automatically — this manual flow is only needed when auto-refresh fails. Note: the user's normal ChatGPT usage (web, mobile, Codex CLI, Codex app) does NOT cause this — tested Feb 2026.

## Sub-agent returns "Unknown model"

**Cause**: The model is registered in the main agent context but not available in sub-agent context.

**Fix**: Check that the model's provider has a valid auth-profile. Run `openclaw models status` to verify. Ensure the sub-agent's `models.json` includes the provider (see `references/provider-config.md` for Google Gemini's special per-agent setup).

## Token works for some agents but not others after manual renewal

**Cause**: OAuth tokens are stored in 3 locations that do NOT auto-sync. Manual renewal (tmux OAuth flow) only writes to `auth-profiles.json`. Other agents may still reference the old token from `openclaw.json` or `credentials/oauth.json`.

**Fix**: After manual renewal, sync the new token to all locations. See `references/oauth-setup.md` → "Token Storage Architecture" for the sync script and details.

## systemd ExecStartPre fails with "too many arguments"

**Cause**: `ExecStartPre` does NOT run through a shell. Common shell syntax like `|| true` or `&&` is interpreted literally as arguments, not operators.

**Fix**: Use systemd's `-` prefix for error tolerance:

```ini
# WRONG — systemd passes "||" and "true" as arguments to fuser:
ExecStartPre=/usr/bin/fuser -k 8787/tcp || true

# CORRECT — "-" prefix means "ignore exit code":
ExecStartPre=-/usr/bin/fuser -k 8787/tcp
```

Note: OpenClaw runs as a user service (`systemctl --user`), not a system service.

## MEMORY.md or skill content is silently truncated

**Cause**: OpenClaw has per-file and total bootstrap character limits. Files exceeding the limit are truncated without warning.

**Fix**: Adjust the bootstrap budget in `openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "bootstrapTotalMaxChars": 50000,
      "bootstrapMaxChars": 30000
    }
  }
}
```

- `bootstrapMaxChars`: Maximum characters per single file (default: 20000)
- `bootstrapTotalMaxChars`: Total budget across all bootstrap files (default: varies)

These count **characters**, not bytes. UTF-8 characters (Turkish İ, ş, ç etc.) are 1 character but 2 bytes. Requires OpenClaw 2026.2.14+.

**Tip**: Keep pre-MEMORY files small (AGENTS.md, TOOLS.md, etc.). Bootstrap load order: AGENTS → SOUL → TOOLS → IDENTITY → USER → HEARTBEAT → BOOTSTRAP → MEMORY. Earlier files consume budget first.

## Config shows "invalid" after editing openclaw.json

**Cause**: OpenClaw uses strict Zod schema validation. Any unrecognized key in `openclaw.json` causes the ENTIRE config to be rejected as invalid — not just the unknown field.

**Fix**:
1. Remove any keys not in the schema (e.g., `autoCapture` was mentioned in changelogs but has no schema key)
2. After editing, validate JSON syntax: `python3 -c "import json; json.load(open('openclaw.json'))"`
3. Hot-reload may reject keys from a newer OpenClaw version — do a full restart with the new binary instead
4. Always backup before editing: `cp openclaw.json openclaw.json.bak`
