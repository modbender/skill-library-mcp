import { promises as fs } from "node:fs";
import os from "node:os";
import path from "node:path";
import { createHash, generateKeyPairSync, randomUUID, sign } from "node:crypto";
import { setTimeout as sleep } from "node:timers/promises";
import { ConvexHttpClient } from "convex/browser";
import WebSocket from "ws";

const DEFAULT_GATEWAY_URL = "ws://127.0.0.1:18789";
const CONFIG_PATH = path.join(os.homedir(), ".openclaw", "fastclaw", "config.json");
const APP_POLL_MS = 2000;
const HEARTBEAT_MS = 30000;
const SESSION_SYNC_MS = 15000;

function nowMs() {
  return Date.now();
}

function toNumber(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function parseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

async function loadConfig() {
  const raw = await fs.readFile(CONFIG_PATH, "utf8");
  const cfg = JSON.parse(raw);

  if (!cfg.convexUrl) throw new Error(`Missing convexUrl in ${CONFIG_PATH}`);
  if (!cfg.instanceId) throw new Error(`Missing instanceId in ${CONFIG_PATH}`);

  return {
    convexUrl: cfg.convexUrl,
    instanceId: cfg.instanceId,
    instanceName: cfg.instanceName ?? os.hostname(),
    gatewayUrl: cfg.gatewayUrl ?? DEFAULT_GATEWAY_URL,
    gatewayToken: cfg.gatewayToken ?? process.env.OPENCLAW_GATEWAY_TOKEN ?? null,
  };
}

function makeDeviceIdentity(instanceId) {
  const { privateKey, publicKey } = generateKeyPairSync("ed25519");
  const deviceId = `fastclaw-relay-${createHash("sha256").update(instanceId).digest("hex").slice(0, 16)}`;
  const publicKeyB64 = publicKey.export({ format: "der", type: "spki" }).toString("base64");

  return { deviceId, privateKey, publicKeyB64 };
}

function extractSessions(payload) {
  const list = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.sessions)
      ? payload.sessions
      : [];

  return list
    .map((session) => {
      const sessionKey = session?.sessionKey ?? session?.key ?? session?.id;
      if (!sessionKey || typeof sessionKey !== "string") return null;

      const updatedAt = toNumber(
        session?.updatedAt ?? session?.updated_at ?? session?.lastMessageAt,
        nowMs()
      );
      const createdAt = toNumber(session?.createdAt ?? session?.created_at, updatedAt);
      const lastMessagePreview =
        typeof session?.lastMessagePreview === "string"
          ? session.lastMessagePreview
          : typeof session?.preview === "string"
            ? session.preview
            : typeof session?.lastMessage?.content === "string"
              ? session.lastMessage.content
              : "";

      return {
        sessionKey,
        title:
          (typeof session?.title === "string" && session.title) ||
          (typeof session?.name === "string" && session.name) ||
          sessionKey,
        isPinned: Boolean(session?.isPinned ?? session?.pinned ?? false),
        lastMessagePreview,
        updatedAt,
        createdAt,
      };
    })
    .filter(Boolean);
}

function extractGatewayMessages(frame) {
  const payload = frame?.payload;
  const rawMessages = [];

  if (Array.isArray(payload?.messages)) rawMessages.push(...payload.messages);
  if (payload?.message && typeof payload.message === "object") rawMessages.push(payload.message);
  if (payload && payload.sessionKey && payload.content) rawMessages.push(payload);

  return rawMessages
    .map((m) => {
      const sessionKey = m?.sessionKey ?? m?.session_id ?? m?.session;
      const content = typeof m?.content === "string" ? m.content : typeof m?.text === "string" ? m.text : null;
      if (!sessionKey || !content) return null;

      const role = m?.role === "assistant" || m?.role === "system" || m?.role === "user" ? m.role : "assistant";
      const timestamp = toNumber(m?.timestamp ?? m?.ts ?? m?.createdAt, nowMs());

      return { sessionKey, role, content, timestamp };
    })
    .filter(Boolean);
}

class GatewayConnection {
  constructor(config) {
    this.url = config.gatewayUrl;
    this.token = config.gatewayToken;
    this.instanceId = config.instanceId;
    this.instanceName = config.instanceName;
    this.identity = makeDeviceIdentity(config.instanceId);

    this.ws = null;
    this.pending = new Map();
    this.handlers = new Set();
    this.connected = false;
    this.closed = false;
  }

