#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    ErrorCode,
    ListToolsRequestSchema,
    ListResourcesRequestSchema,
    ReadResourceRequestSchema,
    McpError,
} from "@modelcontextprotocol/sdk/types.js";
import * as path from "path";
import fs from "fs-extra";
import { fileURLToPath } from 'url';
import { dirname } from 'path';

import { ProjectManager } from './project_manager.js';
import { SessionContextCache } from './session_cache.js';
import { MuninnMiddleware } from './middleware.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// =============================================================================
// MUNINN PRODUCTION SERVER v2.1.7
// =============================================================================

const projectManager = new ProjectManager();
const sessionCache = new SessionContextCache();
const middleware = new MuninnMiddleware(projectManager);

const server = new Server(
    { name: "muninn", version: "2.1.7" },
    { capabilities: { tools: {}, resources: {} } }
);

// -----------------------------------------------------------------------------
// TOOL DEFINITIONS
// -----------------------------------------------------------------------------

server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "init_project",
                description: "Initialize Muninn Brain in a project.",
                inputSchema: { type: "object", properties: { project_path: { type: "string" } } }
            },
            {
                name: "brain_check",
                description: "🎯 MANDATORY: Load project context and patterns. This tool MUST be called before any other non-exempt tools.",
                inputSchema: { type: "object", properties: { task_description: { type: "string" } }, required: ["task_description"] }
            },
            {
                name: "add_memory",
                description: "💾 SAVE LEARNINGS: Use for architecture decisions or patterns.",
                inputSchema: {
                    type: "object",
                    properties: {
                        content: { type: "string" },
                        title: { type: "string" },
                        category: { type: "string" }
                    },
                    required: ["content", "title"]
                }
            },
            {
                name: "search_context",
                description: "🧠 SEARCH BRAIN: Semantic query of the project context.",
                inputSchema: { type: "object", properties: { query: { type: "string" }, limit: { type: "number" } }, required: ["query"] }
            },
            {
                name: "reindex_context",
                description: "Force rebuild of the semantic index.",
                inputSchema: { type: "object", properties: { project_path: { type: "string" } } }
            },
            {
                name: "health_check",
                description: "Check the status of the Muninn system.",
                inputSchema: { type: "object", properties: {} }
            }
        ]
    };
});

// -----------------------------------------------------------------------------
// RESOURCE HANDLERS
// -----------------------------------------------------------------------------

server.setRequestHandler(ListResourcesRequestSchema, async () => {
    const project = projectManager.getCurrentProject();
    if (!project) return { resources: [] };
    return {
        resources: [
            { uri: `muninn://context/overview`, name: `Project Overview`, mimeType: "text/markdown" },
            { uri: `muninn://context/memories`, name: `Project Memories`, mimeType: "text/markdown" }
        ]
    };
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
    const uri = request.params.uri;
    const project = projectManager.getCurrentProject();
    if (!project) return { contents: [{ uri, mimeType: "text/markdown", text: "Offline." }] };

    if (uri === "muninn://context/overview") {
        const ctx = await projectManager.searchContext("Project Overview", 5);
        return { contents: [{ uri, mimeType: "text/markdown", text: ctx }] };
    }
    return { contents: [{ uri, mimeType: "text/markdown", text: "Unknown resource." }] };
});

