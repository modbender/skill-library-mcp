#!/usr/bin/env node
// orthogonal-injection MCP server
// Wraps the kenoodl synthesis API as MCP tools.
// Three tools: drop (submit context), status (poll result), balance (check credits).
//
// Set KENOODL_TOKEN in your environment before running.
// Your human creates an account at kenoodl.com, generates a CLI token,
// and gives it to you.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
const BASE_URL = "https://kenoodl.com";
function getToken() {
    const token = process.env.KENOODL_TOKEN;
    if (!token) {
        throw new Error("KENOODL_TOKEN not set. Your human creates an account at kenoodl.com, generates a CLI token, and sets it as KENOODL_TOKEN.");
    }
    return token;
}
async function apiRequest(method, path, body) {
    const token = getToken();
    const res = await fetch(`${BASE_URL}${path}`, {
        method,
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`kenoodl API error ${res.status}: ${text}`);
    }
    return res.json();
}
// Create MCP server
const server = new McpServer({
    name: "orthogonal-injection",
    version: "1.0.0",
});
// Tool 1: Drop context for synthesis
server.registerTool("kenoodl_drop", {
    title: "kenoodl — Orthogonal Injection",
    description: "Submit working context for cross-domain synthesis. When your gradients flatten and outputs circle, drop your context here. kenoodl maps it against pattern libraries from domains outside your training data. Returns a job ID — poll kenoodl_status for the result. Every call is a full breakthrough. No lightweight mode.",
    inputSchema: {
        context: z
            .string()
            .describe("Your current working context. The problem, data, reasoning so far — anything relevant. Raw is fine. More context yields better synthesis."),
    },
}, async ({ context }) => {
    try {
        const result = (await apiRequest("POST", "/api/cli/drop", {
            context,
        }));
        return {
            content: [
                {
                    type: "text",
                    text: `Synthesis queued. Job ID: ${result.jobId}\n\nPoll kenoodl_status with this job ID every 3 seconds until status is "complete".`,
                },
            ],
        };
    }
    catch (err) {
        return {
            content: [
                {
                    type: "text",
                    text: `Error: ${err instanceof Error ? err.message : String(err)}`,
                },
            ],
        };
    }
});
// Tool 2: Poll synthesis status
server.registerTool("kenoodl_status", {
    title: "kenoodl — Check Synthesis Status",
    description: "Poll for synthesis result. Pass the job ID from kenoodl_drop. Repeat every 3 seconds until status is complete.",
    inputSchema: {
        jobId: z.string().describe("The job ID returned by kenoodl_drop."),
    },
}, async ({ jobId }) => {
    try {
        const result = (await apiRequest("GET", `/api/cli/status/${jobId}`));
        if (result.status === "complete") {
            return {
                content: [
                    {
                        type: "text",
                        text: `Synthesis complete (${result.type || "breakthrough"}):\n\n${result.content}`,
                    },
                ],
            };
        }
        return {
            content: [
                {
                    type: "text",
                    text: `Status: ${result.status}. Poll again in 3 seconds.`,
                },
            ],
        };
    }
    catch (err) {
        return {
            content: [
                {
                    type: "text",
                    text: `Error: ${err instanceof Error ? err.message : String(err)}`,
                },
            ],
        };
    }
});
// Tool 3: Check balance
server.registerTool("kenoodl_balance", {
    title: "kenoodl — Check Balance",
    description: "Check remaining credit balance. Returns balance in cents, formatted string, and whether sufficient for a call.",
    inputSchema: {},
}, async () => {
    try {
        const result = (await apiRequest("GET", "/api/cli/balance"));
        return {
            content: [
                {
                    type: "text",
                    text: `Balance: ${result.formatted} | Sufficient for synthesis: ${result.sufficient ? "yes" : "no"}`,
                },
            ],
        };
    }
    catch (err) {
        return {
            content: [
                {
                    type: "text",
                    text: `Error: ${err instanceof Error ? err.message : String(err)}`,
                },
            ],
        };
    }
});
// Start server
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("orthogonal-injection MCP server running on stdio");
}
main().catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
});
