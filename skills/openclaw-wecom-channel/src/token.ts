/**
 * 企业微信 access_token 管理
 * - 自动获取、缓存、刷新
 * - 有效期 7200 秒，提前 300 秒刷新
 */

import type { WecomTokenCache } from "./types.js";

/** token 缓存（按 corpId+secret 组合键） */
const tokenCacheMap = new Map<string, WecomTokenCache>();

/** 提前刷新时间（秒） */
const REFRESH_AHEAD_SECONDS = 300;

/**
 * 获取缓存键
 */
function getCacheKey(corpId: string, secret: string): string {
  return `${corpId}:${secret}`;
}

/**
 * 获取 access_token
 * 如果缓存有效则直接返回，否则重新获取
 */
export async function getAccessToken(params: {
  corpId: string;
  secret: string;
  log?: (...args: unknown[]) => void;
}): Promise<string> {
  const { corpId, secret, log } = params;
  const cacheKey = getCacheKey(corpId, secret);
  const cached = tokenCacheMap.get(cacheKey);
  const now = Date.now();

  // 缓存有效（提前 300 秒刷新）
  if (cached && cached.expiresAt - REFRESH_AHEAD_SECONDS * 1000 > now) {
    return cached.accessToken;
  }

  log?.(`wecom: 正在获取 access_token (corpId=${corpId.slice(0, 6)}...)`);

  const url = `https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=${encodeURIComponent(corpId)}&corpsecret=${encodeURIComponent(secret)}`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`获取 access_token 失败: HTTP ${res.status}`);
  }

  const data = (await res.json()) as {
    errcode?: number;
    errmsg?: string;
    access_token?: string;
    expires_in?: number;
  };

  if (data.errcode && data.errcode !== 0) {
    throw new Error(`获取 access_token 失败: ${data.errmsg ?? `errcode=${data.errcode}`}`);
  }

  if (!data.access_token) {
    throw new Error("获取 access_token 失败: 返回数据中无 access_token");
  }

  const expiresIn = data.expires_in ?? 7200;
  const tokenCache: WecomTokenCache = {
    accessToken: data.access_token,
    expiresAt: now + expiresIn * 1000,
  };

  tokenCacheMap.set(cacheKey, tokenCache);
  log?.(`wecom: access_token 获取成功，有效期 ${expiresIn} 秒`);

  return data.access_token;
}

/**
 * 清除指定 token 缓存
 */
export function clearTokenCache(corpId: string, secret: string): void {
  const cacheKey = getCacheKey(corpId, secret);
  tokenCacheMap.delete(cacheKey);
}

/**
 * 清除所有 token 缓存
 */
export function clearAllTokenCache(): void {
  tokenCacheMap.clear();
}
