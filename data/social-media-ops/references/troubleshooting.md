# Troubleshooting — Known Issues & Solutions

## Node.js IPv6 Connection Failures

**Symptom:** `ENETUNREACH` when connecting to Telegram API or other services
**Cause:** Node.js 22's Happy Eyeballs (`autoSelectFamily`) prefers IPv6, but the machine's IPv6 connectivity may be broken

**Solution (OpenClaw v2026.2.24+):**
OpenClaw now natively prioritizes IPv4 for Telegram media fetches and patches Node 22's undici dispatcher with `autoSelectFamily` IPv4 fallback. No manual workaround needed.

Run `openclaw doctor` to verify connectivity.

## Gateway Won't Start

**Symptom:** `openclaw gateway start` fails or hangs
**Checks:**
1. Is the port already in use? Check with `lsof -i :18789`
2. Is the config valid? Run `openclaw config validate`
4. Check logs at `~/.openclaw/logs/`

## Agent Not Responding

**Symptom:** `sessions_send` times out or agent doesn't respond
**Checks:**
1. Is the agent configured in `openclaw.json`?
2. Is the workspace directory accessible?
3. Does the agent's SOUL.md exist?
4. Check model availability (API key valid, provider online)
5. Try `openclaw gateway restart`

## Telegram Bot Not Receiving Messages

**Symptom:** Bot is online but doesn't respond to group messages
**Checks:**
1. Is `requireMention` set correctly? (should be `false` for always-respond)
2. Is `groupPolicy` set to `"open"`?
3. Is the bot an admin in the group?
4. Is the group ID correct in `openclaw.json` bindings?
5. Check for IPv6 issues (see above)

## Image Generation Fails

**Symptom:** Designer's image generation tool returns errors
**Checks:**
1. Is the API key set? (e.g., `GEMINI_API_KEY` for nano-banana-pro)
2. Is the skill installed in the Designer's workspace?
3. Check rate limits / quota
4. Try simplifying the generation prompt

## QMD Semantic Search Not Working

**Symptom:** Agents can't find relevant shared/ content via semantic search
**Checks:**
1. Check if `~/.openclaw/memory/main.sqlite` exists
2. Verify QMD config in `openclaw.json` has correct paths
3. Wait 5 minutes for auto-reindex
4. Check that shared/ symlinks are valid in each workspace

## Exec Fails for Designer/Engineer (Permission Denied)

**Symptom:** Designer's image generation or Engineer's CLI tools fail with exec approval errors
**Cause:** v2026.2.24+ restricts safe-bin trusted directories to `/bin` and `/usr/bin` only
**Solution:** Add tool paths to `openclaw.json`:
```json
"tools": {
  "exec": {
    "safeBinTrustedDirs": ["/bin", "/usr/bin", "/opt/homebrew/bin", "/usr/local/bin"]
  }
}
```
Then `openclaw gateway restart`.

## Stale Sessions / Missing Transcripts

**Symptom:** `openclaw doctor` reports missing transcript files
**Solution:** Run `openclaw sessions cleanup --fix-missing` to prune orphaned entries.

## DM Allowlist Not Working After Upgrade

**Symptom:** Bot stops responding to DMs after upgrading
**Cause:** v2026.2.26 enforces strict DM allowlist inheritance across account+parent config
**Solution:** Run `openclaw doctor` — it now validates DM allowlist inheritance logic.

## Common Error Patterns

| Error | Likely Cause | Quick Fix |
|-------|-------------|-----------|
| `ENETUNREACH` | IPv6 not working | Native fix in v2026.2.24+; run `openclaw doctor` |
| `401 Unauthorized` | Invalid/expired API token | Rotate the token |
| `429 Too Many Requests` | Rate limited | Wait and retry; consider using fallback model |
| `ENOENT: no such file` | Missing workspace file | Re-run scaffold.sh |
| `timeout` | Agent task took too long | Simplify the brief or increase timeout |
| `exec approval denied` | Safe-bin trusted dirs missing tool path | Add path to `tools.exec.safeBinTrustedDirs` |
