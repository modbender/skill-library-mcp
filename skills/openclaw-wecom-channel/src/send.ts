/**
 * 企业微信消息发送
 * 通过主动推送 API 发送消息（不使用被动回复，因为被动回复有 5 秒超时限制）
 * 接口文档：https://developer.work.weixin.qq.com/document/path/90236
 */

import type { ClawdbotConfig } from "openclaw/plugin-sdk";
import type { WecomSendResult } from "./types.js";
import { resolveWecomAccount } from "./accounts.js";
import { getAccessToken } from "./token.js";

const SEND_API = "https://qyapi.weixin.qq.com/cgi-bin/message/send";

export type SendWecomMessageParams = {
  cfg: ClawdbotConfig;
  /** 接收者 userId（企业微信内部 userid） */
  to: string;
  /** 消息文本 */
  text: string;
  /** 账号 ID */
  accountId?: string;
};

/**
 * 通过企业微信 API 发送文本消息
 */
export async function sendMessageWecom(params: SendWecomMessageParams): Promise<WecomSendResult> {
  const { cfg, to, text, accountId } = params;
  const account = resolveWecomAccount({ cfg, accountId });

  if (!account.configured || !account.corpId || !account.secret || !account.agentId) {
    throw new Error(`企业微信账号 "${account.accountId}" 未配置`);
  }

  const accessToken = await getAccessToken({
    corpId: account.corpId,
    secret: account.secret,
  });

  // 去掉 "user:" 前缀（如果有的话）
  const toUser = to.replace(/^user:/i, "");

  const body = {
    touser: toUser,
    msgtype: "text",
    agentid: Number(account.agentId),
    text: {
      content: text,
    },
  };

  const res = await fetch(`${SEND_API}?access_token=${encodeURIComponent(accessToken)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(`企业微信发送消息失败: HTTP ${res.status}`);
  }

  const data = (await res.json()) as WecomSendResult;

  if (data.errcode !== 0) {
    throw new Error(`企业微信发送消息失败: ${data.errmsg ?? `errcode=${data.errcode}`}`);
  }

  return data;
}
