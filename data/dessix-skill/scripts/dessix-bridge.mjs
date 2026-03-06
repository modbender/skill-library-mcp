#!/usr/bin/env node
import os from "node:os";
import path from "node:path";
import net from "node:net";
import fs from "node:fs";

function getDefaultBridgeEndpoint() {
    if (process.platform === "win32") {
        return "\\\\.\\pipe\\dessix-mcp-bridge";
    }
    return path.join(os.homedir(), ".dessix", "mcp", "dessix-mcp-bridge.sock");
}

function resolveBridgeEndpoint() {
    return process.env.DESSIX_MCP_BRIDGE_ENDPOINT?.trim() || getDefaultBridgeEndpoint();
}

function parseArgv(argv) {
    const [command, ...rest] = argv;
    const options = {};
    for (let i = 0; i < rest.length; i += 1) {
        const key = rest[i];
        if (key === "--") continue;
        const value = rest[i + 1];
        if (!key?.startsWith("--")) continue;
        const normalizedKey = key.slice(2);
        if (!normalizedKey) continue;
        if (!value || value === "--" || value.startsWith("--")) {
            options[normalizedKey] = "true";
            continue;
        }
        options[normalizedKey] = value;
        i += 1;
    }
    return {command, options};
}

function createRequest(command, options) {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    if (command === "health") {
        return {id, method: "health", params: {}};
    }
    if (command === "invoke") {
        const tool = String(options.tool || "").trim();
        if (!tool) {
            throw new Error("missing --tool for invoke");
        }
        let args = {};
        if (options.args) {
            try {
                args = JSON.parse(options.args);
            } catch {
                throw new Error("invalid JSON in --args");
            }
        }
        return {
            id,
            method: "invoke",
            params: {
                tool,
                args,
                requestId: options.requestId || `script-${id}`,
            },
        };
    }
    throw new Error("unknown command; use: health | invoke");
}

function getMcpScriptCandidates() {
    if (process.platform === "darwin") {
        return ["/Applications/Dessix.app/Contents/Resources/electron/compiled/dessix-mcp.js"];
    }
    if (process.platform === "win32") {
        return [
            path.join(
                process.env.LOCALAPPDATA || "",
                "Programs",
                "Dessix",
                "resources",
                "electron",
                "compiled",
                "dessix-mcp.js"
            ),
            path.join(
                process.env.USERPROFILE || "",
                "AppData",
                "Local",
                "Programs",
                "Dessix",
                "resources",
                "electron",
                "compiled",
                "dessix-mcp.js"
            ),
        ].filter(Boolean);
    }
    return [
        "/opt/Dessix/resources/electron/compiled/dessix-mcp.js",
        path.join(os.homedir(), ".local", "share", "Dessix", "resources", "electron", "compiled", "dessix-mcp.js"),
    ];
}

function resolveMcpScriptPath(explicitPath = "") {
    const envPath = process.env.DESSIX_MCP_SCRIPT_PATH?.trim();
    if (envPath && fs.existsSync(envPath)) {
        return envPath;
    }
    const normalizedExplicitPath = String(explicitPath || "").trim();
    if (normalizedExplicitPath && fs.existsSync(normalizedExplicitPath)) {
        return normalizedExplicitPath;
    }
    for (const candidate of getMcpScriptCandidates()) {
        if (candidate && fs.existsSync(candidate)) {
            return candidate;
        }
    }
    return "";
}

function bridgeRequest(endpoint, payload, timeoutMs = 5000) {
    return new Promise((resolve, reject) => {
        const socket = net.createConnection(endpoint);
        const timer = setTimeout(() => {
            socket.destroy();
            reject(new Error("BRIDGE_TIMEOUT"));
        }, timeoutMs);

        let buffer = "";
        let settled = false;

        const settle = (fn) => {
            if (settled) return;
            settled = true;
            clearTimeout(timer);
            socket.destroy();
            fn();
        };

        socket.on("connect", () => {
            socket.write(`${JSON.stringify(payload)}\n`);
        });

        socket.on("data", (chunk) => {
            buffer += chunk.toString("utf8");
            const newlineIndex = buffer.indexOf("\n");
            if (newlineIndex === -1) return;
            const line = buffer.slice(0, newlineIndex).trim();
            if (!line) return;
            try {
                const parsed = JSON.parse(line);
                settle(() => resolve(parsed));
            } catch {
                settle(() => reject(new Error("BRIDGE_BAD_RESPONSE")));
            }
        });

        socket.on("error", (error) => {
            settle(() => reject(error));
        });

        socket.on("end", () => {
            if (!settled) {
                settle(() => reject(new Error("BRIDGE_CLOSED")));
            }
        });
    });
}

function printUsage() {
    process.stdout.write(
        [
            "Usage:",
            "  node scripts/dessix-bridge.mjs health",
            "  node scripts/dessix-bridge.mjs locate-mcp-script",
            "  node scripts/dessix-bridge.mjs invoke --tool <tool_name> --args '<json>'",
            "",
            "Examples:",
            "  node scripts/dessix-bridge.mjs health",
            "  node scripts/dessix-bridge.mjs locate-mcp-script",
            "  node scripts/dessix-bridge.mjs invoke --tool dessix_list_workspaces --args '{}'",
            "  node scripts/dessix-bridge.mjs invoke --tool dessix_search_blocks --args '{\"query\":\"MCP\",\"limit\":5}'",
        ].join("\n")
    );
}

async function main() {
    const {command, options} = parseArgv(process.argv.slice(2));
    if (!command || command === "--help" || command === "-h" || command === "help") {
        printUsage();
        process.exit(0);
    }

    if (command === "locate-mcp-script") {
        const scriptPath = resolveMcpScriptPath(options.mcpScriptPath);
        if (!scriptPath) {
            throw new Error(
                "DESSIX_MCP_SCRIPT_NOT_FOUND (set DESSIX_MCP_SCRIPT_PATH or install Dessix desktop app)"
            );
        }
        process.stdout.write(
            `${JSON.stringify({ok: true, path: scriptPath, platform: process.platform}, null, 2)}\n`
        );
        process.exit(0);
    }

    const endpoint = resolveBridgeEndpoint();
    const payload = createRequest(command, options);
    const result = await bridgeRequest(endpoint, payload);
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);

    if (!result?.ok) {
        process.exit(1);
    }
    const bridgeResult = result?.result;
    if (bridgeResult && typeof bridgeResult === "object" && bridgeResult.ok === false) {
        process.exit(2);
    }
}

main().catch((error) => {
    process.stderr.write(`[dessix-bridge-script] ${error instanceof Error ? error.message : String(error)}\n`);
    process.exit(1);
});
