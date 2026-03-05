#!/bin/bash
# Auto-apply claw-lark patches after plugin update
# Usage: bash apply-patches.sh
#
# Environment variables (optional overrides):
#   CLAW_LARK_DIST  — path to claw-lark dist/src (default: ~/.openclaw/extensions/claw-lark/dist/src)
#   BOT_OPEN_ID     — your bot's open_id for requireMention filter
#   BOT_NAME        — your bot's display name for @mention text fallback
set -e

DIST="${CLAW_LARK_DIST:-$HOME/.openclaw/extensions/claw-lark/dist/src}"
BOT_OPEN_ID="${BOT_OPEN_ID:-}"
BOT_NAME="${BOT_NAME:-}"

echo "=== claw-lark Patch Applicator ==="
echo "Target: $DIST"

if [ -z "$BOT_OPEN_ID" ]; then
  echo "⚠️  BOT_OPEN_ID not set. requireMention patch will use placeholder."
  echo "   Set it: export BOT_OPEN_ID=ou_xxxxx"
fi

# Check files exist
for f in channel.js monitor.js provider.js send.js; do
  if [ ! -f "$DIST/$f" ]; then
    echo "❌ $DIST/$f not found. Is claw-lark installed?"
    exit 1
  fi
done

export DIST BOT_OPEN_ID BOT_NAME

node << 'PATCH_EOF'
const fs = require('fs');
const DIST = process.env.DIST;
const BOT_OPEN_ID = process.env.BOT_OPEN_ID || 'YOUR_BOT_OPEN_ID';
const BOT_NAME = process.env.BOT_NAME || 'YOUR_BOT_NAME';

function patchFile(file, patches) {
  const path = `${DIST}/${file}`;
  let content = fs.readFileSync(path, 'utf8');
  let applied = 0;
  for (const [desc, search, replace] of patches) {
    if (content.includes(replace)) {
      console.log(`  ⏭️  ${desc} (already applied)`);
      continue;
    }
    if (!content.includes(search)) {
      console.log(`  ⚠️  ${desc} (search text not found — file may have changed)`);
      continue;
    }
    content = content.replace(search, replace);
    applied++;
    console.log(`  ✅ ${desc}`);
  }
  if (applied > 0) {
    fs.writeFileSync(path, content);
    console.log(`  📝 ${file} saved (${applied} patches)`);
  }
  return applied;
}

let total = 0;

// ── channel.js patches ──
console.log('\n📦 channel.js');

// Patch 0a: Add imports for looksLikeLarkId and normalizeLarkTarget
total += patchFile('channel.js', [
  [
    'import looksLikeLarkId + normalizeLarkTarget',
    'import { inferReceiveIdType } from "./utils.js";',
    'import { inferReceiveIdType, looksLikeLarkId, normalizeLarkTarget } from "./utils.js";'
  ],
]);

// Patch 0b: Add messaging.targetResolver to larkPlugin
total += patchFile('channel.js', [
  [
    'messaging.targetResolver for target ID recognition',
    '    outbound: {\n        deliveryMode: "direct",',
    `    messaging: {
        targetResolver: {
            looksLikeId: (raw, _normalized) => looksLikeLarkId(raw),
            hint: "Use a chat_id (oc_xxx), open_id (ou_xxx), or user/group name.",
        },
        normalizeTarget: (raw) => normalizeLarkTarget(raw) ?? raw,
    },
    outbound: {
        deliveryMode: "direct",`
  ],
]);

// Patch 0c: Fix outbound.sendText account resolution
total += patchFile('channel.js', [
  [
    'sendText account+recipientId compat',
    `async sendText(args) {
            const { account, recipientId, text, threadId } = args;
            return sendTextMessage(account, recipientId, text, threadId);`,
    `async sendText(args) {
            const account = args.account ?? resolveAccount(args.cfg, args.accountId ?? "default");
            const recipientId = args.recipientId ?? args.to;
            const { text, threadId } = args;
            return sendTextMessage(account, recipientId, text, threadId);`
  ],
  [
    'sendMedia account+recipientId compat',
    `async sendMedia(args) {
            const { account, recipientId, mediaId, mediaType, fileName, threadId } = args;`,
    `async sendMedia(args) {
            const account = args.account ?? resolveAccount(args.cfg, args.accountId ?? "default");
            const recipientId = args.recipientId ?? args.to;
            const { mediaId, mediaType, fileName, threadId } = args;`
  ],
  [
    'downloadMedia account compat',
    `async downloadMedia(args) {
            const { account, mediaId, messageId, mediaType } = args;`,
    `async downloadMedia(args) {
            const account = args.account ?? resolveAccount(args.cfg, args.accountId ?? "default");
            const { mediaId, messageId, mediaType } = args;`
  ],
  [
    'addReaction account compat',
    `async addReaction(args) {
            await addReactionLark({
                account: args.account,`,
    `async addReaction(args) {
            const account = args.account ?? resolveAccount(args.cfg, args.accountId ?? "default");
            await addReactionLark({
                account,`
  ],
  [
    'removeReaction account compat',
    `async removeReaction(args) {
            // If reactionId is not provided, we might need to find it first
            // But for now assume we have it or the API supports emoji removal (it doesn't, it needs reaction_id)
            // This is a limitation. We need to list reactions to find the ID if not provided.
            let reactionId = args.reactionId;
            if (!reactionId) {
                const reactions = await listReactionsLark({
                    account: args.account,`,
    `async removeReaction(args) {
            const account = args.account ?? resolveAccount(args.cfg, args.accountId ?? "default");
            let reactionId = args.reactionId;
            if (!reactionId) {
                const reactions = await listReactionsLark({
                    account,`
  ],
]);

