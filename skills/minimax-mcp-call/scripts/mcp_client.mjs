#!/usr/bin/env node
/**
 * MiniMax MCP Client - Direct protocol implementation
 * Communicates with minimax-coding-plan-mcp via JSON-RPC over stdio
 */

import { spawn } from "child_process";

const API_KEY = process.env.MINIMAX_API_KEY;
const API_HOST = process.env.MINIMAX_API_HOST || "https://api.minimaxi.com";

let mcpProcess = null;
let requestId = 0;
const pendingRequests = new Map();

// Initialize MCP server process
function initMcpServer() {
  return new Promise((resolve, reject) => {
    mcpProcess = spawn("uvx", ["minimax-coding-plan-mcp", "-y"], {
      env: {
        ...process.env,
        MINIMAX_API_KEY: API_KEY,
        MINIMAX_API_HOST: API_HOST,
      },
      stdio: ["pipe", "pipe", "pipe"],
    });

    let buffer = "";

    mcpProcess.stdout.on("data", (data) => {
      buffer += data.toString();
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (line.trim()) {
          try {
            const response = JSON.parse(line);
            handleResponse(response);
          } catch (e) {
            // Skip non-JSON lines
          }
        }
      }
    });

    mcpProcess.stderr.on("data", (data) => {
      console.error("MCP stderr:", data.toString());
    });

    mcpProcess.on("error", reject);
    mcpProcess.on("close", (code) => {
      console.log("MCP server closed with code:", code);
    });

    // Wait a bit for server to initialize
    setTimeout(() => resolve(), 2000);
  });
}

function handleResponse(response) {
  if (response.id !== undefined && pendingRequests.has(response.id)) {
    const { resolve } = pendingRequests.get(response.id);
    pendingRequests.delete(response.id);
    resolve(response.result || response);
  }
}

function sendRequest(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++requestId;
    const request = {
      jsonrpc: "2.0",
      id,
      method,
      params,
    };

    pendingRequests.set(id, { resolve, reject });
    mcpProcess.stdin.write(JSON.stringify(request) + "\n");

    // Timeout after 30 seconds
    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error("Request timeout"));
      }
    }, 30000);
  });
}

// MCP Tools
async function initialize() {
  const result = await sendRequest("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "minimax-mcp-client", version: "1.0.0" },
  });
  return result;
}

async function callTool(name, args) {
  return sendRequest("tools/call", {
    name,
    arguments: args,
  });
}

async function listTools() {
  return sendRequest("tools/list");
}

async function webSearch(query) {
  return callTool("web_search", { query });
}

async function understandImage(imageUrl, prompt) {
  return callTool("understand_image", { image_url: imageUrl, prompt });
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

async function main() {
  if (!API_KEY) {
    console.error("Error: MINIMAX_API_KEY not set");
    process.exit(1);
  }

  try {
    console.log("Starting MCP server...");
    await initMcpServer();
    console.log("MCP server ready");

    // Initialize
    await initialize();

    let result;
    switch (command) {
      case "web_search":
        result = await webSearch(args[1]);
        break;
      case "understand_image":
        result = await understandImage(args[1], args[2]);
        break;
      case "list":
        result = await listTools();
        break;
      default:
        console.log(`Usage: node mcp_client.mjs <web_search|understand_image|list> [args...]`);
        process.exit(1);
    }

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error("Error:", err.message);
    process.exit(1);
  } finally {
    if (mcpProcess) {
      mcpProcess.kill();
    }
  }
}

main();
