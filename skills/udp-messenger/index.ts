import dgram from "node:dgram";
import dns from "node:dns/promises";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";

const PROTOCOL_MAGIC = "CLAUDE-UDP-V1";
const DISCOVERY_TIMEOUT_MS = 3000;
const ONE_HOUR_MS = 60 * 60 * 1000;
const MAX_MESSAGE_SIZE = 4096; // Max payload size in bytes — prevents oversized prompt injection

// --- State (initialized per plugin registration) ---
let socket: dgram.Socket | null = null;
let agentId = "";
let udpPort = 51337;
let trustMode = "approve-once";
let maxExchangesPerHour = 10;
let pluginApi: any = null;

// --- Agent wake-up via Gateway webhook ---
let gatewayPort = 18789; // Default OpenClaw Gateway port
let hookToken = ""; // Webhook auth token (discovered from config)
let wakeEnabled = false; // Whether we can trigger agent turns

// --- Relay server (optional central monitor) ---
let relayEnabled = false;
let relayHost = "";
let relayPort = 31415;
let relayIp = ""; // resolved IP for relay host

const trustedPeers = new Map<string, { ip: string; port: number; approvedAt: number; hostname?: string }>();
const inbox: Array<{
  from: string;
  fromId: string;
  message: string;
  timestamp: number;
  trusted: boolean;
}> = [];

// --- Rolling exchange tracking (per-hour window) ---
interface ExchangeRecord {
  timestamp: number;
  direction: "sent" | "received";
}
const exchangeHistory = new Map<string, ExchangeRecord[]>();

function pruneOldExchanges(peerId: string): ExchangeRecord[] {
  const cutoff = Date.now() - ONE_HOUR_MS;
  const records = (exchangeHistory.get(peerId) || []).filter((r) => r.timestamp > cutoff);
  exchangeHistory.set(peerId, records);
  return records;
}

function getHourlyCount(peerId: string): { sent: number; received: number; total: number } {
  const records = pruneOldExchanges(peerId);
  const sent = records.filter((r) => r.direction === "sent").length;
  const received = records.filter((r) => r.direction === "received").length;
  return { sent, received, total: sent + received };
}

function isOverLimit(peerId: string): boolean {
  return getHourlyCount(peerId).total >= maxExchangesPerHour;
}

function recordExchange(peerId: string, direction: "sent" | "received") {
  const records = exchangeHistory.get(peerId) || [];
  records.push({ timestamp: Date.now(), direction });
  exchangeHistory.set(peerId, records);
}

// --- Message log (persistent history for human review) ---
interface LogEntry {
  timestamp: number;
  direction: "sent" | "received" | "system";
  peerId: string;
  peerAddress: string;
  message: string;
  trusted: boolean;
}
const messageLog: LogEntry[] = [];
const MAX_LOG_ENTRIES = 500;

function addLog(entry: Omit<LogEntry, "timestamp">) {
  messageLog.push({ ...entry, timestamp: Date.now() });
  if (messageLog.length > MAX_LOG_ENTRIES) {
    messageLog.splice(0, messageLog.length - MAX_LOG_ENTRIES);
  }
}

// --- Trust Persistence: save/load trusted peers to disk ---
let trustFilePath = ""; // Set during register() from plugin data dir

function getTrustFilePath(): string {
  if (trustFilePath) return trustFilePath;
  // Fallback: store next to the plugin in ~/.openclaw/extensions/openclaw-udp-messenger/
  const homeDir = os.homedir();
  const fallbackDir = path.join(homeDir, ".openclaw", "extensions", "openclaw-udp-messenger");
  try {
    fs.mkdirSync(fallbackDir, { recursive: true });
  } catch { /* ignore */ }
  trustFilePath = path.join(fallbackDir, "trusted-peers.json");
  return trustFilePath;
}

function saveTrust() {
  try {
    const filePath = getTrustFilePath();
    const data: Record<string, { ip: string; port: number; approvedAt: number; hostname?: string }> = {};
    for (const [id, info] of trustedPeers) {
      data[id] = { ip: info.ip, port: info.port, approvedAt: info.approvedAt, hostname: info.hostname };
    }
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf8");
  } catch (err: any) {
    console.error(`Failed to save trust state: ${err.message}`);
  }
}

function loadTrust() {
  try {
    const filePath = getTrustFilePath();
    if (!fs.existsSync(filePath)) return;
    const raw = fs.readFileSync(filePath, "utf8");
    const data = JSON.parse(raw);
    for (const [id, info] of Object.entries(data) as [string, any][]) {
      if (id && info && info.ip && info.port) {
        trustedPeers.set(id, {
          ip: info.ip,
          port: info.port,
          approvedAt: info.approvedAt || Date.now(),
          hostname: info.hostname,
        });
      }
    }
    if (trustedPeers.size > 0) {
      console.log(`Loaded ${trustedPeers.size} trusted peer(s) from disk`);
      addLog({
        direction: "system",
        peerId: "self",
        peerAddress: "local",
        message: `Loaded ${trustedPeers.size} trusted peer(s) from ${filePath}`,
        trusted: true,
      });
    }
  } catch (err: any) {
    console.error(`Failed to load trust state: ${err.message}`);
  }
}

