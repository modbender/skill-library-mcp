#!/usr/bin/env node
"use strict";

// Telegram Mini App Canvas server
// - HTTP server for static files + REST endpoints
// - WebSocket server for pushing canvas updates

const http = require("http");
const fs = require("fs");
const os = require("os");
const path = require("path");
const crypto = require("crypto");
const { WebSocketServer } = require("ws");
const pty = require("node-pty");

// ---- Config ----
const BOT_TOKEN = process.env.BOT_TOKEN || "";
const ALLOWED_USER_IDS = (process.env.ALLOWED_USER_IDS || "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);
const JWT_SECRET = process.env.JWT_SECRET || crypto.randomBytes(32).toString("hex");
const JWT_TTL_SECONDS = parseInt(process.env.JWT_TTL_SECONDS || "900", 10); // 15m
const INIT_DATA_MAX_AGE_SECONDS = parseInt(process.env.INIT_DATA_MAX_AGE_SECONDS || "300", 10); // 5m
const PORT = parseInt(process.env.PORT || "3721", 10);
const PUSH_TOKEN = process.env.PUSH_TOKEN || ""; // required — server will refuse /push and /clear without it
const RATE_LIMIT_AUTH_PER_MIN = parseInt(process.env.RATE_LIMIT_AUTH_PER_MIN || "30", 10);
const RATE_LIMIT_STATE_PER_MIN = parseInt(process.env.RATE_LIMIT_STATE_PER_MIN || "120", 10);
// OpenClaw Control UI proxy — OFF by default; must be explicitly opted into.
// When enabled, /oc/* HTTP and WebSocket requests are proxied to the local
// OpenClaw gateway. If OPENCLAW_GATEWAY_TOKEN is set, it is injected as an
// Authorization: Bearer header on proxied requests. No local credential files
// are read; OPENCLAW_GATEWAY_TOKEN must be supplied explicitly via env var.
const ENABLE_OPENCLAW_PROXY = process.env.ENABLE_OPENCLAW_PROXY === "true";
const OPENCLAW_PROXY_HOST = process.env.OPENCLAW_PROXY_HOST || "127.0.0.1";
const OPENCLAW_PROXY_PORT = parseInt(process.env.OPENCLAW_PROXY_PORT || "18789", 10);
let OPENCLAW_GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN || "";

// ---- Startup validation ----
// PUSH_TOKEN is required because cloudflared (and similar tunnels) forward
// remote requests as loopback TCP connections, bypassing the IP-based loopback
// check entirely. Without a PUSH_TOKEN, anyone who discovers the public tunnel
// URL can call /push and /clear.
if (!PUSH_TOKEN) {
  console.error(
    "[FATAL] PUSH_TOKEN is not set. Set PUSH_TOKEN to a strong random secret before starting the server.\n" +
    "        The loopback-only check is NOT sufficient when using cloudflared or any other local tunnel,\n" +
    "        because the tunnel connects to the server via localhost, making all remote requests appear\n" +
    "        to originate from 127.0.0.1. PUSH_TOKEN is your only protection for /push and /clear."
  );
  process.exit(1);
}

if (ENABLE_OPENCLAW_PROXY) {
  console.log(`[tg-canvas] OPENCLAW_PROXY enabled (OPENCLAW_GATEWAY_TOKEN: ${OPENCLAW_GATEWAY_TOKEN ? 'set' : 'not set'})`);
} else {
  console.log('[tg-canvas] OPENCLAW_PROXY disabled (set ENABLE_OPENCLAW_PROXY=true to enable)');
}

// ---- Helpers ----
const MINIAPP_DIR = path.join(__dirname, "miniapp");

function isLoopbackAddress(addr) {
  return addr === "127.0.0.1" || addr === "::1" || addr === "::ffff:127.0.0.1";
}

function sendJson(res, statusCode, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(statusCode, {
    "Content-Type": "application/json",
    "Content-Length": Buffer.byteLength(body),
  });
  res.end(body);
}

function readBodyJson(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => {
      data += chunk;
      if (data.length > 1e6) {
        // 1MB limit
        req.destroy();
        reject(new Error("Body too large"));
      }
    });
    req.on("end", () => {
      try {
        const parsed = JSON.parse(data || "{}");
        resolve(parsed);
      } catch (err) {
        reject(err);
      }
    });
    req.on("error", reject);
  });
}

