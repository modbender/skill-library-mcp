#!/usr/bin/env node
/**
 * 用一个端口同时提供：
 * 1) noVNC 静态资源（正确 Content-Type，避免 module strict MIME 报错）
 * 2) WebSocket -> TCP VNC 代理（路径 /websockify）
 *
 * 依赖：ws（workspace/node_modules 里通常已有）
 */
const http = require("http");
const fs = require("fs");
const path = require("path");
const net = require("net");

function envInt(name, def) {
  const v = process.env[name];
  if (!v) return def;
  const n = Number(v);
  return Number.isFinite(n) ? n : def;
}

const WEB_ROOT = process.env.NOVNC_WEB || "/root/.openclaw/workspace/novnc-web";
const LISTEN_HOST = process.env.LISTEN_HOST || "0.0.0.0";
const LISTEN_PORT = envInt("NOVNC_PORT", 6080);
const WS_PATH = process.env.WS_PATH || "/websockify";
const VNC_HOST = process.env.VNC_HOST || "127.0.0.1";
const VNC_PORT = envInt("VNC_PORT", 5901);
const ACCESS_TOKEN = process.env.ACCESS_TOKEN || "";
const TOKEN_EXPIRES_AT = envInt("TOKEN_EXPIRES_AT", 0);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".ttf": "font/ttf",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".mp3": "audio/mpeg",
  ".oga": "audio/ogg",
};

function safeJoin(root, reqPath) {
  const decoded = decodeURIComponent(reqPath);
  const clean = decoded.replace(/\0/g, "");
  const rel = clean.replace(/^\/+/, "");
  const joined = path.join(root, rel);
  const resolved = path.resolve(joined);
  const rootResolved = path.resolve(root);
  if (!resolved.startsWith(rootResolved + path.sep) && resolved !== rootResolved) {
    return null;
  }
  return resolved;
}

function serveFile(res, filePath) {
  fs.stat(filePath, (err, st) => {
    if (err || !st.isFile()) {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Not Found");
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const ct = MIME[ext] || "application/octet-stream";
    res.writeHead(200, {
      "Content-Type": ct,
      "Content-Length": st.size,
      "Cache-Control": "no-cache",
      "X-Content-Type-Options": "nosniff",
    });
    fs.createReadStream(filePath).pipe(res);
  });
}

function parseCookies(cookieHeader) {
  const out = {};
  if (!cookieHeader) return out;
  for (const p of cookieHeader.split(";")) {
    const i = p.indexOf("=");
    if (i <= 0) continue;
    const k = p.slice(0, i).trim();
    const v = p.slice(i + 1).trim();
    out[k] = v;
  }
  return out;
}

function hasValidToken(urlObj, req) {
  if (TOKEN_EXPIRES_AT > 0 && Math.floor(Date.now() / 1000) > TOKEN_EXPIRES_AT) return false;
  if (!ACCESS_TOKEN) return true;
  if (urlObj.searchParams.get("token") === ACCESS_TOKEN) return true;
  const cookies = parseCookies(req.headers.cookie || "");
  return cookies.vrd_token === ACCESS_TOKEN;
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url || "/", "http://localhost");
  const needsToken = url.pathname === "/" || url.pathname === "/vnc.html" || url.pathname === "/vnc_lite.html";
  if (needsToken && !hasValidToken(url, req)) {
    res.writeHead(403, { "Content-Type": "text/plain; charset=utf-8" });
    if (TOKEN_EXPIRES_AT > 0 && Math.floor(Date.now() / 1000) > TOKEN_EXPIRES_AT) {
      res.end("Forbidden: token expired");
    } else {
      res.end("Forbidden: invalid token");
    }
    return;
  }

  if (url.pathname === "/") {
    const target = ACCESS_TOKEN ? `/vnc.html?token=${encodeURIComponent(ACCESS_TOKEN)}` : "/vnc.html";
    res.writeHead(302, { Location: target });
    res.end();
    return;
  }

  // WebSocket upgrade 不走这里
  const p = url.pathname;
  const filePath = safeJoin(WEB_ROOT, p);
  if (!filePath) {
    res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Bad Request");
    return;
  }

  // 目录默认 index.html（noVNC 根目录里一般没有，但保留行为）
  if (p.endsWith("/")) {
    serveFile(res, path.join(filePath, "index.html"));
    return;
  }
  if ((p === "/vnc.html" || p === "/vnc_lite.html") && ACCESS_TOKEN) {
    fs.stat(filePath, (err, st) => {
      if (err || !st.isFile()) {
        res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
        res.end("Not Found");
        return;
      }
      const ext = path.extname(filePath).toLowerCase();
      const ct = MIME[ext] || "application/octet-stream";
      res.writeHead(200, {
        "Content-Type": ct,
        "Content-Length": st.size,
        "Cache-Control": "no-cache",
        "X-Content-Type-Options": "nosniff",
        "Set-Cookie": `vrd_token=${ACCESS_TOKEN}; HttpOnly; SameSite=Lax; Path=/`,
      });
      fs.createReadStream(filePath).pipe(res);
    });
    return;
  }
  serveFile(res, filePath);
});

let WebSocketServer;
try {
  ({ WebSocketServer } = require("ws"));
} catch (e) {
  console.error("[ERR] missing dependency 'ws'. Ensure NODE_PATH points to workspace/node_modules.");
  process.exit(1);
}

const wss = new WebSocketServer({ noServer: true });

server.on("upgrade", (req, socket, head) => {
  try {
    const url = new URL(req.url || "/", "http://localhost");
    if (url.pathname !== WS_PATH) {
      socket.destroy();
      return;
    }
    if (!hasValidToken(url, req)) {
      socket.destroy();
      return;
    }
    wss.handleUpgrade(req, socket, head, (ws) => wss.emit("connection", ws, req));
  } catch {
    socket.destroy();
  }
});

wss.on("connection", (ws) => {
  const vnc = net.createConnection({ host: VNC_HOST, port: VNC_PORT });

  ws.on("message", (data) => {
    if (vnc.writable) vnc.write(data);
  });
  ws.on("close", () => {
    vnc.destroy();
  });
  ws.on("error", () => {
    vnc.destroy();
  });

  vnc.on("data", (chunk) => {
    if (ws.readyState === ws.OPEN) ws.send(chunk);
  });
  vnc.on("close", () => {
    try {
      ws.close();
    } catch {}
  });
  vnc.on("error", () => {
    try {
      ws.close();
    } catch {}
  });
});

server.listen(LISTEN_PORT, LISTEN_HOST, () => {
  console.log(`noVNC web: http://${LISTEN_HOST}:${LISTEN_PORT}/vnc.html`);
  console.log(`ws proxy: ws://${LISTEN_HOST}:${LISTEN_PORT}${WS_PATH} -> ${VNC_HOST}:${VNC_PORT}`);
  console.log(`web root: ${WEB_ROOT}`);
});