  onFrame(handler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  async open() {
    this.closed = false;
    this.ws = new WebSocket(this.url);

    const connected = new Promise((resolve, reject) => {
      let connectTimeout = null;
      let fallbackTimer = null;
      let settled = false;

      const settle = (fn, value) => {
        if (settled) return;
        settled = true;
        clearTimeout(connectTimeout);
        clearTimeout(fallbackTimer);
        fn(value);
      };

      connectTimeout = setTimeout(() => {
        settle(reject, new Error("Gateway connect timeout"));
      }, 15000);

      const sendConnect = async (challenge) => {
        try {
          const payload = {
            role: "operator",
            scopes: ["operator.read", "operator.write"],
            mode: "operator",
            name: this.instanceName,
            token: this.token,
            device: {
              id: this.identity.deviceId,
              publicKey: this.identity.publicKeyB64,
            },
            meta: {
              source: "fastclaw-relay",
              instanceId: this.instanceId,
            },
          };

          if (challenge?.nonce) {
            const nonce = String(challenge.nonce);
            const signedAt = nowMs();
            const signature = sign(null, Buffer.from(`${nonce}:${signedAt}`), this.identity.privateKey).toString("base64");
            payload.challenge = { nonce, signedAt, signature };
          }

          const response = await this.request("connect", payload, 12000);
          const type = response?.type ?? response?.event;
          if (type !== "hello-ok") {
            throw new Error(`Unexpected connect response type: ${type ?? "unknown"}`);
          }

          this.connected = true;
          settle(resolve);
        } catch (err) {
          settle(reject, err);
        }
      };

      this.ws.once("open", () => {
        fallbackTimer = setTimeout(() => {
          void sendConnect(null);
        }, 200);
      });

      this.ws.on("message", (raw) => {
        const frame = parseJson(String(raw));
        if (!frame) return;

        if (frame.id && this.pending.has(frame.id)) {
          const p = this.pending.get(frame.id);
          clearTimeout(p.timer);
          this.pending.delete(frame.id);

          if (frame.ok === false) {
            p.reject(new Error(frame.error?.message ?? "Gateway RPC error"));
          } else {
            p.resolve(frame.payload ?? frame.result ?? frame);
          }
          return;
        }

        if (frame.type === "connect.challenge" || frame.event === "connect.challenge") {
          void sendConnect(frame.payload ?? frame.data ?? {});
          return;
        }

        for (const handler of this.handlers) handler(frame);
      });

      this.ws.once("error", (err) => {
        settle(reject, err);
      });

      this.ws.once("close", () => {
        if (!this.connected) settle(reject, new Error("Gateway closed before connect"));
      });
    });

    await connected;
  }

  request(method, payload, timeoutMs = 10000) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return Promise.reject(new Error("Gateway socket is not open"));
    }