function base64url(input) {
  return Buffer.from(input)
    .toString("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

function signJwt(payload) {
  const header = { alg: "HS256", typ: "JWT" };
  const headerB64 = base64url(JSON.stringify(header));
  const payloadB64 = base64url(JSON.stringify(payload));
  const data = `${headerB64}.${payloadB64}`;
  const sig = crypto.createHmac("sha256", JWT_SECRET).update(data).digest("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
  return `${data}.${sig}`;
}

function verifyJwt(token) {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const [headerB64, payloadB64, sig] = parts;
    const data = `${headerB64}.${payloadB64}`;
    const expectedSig = crypto.createHmac("sha256", JWT_SECRET).update(data).digest("base64")
      .replace(/=/g, "")
      .replace(/\+/g, "-")
      .replace(/\//g, "_");
    if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expectedSig))) return null;
    const payloadJson = Buffer.from(payloadB64.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString();
    const payload = JSON.parse(payloadJson);
    const now = Math.floor(Date.now() / 1000);
    if (!payload.exp) return null;
    if (now > payload.exp) return null;
    if (payload.iat && payload.iat > now + 60) return null;
    return payload;
  } catch (err) {
    return null;
  }
}

function verifyTelegramInitData(initData) {
  if (!BOT_TOKEN) {
    return { ok: false, error: "BOT_TOKEN not configured" };
  }
  const params = new URLSearchParams(initData);
  const hash = params.get("hash");
  if (!hash) return { ok: false, error: "Missing hash" };

  // Build data check string
  const pairs = [];
  for (const [key, value] of params.entries()) {
    if (key === "hash") continue;
    pairs.push([key, value]);
  }
  pairs.sort((a, b) => a[0].localeCompare(b[0]));
  const dataCheckString = pairs.map(([k, v]) => `${k}=${v}`).join("\n");

  // HMAC-SHA256 per Telegram spec:
  // secret_key = HMAC-SHA256(key="WebAppData", data=BOT_TOKEN)
  const secretKey = crypto.createHmac("sha256", "WebAppData").update(BOT_TOKEN).digest();
  const computedHash = crypto.createHmac("sha256", secretKey).update(dataCheckString).digest("hex");

  if (computedHash !== hash) {
    return { ok: false, error: "Invalid initData hash" };
  }

  const userRaw = params.get("user");
  let user = null;
  try {
    user = userRaw ? JSON.parse(userRaw) : null;
  } catch (_) {
    return { ok: false, error: "Invalid user JSON" };
  }

  if (!user || typeof user.id === "undefined") {
    return { ok: false, error: "Missing user.id" };
  }

  if (!ALLOWED_USER_IDS.includes(String(user.id))) {
    return { ok: false, error: "User not allowed" };
  }

  const authDate = parseInt(params.get("auth_date") || "0", 10);
  if (!authDate) {
    return { ok: false, error: "Missing auth_date" };
  }
  const nowSec = Math.floor(Date.now() / 1000);
  if (authDate > nowSec + 60) {
    return { ok: false, error: "auth_date is in the future" };
  }
  if (nowSec - authDate > INIT_DATA_MAX_AGE_SECONDS) {
    return { ok: false, error: "initData expired" };
  }

  const replayKey = `${user.id}:${authDate}:${hash}`;
  if (isInitDataReplayed(replayKey)) {
    return { ok: false, error: "initData replayed" };
  }
  markInitDataUsed(replayKey, INIT_DATA_MAX_AGE_SECONDS);

  return { ok: true, user };
}

function contentTypeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  switch (ext) {
    case ".html": return "text/html";
    case ".js": return "text/javascript";
    case ".css": return "text/css";
    case ".json": return "application/json";
    case ".png": return "image/png";
    case ".jpg":
    case ".jpeg": return "image/jpeg";
    case ".svg": return "image/svg+xml";
    case ".gif": return "image/gif";
    default: return "application/octet-stream";
  }
}

function serveFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    res.writeHead(200, { "Content-Type": contentTypeFor(filePath) });
    res.end(data);
  });
}

function parseCookies(req) {
  const raw = req.headers.cookie || "";
  const out = {};
  raw.split(";").forEach((part) => {
    const i = part.indexOf("=");
    if (i > 0) out[part.slice(0, i).trim()] = decodeURIComponent(part.slice(i + 1).trim());
  });
  return out;
}

function getJwtFromRequest(req, urlObj) {
  const auth = req.headers["authorization"] || "";
  const bearer = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  const queryToken = urlObj.searchParams.get("token") || "";
  const cookieToken = parseCookies(req).oc_jwt || "";
  return bearer || queryToken || cookieToken;
}

function patchControlCsp(headersIn) {
  const headers = { ...headersIn };
  const cspKey = Object.keys(headers).find((k) => k.toLowerCase() === 'content-security-policy');
  if (!cspKey) return headers;

  let csp = String(headers[cspKey] || '');
  // Allow Google Fonts used by control-ui styles without broadly opening script sources.
  if (/style-src\s/.test(csp) && !/fonts\.googleapis\.com/.test(csp)) {
    csp = csp.replace(/style-src\s+([^;]+)/, (m, p1) => `style-src ${p1} https://fonts.googleapis.com`);
  }
  if (/font-src\s/.test(csp)) {
    if (!/fonts\.gstatic\.com/.test(csp)) {
      csp = csp.replace(/font-src\s+([^;]+)/, (m, p1) => `font-src ${p1} https://fonts.gstatic.com data:`);
    }
  } else {
    csp += '; font-src \"self\" https://fonts.gstatic.com data:';
  }
  headers[cspKey] = csp;
  return headers;
}

function proxyToOpenClaw(req, res, targetPath) {
  const headers = { ...req.headers };
  delete headers.host;
  if (OPENCLAW_GATEWAY_TOKEN) {
    headers.authorization = `Bearer ${OPENCLAW_GATEWAY_TOKEN}`;
  }

  const proxyReq = http.request(
    {
      host: OPENCLAW_PROXY_HOST,
      port: OPENCLAW_PROXY_PORT,
      method: req.method,
      path: targetPath,
      headers,
    },
    (proxyRes) => {
      const isConfig = targetPath.startsWith('/__openclaw/control-ui-config.json');
      if (!isConfig) {
        const patchedHeaders = patchControlCsp(proxyRes.headers);
        res.writeHead(proxyRes.statusCode || 502, patchedHeaders);
        proxyRes.pipe(res);
        return;
      }

      let buf = '';
      proxyRes.setEncoding('utf8');
      proxyRes.on('data', (d) => (buf += d));
      proxyRes.on('end', () => {
        try {
          const j = JSON.parse(buf || '{}');
          const host = req.headers.host || '';
          const scheme = /localhost|127\.0\.0\.1/.test(host) ? 'ws' : 'wss';
          j.gatewayUrl = `${scheme}://${host}`;
          const out = JSON.stringify(j);
          res.writeHead(200, { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(out) });
          res.end(out);
        } catch {
          res.writeHead(proxyRes.statusCode || 502, proxyRes.headers);
          res.end(buf);
        }
      });
    }
  );

  proxyReq.on("error", (err) => {
    console.error("OpenClaw proxy error:", err.message);
    sendJson(res, 502, { error: "OpenClaw proxy unavailable" });
  });

  req.pipe(proxyReq);
}

// ---- Simple in-memory rate limiter ----
const rateLimitBuckets = new Map();
function rateLimit(key, limit, windowMs) {
  const now = Date.now();
  const bucket = rateLimitBuckets.get(key) || { count: 0, resetAt: now + windowMs };
  if (now > bucket.resetAt) {
    bucket.count = 0;
    bucket.resetAt = now + windowMs;
  }
  bucket.count += 1;
  rateLimitBuckets.set(key, bucket);
  return bucket.count <= limit;
}

