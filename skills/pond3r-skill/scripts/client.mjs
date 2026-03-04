#!/usr/bin/env node
/**
 * Minimal MCP client for Pond3r Streamable HTTP.
 * Reads POND3R_API_KEY from env. Sends JSON-RPC to https://mcp.pond3r.xyz/mcp
 */

const MCP_URL = "https://mcp.pond3r.xyz/mcp";

function requireEnv(name) {
  const v = process.env[name];
  if (!v || !String(v).trim()) {
    throw new Error(`Missing required env var: ${name}. Add it to .env`);
  }
  return v.trim();
}

let _sessionId = null;

function parseSseBody(text) {
  const lines = text.split(/\r?\n/);
  const messages = [];
  let dataLines = [];

  const flush = () => {
    if (dataLines.length === 0) return;
    const payload = dataLines.join("\n").trim();
    dataLines = [];
    if (!payload) return;
    try {
      messages.push(JSON.parse(payload));
    } catch {
      // Ignore non-JSON frames.
    }
  };

  for (const line of lines) {
    if (line === "") {
      flush();
      continue;
    }
    if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trimStart());
    }
  }
  flush();

  // Return the last JSON-RPC object from the stream.
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg && (Object.prototype.hasOwnProperty.call(msg, "result") || Object.prototype.hasOwnProperty.call(msg, "error"))) {
      return msg;
    }
  }
  return null;
}

function parseMcpResponse(text, contentType) {
  if (contentType?.includes("text/event-stream")) {
    const sseData = parseSseBody(text);
    if (!sseData) {
      throw new Error(`Pond3r MCP invalid SSE payload: ${text.slice(0, 200)}`);
    }
    return sseData;
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Pond3r MCP invalid JSON: ${text.slice(0, 200)}`);
  }
}

/**
 * Send JSON-RPC request to Pond3r MCP.
 */
export async function mcpCall(method, params = {}) {
  const apiKey = requireEnv("POND3R_API_KEY");
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json, text/event-stream",
    Authorization: `Bearer ${apiKey}`,
  };
  if (_sessionId) {
    headers["Mcp-Session-Id"] = _sessionId;
  }

  const body = {
    jsonrpc: "2.0",
    id: Date.now(),
    method,
    params,
  };

  const res = await fetch(MCP_URL, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  const sessionId = res.headers.get("Mcp-Session-Id");
  if (sessionId) _sessionId = sessionId;

  const text = await res.text();
  const contentType = res.headers.get("content-type") || "";
  if (!res.ok) {
    throw new Error(`Pond3r MCP HTTP ${res.status}: ${text}`);
  }

  const data = parseMcpResponse(text, contentType);

  if (data.error) {
    throw new Error(`Pond3r MCP error: ${data.error.message || JSON.stringify(data.error)}`);
  }

  return data.result;
}

/**
 * Call a tool by name with arguments
 */
export async function callTool(name, args = {}) {
  const result = await mcpCall("tools/call", { name, arguments: args });
  return result;
}

/**
 * Pond3r often returns structured JSON embedded as text in result.content[0].text.
 * This unwraps that shape when possible for easier downstream consumption.
 */
export function normalizeToolResult(result) {
  const text = result?.content?.[0]?.text;
  if (typeof text !== "string") return result;
  const trimmed = text.trim();
  if (!trimmed.startsWith("{") && !trimmed.startsWith("[")) return result;
  try {
    return JSON.parse(trimmed);
  } catch {
    return result;
  }
}
