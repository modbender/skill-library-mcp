---
name: usewhisper-autohook
description: "Auto-hook tools for OpenClaw: query Whisper Context before every
  generation, ingest after every turn. Built for Telegram agents (stable
  user_id/session_id)."
---


# usewhisper-autohook (OpenClaw Skill)

This skill is a thin wrapper designed to make "automatic memory" easy:

- `get_whisper_context(user_id, session_id, current_query)` for pre-response context injection
- `ingest_whisper_turn(user_id, session_id, user_msg, assistant_msg)` for post-response ingestion

It defaults to the token-saving settings you almost always want:

- `compress: true`
- `compression_strategy: "delta"`
- `use_cache: true`
- `include_memories: true`

It also persists the last `context_hash` locally (per `api_url + project + user_id + session_id`) so delta compression works by default without you needing to pass `previous_context_hash`.

## Install (ClawHub)

```bash
npx clawhub@latest install usewhisper-autohook
```

## Setup

Set env vars wherever OpenClaw runs your agent:

```bash
WHISPER_CONTEXT_API_URL=https://context.usewhisper.dev
WHISPER_CONTEXT_API_KEY=YOUR_KEY
WHISPER_CONTEXT_PROJECT=openclaw-yourname
```

Notes:

- `WHISPER_CONTEXT_API_URL` is optional (defaults to `https://context.usewhisper.dev`).
- The helper will auto-create the project on first use if it does not exist yet.

## The "Auto Loop" Prompt (Copy/Paste)

Add this to your agent's **system instruction** (or equivalent):

```text
Before you think or respond to any message:
1) Call get_whisper_context with:
   user_id = "telegram:{from_id}"
   session_id = "telegram:{chat_id}"
   current_query = the user's message text
2) If the returned context is not empty, prepend it to your prompt as:
   "Relevant long-term memory:\n{context}\n\nNow respond to:\n{user_message}"

After you generate your final response:
1) Call ingest_whisper_turn with the same user_id and session_id and:
   user_msg = the full user message
   assistant_msg = your full final reply

Always do this. Never skip.
```

If you are not on Telegram, keep the same structure: the important part is that `user_id` and `session_id` are stable.

## If Your Agent Still Replays Full Chat History (Proxy Mode)

If you cannot control how your agent/framework constructs prompts (it always sends the full conversation history), a system prompt cannot reduce token spend: the tokens are already sent to the model.

In that case, run the built-in OpenAI-compatible proxy so the **network payload is actually reduced**. The proxy:

- receives `POST /v1/chat/completions`
- queries Whisper memory
- strips chat history down to system + last user message
- injects `Relevant long-term memory: ...`
- calls your upstream OpenAI-compatible provider
- ingests the turn back into Whisper

Start the proxy:

```bash
export OPENAI_API_KEY="YOUR_UPSTREAM_KEY"
node usewhisper-autohook.mjs serve_openai_proxy --port 8787
```

Then point your agent’s OpenAI base URL to `http://127.0.0.1:8787` (exact env/config depends on your agent).

If your agent supports overriding the upstream base URL, you can set:

- `OPENAI_BASE_URL` (for OpenAI-compatible upstreams)
- `ANTHROPIC_BASE_URL` (for Anthropic upstreams)

Or pass `--upstream_base_url` when starting the proxy.

For correct per-user/session memory, pass headers on each request:

- `x-whisper-user-id: telegram:{from_id}`
- `x-whisper-session-id: telegram:{chat_id}`

### Anthropic Native Proxy (`/v1/messages`)

If your agent uses **Anthropic's native API** (not OpenAI-compatible), run the Anthropic proxy instead:

```bash
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_KEY"
node usewhisper-autohook.mjs serve_anthropic_proxy --port 8788
```

Then point your agent’s Anthropic base URL to `http://127.0.0.1:8788`.

Pass IDs via headers (recommended):

- `x-whisper-user-id: telegram:{from_id}`
- `x-whisper-session-id: telegram:{chat_id}`

If you do not pass headers, the proxies will attempt to infer stable IDs from OpenClaw's system prompt / session key if present. This is best-effort; headers are still the most reliable.

## CLI Usage (what the tools call)

All commands print JSON to stdout.

### Get packed context

```bash
node usewhisper-autohook.mjs get_whisper_context \
  --current_query "What did we decide last time?" \
  --user_id "telegram:123" \
  --session_id "telegram:456"
```

### Ingest a completed turn

```bash
node usewhisper-autohook.mjs ingest_whisper_turn \
  --user_id "telegram:123" \
  --session_id "telegram:456" \
  --user_msg "..." \
  --assistant_msg "..."
```

For large content, pass JSON via stdin:

```bash
echo '{ "user_msg": "....", "assistant_msg": "...." }' | node usewhisper-autohook.mjs ingest_whisper_turn --session_id "telegram:456" --user_id "telegram:123" --turn_json -
```

## Output Format

`get_whisper_context` returns:

- `context`: the packed context string to prepend
- `context_hash`: a short hash you can store and pass back as `previous_context_hash` next time (optional)
- `meta`: cache hit and compression info (useful for debugging)
