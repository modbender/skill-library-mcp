/**
 * 企业微信 ChannelPlugin 定义
 * 参考飞书插件的 channel.ts 架构
 */

import type { ChannelMeta, ChannelPlugin, ClawdbotConfig } from "openclaw/plugin-sdk";
import { DEFAULT_ACCOUNT_ID, PAIRING_APPROVED_MESSAGE } from "openclaw/plugin-sdk";
import type { ResolvedWecomAccount } from "./types.js";
import { resolveWecomAccount, listWecomAccountIds } from "./accounts.js";
import { wecomOutbound } from "./outbound.js";
import { sendMessageWecom } from "./send.js";

const meta: ChannelMeta = {
  id: "wecom",
  label: "WeCom",
  selectionLabel: "企业微信 (WeCom/WxWork)",
  docsPath: "/channels/wecom",
  docsLabel: "wecom",
  blurb: "企业微信 (WeCom) enterprise messaging.",
  aliases: ["wxwork", "wechat-work"],
  order: 75,
};

export const wecomPlugin: ChannelPlugin<ResolvedWecomAccount> = {
  id: "wecom",
  meta: { ...meta },

  pairing: {
    idLabel: "wecomUserId",
    normalizeAllowEntry: (entry) => entry.replace(/^(wecom|user):/i, ""),
    notifyApproval: async ({ cfg, id }) => {
      await sendMessageWecom({
        cfg,
        to: id,
        text: PAIRING_APPROVED_MESSAGE,
      });
    },
  },

  capabilities: {
    chatTypes: ["direct"],
    media: false,
    reactions: false,
    threads: false,
    polls: false,
    nativeCommands: false,
    blockStreaming: false,
  },

  agentPrompt: {
    messageToolHints: () => [
      "- WeCom targeting: omit `target` to reply to the current conversation (auto-inferred). Explicit targets: `user:userId`.",
      "- WeCom only supports plain text messages.",
    ],
  },

  reload: { configPrefixes: ["channels.wecom"] },

  configSchema: {
    schema: {
      type: "object",
      additionalProperties: false,
      properties: {
        enabled: { type: "boolean" },
        corpId: { type: "string" },
        agentId: { oneOf: [{ type: "string" }, { type: "number" }] },
        secret: { type: "string" },
        token: { type: "string" },
        encodingAESKey: { type: "string" },
        port: { type: "integer", minimum: 1 },
        dmPolicy: { type: "string", enum: ["open", "pairing", "allowlist"] },
        allowFrom: {
          type: "array",
          items: { oneOf: [{ type: "string" }, { type: "number" }] },
        },
      },
    },
  },

  config: {
    listAccountIds: (cfg) => listWecomAccountIds(cfg),
    resolveAccount: (cfg, accountId) => resolveWecomAccount({ cfg, accountId }),
    defaultAccountId: () => DEFAULT_ACCOUNT_ID,
    setAccountEnabled: ({ cfg, accountId, enabled }) => {
      const isDefault = !accountId || accountId === DEFAULT_ACCOUNT_ID;
      if (isDefault) {
        return {
          ...cfg,
          channels: {
            ...cfg.channels,
            wecom: {
              ...cfg.channels?.wecom,
              enabled,
            },
          },
        };
      }
      return cfg;
    },
    deleteAccount: ({ cfg, accountId }) => {
      const isDefault = !accountId || accountId === DEFAULT_ACCOUNT_ID;
      if (isDefault) {
        const next = { ...cfg } as ClawdbotConfig;
        const nextChannels = { ...cfg.channels };
        delete (nextChannels as Record<string, unknown>).wecom;
        if (Object.keys(nextChannels).length > 0) {
          next.channels = nextChannels;
        } else {
          delete next.channels;
        }
        return next;
      }
      return cfg;
    },
    isConfigured: (account) => account.configured,
    describeAccount: (account) => ({
      accountId: account.accountId,
      enabled: account.enabled,
      configured: account.configured,
      corpId: account.corpId,
      agentId: account.agentId,
      port: account.port,
    }),
    resolveAllowFrom: ({ cfg, accountId }) => {
      const account = resolveWecomAccount({ cfg, accountId });
      return (account.config?.allowFrom ?? []).map((entry) => String(entry));
    },
    formatAllowFrom: ({ allowFrom }) =>
      allowFrom
        .map((entry) => String(entry).trim())
        .filter(Boolean)
        .map((entry) => entry.toLowerCase()),
  },

  security: {
    collectWarnings: () => [],
  },

  setup: {
    resolveAccountId: () => DEFAULT_ACCOUNT_ID,
    applyAccountConfig: ({ cfg }) => ({
      ...cfg,
      channels: {
        ...cfg.channels,
        wecom: {
          ...cfg.channels?.wecom,
          enabled: true,
        },
      },
    }),
  },

  messaging: {
    normalizeTarget: (raw) => {
      if (!raw) return undefined;
      // 去掉 "user:" 前缀
      return raw.replace(/^user:/i, "") || undefined;
    },
    targetResolver: {
      looksLikeId: (id: string) => /^[a-zA-Z0-9_-]+$/.test(id),
      hint: "<userId>",
    },
  },

  outbound: wecomOutbound,

  status: {
    defaultRuntime: {
      accountId: DEFAULT_ACCOUNT_ID,
      running: false,
      lastStartAt: null,
      lastStopAt: null,
      lastError: null,
      port: null,
    },
    buildChannelSummary: ({ snapshot }) => ({
      configured: snapshot.configured ?? false,
      running: snapshot.running ?? false,
      lastStartAt: snapshot.lastStartAt ?? null,
      lastStopAt: snapshot.lastStopAt ?? null,
      lastError: snapshot.lastError ?? null,
      port: snapshot.port ?? null,
    }),
    buildAccountSnapshot: ({ account, runtime }) => ({
      accountId: account.accountId,
      enabled: account.enabled,
      configured: account.configured,
      corpId: account.corpId,
      agentId: account.agentId,
      running: runtime?.running ?? false,
      lastStartAt: runtime?.lastStartAt ?? null,
      lastStopAt: runtime?.lastStopAt ?? null,
      lastError: runtime?.lastError ?? null,
      port: runtime?.port ?? null,
    }),
  },

  gateway: {
    startAccount: async (ctx) => {
      const { monitorWecomProvider } = await import("./monitor.js");
      const account = resolveWecomAccount({ cfg: ctx.cfg, accountId: ctx.accountId });
      ctx.setStatus({ accountId: ctx.accountId, port: account.port });
      ctx.log?.info(`starting wecom[${ctx.accountId}] (port: ${account.port})`);
      return monitorWecomProvider({
        config: ctx.cfg,
        runtime: ctx.runtime,
        abortSignal: ctx.abortSignal,
        accountId: ctx.accountId,
      });
    },
  },
};
