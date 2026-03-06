---
name: claw-lark-patches
description: Re-apply custom patches to claw-lark plugin dist files after updates. Use when claw-lark plugin is updated/reinstalled and custom behaviors (requireMention filtering, reply_in_thread, thread-based replies) stop working. Also use when debugging Lark message routing issues.
---

# claw-lark Patches

claw-lark is a compiled plugin — we patch dist files directly. **Every plugin update wipes these patches.** This skill documents exactly what to change and provides an auto-apply script.

## Quick Apply

```bash
bash scripts/apply-patches.sh
```

Then restart gateway: `openclaw gateway restart`

## Patches Overview

Four files are patched:
1. **channel.js** — messaging.targetResolver (target ID recognition) + outbound account resolution
2. **monitor.js** — requireMention filtering + reply-in-thread for deliver callback
3. **provider.js** — reply-in-thread for sendTextMessage
4. **send.js** — reply-in-thread for SDK reply calls

## Patch Details

### 0. channel.js — Target Resolution + Account Resolution (2026-02-22)

**Problem 1**: `message(send, lark, "oc_xxx")` returns "Unknown target" because claw-lark has no `messaging.targetResolver.looksLikeId`. The core doesn't recognize `oc_/ou_/on_` as valid IDs and falls through to directory lookup which fails.

**Fix**: Add `messaging` property to `larkPlugin` export:
- Import `looksLikeLarkId, normalizeLarkTarget` from `./utils.js`
- Add `messaging.targetResolver.looksLikeId` using existing `looksLikeLarkId()`
- Add `messaging.normalizeTarget` using existing `normalizeLarkTarget()`

**Problem 2**: `outbound.sendText` gets `{ cfg, to, accountId }` from core but expects `{ account, recipientId }`. The `account` object is undefined → "Cannot read properties of undefined (reading 'appId')".

**Fix**: All 5 outbound methods (`sendText`, `sendMedia`, `downloadMedia`, `addReaction`, `removeReaction`) add:
```javascript
const account = args.account ?? resolveAccount(args.cfg, args.accountId ?? "default");
const recipientId = args.recipientId ?? args.to;
```

### 1. monitor.js — requireMention Filter

**Location**: `routeMessage()` function, after `parseMessage(event)` and the log line.

**What**: In group chats, skip messages that don't @mention our bot.

**Key facts**:
- `event.message` is the correct path (NOT `event.event.message`)
- Lark webhook `message.mentions` contains mention data with `id.open_id`
- Bot open_id: set via `BOT_OPEN_ID` env var when running `apply-patches.sh`
- All bots lack `user_id` (empty string) — cannot use `!user_id` to detect "is it me"
- `@_user_N` text placeholders appear for ALL @'d bots, not just ours — don't use regex match
- Fallback: if mentions array empty, check `parsed.text.includes("@" + BOT_NAME)` (set via `BOT_NAME` env var)

### 2. monitor.js — Reply in Thread (deliver callback)

**Location**: Inside `dispatchReplyWithBufferedBlockDispatcher` deliver callback.

**What**: 
- Set `replyToId = payload.replyToId || parsed.threadId || parsed.messageId` (always have a value)
- Use `client.im.message.reply()` with `reply_in_thread: true` instead of `client.im.message.create()` with `root_id`

**Key facts**:
- `root_id` on create only associates with existing thread, does NOT create new thread
- `reply_in_thread: true` on reply API creates a new thread
- Works in both p2p and group chats

### 3. provider.js — sendTextMessage Thread Reply

**Location**: `sendTextMessage()` function.

**What**: When `threadId` is provided, use `client.im.message.reply()` instead of `client.im.message.create()`.

### 4. send.js — reply_in_thread on SDK Reply

**Location**: `sendMessageLark()` and `sendCardLark()` reply branches.

**What**: Add `reply_in_thread: true` to data object in `client.im.message.reply()` calls.

## Verification

After applying patches and restarting gateway:
1. Send a group message WITHOUT @bot → should be silently ignored
2. Send a group message WITH @bot → should reply in thread
3. Send a DM → should reply in thread
4. @ another bot → should be silently ignored

## See Also

- `references/patch-details.md` — Full code diffs for each patch
