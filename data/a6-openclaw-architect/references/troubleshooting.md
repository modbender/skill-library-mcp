# OpenClaw Troubleshooting Guide

Real issues from production deployment with fixes.

## Session & Context Issues

### Session crashed / context overflow (780+ messages)
**Symptom:** Agent stops responding, session becomes unrecoverable.
**Cause:** Context window exceeded + credits exhausted simultaneously — can't compact.
**Fix:**
1. Check for backup: `ls ~/.openclaw/sessions/*.jsonl.reset`
2. Extract messages from backup if needed
3. Start fresh session — old context is lost
4. **Prevention:** Enable `memoryFlush` in compaction config, keep conversations focused

### Agent guessing instead of researching
**Symptom:** Agent fabricates information, claims tools are installed when they aren't.
**Cause:** Model hallucination — no guardrail forcing tool use.
**Fix:** Add rule to AGENTS.md/MEMORY.md: "NEVER guess or assume. Always use web_search or tools."
**Prevention:** Include in system prompt, verify claims with actual commands.

## Model & Routing Issues

### OpenRouter credits exhausted
**Symptom:** All OpenRouter-backed operations fail, fallback models fail.
**Cause:** Heavy operations (publishing batches, sub-agents) burned through balance.
**Fix:**
1. Check balance at openrouter.ai/credits
2. Add credits
3. Set budget alerts on OpenRouter dashboard
**Prevention:** Monitor via cron job, use cheaper models for bulk work (Sonnet not Opus for publishing).

### Model fallback not working
**Symptom:** Primary model fails, agent doesn't switch to fallback.
**Cause:** Fallback model ID incorrect or provider auth missing.
**Fix:**
1. Verify model IDs: `openclaw models`
2. Test each fallback: send a message with primary disabled
3. Ensure OpenRouter auth profile is configured
4. Check model ID format: `openrouter/provider/model-name`

### "Unknown model" errors
**Symptom:** Gateway logs show model not found.
**Cause:** Model renamed or deprecated by provider.
**Fix:** Check OpenRouter model list, update model IDs in config.

## Brain Stack Issues

### Split brain — two Qdrant collections
**Symptom:** Some memories found, others missing.
**Cause:** Mem0 config changed, created a new collection instead of using existing.
**Fix:**
1. Check collections: `curl localhost:6333/collections`
2. Migrate to single collection
3. Update brain_engine.py config to use correct collection name

### Neo4j schema chaos (80+ labels)
**Symptom:** Graph queries return inconsistent results.
**Cause:** No schema enforcement, Mem0 auto-creates arbitrary labels.
**Fix:** Run schema normalization script, consolidate to canonical labels.
**Our canonical labels:** 19 labels, 16 relationship types.

### brain_engine.py timeouts (15-25s per call)
**Symptom:** Batch operations time out.
**Cause:** Each `remember` call → embedding + LLM entity extraction + Qdrant write + Neo4j write.
**Workaround:** For bulk ops, write directly to Qdrant/Neo4j, bypass Mem0.

### Brain system empty despite being "installed"
**Symptom:** `recall` returns nothing, but Mem0/Qdrant/Neo4j are running.
**Cause:** Nobody called `remember` — all content went to markdown files.
**Fix:** Backfill: `$PY tools/brain_backfill.py` or manually call `brain_engine.py remember` for key facts.

## Cron Issues

### Cron job fires but nothing happens
**Check:**
1. `openclaw cron list` — is it enabled?
2. Delivery mode — `system` is silent
3. Target — valid channel/user?
4. Gateway logs — any errors?

### Skill publisher cron failing (27+ errors)
**Symptom:** Consecutive errors in cron logs.
**Common causes:** Exec host permissions, script path wrong, missing env vars.
**Fix:** Check script exists and is executable, verify paths, test manually first.

### Daily check-in cron failing
**Symptom:** Announce delivery failed.
**Common causes:** Session targeting issue, channel not connected.
**Fix:** Verify channel is online: `openclaw status`

## Infrastructure Issues

### Gateway telemetry errors
**Symptom:** SigNoz/Langfuse/Kuma errors in logs.
**Cause:** OTEL collector endpoint unreachable or misconfigured.
**Fix:** Check `diagnostics.otel.endpoint` in config, verify collector is running.
**Workaround:** Disable OTEL if not needed: `"diagnostics.otel.enabled": false`

### Docker socket permissions
**Symptom:** `docker` commands fail inside container.
**Fix:** Ensure socket is mounted and group matches: `-v /var/run/docker.sock:/var/run/docker.sock`
**Container must be in docker group (988).**

### Tailscale VPN not connecting
**Symptom:** Can't reach other nodes on Tailscale network.
**Fix:**
1. Check: `tailscale status`
2. Ensure `--net=host` or proper network config
3. ⚠️ NEVER use `tailscale set --exit-node=...` on the server — breaks all inbound connections

### VPS resource exhaustion (8GB RAM)
**Symptom:** Services crashing, OOM kills.
**Current usage:** ~4.5GB of 8GB.
**Heavy services:** Qdrant (~512MB), Neo4j (~1GB), OpenClaw (~1GB).
**Fix:** Don't add Wazuh (needs 6-7GB alone). Use Falco (~512MB) for security instead.

## Channel Issues

### Telegram bot not responding
1. Check bot token is valid
2. `openclaw status` — is Telegram connected?
3. `openclaw channels` — any errors?
4. Restart gateway: `openclaw gateway restart`

### Messages not streaming
**Check:** `channels.telegram.streamMode` should be `"partial"`.

## Quick Diagnostic Commands

```bash
openclaw health              # Gateway alive?
openclaw status              # Channels connected?
openclaw doctor              # Full diagnostic
openclaw logs                # Recent gateway logs
openclaw cron list           # Cron jobs status
openclaw skills              # Skills loaded?
openclaw models              # Available models?
```
