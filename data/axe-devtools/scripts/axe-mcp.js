#!/usr/bin/env node
// axe MCP Server wrapper — sends JSON-RPC requests over Docker stdio
// Usage: node axe-mcp.js analyze <url>
//        node axe-mcp.js remediate <ruleId> <elementHtml> <issueRemediation> [pageUrl]
//        node axe-mcp.js tools-list

const { spawn } = require("child_process");

const AXE_API_KEY = process.env.AXE_API_KEY;
if (!AXE_API_KEY) {
  console.error("Error: Set AXE_API_KEY environment variable");
  process.exit(1);
}

const DOCKER_IMAGE = "dequesystems/axe-mcp-server:latest";

const INIT = JSON.stringify({
  jsonrpc: "2.0",
  id: 1,
  method: "initialize",
  params: {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "openclaw", version: "1.0" },
  },
});

const INITIALIZED = JSON.stringify({
  jsonrpc: "2.0",
  method: "notifications/initialized",
});

function sendMcp(call) {
  return new Promise((resolve, reject) => {
    const dockerArgs = [
      "run", "-i", "--rm",
      "-e", `AXE_API_KEY=${AXE_API_KEY}`,
    ];
    if (process.env.AXE_SERVER_URL) {
      dockerArgs.push("-e", `AXE_SERVER_URL=${process.env.AXE_SERVER_URL}`);
    }
    dockerArgs.push(DOCKER_IMAGE);

    const proc = spawn("docker", dockerArgs, { stdio: ["pipe", "pipe", "pipe"] });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (d) => (stdout += d.toString()));
    proc.stderr.on("data", (d) => (stderr += d.toString()));

    proc.on("close", (code) => {
      if (code !== 0) {
        return reject(new Error(`Docker exited with code ${code}: ${stderr}`));
      }
      // Find the response line with id:2
      const lines = stdout.trim().split("\n");
      for (const line of lines) {
        try {
          const parsed = JSON.parse(line);
          if (parsed.id === 2) return resolve(parsed);
        } catch {}
      }
      reject(new Error(`No response found. stdout: ${stdout}`));
    });

    proc.on("error", reject);

    const messages = `${INIT}\n${INITIALIZED}\n${JSON.stringify(call)}\n`;
    proc.stdin.write(messages);
    proc.stdin.end();
  });
}

async function main() {
  const [, , command, ...args] = process.argv;

  let call;

  switch (command) {
    case "analyze": {
      const url = args[0];
      if (!url) {
        console.error("Usage: axe-mcp.js analyze <url>");
        process.exit(1);
      }
      call = {
        jsonrpc: "2.0",
        id: 2,
        method: "tools/call",
        params: { name: "analyze", arguments: { url } },
      };
      break;
    }

    case "remediate": {
      const [ruleId, elementHtml, issueRemediation, pageUrl] = args;
      if (!ruleId || !elementHtml || !issueRemediation) {
        console.error(
          "Usage: axe-mcp.js remediate <ruleId> <elementHtml> <issueRemediation> [pageUrl]"
        );
        process.exit(1);
      }
      const remArgs = { ruleId, elementHtml, issueRemediation };
      if (pageUrl) remArgs.pageUrl = pageUrl;
      call = {
        jsonrpc: "2.0",
        id: 2,
        method: "tools/call",
        params: { name: "remediate", arguments: remArgs },
      };
      break;
    }

    case "tools-list": {
      call = {
        jsonrpc: "2.0",
        id: 2,
        method: "tools/list",
        params: {},
      };
      break;
    }

    default:
      console.error("Usage: axe-mcp.js {analyze|remediate|tools-list} [args...]");
      process.exit(1);
  }

  try {
    const response = await sendMcp(call);
    console.log(JSON.stringify(response, null, 2));
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
