---
name: granola
description: Access Granola AI meeting notes via MCP (mcporter). Query meetings, list by date range, get full details, and pull verbatim transcripts. Use when the user asks about meeting notes, what was discussed, action items, decisions, or anything from their meetings. Also handles OAuth token refresh when calls fail with auth errors.
metadata:
  openclaw:
    requires:
      bins: [mcporter, bash, curl, python3]
    config:
      - path: config/granola_oauth.json
        description: "OAuth credentials: client_id, refresh_token, access_token, token_endpoint (from Granola MCP auth flow)"
      - path: config/mcporter.json
        description: "MCP server config with bearer token header for Granola API"
---

# Granola MCP

Meeting notes AI connected via `mcporter call granola.<tool>`.

## Tools

```
granola.query_granola_meetings  query=<string> [document_ids=<uuid[]>]
granola.list_meetings           [time_range=this_week|last_week|last_30_days|custom] [custom_start=<ISO>] [custom_end=<ISO>]
granola.get_meetings            meeting_ids=<uuid[]>  (max 10)
granola.get_meeting_transcript  meeting_id=<uuid>
```

## Usage Pattern

1. For open-ended questions ("what did we discuss about X?"), use `query_granola_meetings`
2. For listing meetings in a range, use `list_meetings`
3. For full details on specific meetings, use `get_meetings` with IDs from list results
4. For exact quotes or verbatim content, use `get_meeting_transcript`

Prefer `query_granola_meetings` over list+get for natural language questions. Responses include citation links (e.g. `[[0]](url)`). Preserve these in replies so the user can click through to original notes.

## Setup

1. Complete the Granola OAuth flow at `https://mcp-auth.granola.ai/oauth2/authorize`
2. Save credentials to `config/granola_oauth.json` with keys: `client_id`, `refresh_token`, `access_token`, `token_endpoint`
3. Configure `config/mcporter.json` with the Granola MCP server entry and `Authorization: Bearer <token>` header
4. (Optional) Set up a cron job to run `scripts/refresh_token.sh` periodically, since OAuth tokens expire every ~6 hours

## Auth & Token Refresh

**If a call fails with 401/auth error:**

```bash
bash {baseDir}/scripts/refresh_token.sh
```

The script reads `config/granola_oauth.json`, posts to the token endpoint (`https://mcp-auth.granola.ai/oauth2/token`), and updates both `config/granola_oauth.json` and `config/mcporter.json` with the new access token.

Then retry the call. If refresh also fails, the user needs to re-authenticate manually via the OAuth flow above.

## Config Files

- `config/granola_oauth.json` — OAuth credentials (client_id, refresh_token, access_token, token_endpoint). **Contains secrets; do not commit.**
- `config/mcporter.json` — MCP server config with bearer token header. **Contains secrets; do not commit.**
