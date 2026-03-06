/**
 * OpenClaw Godot Plugin
 * Connects Godot 4.x Editor to OpenClaw AI assistant via HTTP
 */

import type { IncomingMessage, ServerResponse } from "node:http";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";

interface GodotSession {
  sessionId: string;
  registeredAt: number;
  lastHeartbeat: number;
  projectName: string;
  godotVersion: string;
  platform: string;
  toolCount: number;
  pendingCommands: Array<{
    toolCallId: string;
    tool: string;
    arguments: Record<string, any>;
    createdAt: number;
  }>;
  results: Map<string, any>;
}

// Store active Godot sessions
const sessions = new Map<string, GodotSession>();

// Generate unique ID
function generateId(): string {
  return `godot_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

// Clean up stale sessions (no heartbeat for 60 seconds)
function cleanupStaleSessions() {
  const now = Date.now();
  const staleThreshold = 120000; // 2 minutes
  
  for (const [id, session] of sessions) {
    if (now - session.lastHeartbeat > staleThreshold) {
      sessions.delete(id);
    }
  }
}

// Read JSON body from request
async function readJsonBody(req: IncomingMessage, maxBytes = 1024 * 1024): Promise<any> {
  const chunks: Buffer[] = [];
  let total = 0;
  
  return new Promise((resolve, reject) => {
    req.on("data", (chunk: Buffer) => {
      total += chunk.length;
      if (total > maxBytes) {
        reject(new Error("Payload too large"));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    
    req.on("end", () => {
      try {
        const raw = Buffer.concat(chunks).toString("utf8");
        if (!raw.trim()) {
          resolve({});
          return;
        }
        resolve(JSON.parse(raw));
      } catch (err) {
        reject(err);
      }
    });
    
    req.on("error", reject);
  });
}

// Send JSON response
function sendJson(res: ServerResponse, status: number, data: any) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.end(JSON.stringify(data));
}

// HTTP Handler for Godot endpoints
async function handleGodotHttpRequest(
  req: IncomingMessage,
  res: ServerResponse
): Promise<boolean> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const path = url.pathname;
  
  // Only handle /godot/* paths
  if (!path.startsWith("/godot/")) {
    return false;
  }
  
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
    res.statusCode = 204;
    res.end();
    return true;
  }
  
  const endpoint = path.replace("/godot/", "");
  
  try {
    switch (endpoint) {
      case "register": {
        if (req.method !== "POST") {
          sendJson(res, 405, { error: "Method not allowed" });
          return true;
        }
        
        const body = await readJsonBody(req);
        const { project, version, platform, tools } = body;
        
        const sessionId = generateId();
        const session: GodotSession = {
          sessionId,
          registeredAt: Date.now(),
          lastHeartbeat: Date.now(),
          projectName: project || "Unknown",
          godotVersion: version || "Unknown",
          platform: platform || "GodotEditor",
          toolCount: tools || 0,
          pendingCommands: [],
          results: new Map(),
        };
        
        sessions.set(sessionId, session);
        console.log(`[Godot] Registered: ${project} (${version}) - Session: ${sessionId}`);
        
        sendJson(res, 200, { sessionId, status: "connected" });
        return true;
      }
      
      case "heartbeat": {
        if (req.method !== "POST") {
          sendJson(res, 405, { error: "Method not allowed" });
          return true;
        }
        
        const body = await readJsonBody(req);
        const { sessionId } = body;
        
        const session = sessions.get(sessionId);
        if (!session) {
          sendJson(res, 404, { error: "Session not found" });
          return true;
        }
        
        session.lastHeartbeat = Date.now();
        sendJson(res, 200, { ok: true });
        return true;
      }
      
      case "poll": {
        const sessionId = url.searchParams.get("sessionId");
        
        const session = sessions.get(sessionId || "");
        if (!session) {
          sendJson(res, 404, { error: "Session not found" });
          return true;
        }
        
        session.lastHeartbeat = Date.now();
        
        // Return next pending command if any
        if (session.pendingCommands.length > 0) {
          const command = session.pendingCommands.shift()!;
          sendJson(res, 200, command);
        } else {
          // No content
          res.statusCode = 204;
          res.end();
        }
        return true;
      }
      
      case "result": {
        if (req.method !== "POST") {
          sendJson(res, 405, { error: "Method not allowed" });
          return true;
        }
        
        const body = await readJsonBody(req);
        const { sessionId, toolCallId, result } = body;
        
        const session = sessions.get(sessionId);
        if (!session) {
          sendJson(res, 404, { error: "Session not found" });
          return true;
        }
        
        session.results.set(toolCallId, result);
        console.log(`[Godot] Tool result received for: ${toolCallId}`);
        
        sendJson(res, 200, { ok: true });
        return true;
      }
      
      case "status": {
        const activeSessions = Array.from(sessions.values()).map(s => ({
          sessionId: s.sessionId,
          project: s.projectName,
          version: s.godotVersion,
          platform: s.platform,
          connectedAt: new Date(s.registeredAt).toISOString(),
          lastSeen: new Date(s.lastHeartbeat).toISOString(),
          pendingCommands: s.pendingCommands.length,
        }));
        
        sendJson(res, 200, {
          enabled: true,
          sessions: activeSessions,
          sessionCount: activeSessions.length,
        });
        return true;
      }
      
      default:
        sendJson(res, 404, { error: "Unknown endpoint" });
        return true;
    }
  } catch (err: any) {
    console.error("[Godot] HTTP error:", err);
    sendJson(res, 500, { error: err.message });
    return true;
  }
}

const plugin = {
  id: "godot",
  name: "Godot Plugin",
  description: "Connect Godot 4.x Editor to OpenClaw AI assistant",
  
  register(api: OpenClawPluginApi) {
    const logger = api.logger;
    
    // Cleanup timer
    setInterval(cleanupStaleSessions, 30000);
    
    // Register HTTP handler
    api.registerHttpHandler(handleGodotHttpRequest);
    
    // ===== Agent Tools =====
    
    // Tool: Execute a Godot command
    api.registerTool({
      name: "godot_execute",
      description: "Execute a tool in the connected Godot Editor. Available tools: scene.getCurrent, scene.list, scene.open, node.find, node.create, node.delete, node.getData, transform.setPosition, debug.tree, debug.screenshot, editor.play, editor.stop, editor.getState, script.list, script.read, resource.list, and more.",
      parameters: {
        type: "object" as const,
        properties: {
          tool: { type: "string" as const, description: "The Godot tool to execute (e.g., 'debug.tree', 'node.find')" },
          parameters: { type: "object" as const, description: "Parameters for the tool (varies by tool)" },
          sessionId: { type: "string" as const, description: "Optional: specific Godot session ID" },
        },
        required: ["tool"] as const,
      },
      execute: async (toolCallId: string, args: any) => {
        // Helper to format result for OpenClaw
        const jsonResult = (payload: any) => ({
          content: [{ type: "text", text: JSON.stringify(payload, null, 2) }],
          details: payload,
        });
        
        // Extract parameters
        const tool = args?.tool;
        const parameters = args?.parameters;
        const sessionId = args?.sessionId;
        
        if (!tool) {
          return jsonResult({
            success: false,
            error: "Missing 'tool' parameter. Specify which Godot tool to execute (e.g., 'debug.tree', 'node.find').",
          });
        }
        
        // Find session
        let session: GodotSession | undefined;
        
        if (sessionId) {
          session = sessions.get(sessionId);
        } else {
          // Use first active session
          const firstSession = sessions.values().next();
          session = firstSession.done ? undefined : firstSession.value;
        }
        
        if (!session) {
          return jsonResult({
            success: false,
            error: "No Godot session connected. Make sure Godot Editor is running with OpenClaw plugin enabled.",
          });
        }
        
        // Create command
        const requestId = generateId();
        session.pendingCommands.push({
          toolCallId: requestId,
          tool,
          arguments: parameters || {},
          createdAt: Date.now(),
        });
        
        logger.info(`[Godot] Queued command: ${tool} (request: ${requestId})`);
        
        // Wait for result (with timeout)
        const timeout = 60000; // 60 seconds
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
          if (session.results.has(requestId)) {
            const result = session.results.get(requestId);
            session.results.delete(requestId);
            
            return jsonResult({
              success: true,
              result,
            });
          }
          
          await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        return jsonResult({
          success: false,
          error: "Timeout waiting for Godot response. Make sure the OpenClaw plugin is enabled in Godot Editor.",
        });
      },
    });
    
    // Tool: List Godot sessions
    api.registerTool({
      name: "godot_sessions",
      description: "List all connected Godot Editor sessions",
      parameters: {
        type: "object" as const,
        properties: {
          _dummy: { type: "string" as const, description: "Unused parameter" },
        },
        required: [] as const,
      },
      execute: async (_toolCallId: string, _args: any) => {
        const activeSessions = Array.from(sessions.values()).map(s => ({
          sessionId: s.sessionId,
          project: s.projectName,
          version: s.godotVersion,
          platform: s.platform,
          tools: s.toolCount,
        }));
        
        const payload = {
          success: true,
          sessions: activeSessions,
          count: activeSessions.length,
        };
        
        return {
          content: [{ type: "text", text: JSON.stringify(payload, null, 2) }],
          details: payload,
        };
      },
    });
    
    // ===== CLI Commands =====
    
    api.registerCli(
      ({ program }) => {
        const godotCmd = program
          .command("godot")
          .description("Godot Plugin commands");
        
        godotCmd
          .command("status")
          .description("Show Godot connection status")
          .action(() => {
            console.log("\n🎮 Godot Plugin Status\n");
            
            if (sessions.size === 0) {
              console.log("  No Godot sessions connected.\n");
              console.log("  To connect Godot:");
              console.log("  1. Copy addons/openclaw to your project");
              console.log("  2. Enable the plugin in Project Settings > Plugins");
              console.log("  3. Check the OpenClaw dock panel\n");
              return;
            }
            
            for (const [id, session] of sessions) {
              const age = Math.round((Date.now() - session.registeredAt) / 1000);
              const lastSeen = Math.round((Date.now() - session.lastHeartbeat) / 1000);
              
              console.log(`  ✅ ${session.projectName}`);
              console.log(`     Version: ${session.godotVersion}`);
              console.log(`     Platform: ${session.platform}`);
              console.log(`     Session: ${id}`);
              console.log(`     Connected: ${age}s ago`);
              console.log(`     Last seen: ${lastSeen}s ago`);
              console.log(`     Pending: ${session.pendingCommands.length} commands\n`);
            }
          });
      },
      { commands: ["godot"] }
    );
    
    logger.info("[Godot] Plugin loaded - HTTP endpoints at /godot/*");
  },
};

export default plugin;
