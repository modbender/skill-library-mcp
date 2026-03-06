# OpenClaw Docs Errata

Known discrepancies between the local docs and actual runtime behavior. Always verify config keys against the gateway reload log before trusting docs blindly.

## Discord Streaming (channels/discord.md)
**Doc claims**: `channels.discord.streaming` supports `off | partial | block | progress`
**Reality**: Streaming preview is **Telegram-only** as of v2026.2.21-2. The concepts/streaming doc says: "Telegram preview streaming is the only partial-stream surface." The gateway config validator rejects `streaming` under `channels.discord`.
**Source**: Confirmed via Context7 `/openclaw/openclaw` — concepts/streaming.md explicitly states Telegram-only.

## Discord threadBindings (channels/discord.md)
**Doc claims**: `channels.discord.threadBindings` is a valid per-channel override
**Reality**: Thread bindings go under `session.threadBindings` (global). The gateway rejects `threadBindings` under `channels.discord` as an unrecognized key. The global `session.threadBindings` key works correctly.

## Validation Approach
When implementing config changes from docs:
1. Add keys one at a time
2. Check `tail /tmp/openclaw/openclaw.log | grep -i reload` after each change
3. If you see "Unrecognized key", the feature may not exist in this version or the doc is wrong
4. Use Context7 (`/openclaw/openclaw`) to cross-reference against the actual source repo
5. The `gateway/configuration-reference` doc is the most reliable local source of truth for config keys