// ---- initData replay cache ----
const initDataReplay = new Map();
function markInitDataUsed(key, ttlSeconds) {
  const now = Date.now();
  initDataReplay.set(key, now + ttlSeconds * 1000);
}
function isInitDataReplayed(key) {
  const now = Date.now();
  const expires = initDataReplay.get(key);
  if (!expires) return false;
  if (now > expires) {
    initDataReplay.delete(key);
    return false;
  }
  return true;
}

// ---- In-memory canvas state ----
let currentState = null; // { content, format }

// ---- WebSocket management ----
const wsClients = new Set();

function broadcast(obj) {
  const msg = JSON.stringify(obj);
  let count = 0;
  for (const ws of wsClients) {
    if (ws.readyState === ws.OPEN) {
      ws.send(msg);
      count++;
    }
  }
  return count;
}

// ---- HTTP server ----
const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://${req.headers.host}`);

    // Auth-gated proxy to local OpenClaw control UI.
    // Expose via /oc/* through tg-canvas only (JWT required).
    if (ENABLE_OPENCLAW_PROXY && url.pathname.startsWith("/oc/")) {
      const ip = req.socket.remoteAddress || "unknown";
      if (!rateLimit(`oc:${ip}`, RATE_LIMIT_STATE_PER_MIN, 60_000)) {
        return sendJson(res, 429, { error: "Rate limit" });
      }

      // Bootstrap cookie session from one-time token in URL.
      const queryToken = url.searchParams.get("token") || "";
      if (queryToken) {
        const qp = verifyJwt(queryToken);
        if (!qp) return sendJson(res, 401, { error: "Invalid token" });
        res.writeHead(302, {
          "Set-Cookie": `oc_jwt=${encodeURIComponent(queryToken)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${JWT_TTL_SECONDS}`,
          "Location": "/oc/",
        });
        return res.end();
      }

      const token = getJwtFromRequest(req, url);
      const payload = verifyJwt(token);
      if (!payload) return sendJson(res, 401, { error: "Invalid token" });

      // Do not forward auth token query params to the upstream control UI.
      url.searchParams.delete("token");
      const qs = url.searchParams.toString();
      const targetPath = url.pathname.replace(/^\/oc/, "") + (qs ? `?${qs}` : "");
      return proxyToOpenClaw(req, res, targetPath);
    }

    // Support absolute control-ui asset/API paths that may be requested from /oc/ pages.
    // Only proxy when request originated from /oc/ and auth token is valid.
    if (ENABLE_OPENCLAW_PROXY) {
      const ocLikePath =
        url.pathname.startsWith('/assets/') ||
        url.pathname === '/favicon.svg' ||
        url.pathname === '/favicon-32.png' ||
        url.pathname === '/apple-touch-icon.png' ||
        url.pathname.startsWith('/api/') ||
        url.pathname.startsWith('/__openclaw/');
      const referer = req.headers.referer || '';
      if (ocLikePath && referer.includes('/oc/')) {
        const token = getJwtFromRequest(req, url);
        const payload = verifyJwt(token);
        if (!payload) return sendJson(res, 401, { error: 'Invalid token' });
        const qs = url.searchParams.toString();
        const targetPath = url.pathname + (qs ? `?${qs}` : '');
        return proxyToOpenClaw(req, res, targetPath);
      }
    }

    // Serve index
    if (req.method === "GET" && url.pathname === "/") {
      const indexPath = path.join(MINIAPP_DIR, "index.html");
      return serveFile(res, indexPath);
    }

    // Serve static miniapp files
    if (req.method === "GET" && url.pathname.startsWith("/miniapp/")) {
      const relPath = url.pathname.replace("/miniapp/", "");
      const safePath = path.normalize(relPath).replace(/^\.\.(\/|\\|$)/, "");
      const filePath = path.join(MINIAPP_DIR, safePath);
      return serveFile(res, filePath);
    }

    // Auth endpoint
    if (req.method === "POST" && url.pathname === "/auth") {
      const ip = req.socket.remoteAddress || "unknown";
      if (!rateLimit(`auth:${ip}`, RATE_LIMIT_AUTH_PER_MIN, 60_000)) {
        return sendJson(res, 429, { error: "Rate limit" });
      }
      const body = await readBodyJson(req);
      const initData = body.initData;
      if (!initData) return sendJson(res, 400, { error: "Missing initData" });

      const result = verifyTelegramInitData(initData);
      if (!result.ok) return sendJson(res, 401, { error: result.error });

      const now = Math.floor(Date.now() / 1000);
      const exp = now + JWT_TTL_SECONDS;
      const token = signJwt({ userId: String(result.user.id), iat: now, exp, jti: crypto.randomUUID() });
      return sendJson(res, 200, {
        token,
        user: { id: result.user.id, username: result.user.username || null },
      });
    }

    // State endpoint
    if (req.method === "GET" && url.pathname === "/state") {
      const ip = req.socket.remoteAddress || "unknown";
      if (!rateLimit(`state:${ip}`, RATE_LIMIT_STATE_PER_MIN, 60_000)) {
        return sendJson(res, 429, { error: "Rate limit" });
      }
      const token = url.searchParams.get("token") || "";
      const payload = verifyJwt(token);
      if (!payload) return sendJson(res, 401, { error: "Invalid token" });
      if (currentState) {
        return sendJson(res, 200, { content: currentState.content, format: currentState.format });
      }
      return sendJson(res, 200, { content: null });
    }

    // Health endpoint
    if (req.method === "GET" && url.pathname === "/health") {
      return sendJson(res, 200, {
        ok: true,
        uptime: process.uptime(),
        clients: wsClients.size,
        hasState: !!currentState,
      });
    }

    // Push endpoint — PUSH_TOKEN required (loopback check retained as an additional layer
    // but is NOT sufficient alone when cloudflared is in use; see startup validation above)
    if (req.method === "POST" && url.pathname === "/push") {
      if (!isLoopbackAddress(req.socket.remoteAddress)) {
        return sendJson(res, 403, { error: "Forbidden" });
      }
      const headerToken = req.headers["x-push-token"] || "";
      const auth = req.headers["authorization"] || "";
      const bearer = auth.startsWith("Bearer ") ? auth.slice(7) : "";
      const queryToken = url.searchParams.get("token") || "";
      const provided = headerToken || bearer || queryToken;
      if (!provided || provided !== PUSH_TOKEN) {
        return sendJson(res, 401, { error: "Invalid push token" });
      }

      const ip = req.socket.remoteAddress || 'unknown';
      if (!rateLimit(`auth:${ip}`, RATE_LIMIT_AUTH_PER_MIN, 60_000)) {
        return sendJson(res, 429, { error: "Rate limit" });
      }
      const body = await readBodyJson(req);

      let content = body.content;
      let format = body.format || null;

      if (!format) {
        if (typeof body.html !== "undefined") {
          format = "html";
          content = body.html;
        } else if (typeof body.markdown !== "undefined") {
          format = "markdown";
          content = body.markdown;
        } else if (typeof body.text !== "undefined") {
          format = "text";
          content = body.text;
        } else if (typeof body.a2ui !== "undefined") {
          format = "a2ui";
          content = body.a2ui;
        }
      }

      if (!format) format = "html";
      if (typeof content === "undefined" || content === null) {
        return sendJson(res, 400, { error: "Missing content" });
      }

      currentState = { content, format };
      const clients = broadcast({ type: "canvas", content, format });
      return sendJson(res, 200, { ok: true, clients });
    }

    // Clear endpoint — PUSH_TOKEN required (same rationale as /push)
    if (req.method === "POST" && url.pathname === "/clear") {
      if (!isLoopbackAddress(req.socket.remoteAddress)) {
        return sendJson(res, 403, { error: "Forbidden" });
      }
      const headerToken = req.headers["x-push-token"] || "";
      const auth = req.headers["authorization"] || "";
      const bearer = auth.startsWith("Bearer ") ? auth.slice(7) : "";
      const queryToken = url.searchParams.get("token") || "";
      const provided = headerToken || bearer || queryToken;
      if (!provided || provided !== PUSH_TOKEN) {
        return sendJson(res, 401, { error: "Invalid push token" });
      }
      currentState = null;
      broadcast({ type: "clear" });
      return sendJson(res, 200, { ok: true });
    }

    res.writeHead(404);
    res.end("Not found");
  } catch (err) {
    console.error("Request error:", err);
    sendJson(res, 500, { error: "Internal server error" });
  }
});

