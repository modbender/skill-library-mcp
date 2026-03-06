/**
 * 企业微信 HTTP 回调监听器
 * - GET 请求：URL 验证回调
 * - POST 请求：接收加密消息 → 解密 → 分发给 bot 处理
 *
 * 企业微信被动回复有 5 秒超时限制，所以不使用被动回复，
 * 直接返回空 200，然后通过主动推送 API 发送回复。
 */

import http from "node:http";
import type { ClawdbotConfig, RuntimeEnv } from "openclaw/plugin-sdk";
import { resolveWecomAccount } from "./accounts.js";
import { handleWecomMessage, extractXmlValue } from "./bot.js";
import { WXBizMsgCrypt } from "./crypto.js";

export type MonitorWecomOpts = {
  config?: ClawdbotConfig;
  runtime?: RuntimeEnv;
  abortSignal?: AbortSignal;
  accountId?: string;
};

/**
 * 读取 HTTP 请求体
 */
function readRequestBody(req: http.IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (chunk: Buffer) => chunks.push(chunk));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
    req.on("error", reject);
  });
}

/**
 * 解析 URL 查询参数
 */
function parseQuery(url: string): Record<string, string> {
  const idx = url.indexOf("?");
  if (idx === -1) return {};
  const qs = url.slice(idx + 1);
  const params: Record<string, string> = {};
  for (const pair of qs.split("&")) {
    const [key, val] = pair.split("=");
    if (key) {
      params[decodeURIComponent(key)] = decodeURIComponent(val ?? "");
    }
  }
  return params;
}

/**
 * 启动企业微信 HTTP 回调服务器
 */
export async function monitorWecomProvider(opts: MonitorWecomOpts = {}): Promise<void> {
  const cfg = opts.config;
  if (!cfg) {
    throw new Error("Config is required for WeCom monitor");
  }

  const log = opts.runtime?.log ?? console.log;
  const error = opts.runtime?.error ?? console.error;
  const accountId = opts.accountId;
  const account = resolveWecomAccount({ cfg, accountId });

  if (!account.enabled || !account.configured) {
    throw new Error(`企业微信账号 "${account.accountId}" 未配置或已禁用`);
  }

  if (!account.corpId || !account.token || !account.encodingAESKey || !account.secret) {
    throw new Error(`企业微信账号 "${account.accountId}" 缺少必要的加密配置`);
  }

  const crypt = new WXBizMsgCrypt(account.token, account.encodingAESKey, account.corpId);
  const port = account.port;

  // 已处理消息的去重集合（防止企业微信重试导致重复处理）
  const processedMsgIds = new Set<string>();
  const MSG_ID_TTL_MS = 60 * 1000; // 消息 ID 保留 60 秒

  function markProcessed(msgId: string): boolean {
    if (processedMsgIds.has(msgId)) {
      return false; // 已处理过
    }
    processedMsgIds.add(msgId);
    // 超时自动清理
    setTimeout(() => processedMsgIds.delete(msgId), MSG_ID_TTL_MS);
    return true; // 首次处理
  }

  const server = http.createServer(async (req, res) => {
    try {
      const url = req.url ?? "/";
      const query = parseQuery(url);
      const msgSignature = query.msg_signature ?? "";
      const timestamp = query.timestamp ?? "";
      const nonce = query.nonce ?? "";

      // GET 请求：URL 验证回调
      if (req.method === "GET") {
        const echostr = query.echostr ?? "";
        if (!echostr) {
          res.writeHead(400, { "Content-Type": "text/plain" });
          res.end("missing echostr");
          return;
        }

        try {
          const decrypted = crypt.verifyURL(msgSignature, timestamp, nonce, echostr);
          log(`wecom[${account.accountId}]: URL 验证成功`);
          res.writeHead(200, { "Content-Type": "text/plain" });
          res.end(decrypted);
        } catch (err) {
          error(`wecom[${account.accountId}]: URL 验证失败: ${String(err)}`);
          res.writeHead(403, { "Content-Type": "text/plain" });
          res.end("signature verification failed");
        }
        return;
      }

      // POST 请求：接收加密消息
      if (req.method === "POST") {
        const body = await readRequestBody(req);

        // 立即返回 200，避免企业微信 5 秒超时重试
        res.writeHead(200, { "Content-Type": "text/plain" });
        res.end("");

        // 从 XML 中提取加密内容
        const encrypt = extractXmlValue(body, "Encrypt");
        if (!encrypt) {
          error(`wecom[${account.accountId}]: POST 请求中无 Encrypt 字段`);
          return;
        }

        // 解密消息
        let decryptedXml: string;
        try {
          decryptedXml = crypt.decryptMsg(msgSignature, timestamp, nonce, encrypt);
        } catch (err) {
          error(`wecom[${account.accountId}]: 消息解密失败: ${String(err)}`);
          return;
        }

        log(`wecom[${account.accountId}]: 收到消息 XML (已解密)`);

        // 提取 MsgId 做去重
        const msgId = extractXmlValue(decryptedXml, "MsgId");
        if (msgId && !markProcessed(msgId)) {
          log(`wecom[${account.accountId}]: 重复消息 ${msgId}，忽略`);
          return;
        }

        // 异步处理消息（不阻塞 HTTP 响应）
        handleWecomMessage({
          cfg,
          msgXml: decryptedXml,
          runtime: opts.runtime,
          accountId: account.accountId,
        }).catch((err) => {
          error(`wecom[${account.accountId}]: 消息处理失败: ${String(err)}`);
        });

        return;
      }

      // 其他方法
      res.writeHead(405, { "Content-Type": "text/plain" });
      res.end("Method Not Allowed");
    } catch (err) {
      error(`wecom[${account.accountId}]: HTTP 请求处理异常: ${String(err)}`);
      if (!res.headersSent) {
        res.writeHead(500, { "Content-Type": "text/plain" });
        res.end("Internal Server Error");
      }
    }
  });

  return new Promise<void>((resolve, reject) => {
    const handleAbort = () => {
      log(`wecom[${account.accountId}]: 收到终止信号，关闭 HTTP 服务器`);
      server.close(() => {
        log(`wecom[${account.accountId}]: HTTP 服务器已关闭`);
        resolve();
      });
    };

    if (opts.abortSignal?.aborted) {
      resolve();
      return;
    }

    opts.abortSignal?.addEventListener("abort", handleAbort, { once: true });

    server.on("error", (err) => {
      error(`wecom[${account.accountId}]: HTTP 服务器错误: ${String(err)}`);
      opts.abortSignal?.removeEventListener("abort", handleAbort);
      reject(err);
    });

    server.listen(port, () => {
      log(`wecom[${account.accountId}]: HTTP 回调服务器已启动，监听端口 ${port}`);
    });
  });
}
