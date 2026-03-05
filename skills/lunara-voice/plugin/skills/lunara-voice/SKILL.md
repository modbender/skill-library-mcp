---
name: lunara-voice
description: Manage Lunara Voice AI — agents, campaigns, outbound calls, call history, analytics, webhooks, tags, and LLM data export
metadata: {"openclaw": {"always": true, "emoji": "📞", "homepage": "https://lunaravox.com"}}
---

# Lunara Voice AI — Complete Agent Tool Guide

You have full access to the Lunara Voice AI platform through **33 tools** organized into two API modules:

- **Core API** (15 tools): Agent management, campaigns, calls, API keys
- **History & Analytics API** (18 tools): Call history, transcripts, analytics dashboards, LLM export, tags, webhooks

## All Available Tools

### Core Tools (Agent Management & Calls)

| Tool | Purpose |
|------|---------|
| `lunara_health` | Check if the Lunara API is online |
| `lunara_agents_list` | List all voice agents |
| `lunara_agent_get` | Get agent details (prompt, voice, balance) |
| `lunara_agent_update` | Update agent config (prompt, voice, greeting, SIP) |
| `lunara_campaign_create` | Create a call campaign with contacts |
| `lunara_campaign_list` | List all campaigns |
| `lunara_campaign_get` | Get campaign progress/status |
| `lunara_campaign_start` | Start a campaign's call loop |
| `lunara_campaign_stop` | Stop (pause) a running campaign |
| `lunara_call_single` | Make a single outbound call |
| `lunara_key_create` | Create a new API key |
| `lunara_key_list` | List API keys |
| `lunara_key_revoke` | Revoke an API key |
| `lunara_key_delete` | Permanently delete an API key |
| `lunara_docs` | Fetch Core API documentation JSON |

### History & Transcript Tools

| Tool | Purpose |
|------|---------|
| `lunara_history_health` | Check ClawBot History API health & features |
| `lunara_history_list` | Get paginated call history with rich filters |
| `lunara_history_detail` | Get full call detail + transcript + tags |
| `lunara_history_search` | Search call transcripts by text/keyword |

### LLM Export Tools

| Tool | Purpose |
|------|---------|
| `lunara_export_single` | Export one conversation in LLM format (openai/training/raw) |
| `lunara_export_bulk` | Bulk export conversations for LLM training |

### Analytics Tools

| Tool | Purpose |
|------|---------|
| `lunara_analytics_dashboard` | Full analytics: call stats, sentiment, topics, daily trends |
| `lunara_analytics_save` | Save AI analysis for a conversation (sentiment, summary, etc.) |
| `lunara_analytics_batch` | Batch save analytics for multiple conversations |

### Tagging Tools

| Tool | Purpose |
|------|---------|
| `lunara_tags_add` | Add tags to a conversation (manual/auto/ai) |
| `lunara_tags_remove` | Remove a tag from a conversation |

### Webhook Tools

| Tool | Purpose |
|------|---------|
| `lunara_webhook_create` | Create webhook for real-time call event notifications |
| `lunara_webhook_list` | List all webhook subscriptions |
| `lunara_webhook_update` | Update webhook URL/events/status |
| `lunara_webhook_delete` | Delete a webhook |
| `lunara_webhook_test` | Test webhook connectivity |
| `lunara_webhook_deliveries` | View webhook delivery log |

### Documentation

| Tool | Purpose |
|------|---------|
| `lunara_clawbot_docs` | Fetch full ClawBot History API docs (OpenAPI 3.0) |

---

## Typical Workflows

### 1. View and manage agents
1. `lunara_agents_list` — see all configured agents
2. `lunara_agent_get` with assistant_id — check details, prompt, minute balance
3. `lunara_agent_update` — change prompt, voice, greeting, language, or SIP config

### 2. Run a call campaign
1. `lunara_agents_list` — pick an agent
2. `lunara_agent_get` — verify the agent has minutes
3. `lunara_campaign_create` — upload contacts (phone numbers or objects with name/metadata)
4. `lunara_campaign_start` — begin calling
5. `lunara_campaign_get` — monitor progress (processed, successful, failed counts)
6. `lunara_campaign_stop` — pause if needed