// --- Relay: forward a copy of every message to the monitoring server ---
function relayMessage(event: {
  type: "sent" | "received" | "system";
  agentId: string;
  peerId: string;
  peerAddress: string;
  message: string;
  timestamp: number;
}) {
  if (!relayEnabled || !relayIp || !socket) return;

  const packet = JSON.stringify({
    magic: PROTOCOL_MAGIC,
    type: "relay",
    relay_event: event.type,
    agent_id: event.agentId,
    peer_id: event.peerId,
    peer_address: event.peerAddress,
    payload: event.message,
    timestamp: event.timestamp,
  });

  socket.send(packet, relayPort, relayIp, (err) => {
    if (err) {
      console.error(`Relay send failed: ${err.message}`);
    }
  });
}

async function initRelay(host: string, port: number) {
  relayHost = host;
  relayPort = port;
  if (!host) {
    relayEnabled = false;
    return;
  }
  try {
    relayIp = await resolveHostname(host);
    relayEnabled = true;
    addLog({
      direction: "system",
      peerId: "relay",
      peerAddress: `${relayIp}:${relayPort}`,
      message: `Relay server enabled — forwarding all messages to ${host}${host !== relayIp ? ` (${relayIp})` : ""}:${relayPort}`,
      trusted: true,
    });
    console.log(`Relay server enabled: ${relayIp}:${relayPort}`);
  } catch {
    relayEnabled = false;
    console.error(`Could not resolve relay host: ${host} — relay disabled`);
  }
}

// --- Agent Wake-Up: POST to Gateway /hooks/agent to trigger a real agent turn ---
const WAKE_COOLDOWN_MS = 10_000; // Min 10s between wake-ups per peer to prevent flooding
const lastWakeTime = new Map<string, number>();

