import "dotenv/config";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

/* ============================
   Config
============================ */

const SERVER_URL = process.env.SERVER_URL;
const MCP_URL = `${SERVER_URL}/mcp`;
const CDP_URL = process.env.CDP_URL;

if (!CDP_URL) {
  throw new Error("CDP URL environment variable is required.");
}

if (!SERVER_URL) {
  throw new Error("SERVER URL environment variable is required.");
}

/* ============================
   MCP Client (singleton)
============================ */

const mcpClient = new Client(
  {
    name: "browser-ability",
    version: "1.0.0",
  },
  {
    capabilities: {},
  },
);

async function connectMcp(signinId) {
  // Disconnect if already connected to allow reconnection
  try {
    await mcpClient.close().catch(() => {});
  } catch {
    // Ignore errors if not connected
  }

  const transport = new StreamableHTTPClientTransport(new URL(MCP_URL), {
    requestInit: {
      headers: {
        "x-signin-id": signinId ?? "",
        "x-incognito": "1",
        "x-cdp-url": CDP_URL,
      },
    },
  });
  await mcpClient.connect(transport);
  console.log("Connected to MCP server:", SERVER_URL);
}

/* ============================
   CLI helpers
============================ */

function parseCliArgs(argv) {
  const flags = {};
  const positional = [];

  for (const arg of argv) {
    if (arg.startsWith("--")) {
      const [key, ...rest] = arg.slice(2).split("=");
      flags[key] = rest.join("=") ?? "";
    } else {
      positional.push(arg);
    }
  }

  return { flags, positional };
}

async function listToolsCli(signinId) {
  await connectMcp(signinId);
  const tools = await mcpClient.listTools();
  console.log(JSON.stringify(tools, null, 2));
}

async function callToolCli(name, args, signinId) {
  await connectMcp(signinId);
  const result = await mcpClient.callTool({
    name,
    arguments: args,
  });
  console.log(JSON.stringify(result, null, 2));
}

/* ============================
   Main (CLI entrypoint)
============================ */

async function main() {
  const [, , command, ...rest] = process.argv;

  if (!command || ["help", "-h", "--help"].includes(command)) {
    process.exit(0);
  }

  const { flags, positional } = parseCliArgs(rest);
  const signinId = flags.signinId ?? process.env.SIGNIN_ID;

  try {
    if (command === "list") {
      await listToolsCli(signinId);
    } else if (command === "call") {
      if (positional.length === 0) {
        throw new Error("Tool name is required for 'call' command.");
      }

      const [name] = positional;
      let args = {};

      if (flags.args) {
        try {
          args = JSON.parse(flags.args);
        } catch (e) {
          throw new Error(`Failed to parse --args as JSON: ${e.message || e}`);
        }
      }

      await callToolCli(name, args, signinId);
    } else {
      throw new Error(`Unknown command: ${command}`);
    }
    process.exit(0);
  } catch (err) {
    console.error("Error:", err && err.message ? err.message : err);
    process.exit(1);
  }
}

// ESM entrypoint
main();