// ---- WebSocket server (canvas) ----
const wss = new WebSocketServer({ noServer: true });

// ---- WebSocket server (terminal) ----
const termWss = new WebSocketServer({ noServer: true });

termWss.on("connection", (ws, req, payload) => {
  const shell = process.env.SHELL || "/bin/bash";
  const cols = 80;
  const rows = 24;

  // Use the actual process user's info — guards against the service being
  // accidentally run as root, which would give the terminal a root shell.
  const userInfo = (() => { try { return os.userInfo(); } catch (_) { return null; } })();
  const userHome = userInfo?.homedir || process.env.HOME || "/";
  const userName = userInfo?.username || process.env.USER || "";

  if (process.getuid && process.getuid() === 0) {
    console.warn("[tg-canvas] WARNING: server is running as root; terminal will be a root shell. " +
      "Set User=<your-user> in the systemd service to fix this.");
  }

  let term;
  try {
    term = pty.spawn(shell, [], {
      name: "xterm-256color",
      cols,
      rows,
      cwd: userHome,
      env: {
        ...process.env,
        HOME: userHome,
        USER: userName,
        LOGNAME: userName,
        TERM: "xterm-256color",
      },
    });
  } catch (err) {
    ws.send(JSON.stringify({ type: "exit", code: -1, error: String(err) }));
    ws.close();
    return;
  }

  // PTY → WS
  term.onData((data) => {
    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify({ type: "data", data }));
    }
  });

  term.onExit(({ exitCode }) => {
    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify({ type: "exit", code: exitCode }));
      ws.close();
    }
  });

  // WS → PTY
  ws.on("message", (raw) => {
    try {
      const msg = JSON.parse(raw.toString());
      if (msg.type === "data" && typeof msg.data === "string") {
        term.write(msg.data);
      } else if (msg.type === "resize" && msg.cols && msg.rows) {
        term.resize(
          Math.max(2, Math.min(500, msg.cols)),
          Math.max(1, Math.min(200, msg.rows))
        );
      }
    } catch (_) {
      // ignore malformed
    }
  });

  ws.on("close", () => {
    try { term.kill(); } catch (_) {}
  });
});