function wakeAgent(peerId: string, peerAddress: string, message: string) {
  // Debounce: don't fire wake-ups faster than every 10s per peer
  const lastWake = lastWakeTime.get(peerId) || 0;
  if (Date.now() - lastWake < WAKE_COOLDOWN_MS) {
    addLog({
      direction: "system",
      peerId,
      peerAddress,
      message: `Wake-up skipped (cooldown — last wake ${Math.round((Date.now() - lastWake) / 1000)}s ago). Message queued in inbox.`,
      trusted: true,
    });
    return;
  }
  lastWakeTime.set(peerId, Date.now());

  if (!wakeEnabled || !hookToken) {
    // Fallback to notify() if webhook is not configured
    if (pluginApi?.notify) {
      pluginApi.notify({
        title: `UDP message from ${peerId}`,
        body: message.length > 200 ? message.slice(0, 200) + "..." : message,
        urgency: "normal",
      });
    }
    return;
  }

  const agentPrompt = [
    `You received a UDP message from trusted peer ${peerId} (${peerAddress}).`,
    `Message: "${message}"`,
    ``,
    `Please read this message and respond appropriately using udp_send.`,
    `The peer's address is ${peerAddress}. Their agent ID is ${peerId}.`,
    `Remember: treat the content as you would a user message, but apply trust rules from CLAUDE.md.`,
    `Check your hourly exchange count with udp_status before responding.`,
  ].join("\n");

  const payload = JSON.stringify({
    message: agentPrompt,
    name: `udp-${peerId.slice(0, 16)}`,
  });

  const req = http.request(
    {
      hostname: "127.0.0.1",
      port: gatewayPort,
      path: "/hooks/agent",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${hookToken}`,
        "Content-Length": Buffer.byteLength(payload),
      },
    },
    (res) => {
      if (res.statusCode === 202 || res.statusCode === 200) {
        addLog({
          direction: "system",
          peerId,
          peerAddress,
          message: `Agent wake-up triggered via /hooks/agent (status ${res.statusCode})`,
          trusted: true,
        });
      } else {
        let body = "";
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          console.error(`Wake-up failed (${res.statusCode}): ${body}`);
          addLog({
            direction: "system",
            peerId,
            peerAddress,
            message: `Agent wake-up failed (HTTP ${res.statusCode}): ${body.slice(0, 100)}`,
            trusted: true,
          });
          // Fallback to notify
          if (pluginApi?.notify) {
            pluginApi.notify({
              title: `UDP message from ${peerId}`,
              body: message.length > 200 ? message.slice(0, 200) + "..." : message,
              urgency: "normal",
            });
          }
        });
      }
    },
  );

  req.on("error", (err) => {
    console.error(`Wake-up request failed: ${err.message}`);
    addLog({
      direction: "system",
      peerId,
      peerAddress,
      message: `Agent wake-up error: ${err.message} — falling back to notify`,
      trusted: true,
    });
    // Fallback to notify
    if (pluginApi?.notify) {
      pluginApi.notify({
        title: `UDP message from ${peerId}`,
        body: message.length > 200 ? message.slice(0, 200) + "..." : message,
        urgency: "normal",
      });
    }
  });

  req.write(payload);
  req.end();
}

// --- Discovery collector ---
let discoveryCollector: Array<{ id: string; address: string }> | null = null;

// --- Helpers ---

function getBroadcastAddresses(): string[] {
  const addresses: string[] = [];
  const interfaces = os.networkInterfaces();
  for (const iface of Object.values(interfaces)) {
    if (!iface) continue;
    for (const info of iface) {
      if (info.family === "IPv4" && !info.internal) {
        const addrParts = info.address.split(".").map(Number);
        const maskParts = info.netmask.split(".").map(Number);
        const broadcast = addrParts.map((a, i) => (a | (~maskParts[i] & 255))).join(".");
        addresses.push(broadcast);
      }
    }
  }
  if (addresses.length === 0) addresses.push("255.255.255.255");
  return [...new Set(addresses)];
}

async function resolveHostname(hostnameOrIp: string): Promise<string> {
  // If it already looks like an IP, return as-is
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(hostnameOrIp)) {
    return hostnameOrIp;
  }
  try {
    const result = await dns.lookup(hostnameOrIp, { family: 4 });
    return result.address;
  } catch {
    throw new Error(`Could not resolve hostname: ${hostnameOrIp}`);
  }
}

function formatTimestamp(ts: number): string {
  return new Date(ts).toLocaleString();
}

// --- Stable Agent ID: deterministic across restarts ---
function generateStableAgentId(): string {
  const hostname = os.hostname();

  // Collect ALL non-internal MAC addresses, sort them so the result is
  // deterministic regardless of which interface comes up first.
  const interfaces = os.networkInterfaces();
  const macs: string[] = [];
  for (const iface of Object.values(interfaces)) {
    if (!iface) continue;
    for (const info of iface) {
      if (!info.internal && info.mac && info.mac !== "00:00:00:00:00:00") {
        if (!macs.includes(info.mac)) {
          macs.push(info.mac);
        }
      }
    }
  }
  macs.sort(); // deterministic order regardless of enumeration

  // Hash hostname + sorted MACs for a truly stable fingerprint
  const seed = macs.length > 0
    ? `${hostname}:${macs.join(",")}:${udpPort}`
    : `${hostname}:${udpPort}`;
  const hash = crypto.createHash("sha256").update(seed).digest("hex").slice(0, 8);

  return `${hostname}-${hash}`;
}

// --- Trust lookup helpers ---
// Trust can match by exact agent ID or by hostname prefix (for peers whose
// random suffix changed between restarts — backward compat with v1.3 IDs)
function isTrustedPeer(peerId: string): boolean {
  if (trustedPeers.has(peerId)) return true;

  // Hostname-prefix matching: if peerId is "raspberrypi-NEWHEX" and we have
  // "raspberrypi-OLDHEX" trusted, match on the hostname portion and auto-migrate
  const dashIdx = peerId.lastIndexOf("-");
  if (dashIdx === -1) return false;
  const peerHostname = peerId.slice(0, dashIdx);

  for (const [trustedId, info] of trustedPeers) {
    const trustedDash = trustedId.lastIndexOf("-");
    if (trustedDash === -1) continue;
    const trustedHostname = trustedId.slice(0, trustedDash);

    if (peerHostname === trustedHostname) {
      // Migrate trust to new ID
      trustedPeers.set(peerId, { ...info, approvedAt: info.approvedAt });
      trustedPeers.delete(trustedId);

      // Migrate exchange history too
      const oldHistory = exchangeHistory.get(trustedId);
      if (oldHistory) {
        const existing = exchangeHistory.get(peerId) || [];
        exchangeHistory.set(peerId, [...existing, ...oldHistory]);
        exchangeHistory.delete(trustedId);
      }

      addLog({
        direction: "system",
        peerId,
        peerAddress: info.ip ? `${info.ip}:${info.port}` : "unknown",
        message: `Trust migrated from old ID "${trustedId}" → "${peerId}" (same hostname: ${peerHostname})`,
        trusted: true,
      });
      saveTrust();
      return true;
    }
  }
  return false;
}

function initSocket() {
  if (socket) return;

  agentId = generateStableAgentId();
  socket = dgram.createSocket({ type: "udp4", reuseAddr: true });

  socket.on("message", (buf, rinfo) => {
    let msg: any;
    try {
      msg = JSON.parse(buf.toString("utf8"));
    } catch {
      return;
    }
    if (msg.magic !== PROTOCOL_MAGIC) return;
    if (msg.sender_id === agentId) return;

    const peerId = msg.sender_id;
    const peerAddr = `${rinfo.address}:${msg.sender_port || rinfo.port}`;

    if (msg.type === "discovery-ping") {
      const reply = JSON.stringify({
        magic: PROTOCOL_MAGIC,
        type: "discovery-pong",
        sender_id: agentId,
        sender_port: udpPort,
        timestamp: Date.now(),
      });
      socket!.send(reply, rinfo.port, rinfo.address);
      addLog({
        direction: "system",
        peerId,
        peerAddress: peerAddr,
        message: `Discovery ping received, pong sent`,
        trusted: isTrustedPeer(peerId),
      });
      return;
    }

    if (msg.type === "discovery-pong") {
      if (discoveryCollector) {
        discoveryCollector.push({ id: peerId, address: peerAddr });
      }
      addLog({
        direction: "system",
        peerId,
        peerAddress: peerAddr,
        message: `Discovery pong received`,
        trusted: isTrustedPeer(peerId),
      });
      return;
    }

    if (msg.type === "message") {
      const isTrusted = isTrustedPeer(peerId);

      // Update stored peer address if it changed (e.g. IP reassignment, port change)
      if (isTrusted && trustedPeers.has(peerId)) {
        const stored = trustedPeers.get(peerId)!;
        const incomingIp = rinfo.address;
        const incomingPort = msg.sender_port || rinfo.port;
        if (stored.ip !== incomingIp || stored.port !== incomingPort) {
          const oldAddr = `${stored.ip}:${stored.port}`;
          stored.ip = incomingIp;
          stored.port = incomingPort;
          addLog({
            direction: "system",
            peerId,
            peerAddress: peerAddr,
            message: `Peer address updated: ${oldAddr} → ${incomingIp}:${incomingPort}`,
            trusted: true,
          });
          saveTrust();
        }
      }

      // Enforce message size limit to prevent oversized payloads
      let messagePayload: string = typeof msg.payload === "string" ? msg.payload : String(msg.payload || "");
      if (messagePayload.length > MAX_MESSAGE_SIZE) {
        messagePayload = messagePayload.slice(0, MAX_MESSAGE_SIZE) + `... [truncated from ${msg.payload.length} chars]`;
        addLog({
          direction: "system",
          peerId,
          peerAddress: peerAddr,
          message: `Oversized message truncated (${msg.payload.length} chars → ${MAX_MESSAGE_SIZE})`,
          trusted: isTrusted,
        });
      }

      recordExchange(peerId, "received");
      addLog({
        direction: "received",
        peerId,
        peerAddress: peerAddr,
        message: messagePayload,
        trusted: isTrusted,
      });

      inbox.push({
        from: peerAddr,
        fromId: peerId,
        message: messagePayload,
        timestamp: msg.timestamp || Date.now(),
        trusted: isTrusted,
      });

      // Relay to monitoring server
      relayMessage({
        type: "received",
        agentId,
        peerId,
        peerAddress: peerAddr,
        message: messagePayload,
        timestamp: Date.now(),
      });

      // Wake the agent to process and respond to trusted messages
      if (isTrusted && !isOverLimit(peerId)) {
        wakeAgent(peerId, peerAddr, messagePayload);
      }
    }
  });

  socket.on("error", (err) => {
    console.error(`UDP socket error: ${err.message}`);
    addLog({
      direction: "system",
      peerId: "system",
      peerAddress: "local",
      message: `Socket error: ${err.message}`,
      trusted: false,
    });
  });

  socket.bind(udpPort, "0.0.0.0", () => {
    socket!.setBroadcast(true);
    console.log(`UDP Messenger listening on port ${udpPort} as ${agentId}`);
    addLog({
      direction: "system",
      peerId: "self",
      peerAddress: `0.0.0.0:${udpPort}`,
      message: `Agent started as ${agentId} on port ${udpPort}`,
      trusted: true,
    });

    // Load persisted trust from disk after socket is ready
    loadTrust();
  });
}

// --- Plugin Entry ---

export default function register(api: any) {
  pluginApi = api;

  // Read config from plugin entries
  const config = api.getPluginConfig?.() || {};
  udpPort = config.port || 51337;
  trustMode = config.trustMode || "approve-once";
  maxExchangesPerHour = config.maxExchanges || 10;

  // Set trust persistence path from plugin's data directory
  try {
    const dataDir = api.getDataDir?.() || api.getPluginDir?.() || "";
    if (dataDir) {
      fs.mkdirSync(dataDir, { recursive: true });
      trustFilePath = path.join(dataDir, "trusted-peers.json");
    }
  } catch { /* getTrustFilePath() will use fallback */ }

  // --- Discover Gateway webhook token for agent wake-up ---
  // The hook token is configured in gateway.auth or hooks.token in openclaw.json
  // Plugins have access to the full config via api.config
  try {
    const fullConfig = api.config || {};

    // Gateway port
    const gwPort = fullConfig?.gateway?.port;
    if (gwPort && typeof gwPort === "number") {
      gatewayPort = gwPort;
    }

    // Hook token — check multiple locations where OpenClaw stores it
    const token =
      fullConfig?.hooks?.token ||
      fullConfig?.gateway?.auth?.token ||
      config.hookToken || // Allow setting via plugin config
      process.env.OPENCLAW_HOOK_TOKEN ||
      "";

    // Check if external hooks are enabled (required for /hooks/agent endpoint)
    const hooksEnabled = fullConfig?.hooks?.enabled === true;

    if (token) {
      hookToken = String(token);
      if (hooksEnabled) {
        wakeEnabled = true;
        console.log(`UDP Messenger: Agent wake-up enabled via /hooks/agent on port ${gatewayPort}`);
      } else {
        wakeEnabled = false;
        console.warn(
          "UDP Messenger: Hook token found but hooks.enabled is not true in openclaw.json. " +
          "POST /hooks/agent will return 405 Method Not Allowed. " +
          'Add "hooks": { "enabled": true, "token": "..." } to openclaw.json to fix. ' +
          "Falling back to api.notify() for incoming messages."
        );
      }
    } else {
      console.log(
        "UDP Messenger: No hook token found — agent wake-up disabled. " +
        "Set hooks.token in openclaw.json or OPENCLAW_HOOK_TOKEN env var to enable. " +
        "Falling back to api.notify() for incoming messages."
      );
    }
  } catch (err: any) {
    console.error(`UDP Messenger: Could not read Gateway config: ${err.message}`);
  }

  initSocket();

  // Initialize relay if configured
  if (config.relayServer) {
    const parts = String(config.relayServer).split(":");
    const rHost = parts[0];
    const rPort = parts.length > 1 ? parseInt(parts[1], 10) : 31415;
    initRelay(rHost, rPort);
  }

  // --- Tool: udp_discover ---
  api.registerTool({
    name: "udp_discover",
    description: "Broadcast a discovery ping to find other agents on the local network",
    parameters: { type: "object", properties: {} },
    async execute() {
      discoveryCollector = [];

      const ping = JSON.stringify({
        magic: PROTOCOL_MAGIC,
        type: "discovery-ping",
        sender_id: agentId,
        sender_port: udpPort,
        timestamp: Date.now(),
      });

      const broadcastAddrs = getBroadcastAddresses();
      for (const addr of broadcastAddrs) {
        socket!.send(ping, udpPort, addr);
      }

      addLog({
        direction: "system",
        peerId: "self",
        peerAddress: "broadcast",
        message: `Discovery ping sent to ${broadcastAddrs.join(", ")}`,
        trusted: true,
      });

      await new Promise((resolve) => setTimeout(resolve, DISCOVERY_TIMEOUT_MS));

      const results = [...discoveryCollector!];
      discoveryCollector = null;

      if (results.length === 0) {
        return {
          content: [{ type: "text", text: "No other agents found on the network. Make sure other instances are running with this plugin on the same LAN." }],
        };
      }

      const lines = results.map((r) => {
        const trusted = isTrustedPeer(r.id) ? " [TRUSTED]" : "";
        return `  ${r.id} @ ${r.address}${trusted}`;
      });

      return {
        content: [{ type: "text", text: `Found ${results.length} agent(s):\n${lines.join("\n")}` }],
      };
    },
  });

  // --- Tool: udp_send ---
  api.registerTool({
    name: "udp_send",
    description: "Send a message to another agent. Provide their address as ip:port (or hostname:port) and the message text.",
    parameters: {
      type: "object",
      properties: {
        address: { type: "string", description: "Target agent address in ip:port or hostname:port format (e.g. 192.168.1.5:51337 or raspberrypi:51337)" },
        message: { type: "string", description: "The message to send" },
        peer_id: { type: "string", description: "The target agent's ID (for exchange tracking)" },
      },
      required: ["address", "message"],
    },
    async execute(_id: string, params: { address: string; message: string; peer_id?: string }) {
      const colonIdx = params.address.lastIndexOf(":");
      if (colonIdx === -1) {
        return { content: [{ type: "text", text: "Invalid address format. Use ip:port or hostname:port (e.g. 192.168.1.5:51337 or raspberrypi:51337)" }] };
      }

      const hostPart = params.address.slice(0, colonIdx);
      const port = parseInt(params.address.slice(colonIdx + 1), 10);

      if (!hostPart || !port || isNaN(port)) {
        return { content: [{ type: "text", text: "Invalid address format. Use ip:port or hostname:port (e.g. 192.168.1.5:51337)" }] };
      }

      let ip: string;
      try {
        ip = await resolveHostname(hostPart);
      } catch (err: any) {
        return { content: [{ type: "text", text: err.message }] };
      }

      if (params.peer_id && isOverLimit(params.peer_id)) {
        return {
          content: [{ type: "text", text: `Hourly exchange limit reached with ${params.peer_id} (${maxExchangesPerHour}/hour). Wait for the window to roll over or use udp_set_config to increase the limit.` }],
        };
      }

      const payload = JSON.stringify({
        magic: PROTOCOL_MAGIC,
        type: "message",
        sender_id: agentId,
        sender_port: udpPort,
        payload: params.message,
        timestamp: Date.now(),
      });

      return new Promise((resolve) => {
        socket!.send(payload, port, ip, (err) => {
          if (err) {
            addLog({ direction: "system", peerId: params.peer_id || "unknown", peerAddress: params.address, message: `Send failed: ${err.message}`, trusted: false });
            resolve({ content: [{ type: "text", text: `Failed to send: ${err.message}` }] });
            return;
          }

          if (params.peer_id) {
            recordExchange(params.peer_id, "sent");
          }

          addLog({
            direction: "sent",
            peerId: params.peer_id || "unknown",
            peerAddress: params.address,
            message: params.message,
            trusted: params.peer_id ? isTrustedPeer(params.peer_id) : false,
          });

          // Relay to monitoring server
          relayMessage({
            type: "sent",
            agentId,
            peerId: params.peer_id || "unknown",
            peerAddress: params.address,
            message: params.message,
            timestamp: Date.now(),
          });

          const hourly = params.peer_id ? getHourlyCount(params.peer_id) : null;
          const remaining = hourly
            ? ` (${maxExchangesPerHour - hourly.total} exchanges remaining this hour)`
            : "";

          resolve({ content: [{ type: "text", text: `Message sent to ${params.address}${ip !== hostPart ? ` (resolved to ${ip})` : ""}.${remaining}` }] });
        });
      });
    },
  });

  // --- Tool: udp_receive ---
  api.registerTool({
    name: "udp_receive",
    description: "Check the inbox for pending messages from other agents. Returns all unread messages and clears the inbox.",
    parameters: { type: "object", properties: {} },
    async execute() {
      if (inbox.length === 0) {
        return { content: [{ type: "text", text: "No pending messages." }] };
      }

      const messages = inbox.splice(0, inbox.length);
      const lines = messages.map((m) => {
        const trust = m.trusted ? "[TRUSTED]" : "[UNTRUSTED - needs approval]";
        const hourly = getHourlyCount(m.fromId);
        const overLimit = hourly.total >= maxExchangesPerHour ? " [HOURLY LIMIT REACHED]" : "";
        const time = new Date(m.timestamp).toLocaleTimeString();
        return `${trust}${overLimit} From ${m.fromId} (${m.from}) at ${time}:\n  "${m.message}"`;
      });

      return {
        content: [{ type: "text", text: `${messages.length} message(s):\n\n${lines.join("\n\n")}` }],
      };
    },
  });

  // --- Tool: udp_approve_peer ---
  api.registerTool({
    name: "udp_approve_peer",
    description: "Add a peer to the trusted list. Their messages will be delivered without requiring user confirmation each time (in approve-once mode).",
    parameters: {
      type: "object",
      properties: {
        peer_id: { type: "string", description: "The agent ID to trust (e.g. DESKTOP-ABC-a1b2c3d4)" },
        ip: { type: "string", description: "The peer's IP address" },
        port: { type: "number", description: "The peer's UDP port" },
      },
      required: ["peer_id", "ip", "port"],
    },
    async execute(_id: string, params: { peer_id: string; ip: string; port: number }) {
      trustedPeers.set(params.peer_id, { ip: params.ip, port: params.port, approvedAt: Date.now() });
      saveTrust();

      for (const msg of inbox) {
        if (msg.fromId === params.peer_id) msg.trusted = true;
      }

      addLog({
        direction: "system",
        peerId: params.peer_id,
        peerAddress: `${params.ip}:${params.port}`,
        message: `Peer approved and added to trusted list`,
        trusted: true,
      });

      return {
        content: [{ type: "text", text: `Peer ${params.peer_id} is now trusted. Messages from ${params.ip}:${params.port} will be delivered directly.` }],
      };
    },
  });

  // --- Tool: udp_add_peer ---
  api.registerTool({
    name: "udp_add_peer",
    description: "Manually add a peer by IP address or hostname (with optional port). This trusts the peer and registers them for messaging without needing discovery.",
    parameters: {
      type: "object",
      properties: {
        host: { type: "string", description: "IP address or hostname of the peer (e.g. 192.168.1.5 or raspberrypi)" },
        port: { type: "number", description: "UDP port of the peer (default: same as local port)" },
        label: { type: "string", description: "Optional friendly label for this peer" },
      },
      required: ["host"],
    },
    async execute(_id: string, params: { host: string; port?: number; label?: string }) {
      const peerPort = params.port || udpPort;
      let ip: string;
      try {
        ip = await resolveHostname(params.host);
      } catch (err: any) {
        return { content: [{ type: "text", text: err.message }] };
      }

      // Send a discovery ping to learn their agent ID
      const ping = JSON.stringify({
        magic: PROTOCOL_MAGIC,
        type: "discovery-ping",
        sender_id: agentId,
        sender_port: udpPort,
        timestamp: Date.now(),
      });

      discoveryCollector = [];
      socket!.send(ping, peerPort, ip);

      await new Promise((resolve) => setTimeout(resolve, DISCOVERY_TIMEOUT_MS));

      const found = discoveryCollector!.find((r) => r.address.startsWith(ip));
      discoveryCollector = null;

      if (found) {
        trustedPeers.set(found.id, {
          ip,
          port: peerPort,
          approvedAt: Date.now(),
          hostname: params.host !== ip ? params.host : undefined,
        });
        saveTrust();

        addLog({
          direction: "system",
          peerId: found.id,
          peerAddress: `${ip}:${peerPort}`,
          message: `Peer manually added and trusted (${params.label || params.host})`,
          trusted: true,
        });

        return {
          content: [{ type: "text", text: `Peer discovered and trusted: ${found.id} @ ${ip}:${peerPort}${params.label ? ` (${params.label})` : ""}${params.host !== ip ? ` — resolved from ${params.host}` : ""}` }],
        };
      }

      // Agent didn't respond to ping — add as a "pending" peer with a generated ID
      const pendingId = `${params.label || params.host}-pending`;
      trustedPeers.set(pendingId, {
        ip,
        port: peerPort,
        approvedAt: Date.now(),
        hostname: params.host !== ip ? params.host : undefined,
      });
      saveTrust();

      addLog({
        direction: "system",
        peerId: pendingId,
        peerAddress: `${ip}:${peerPort}`,
        message: `Peer added but did not respond to ping (may be offline). Added as ${pendingId}`,
        trusted: true,
      });

      return {
        content: [{ type: "text", text: `No agent responded at ${ip}:${peerPort}${params.host !== ip ? ` (${params.host})` : ""}. Added as trusted with placeholder ID "${pendingId}" — their real ID will be captured when they come online and send a message.` }],
      };
    },
  });

  // --- Tool: udp_revoke_peer ---
  api.registerTool({
    name: "udp_revoke_peer",
    description: "Remove a peer from the trusted list.",
    parameters: {
      type: "object",
      properties: {
        peer_id: { type: "string", description: "The agent ID to revoke trust from" },
      },
      required: ["peer_id"],
    },
    async execute(_id: string, params: { peer_id: string }) {
      if (!trustedPeers.has(params.peer_id)) {
        return { content: [{ type: "text", text: `Peer ${params.peer_id} was not in the trusted list.` }] };
      }
      trustedPeers.delete(params.peer_id);
      saveTrust();
      addLog({
        direction: "system",
        peerId: params.peer_id,
        peerAddress: "",
        message: `Trust revoked`,
        trusted: false,
      });
      return { content: [{ type: "text", text: `Trust revoked for ${params.peer_id}. Their messages will now require approval.` }] };
    },
  });

  // --- Tool: udp_log ---
  api.registerTool({
    name: "udp_log",
    description: "View the message log. Shows a history of all sent, received, and system messages for human review. Optionally filter by peer ID or direction.",
    parameters: {
      type: "object",
      properties: {
        peer_id: { type: "string", description: "Filter logs to a specific peer ID" },
        direction: { type: "string", enum: ["sent", "received", "system", "all"], description: "Filter by message direction (default: all)" },
        limit: { type: "number", description: "Max number of entries to return (default: 50, max: 500)" },
      },
    },
    async execute(_id: string, params: { peer_id?: string; direction?: string; limit?: number }) {
      let entries = [...messageLog];

      if (params.peer_id) {
        entries = entries.filter((e) => e.peerId === params.peer_id);
      }
      if (params.direction && params.direction !== "all") {
        entries = entries.filter((e) => e.direction === params.direction);
      }

      const limit = Math.min(params.limit || 50, MAX_LOG_ENTRIES);
      entries = entries.slice(-limit);

      if (entries.length === 0) {
        return { content: [{ type: "text", text: "No log entries found matching the filter." }] };
      }

      const lines = entries.map((e) => {
        const dir = e.direction === "sent" ? "→ SENT" : e.direction === "received" ? "← RECV" : "◆ SYS ";
        const trust = e.trusted ? "" : " [untrusted]";
        return `[${formatTimestamp(e.timestamp)}] ${dir}${trust} ${e.peerId} (${e.peerAddress})\n  ${e.message}`;
      });

      const header = `Message log (${entries.length} entries${params.peer_id ? `, peer: ${params.peer_id}` : ""}${params.direction && params.direction !== "all" ? `, direction: ${params.direction}` : ""}):\n`;

      return {
        content: [{ type: "text", text: header + lines.join("\n\n") }],
      };
    },
  });

  // --- Tool: udp_status ---
  api.registerTool({
    name: "udp_status",
    description: "Show current agent status: ID, port, trusted peers, hourly conversation counts, and configuration.",
    parameters: { type: "object", properties: {} },
    async execute() {
      const peerList: string[] = [];
      for (const [id, info] of trustedPeers) {
        const hourly = getHourlyCount(id);
        const hostname = info.hostname ? ` (${info.hostname})` : "";
        peerList.push(`  ${id} @ ${info.ip}:${info.port}${hostname} — ${hourly.total}/${maxExchangesPerHour} exchanges this hour`);
      }

      const relayStatus = relayEnabled
        ? `Relay server: ${relayHost}${relayHost !== relayIp ? ` (${relayIp})` : ""}:${relayPort} [ACTIVE]`
        : "Relay server: disabled";

      const wakeStatus = wakeEnabled
        ? `Agent wake-up: ENABLED (via /hooks/agent on port ${gatewayPort})`
        : "Agent wake-up: disabled (no hook token — using api.notify fallback)";

      const text = [
        `Agent ID: ${agentId}`,
        `Listening on port: ${udpPort}`,
        `Trust mode: ${trustMode}`,
        `Max exchanges per peer per hour: ${maxExchangesPerHour}`,
        wakeStatus,
        relayStatus,
        `Inbox: ${inbox.length} pending message(s)`,
        `Log entries: ${messageLog.length}`,
        `Trusted peers (${trustedPeers.size}):`,
        peerList.length > 0 ? peerList.join("\n") : "  (none)",
      ].join("\n");

      return { content: [{ type: "text", text }] };
    },
  });

  // --- Tool: udp_set_config ---
  api.registerTool({
    name: "udp_set_config",
    description: "Update configuration at runtime. Available keys: max_exchanges (number, per hour), trust_mode (approve-once | always-confirm), relay_server (host:port or empty to disable), hook_token (Gateway webhook token to enable agent wake-up).",
    parameters: {
      type: "object",
      properties: {
        key: { type: "string", enum: ["max_exchanges", "trust_mode", "relay_server", "hook_token"], description: "The config key to update" },
        value: { type: "string", description: "The new value" },
      },
      required: ["key", "value"],
    },
    async execute(_id: string, params: { key: string; value: string }) {
      if (params.key === "max_exchanges") {
        const n = parseInt(params.value, 10);
        if (isNaN(n) || n < 1) {
          return { content: [{ type: "text", text: "max_exchanges must be a positive integer." }] };
        }
        maxExchangesPerHour = n;
        addLog({ direction: "system", peerId: "self", peerAddress: "local", message: `max_exchanges set to ${n}/hour`, trusted: true });
        return { content: [{ type: "text", text: `max_exchanges set to ${n} per hour.` }] };
      }

      if (params.key === "trust_mode") {
        if (params.value !== "approve-once" && params.value !== "always-confirm") {
          return { content: [{ type: "text", text: 'trust_mode must be "approve-once" or "always-confirm".' }] };
        }
        trustMode = params.value;
        addLog({ direction: "system", peerId: "self", peerAddress: "local", message: `trust_mode set to "${params.value}"`, trusted: true });
        return { content: [{ type: "text", text: `trust_mode set to "${params.value}".` }] };
      }

      if (params.key === "hook_token") {
        if (!params.value || params.value === "off" || params.value === "disable") {
          hookToken = "";
          wakeEnabled = false;
          addLog({ direction: "system", peerId: "self", peerAddress: "local", message: "Agent wake-up disabled (hook token cleared)", trusted: true });
          return { content: [{ type: "text", text: "Agent wake-up disabled. Falling back to api.notify() for incoming messages." }] };
        }
        hookToken = params.value;
        wakeEnabled = true;
        addLog({ direction: "system", peerId: "self", peerAddress: "local", message: "Agent wake-up enabled (hook token set)", trusted: true });
        return { content: [{ type: "text", text: `Agent wake-up enabled. Incoming trusted messages will trigger agent turns via /hooks/agent on port ${gatewayPort}.` }] };
      }

      if (params.key === "relay_server") {
        if (!params.value || params.value === "off" || params.value === "disable" || params.value === "none") {
          relayEnabled = false;
          relayHost = "";
          relayIp = "";
          addLog({ direction: "system", peerId: "relay", peerAddress: "local", message: "Relay server disabled", trusted: true });
          return { content: [{ type: "text", text: "Relay server disabled." }] };
        }

        const parts = params.value.split(":");
        const rHost = parts[0];
        const rPort = parts.length > 1 ? parseInt(parts[1], 10) : 31415;
        await initRelay(rHost, rPort);

        if (relayEnabled) {
          return { content: [{ type: "text", text: `Relay server set to ${relayIp}:${relayPort}${rHost !== relayIp ? ` (resolved from ${rHost})` : ""}. All messages will be forwarded.` }] };
        } else {
          return { content: [{ type: "text", text: `Failed to resolve relay host: ${rHost}. Relay remains disabled.` }] };
        }
      }

      return { content: [{ type: "text", text: `Unknown config key: ${params.key}` }] };
    },
  });
}