// ── monitor.js patches ──
console.log('\n📦 monitor.js');

total += patchFile('monitor.js', [
  [
    'requireMention filter',
    `api.logger.info(\`[lark] Received message from \${parsed.senderId} in \${parsed.chatType} \${parsed.chatId}\`);
    // Route message to OpenClaw's message dispatcher`,
    `api.logger.info(\`[lark] Received message from \${parsed.senderId} in \${parsed.chatType} \${parsed.chatId}\`);
    // requireMention check: in group chats, skip messages that don't @mention our bot
    if (parsed.chatType === "group" && account.requireMention !== false) {
        const message = event?.message || event?.event?.message;
        const rawMentions = message?.mentions ?? [];
        const BOT_OPEN_ID = "${BOT_OPEN_ID}";
        const BOT_NAME = "${BOT_NAME}";
        let isMentioned = rawMentions.some(m => {
            if (m.name === "@_all" || m.key === "@_all") return true;
            const mentionOpenId = m.id?.open_id || m.id || "";
            return mentionOpenId === BOT_OPEN_ID;
        });
        if (!isMentioned && rawMentions.length === 0 && BOT_NAME) {
            isMentioned = parsed.text.includes("@" + BOT_NAME);
        }
        if (!isMentioned) {
            api.logger.debug(\`[lark] Skipping group message (not mentioned) in \${parsed.chatId}\`);
            return;
        }
        api.logger.info(\`[lark] Bot mentioned in group \${parsed.chatId}, processing\`);
    }
    // Route message to OpenClaw's message dispatcher`
  ],
  [
    'replyToId fallback to messageId',
    'const replyToId = payload.replyToId || parsed.threadId;',
    '// Always reply in thread: use original message ID to create/continue thread\n                                const replyToId = payload.replyToId || parsed.threadId || parsed.messageId;'
  ],
]);

// Patch 2: Replace create with reply in deliver callback
total += patchFile('monitor.js', [
  [
    'reply-in-thread for text messages',
    `if (text) {
                                    const client = createLarkClient(account);
                                    const response = await client.im.message.create({
                                        params: {
                                            receive_id_type: inferReceiveIdType(parsed.chatId),
                                        },
                                        data: {
                                            receive_id: parsed.chatId,
                                            msg_type: "text",
                                            content: JSON.stringify({ text }),
                                            ...(replyToId && { root_id: replyToId }),
                                            // Reply to specific message if in thread
                                            ...(parsed.threadId && { parent_id: parsed.messageId }),
                                        },
                                    });`,
    `if (text) {
                                    const client = createLarkClient(account);
                                    let response;
                                    if (replyToId) {
                                        // Reply in thread on the original message
                                        response = await client.im.message.reply({
                                            path: { message_id: replyToId },
                                            data: {
                                                msg_type: "text",
                                                content: JSON.stringify({ text }),
                                                reply_in_thread: true,
                                            },
                                        });
                                    } else {
                                        response = await client.im.message.create({
                                            params: {
                                                receive_id_type: inferReceiveIdType(parsed.chatId),
                                            },
                                            data: {
                                                receive_id: parsed.chatId,
                                                msg_type: "text",
                                                content: JSON.stringify({ text }),
                                            },
                                        });
                                    }`
  ],
]);

// ── provider.js patches ──
console.log('\n📦 provider.js');
total += patchFile('provider.js', [
  [
    'sendTextMessage reply-in-thread',
    `const response = await client.im.message.create({
            params: {
                receive_id_type: inferReceiveIdType(recipientId),
            },
            data: {
                receive_id: recipientId,
                msg_type: msgType,
                content,
                ...(threadId && { root_id: threadId }),
            },
        });
        if (response.code === 0 && response.data) {
            return { ok: true, messageId: response.data.message_id };
        }
        return { ok: false, error: response.msg ?? "Unknown error" };
    }
    catch (error) {
        return {
            ok: false,
            error: error instanceof Error ? error.message : "Unknown error",
        };
    }
}`,
    `// If threadId is provided, reply in thread instead of creating a new message
        if (threadId) {
            const response = await client.im.message.reply({
                path: { message_id: threadId },
                data: {
                    msg_type: msgType,
                    content,
                    reply_in_thread: true,
                },
            });
            if (response.code === 0 && response.data) {
                return { ok: true, messageId: response.data.message_id };
            }
            return { ok: false, error: response.msg ?? "Unknown error" };
        }
        const response = await client.im.message.create({
            params: {
                receive_id_type: inferReceiveIdType(recipientId),
            },
            data: {
                receive_id: recipientId,
                msg_type: msgType,
                content,
            },
        });
        if (response.code === 0 && response.data) {
            return { ok: true, messageId: response.data.message_id };
        }
        return { ok: false, error: response.msg ?? "Unknown error" };
    }
    catch (error) {
        return {
            ok: false,
            error: error instanceof Error ? error.message : "Unknown error",
        };
    }
}`
  ],
]);

// ── send.js patches ──
console.log('\n📦 send.js');
total += patchFile('send.js', [
  [
    'reply_in_thread for text reply',
    `data: {
                content,
                msg_type: "text",
            },`,
    `data: {
                content,
                msg_type: "text",
                reply_in_thread: true,
            },`
  ],
  [
    'reply_in_thread for card reply',
    `data: {
                content,
                msg_type: "interactive",
            },`,
    `data: {
                content,
                msg_type: "interactive",
                reply_in_thread: true,
            },`
  ],
]);

console.log(`\n🏁 Done. Total patches applied: ${total}`);
if (total > 0) {
  console.log('⚡ Restart gateway: openclaw gateway restart');
}
PATCH_EOF

echo ""
echo "=== Patch application complete ==="