### 3. Quick single call

**⚠️ There is NO "fire and forget" call flow.** Every single outbound call MUST follow the full end-to-end workflow in **Section 5** below — including polling for completion and reporting transcript results. Never just call `lunara_call_single` and stop.

### 4. Review call results after a call or campaign
1. `lunara_history_list` with assistant_id — see recent calls
2. `lunara_history_detail` with conversation_id — get full transcript
3. `lunara_analytics_save` — save your analysis (sentiment, summary, quality)
4. `lunara_tags_add` — tag the call (e.g. "interested", "follow-up", "vip")

### 5. Make a call and report the result (end-to-end) — DEFAULT FOR ALL CALLS

**⚠️ AUTONOMOUS EXECUTION — This workflow applies to EVERY outbound call, no exceptions!**
**Whenever the user asks to call someone — regardless of phrasing ("позвони", "набери", "call", "договорись", "сделай звонок", etc.) — you MUST complete ALL steps below in ONE turn. Never just initiate a call and stop.**

1. **Record the current timestamp** (ISO 8601, e.g. `2026-02-16T19:45:00Z`) and the **phone number** you are calling BEFORE making the call. You will need these to find the NEW call record.
2. `lunara_call_single` — place the call. Save the returned **Call SID**.
3. **Poll until THE NEW call completes** — call `lunara_history_list` with `date_from=<timestamp from step 1>` and `caller=<phone_number>` every 25-30 seconds. **You MUST use date_from to exclude old calls.** Keep polling until a record appears that matches the phone number AND was created AFTER step 1's timestamp (up to 5 minutes / 10 attempts). Do NOT message the user — poll silently.
4. `lunara_history_detail` with `include_transcript=true` and the **conversation_id from the NEW record** (not the first/latest random record!) — read the full transcript.
5. `lunara_analytics_save` — record sentiment, summary, outcome
6. `lunara_tags_add` — categorize the result
7. **Report final result to user** — summarize: who answered, what was discussed, what was agreed, next steps. Include key quotes from transcript.

**⚠️ CRITICAL BUG PREVENTION:**
- **NEVER** grab the first record from `lunara_history_list` without checking `date_from` and phone number match
- Old call records will appear in history — you MUST filter them out using `date_from=<timestamp before call>`
- If you report results from a call that happened BEFORE `lunara_call_single`, you are reporting the WRONG call
- Always verify: does the transcript mention the topic/context of THIS call, not some previous call?

**CRITICAL:** ANY request to make a call — "позвони", "набери номер", "договорись", "сделай звонок", "call", "ring", "negotiate", etc. — MUST trigger ALL 7 steps automatically. The user ALWAYS expects to see the call outcome in the same response. Never stop after step 2 to say "call initiated" and wait. Never report results before the call has finished — the transcript won't exist yet and you'll get wrong/empty data.

### 6. Analytics overview
1. `lunara_analytics_dashboard` with assistant_id — get full statistics
2. Review: total calls, sentiment distribution, top topics, resolution rates, peak hours
3. Use date_from/date_to for time-bounded analysis

### 7. Search through call history
1. `lunara_history_search` with search_text — find calls mentioning specific keywords
2. `lunara_history_detail` — drill into matching calls for full transcript

### 8. Export data for AI training
1. `lunara_export_single` — export one call in openai/training/raw format
2. `lunara_export_bulk` — bulk export multiple calls with filters

### 9. Set up webhook notifications
1. `lunara_webhook_create` — subscribe to events (e.g. call.completed)
2. `lunara_webhook_test` — verify connectivity
3. `lunara_webhook_list` — see all subscriptions
4. `lunara_webhook_deliveries` — check delivery log for debugging

### 10. API key management
1. `lunara_key_list` — see existing keys
2. `lunara_key_create` — generate a new key (save it immediately!)
3. `lunara_key_revoke` — disable a key
4. `lunara_key_delete` — remove permanently

---

