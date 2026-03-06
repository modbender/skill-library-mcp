/**
 * 企业微信账号管理
 * - resolveAccount: 解析并合并账号配置
 * - listAccountIds: 列出所有账号 ID
 */

import type { ClawdbotConfig } from "openclaw/plugin-sdk";
import { DEFAULT_ACCOUNT_ID } from "openclaw/plugin-sdk";
import type { WecomConfig, ResolvedWecomAccount } from "./types.js";

/** 默认 HTTP 回调端口 */
const DEFAULT_PORT = 18800;

/**
 * 列出所有企业微信账号 ID
 * 目前只支持单账号（DEFAULT_ACCOUNT_ID）
 */
export function listWecomAccountIds(cfg: ClawdbotConfig): string[] {
  const wecomCfg = cfg.channels?.wecom as WecomConfig | undefined;
  if (!wecomCfg) {
    return [DEFAULT_ACCOUNT_ID];
  }
  return [DEFAULT_ACCOUNT_ID];
}

/**
 * 解析企业微信配置的凭据
 */
function resolveWecomCredentials(cfg?: WecomConfig): {
  corpId: string;
  agentId: string | number;
  secret: string;
  token: string;
  encodingAESKey: string;
} | null {
  const corpId = cfg?.corpId?.trim();
  const secret = cfg?.secret?.trim();
  const token = cfg?.token?.trim();
  const encodingAESKey = cfg?.encodingAESKey?.trim();
  const agentId = cfg?.agentId;

  if (!corpId || !secret || !token || !encodingAESKey || !agentId) {
    return null;
  }

  return { corpId, agentId, secret, token, encodingAESKey };
}

/**
 * 解析完整的企业微信账号（合并配置）
 */
export function resolveWecomAccount(params: {
  cfg: ClawdbotConfig;
  accountId?: string | null;
}): ResolvedWecomAccount {
  const accountId = params.accountId ?? DEFAULT_ACCOUNT_ID;
  const wecomCfg = (params.cfg.channels?.wecom ?? {}) as WecomConfig;
  const enabled = wecomCfg.enabled !== false;
  const creds = resolveWecomCredentials(wecomCfg);

  return {
    accountId,
    enabled,
    configured: Boolean(creds),
    corpId: creds?.corpId,
    agentId: creds?.agentId,
    secret: creds?.secret,
    token: creds?.token,
    encodingAESKey: creds?.encodingAESKey,
    port: wecomCfg.port ?? DEFAULT_PORT,
    config: wecomCfg,
  };
}
