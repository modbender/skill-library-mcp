/**
 * 企业微信 outbound adapter
 * 定义消息发送的出站适配器
 */

import type { ChannelOutboundAdapter } from "openclaw/plugin-sdk";
import { getWecomRuntime } from "./runtime.js";
import { sendMessageWecom } from "./send.js";

export const wecomOutbound: ChannelOutboundAdapter = {
  deliveryMode: "direct",
  chunker: (text, limit) => getWecomRuntime().channel.text.chunkMarkdownText(text, limit),
  chunkerMode: "markdown",
  textChunkLimit: 2048,

  sendText: async ({ cfg, to, text, accountId }) => {
    const result = await sendMessageWecom({
      cfg,
      to,
      text,
      accountId: accountId ?? undefined,
    });
    return { channel: "wecom", messageId: result.msgid ?? "unknown", chatId: to };
  },

  sendMedia: async ({ cfg, to, text, mediaUrl, accountId }) => {
    // 企业微信暂不支持媒体消息上传，回退为文本链接
    let finalText = text ?? "";
    if (mediaUrl) {
      finalText = finalText ? `${finalText}\n\n📎 ${mediaUrl}` : `📎 ${mediaUrl}`;
    }

    const result = await sendMessageWecom({
      cfg,
      to,
      text: finalText,
      accountId: accountId ?? undefined,
    });
    return { channel: "wecom", messageId: result.msgid ?? "unknown", chatId: to };
  },
};