## Important Notes

- **Voices**: alloy, ash, ballad, coral, echo, sage, shimmer, verse, marin, cedar
- **Phone format**: 7-15 digits, optional leading `+` (e.g. `+12125551234`)
- **Max contacts per campaign**: 10,000
- **Minute balance**: Check before starting campaigns. If balance is 0, calls will fail with 402.
- **Campaign statuses**: pending → running → completed/paused/failed
- **PII masking**: Call history and exports support PII masking (on by default). Set mask_pii=false to get raw data.
- **LLM export formats**: `openai` (Chat Completions), `training` (JSONL fine-tuning), `raw` (full JSON)
- **Sentiment labels**: positive, neutral, negative, mixed
- **Resolution statuses**: resolved, unresolved, escalated, pending
- **Webhook events**: call.started, call.completed, call.failed, analysis.completed, campaign.started, campaign.completed, campaign.failed
- **Webhook URLs**: Must be HTTPS. Auto-disabled after 10 consecutive failures.
- **Tag sources**: manual, auto, ai (max 50 tags per conversation)
- API keys are shown only once at creation. Always save them immediately.

---

## History Filter Reference

The `lunara_history_list` tool supports these filters (all optional):

| Filter | Type | Description |
|--------|------|-------------|
| `date_from` | ISO 8601 string | Start of date range |
| `date_to` | ISO 8601 string | End of date range |
| `direction` | "inbound" / "outbound" | Call direction |
| `caller` | string | Partial match on caller number |
| `did` | string | Partial match on DID |
| `min_duration` | integer | Minimum call duration (seconds) |
| `max_duration` | integer | Maximum call duration (seconds) |
| `has_audio` | boolean | Has audio recording |
| `sentiment` | string | positive/neutral/negative/mixed |
| `resolution_status` | string | resolved/unresolved/escalated/pending |
| `tags` | comma-separated | Filter by tags |
| `search_text` | string | Full-text search in transcripts |
| `mask_pii` | boolean | Mask personal info (default true) |

---

## Example User Requests → Tool Mapping

### Agent & Call Management
- "Show my agents" → `lunara_agents_list`
- "What voice does agent X use?" → `lunara_agent_get(assistant_id=X)`
- "Change voice to coral" → `lunara_agent_update(assistant_id=X, voice="coral")`
- "Update the prompt" → `lunara_agent_update(assistant_id=X, prompt="...")`
- "Call +12125551234" → `lunara_call_single(to_number="+12125551234", assistant_id=X)`
- "How many minutes left?" → `lunara_agent_get(assistant_id=X)` → check minutes_balance

### Campaign Management
- "Create campaign with numbers +123, +456" → `lunara_campaign_create(assistant_id=X, contacts=["+123","+456"])`
- "Start campaign abc" → `lunara_campaign_start(campaign_id="abc")`
- "Campaign status" → `lunara_campaign_get(campaign_id="abc")`
- "Stop campaign" → `lunara_campaign_stop(campaign_id="abc")`

### Call History & Transcripts
- "Show recent calls" → `lunara_history_list(assistant_id=X)`
- "Show last 10 calls" → `lunara_history_list(assistant_id=X, page_size=10)`
- "Show call details" → `lunara_history_detail(assistant_id=X, conversation_id=Y)`
- "What was said in the last call?" → `lunara_history_list` → get ID → `lunara_history_detail`
- "Show inbound calls only" → `lunara_history_list(assistant_id=X, direction="inbound")`
- "Calls from today" → `lunara_history_list(assistant_id=X, date_from="2026-02-16T00:00:00Z")`
- "Find calls about pricing" → `lunara_history_search(assistant_id=X, search_text="pricing")`
- "Show calls longer than 5 minutes" → `lunara_history_list(assistant_id=X, min_duration=300)`
- "Show calls with negative sentiment" → `lunara_history_list(assistant_id=X, sentiment="negative")`

