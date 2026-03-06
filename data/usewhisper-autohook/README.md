# usewhisper-autohook (OpenClaw Skill)

Two commands meant to be called on every agent turn:

- `get_whisper_context` (pre-query)
- `ingest_whisper_turn` (post-response)

Install:

```bash
npx clawhub@latest install usewhisper-autohook
```

Env:

```bash
WHISPER_CONTEXT_API_URL=https://context.usewhisper.dev
WHISPER_CONTEXT_API_KEY=YOUR_KEY
WHISPER_CONTEXT_PROJECT=openclaw-yourname
```

One-liners:

```bash
node usewhisper-autohook.mjs get_whisper_context --current_query "USER_MESSAGE" --user_id "telegram:FROM_ID" --session_id "telegram:CHAT_ID"
```

```bash
echo '{ "user_msg": "USER_MESSAGE", "assistant_msg": "ASSISTANT_REPLY" }' | node usewhisper-autohook.mjs ingest_whisper_turn --session_id "telegram:CHAT_ID" --user_id "telegram:FROM_ID" --turn_json -
```