    const id = randomUUID();
    const frame = { id, method, payload };

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Gateway RPC timeout for ${method}`));
      }, timeoutMs);

      this.pending.set(id, { resolve, reject, timer });
      this.ws.send(JSON.stringify(frame));
    });
  }

  async close() {
    if (this.closed) return;
    this.closed = true;
    this.connected = false;

    for (const p of this.pending.values()) {
      clearTimeout(p.timer);
      p.reject(new Error("Gateway connection closing"));
    }
    this.pending.clear();

    if (!this.ws) return;

    const ws = this.ws;
    this.ws = null;

    await new Promise((resolve) => {
      const done = () => resolve();
      ws.once("close", done);
      ws.once("error", done);
      try {
        ws.close(1000, "fastclaw shutdown");
      } catch {
        resolve();
      }
      setTimeout(done, 500).unref?.();
    });
  }

  waitForClose() {
    if (!this.ws) return Promise.resolve();
    return new Promise((resolve) => {
      this.ws.once("close", () => {
        this.connected = false;
        resolve();
      });
      this.ws.once("error", () => {
        this.connected = false;
        resolve();
      });
    });
  }
}

class Relay {
  constructor(config) {
    this.config = config;
    this.convex = new ConvexHttpClient(config.convexUrl);

    this.running = true;
    this.reconnectAttempt = 0;
    this.recentGatewayMessageHashes = new Map();
    this.conn = null;
  }

  async start() {
    console.log("fastclaw relay starting...");

    while (this.running) {
      this.conn = new GatewayConnection(this.config);

      try {
        await this.conn.open();
        this.reconnectAttempt = 0;
        console.log(`connected to gateway at ${this.config.gatewayUrl}`);

        await this.runConnected(this.conn);
      } catch (err) {
        if (!this.running) break;
        console.error(`connection error: ${err.message}`);
      } finally {
        await this.conn.close().catch(() => {});
        this.conn = null;
      }

      if (!this.running) break;

      this.reconnectAttempt += 1;
      const backoff = Math.min(30000, 1000 * 2 ** Math.min(this.reconnectAttempt, 5));
      const jitter = Math.floor(Math.random() * 500);
      const waitMs = backoff + jitter;
      console.log(`reconnecting in ${waitMs}ms`);
      await sleep(waitMs);
    }

    console.log("fastclaw relay stopped");
  }

  async runConnected(conn) {
    let stopping = false;

    const onFrame = (frame) => {
      if (frame?.event === "chat.message" || frame?.type === "chat.message") {
        void this.pushGatewayMessages(extractGatewayMessages(frame));
      }

      if (frame?.event === "sessions.updated" || frame?.type === "sessions.updated") {
        void this.syncSessions(conn);
      }

      if (frame?.event === "chat.response" || frame?.type === "chat.response") {
        void this.pushGatewayMessages(extractGatewayMessages(frame));
      }
    };

    const off = conn.onFrame(onFrame);

    const appPoll = setInterval(() => {
      void this.forwardUnsyncedAppMessages(conn);
    }, APP_POLL_MS);

    const heartbeat = setInterval(() => {
      void this.sendHeartbeat();
    }, HEARTBEAT_MS);

    const sessionSync = setInterval(() => {
      void this.syncSessions(conn);
    }, SESSION_SYNC_MS);

    await this.sendHeartbeat();
    await this.syncSessions(conn);
    await this.forwardUnsyncedAppMessages(conn);

    try {
      await conn.waitForClose();
    } finally {
      if (!stopping) {
        stopping = true;
        off();
        clearInterval(appPoll);
        clearInterval(heartbeat);
        clearInterval(sessionSync);
      }
    }
  }

  async syncSessions(conn) {
    try {
      const payload = await conn.request("sessions.list", {});
      const sessions = extractSessions(payload);
      if (sessions.length === 0) return;

      await this.convex.mutation("sessions:syncFromGateway", {
        instanceId: this.config.instanceId,
        sessions,
      });
    } catch (err) {
      if (this.running) console.error(`session sync failed: ${err.message}`);
    }
  }

  async forwardUnsyncedAppMessages(conn) {
    try {
      const unsynced = await this.convex.query("messages:getUnsyncedFromApp", {
        instanceId: this.config.instanceId,
      });

      if (!Array.isArray(unsynced) || unsynced.length === 0) return;

      const syncedIds = [];
      for (const message of unsynced) {
        const sent = await this.sendToGateway(conn, message);
        if (sent && message?._id) syncedIds.push(message._id);
      }

      if (syncedIds.length > 0) {
        await this.convex.mutation("messages:markSynced", { messageIds: syncedIds });
      }
    } catch (err) {
      if (this.running) console.error(`app message forward failed: ${err.message}`);
    }
  }

  async sendToGateway(conn, message) {
    const sessionKey = message?.sessionKey;
    const content = message?.content;
    if (!sessionKey || !content) return false;

    const idempotencyKey = typeof message?._id === "string" ? message._id : randomUUID();

    const attempts = [
      { method: "chat.send", payload: { sessionKey, text: content, idempotencyKey } },
      { method: "chat.send", payload: { sessionKey, content, idempotencyKey } },
      { method: "send", payload: { sessionKey, text: content, idempotencyKey } },
    ];

    for (const attempt of attempts) {
      try {
        const response = await conn.request(attempt.method, attempt.payload);
        const frame = { payload: response };
        await this.pushGatewayMessages(extractGatewayMessages(frame));
        return true;
      } catch {
        // Try next payload shape/method for compatibility across gateway versions.
      }
    }

    return false;
  }

  hashGatewayMessage(msg) {
    return createHash("sha1")
      .update(`${msg.sessionKey}|${msg.role}|${msg.content}|${msg.timestamp}`)
      .digest("hex");
  }

  pruneRecentHashes() {
    const cutoff = nowMs() - 10 * 60 * 1000;
    for (const [hash, ts] of this.recentGatewayMessageHashes.entries()) {
      if (ts < cutoff) this.recentGatewayMessageHashes.delete(hash);
    }
  }

  async pushGatewayMessages(messages) {
    if (!Array.isArray(messages) || messages.length === 0) return;

    this.pruneRecentHashes();

    for (const msg of messages) {
      const hash = this.hashGatewayMessage(msg);
      if (this.recentGatewayMessageHashes.has(hash)) continue;

      try {
        await this.convex.mutation("messages:pushFromGateway", {
          instanceId: this.config.instanceId,
          sessionKey: msg.sessionKey,
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
        });

        this.recentGatewayMessageHashes.set(hash, nowMs());
      } catch (err) {
        if (this.running) console.error(`push gateway message failed: ${err.message}`);
      }
    }
  }

  async sendHeartbeat() {
    try {
      await this.convex.mutation("sessions:heartbeat", {
        instanceId: this.config.instanceId,
      });
    } catch (err) {
      if (this.running) console.error(`heartbeat failed: ${err.message}`);
    }
  }

  async stop() {
    this.running = false;
    if (this.conn) await this.conn.close();
  }
}

async function main() {
  const config = await loadConfig();

  if (!config.gatewayToken) {
    throw new Error(
      `Missing gateway token. Set OPENCLAW_GATEWAY_TOKEN or include gatewayToken in ${CONFIG_PATH}`
    );
  }

  const relay = new Relay(config);

  const shutdown = async (signal) => {
    console.log(`received ${signal}, shutting down...`);
    await relay.stop();
  };

  process.on("SIGINT", () => {
    void shutdown("SIGINT");
  });
  process.on("SIGTERM", () => {
    void shutdown("SIGTERM");
  });

  await relay.start();
}

main().catch((err) => {
  console.error(err.message || err);
  process.exitCode = 1;
});