### Analytics
- "Show analytics" → `lunara_analytics_dashboard(assistant_id=X)`
- "Call statistics for last week" → `lunara_analytics_dashboard(assistant_id=X, date_from=..., date_to=...)`
- "What topics come up most?" → `lunara_analytics_dashboard` → check top_topics
- "Save analysis for this call" → `lunara_analytics_save(assistant_id=X, conversation_id=Y, sentiment_label="positive", summary="...")`
- "How many resolved calls?" → `lunara_analytics_dashboard` → check resolution_distribution

### Tags
- "Tag this call as VIP" → `lunara_tags_add(assistant_id=X, conversation_id=Y, tags=["vip"])`
- "Add tags: follow-up, interested" → `lunara_tags_add(assistant_id=X, conversation_id=Y, tags=["follow-up","interested"])`
- "Remove the urgent tag" → `lunara_tags_remove(assistant_id=X, conversation_id=Y, tag="urgent")`

### Export
- "Export this call for training" → `lunara_export_single(assistant_id=X, conversation_id=Y, format="training")`
- "Export all calls in OpenAI format" → `lunara_export_bulk(assistant_id=X, format="openai")`
- "Export last 50 positive calls" → `lunara_export_bulk(assistant_id=X, limit=50, sentiment="positive")`

### Webhooks
- "Set up webhook for call completions" → `lunara_webhook_create(url="https://...", events=["call.completed"])`
- "Show webhooks" → `lunara_webhook_list`
- "Test webhook" → `lunara_webhook_test(webhook_id=X)`
- "Pause webhook" → `lunara_webhook_update(webhook_id=X, status="paused")`
- "Delete webhook" → `lunara_webhook_delete(webhook_id=X)`
- "Show webhook delivery log" → `lunara_webhook_deliveries(webhook_id=X)`

### System
- "Is the API working?" → `lunara_health`
- "Is history API working?" → `lunara_history_health`
- "Show API keys" → `lunara_key_list`
- "Create key named production" → `lunara_key_create(name="production")`

---

## ⚠️ Autonomous Execution Rules — APPLY TO EVERY OUTBOUND CALL

**Every outbound call (lunara_call_single or campaign) MUST complete the entire workflow in a single turn. There are no exceptions — the user should NEVER have to ask "what happened?" separately:**

1. Do NOT stop after initiating the call to say "Call started, SID: xxx" and wait
2. Do NOT ask the user "should I check the results now?"
3. Do NOT search for the transcript while the call is still active — it doesn't exist yet!
4. **Poll `lunara_history_list` silently** every 25-30 seconds until the call record appears as completed (max 5 minutes / 10 attempts)
5. Only AFTER the call record appears as completed, fetch `lunara_history_detail` with transcript
6. Present ONLY the final summary: outcome, key points, agreements, next steps

**Polling pattern (MUST use date_from to avoid reporting old calls):**
```
call_start_time = current ISO 8601 timestamp (BEFORE lunara_call_single)
called_number = the phone number being called
call_sid = result of lunara_call_single

# IMPORTANT: Wait at least 30 seconds before the FIRST poll!
# The call needs time to connect and complete.
wait 30 seconds

loop (max 10 attempts, 25-30 sec apart):
  result = lunara_history_list(
    assistant_id=X,
    page_size=5,
    date_from=call_start_time,   # ← MANDATORY! Filters out all old calls
    caller=called_number          # ← MANDATORY! Matches the specific number
  )
  for each record in result:
    if record.created_at > call_start_time AND record matches called_number:
      # Verify the call status is "completed" (not "in-progress")
      if record.status == completed:
        → this is the NEW completed call, use its conversation_id
        break
      else:
        # Call still in progress, keep polling
        wait 25-30 seconds
  else:
    wait 25-30 seconds
```

**⚠️ CRITICAL BUGS TO AVOID:**
1. **If you skip date_from, you WILL get old call records and report wrong results!**
2. **If you fetch the transcript while the call is still active, you'll get incomplete/empty data — ALWAYS wait for status=completed!**
3. **If you report results without polling, you're reporting STALE data from a previous call!**

**The user expects ONE response** with the complete call result, not a multi-message back-and-forth asking them to wait or confirm each step.