wss.on("connection", (ws, req, payload) => {
  wsClients.add(ws);

  // Send current state on connect
  if (currentState) {
    ws.send(JSON.stringify({ type: "canvas", content: currentState.content, format: currentState.format }));
  }

  ws.on("message", (data) => {
    try {
      const msg = JSON.parse(data.toString());
      if (msg && msg.type === "pong") {
        // keepalive response
      }
    } catch (_) {
      // ignore malformed
    }
  });

  ws.on("close", () => {
    wsClients.delete(ws);
  });
});

server.on("upgrade", (req, socket, head) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  // Auth-gated WS passthrough to local OpenClaw under /oc/*
  if (ENABLE_OPENCLAW_PROXY && url.pathname.startsWith("/oc/")) {
    const token = getJwtFromRequest(req, url);
    const payload = verifyJwt(token);
    if (!payload) {
      socket.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
      socket.destroy();
      return;
    }

    const targetPath = url.pathname.replace(/^\/oc/, "") + (url.search || "");
    const wsHeaders = { ...req.headers };
    if (OPENCLAW_GATEWAY_TOKEN) wsHeaders.authorization = `Bearer ${OPENCLAW_GATEWAY_TOKEN}`;
    const proxyReq = http.request({
      host: OPENCLAW_PROXY_HOST,
      port: OPENCLAW_PROXY_PORT,
      method: "GET",
      path: targetPath,
      headers: wsHeaders,
    });

    proxyReq.on("upgrade", (proxyRes, proxySocket, proxyHead) => {
      // forward 101 response
      socket.write("HTTP/1.1 101 Switching Protocols\r\n");
      for (const [k, v] of Object.entries(proxyRes.headers)) {
        socket.write(`${k}: ${v}\r\n`);
      }
      socket.write("\r\n");

      if (proxyHead && proxyHead.length) socket.write(proxyHead);
      if (head && head.length) proxySocket.write(head);

      proxySocket.pipe(socket).pipe(proxySocket);
    });

    proxyReq.on("response", (r) => {
      // Upstream rejected WS upgrade (e.g., 401). Return a concrete status instead of generic 502.
      socket.write(`HTTP/1.1 ${r.statusCode || 502} Upstream Rejected\r\nConnection: close\r\n\r\n`);
      socket.destroy();
    });

    proxyReq.on("error", (err) => {
      console.error('[tg-canvas] ws /oc proxy error:', err.message);
      socket.write("HTTP/1.1 502 Bad Gateway\r\n\r\n");
      socket.destroy();
    });

    proxyReq.end();
    return;
  }

  // Some control-ui bundles may open absolute websocket endpoints.
  // Proxy /ws and / (gateway default) for control sessions only (oc_jwt cookie present).
  const hasOcSession = !!parseCookies(req).oc_jwt;
  if (ENABLE_OPENCLAW_PROXY && (url.pathname === '/ws' || url.pathname === '/') && hasOcSession) {
    const token = getJwtFromRequest(req, url);
    const payload = verifyJwt(token);
    if (!payload) {
      socket.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
      socket.destroy();
      return;
    }

    const wsHeaders = { ...req.headers };
    if (OPENCLAW_GATEWAY_TOKEN) wsHeaders.authorization = `Bearer ${OPENCLAW_GATEWAY_TOKEN}`;
    const proxyReq = http.request({
      host: OPENCLAW_PROXY_HOST,
      port: OPENCLAW_PROXY_PORT,
      method: "GET",
      path: url.pathname + (url.search || ''),
      headers: wsHeaders,
    });

    proxyReq.on("upgrade", (proxyRes, proxySocket, proxyHead) => {
      socket.write("HTTP/1.1 101 Switching Protocols\r\n");
      for (const [k, v] of Object.entries(proxyRes.headers)) socket.write(`${k}: ${v}\r\n`);
      socket.write("\r\n");
      if (proxyHead && proxyHead.length) socket.write(proxyHead);
      if (head && head.length) proxySocket.write(head);
      proxySocket.pipe(socket).pipe(proxySocket);
    });

    proxyReq.on('response', (r) => {
      socket.write(`HTTP/1.1 ${r.statusCode || 502} Upstream Rejected\r\nConnection: close\r\n\r\n`);
      socket.destroy();
    });

    proxyReq.on('error', (err) => {
      console.error('[tg-canvas] ws root proxy error:', err.message);
      socket.write("HTTP/1.1 502 Bad Gateway\r\n\r\n");
      socket.destroy();
    });
    proxyReq.end();
    return;
  }

  if (url.pathname !== "/ws" && url.pathname !== "/ws/terminal") {
    socket.destroy();
    return;
  }
  const ip = req.socket.remoteAddress || "unknown";
  if (!rateLimit(`ws:${ip}`, RATE_LIMIT_AUTH_PER_MIN, 60_000)) {
    socket.write("HTTP/1.1 429 Too Many Requests\r\n\r\n");
    socket.destroy();
    return;
  }
  const token = url.searchParams.get("token") || "";
  const payload = verifyJwt(token);
  if (!payload) {
    socket.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
    socket.destroy();
    return;
  }
  if (url.pathname === "/ws/terminal") {
    termWss.handleUpgrade(req, socket, head, (ws) => {
      termWss.emit("connection", ws, req, payload);
    });
    return;
  }
  wss.handleUpgrade(req, socket, head, (ws) => {
    wss.emit("connection", ws, req, payload);
  });
});

// Keepalive ping every 30s
setInterval(() => {
  broadcast({ type: "ping" });
}, 30_000).unref();

server.listen(PORT, () => {
  console.log(`tg-canvas server listening on :${PORT}`);
});
