/**
 * 企业微信回复分发器
 * 创建 reply dispatcher，将 agent 回复通过企业微信 API 发送给用户
 */

import {
  createReplyPrefixContext,
  createTypingCallbacks,
  logTypingFailure,
  type ClawdbotConfig,
  type RuntimeEnv,
  type ReplyPayload,
} from "openclaw/plugin-sdk";
import { resolveWecomAccount } from "./accounts.js";
import { getWecomRuntime } from "./runtime.js";
import { sendMessageWecom } from "./send.js";

export type CreateWecomReplyDispatcherParams = {
  cfg: ClawdbotConfig;
  agentId: string;
  runtime: RuntimeEnv;
  /** 回复目标（用户 userId） */
  replyTo: string;
  /** 账号 ID */
  accountId?: string;
};

export function createWecomReplyDispatcher(params: CreateWecomReplyDispatcherParams) {
  const core = getWecomRuntime();
  const { cfg, agentId, replyTo, accountId } = params;

  const account = resolveWecomAccount({ cfg, accountId });

  const prefixContext = createReplyPrefixContext({
    cfg,
    agentId,
  });

  // 企业微信没有原生的 typing indicator，使用空回调
  const typingCallbacks = createTypingCallbacks({
    start: async () => {
      // 企业微信不支持 typing 状态，留空
    },
    stop: async () => {
      // 企业微信不支持 typing 状态，留空
    },
    onStartError: (err) => {
      logTypingFailure({
        log: (message) => params.runtime.log?.(message),
        channel: "wecom",
        action: "start",
        error: err,
      });
    },
    onStopError: (err) => {
      logTypingFailure({
        log: (message) => params.runtime.log?.(message),
        channel: "wecom",
        action: "stop",
        error: err,
      });
    },
  });

  const textChunkLimit = core.channel.text.resolveTextChunkLimit(cfg, "wecom", accountId, {
    fallbackLimit: 2048,
  });
  const chunkMode = core.channel.text.resolveChunkMode(cfg, "wecom");

  const { dispatcher, replyOptions, markDispatchIdle } =
    core.channel.reply.createReplyDispatcherWithTyping({
      responsePrefix: prefixContext.responsePrefix,
      responsePrefixContextProvider: prefixContext.responsePrefixContextProvider,
      humanDelay: core.channel.reply.resolveHumanDelayConfig(cfg, agentId),
      onReplyStart: typingCallbacks.onReplyStart,
      deliver: async (payload: ReplyPayload) => {
        params.runtime.log?.(
          `wecom[${account.accountId}] deliver: text=${payload.text?.slice(0, 100)}`,
        );
        const text = payload.text ?? "";
        if (!text.trim()) {
          params.runtime.log?.(`wecom[${account.accountId}] deliver: 空文本，跳过`);
          return;
        }

        // 分块发送
        const chunks = core.channel.text.chunkTextWithMode(text, textChunkLimit, chunkMode);
        params.runtime.log?.(
          `wecom[${account.accountId}] deliver: 发送 ${chunks.length} 个分块到 ${replyTo}`,
        );
        for (const chunk of chunks) {
          await sendMessageWecom({
            cfg,
            to: replyTo,
            text: chunk,
            accountId,
          });
        }
      },
      onError: (err, info) => {
        params.runtime.error?.(
          `wecom[${account.accountId}] ${info.kind} reply failed: ${String(err)}`,
        );
        typingCallbacks.onIdle?.();
      },
      onIdle: typingCallbacks.onIdle,
    });

  return {
    dispatcher,
    replyOptions: {
      ...replyOptions,
      onModelSelected: prefixContext.onModelSelected,
    },
    markDispatchIdle,
  };
}
