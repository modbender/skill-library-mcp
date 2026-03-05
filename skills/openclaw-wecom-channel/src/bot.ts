/**
 * 企业微信消息处理
 * - 解析来自企业微信的 XML 消息
 * - 执行权限检查（dmPolicy / allowFrom）
 * - 构建 inbound context 分发给 agent
 */

import type { ClawdbotConfig, RuntimeEnv } from "openclaw/plugin-sdk";
import type { WecomMessageContext } from "./types.js";
import { resolveWecomAccount } from "./accounts.js";
import { createWecomReplyDispatcher } from "./reply-dispatcher.js";
import { getWecomRuntime } from "./runtime.js";

/**
 * 从 XML 字符串中提取指定标签的值
 * 先匹配 CDATA，再匹配纯文本
 */
export function extractXmlValue(xml: string, tag: string): string {
  // 先尝试 CDATA 格式：<Tag><![CDATA[value]]></Tag>
  const cdataRegex = new RegExp(`<${tag}><!\\[CDATA\\[([\\s\\S]*?)\\]\\]></${tag}>`);
  const cdataMatch = xml.match(cdataRegex);
  if (cdataMatch) {
    return cdataMatch[1];
  }

  // 再尝试纯文本格式：<Tag>value</Tag>
  const textRegex = new RegExp(`<${tag}>([^<]*)</${tag}>`);
  const textMatch = xml.match(textRegex);
  if (textMatch) {
    return textMatch[1];
  }

  return "";
}

/**
 * 解析企业微信 XML 消息为 WecomMessageContext
 */
export function parseWecomMessage(xml: string): WecomMessageContext {
  return {
    userId: extractXmlValue(xml, "FromUserName"),
    content: extractXmlValue(xml, "Content"),
    msgId: extractXmlValue(xml, "MsgId"),
    msgType: extractXmlValue(xml, "MsgType"),
    createTime: parseInt(extractXmlValue(xml, "CreateTime"), 10) || 0,
    agentId: extractXmlValue(xml, "AgentID"),
  };
}

/**
 * 处理来自企业微信的消息
 */
export async function handleWecomMessage(params: {
  cfg: ClawdbotConfig;
  msgXml: string;
  runtime?: RuntimeEnv;
  accountId?: string;
}): Promise<void> {
  const { cfg, msgXml, runtime, accountId } = params;
  const log = runtime?.log ?? console.log;
  const error = runtime?.error ?? console.error;

  const account = resolveWecomAccount({ cfg, accountId });
  const wecomCfg = account.config;

  // 解析消息
  const ctx = parseWecomMessage(msgXml);

  // 只处理文本消息
  if (ctx.msgType !== "text") {
    log(`wecom[${account.accountId}]: 收到非文本消息类型 "${ctx.msgType}"，忽略`);
    return;
  }

  if (!ctx.content.trim()) {
    log(`wecom[${account.accountId}]: 空消息内容，忽略`);
    return;
  }

  log(
    `wecom[${account.accountId}]: 收到消息 from=${ctx.userId} content="${ctx.content.slice(0, 100)}"`,
  );

  // 权限检查：dmPolicy
  const dmPolicy = wecomCfg.dmPolicy ?? "open";
  const allowFrom = (wecomCfg.allowFrom ?? []).map((entry) => String(entry));

  if (dmPolicy === "allowlist") {
    const allowed = allowFrom.some(
      (id) => id.toLowerCase() === ctx.userId.toLowerCase(),
    );
    if (!allowed) {
      log(`wecom[${account.accountId}]: 用户 ${ctx.userId} 不在白名单中，忽略`);
      return;
    }
  }

  try {
    const core = getWecomRuntime();

    const wecomFrom = `wecom:${ctx.userId}`;
    const wecomTo = `user:${ctx.userId}`;

    // 解析路由
    const route = core.channel.routing.resolveAgentRoute({
      cfg,
      channel: "wecom",
      accountId: account.accountId,
      peer: {
        kind: "direct",
        id: ctx.userId,
      },
    });

    const preview = ctx.content.replace(/\s+/g, " ").slice(0, 160);
    const inboundLabel = `WeCom[${account.accountId}] DM from ${ctx.userId}`;

    // 注册系统事件
    core.system.enqueueSystemEvent(`${inboundLabel}: ${preview}`, {
      sessionKey: route.sessionKey,
      contextKey: `wecom:message:${ctx.userId}:${ctx.msgId}`,
    });

    // 构建信封
    const envelopeOptions = core.channel.reply.resolveEnvelopeFormatOptions(cfg);
    const body = core.channel.reply.formatAgentEnvelope({
      channel: "WeCom",
      from: ctx.userId,
      timestamp: new Date(ctx.createTime * 1000),
      envelope: envelopeOptions,
      body: ctx.content,
    });

    // 构建 inbound context
    const ctxPayload = core.channel.reply.finalizeInboundContext({
      Body: body,
      RawBody: ctx.content,
      CommandBody: ctx.content,
      From: wecomFrom,
      To: wecomTo,
      SessionKey: route.sessionKey,
      AccountId: route.accountId,
      ChatType: "direct" as const,
      SenderName: ctx.userId,
      SenderId: ctx.userId,
      Provider: "wecom" as const,
      Surface: "wecom" as const,
      MessageSid: ctx.msgId,
      Timestamp: ctx.createTime * 1000,
      WasMentioned: false,
      CommandAuthorized: true,
      OriginatingChannel: "wecom" as const,
      OriginatingTo: wecomTo,
    });

    // 创建回复分发器
    const { dispatcher, replyOptions, markDispatchIdle } = createWecomReplyDispatcher({
      cfg,
      agentId: route.agentId,
      runtime: runtime as RuntimeEnv,
      replyTo: ctx.userId,
      accountId: account.accountId,
    });

    log(`wecom[${account.accountId}]: 分发消息到 agent (session=${route.sessionKey})`);

    // 分发
    const { queuedFinal, counts } = await core.channel.reply.dispatchReplyFromConfig({
      ctx: ctxPayload,
      cfg,
      dispatcher,
      replyOptions,
    });

    markDispatchIdle();

    log(
      `wecom[${account.accountId}]: 分发完成 (queuedFinal=${queuedFinal}, replies=${counts.final})`,
    );
  } catch (err) {
    error(`wecom[${account.accountId}]: 消息分发失败: ${String(err)}`);
  }
}