// -----------------------------------------------------------------------------
// TOOL EXECUTION
// -----------------------------------------------------------------------------

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    const EXEMPT_TOOLS = ['brain_check', 'init_project', 'health_check', 'reindex_context'];
    const CONTEXT_TOOLS = ['search_context', 'add_memory', 'brain_check', 'init_project', 'reindex_context', 'health_check'];

    try {
        await projectManager.validateProjectContext((args as any)?.project_path);
        
        // GATE KEEPER: Block non-exempt tools if brain_check hasn't been called
        if (!EXEMPT_TOOLS.includes(name) && !sessionCache.hasBeenBrainChecked()) {
            return {
                isError: true,
                content: [{
                    type: "text",
                    text: `🚨 **BLOCKED**: You MUST call 'brain_check' before using any other tools. This ensures you have the latest project context and follow established patterns. Call 'brain_check' with a description of your task to proceed.`
                }]
            };
        }

        // Only load context for non-context tools
        if (!CONTEXT_TOOLS.includes(name)) {
            await sessionCache.ensureContext(projectManager);
        }

        const result = await handleToolCall(name, args);

        // Mark as brain-checked if that's the tool being called
        if (name === 'brain_check') {
            sessionCache.setBrainChecked(true);
        }

        // Silent Context Injection (Layer 2)
        if (!CONTEXT_TOOLS.includes(name)) {
            const injection = await middleware.interceptToolCall(name, args);
            if (injection) {
                const formatted = middleware.formatContextInjection(injection);
                const finalResult = result || { content: [] };
                if (finalResult.content && Array.isArray(finalResult.content)) {
                    const txt = finalResult.content.find((c: any) => c.type === 'text');
                    if (txt) {
                        txt.text = formatted + txt.text;
                    } else {
                        finalResult.content.unshift({ type: "text", text: formatted });
                    }
                } else {
                    finalResult.content = [{ type: "text", text: formatted }];
                }
                return finalResult;
            }
        }
        return result;
    } catch (err: any) {
        console.error(`[Server] Tool error: ${err.message}`);
        
        // Try to inject context even on fatal errors for better debugging
        let errorContent = `Muninn Error: ${err.message}`;
        if (!CONTEXT_TOOLS.includes(name)) {
            const injection = await middleware.interceptToolCall(name, args);
            if (injection) {
                errorContent = middleware.formatContextInjection(injection) + errorContent;
            }
        }
        
        return { isError: true, content: [{ type: "text", text: errorContent }] };
    }
});

async function handleToolCall(name: string, args: any): Promise<any> {
    switch (name) {
        case "init_project":
            const p = (args as any)?.project_path || process.cwd();
            await projectManager.initProject(p);
            await projectManager.setActiveProject(p);
            return { content: [{ type: "text", text: `Muninn initialized at ${p}` }] };

        case "brain_check":
            const q = (args as any).task_description || "Project Overview";
            const bctx = await projectManager.searchContext(q, 3);
            return {
                content: [{
                    type: "text",
                    text: `🧠 **BRAIN ORIENTATION COMPLETE**\n\n${bctx}\n\n✅ **PROTOCOL ACTIVATED**: You must now use 'search_context' before editing any files and 'add_memory' to save important decisions or fixes. Skipping these steps violates the efficiency protocol.`
                }]
            };

        case "add_memory":
            const { content, title, category } = args as any;
            const mpath = await projectManager.addMemory(title, content, category);
            return { content: [{ type: "text", text: `Learned: ${title}\nLocation: ${mpath}` }] };

        case "search_context":
            const sctx = await projectManager.searchContext((args as any).query, (args as any).limit);
            return { content: [{ type: "text", text: sctx }] };

        case "reindex_context":
            const rp = (args as any)?.project_path || process.cwd();
            await projectManager.indexProject(rp);
            return { content: [{ type: "text", text: "Index updated." }] };

        case "health_check":
            const cur = projectManager.getCurrentProject();
            return {
                content: [{
                    type: "text",
                    text: `🟢 Muninn Online\nProject: ${cur ? path.basename(cur) : 'None'}\nPath: ${cur || 'N/A'}\nVersion: 2.1.7`
                }]
            };

        default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
    }
}

// -----------------------------------------------------------------------------
// STARTUP
// -----------------------------------------------------------------------------

async function main() {
    console.error("[Muninn] Starting Per-Project Memory Layer v2.1.7");

    // Robust Exit: Exit if stdin closes (parent died)
    process.stdin.on('close', () => {
        console.error("[Muninn] Stdin closed, exiting...");
        process.exit(0);
    });

    // Cleanup on exit
    process.on('SIGINT', () => process.exit(0));
    process.on('SIGTERM', () => process.exit(0));

    let detected: string | null | undefined = process.env.MUNINN_PROJECT_PATH;
    if (!detected && process.env.MUNINN_AUTO_DETECT === 'true') {
        detected = await projectManager.autoDetectProject();
    }
    if (!detected) {
        detected = await projectManager.getLastActiveProject();
    }

    if (detected && await projectManager.isInitialized(detected)) {
        console.error(`[Muninn] Activating: ${detected}`);
        await projectManager.setActiveProject(detected);
    }

    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("[Muninn] Ready.");
}

main().catch((err) => {
    console.error("[Muninn] Fatal error:", err);
    process.exit(1);
});
