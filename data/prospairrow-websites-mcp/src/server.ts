import http from "node:http";
import path from "node:path";
import { bootstrapLogin, listSites, runTask } from "./framework/service.js";

const PORT = 8799;
const rootDir = path.resolve(process.cwd());

type JsonRpcRequest = {
  jsonrpc: "2.0";
  id?: string | number | null;
  method: string;
  params?: Record<string, unknown>;
};

type RequestMeta = {
  apiKey?: string;
};

function rpcResult(id: JsonRpcRequest["id"], result: unknown) {
  return { jsonrpc: "2.0", id: id ?? null, result };
}

function rpcError(id: JsonRpcRequest["id"], code: number, message: string) {
  return { jsonrpc: "2.0", id: id ?? null, error: { code, message } };
}

const tools = [
  {
    name: "websites.list_sites",
    description: "List registered websites and available tasks."
  },
  {
    name: "websites.bootstrap_login",
    description: "Launch headed browser for manual login and save storage state."
  },
  {
    name: "websites.run_task",
    description: "Run a declared task for a declared site with capability/domain policy checks."
  }
] as const;

async function dispatchTool(name: string, args: Record<string, unknown> = {}, meta: RequestMeta = {}): Promise<unknown> {
  if (name === "websites.list_sites") {
    const reg = await listSites(rootDir);
    return {
      policy: reg.policy,
      sites: reg.sites.map((s) => ({
        siteId: s.siteId,
        baseUrl: s.baseUrl,
        allowedHosts: s.allowedHosts,
        capabilities: s.capabilities,
        tasks: s.tasks.map((t) => ({
          taskId: t.taskId,
          capability: t.capability,
          description: t.description
        }))
      }))
    };
  }

  if (name === "websites.bootstrap_login") {
    const siteId = String(args.siteId ?? "").trim();
    if (!siteId) throw new Error("siteId is required");
    return bootstrapLogin(rootDir, { siteId });
  }

  if (name === "websites.run_task") {
    const siteId = String(args.siteId ?? "").trim();
    const taskId = String(args.taskId ?? "").trim();
    if (!siteId || !taskId) throw new Error("siteId and taskId are required");
    const params = (args.params as Record<string, unknown> | undefined) ?? {};
    return runTask(rootDir, { siteId, taskId, params, apiKey: meta.apiKey });
  }

  throw new Error(`Unknown tool: ${name}`);
}

async function handleRpc(req: JsonRpcRequest, meta: RequestMeta): Promise<unknown> {
  if (req.method === "tools/list") {
    return tools;
  }

  if (req.method === "tools/call") {
    const name = String(req.params?.name ?? "");
    const args = (req.params?.arguments as Record<string, unknown> | undefined) ?? {};
    return dispatchTool(name, args, meta);
  }

  if (["websites.list_sites", "websites.bootstrap_login", "websites.run_task"].includes(req.method)) {
    return dispatchTool(req.method, req.params ?? {}, meta);
  }

  throw new Error(`Unsupported method: ${req.method}`);
}

const server = http.createServer(async (req, res) => {
  if (req.method !== "POST") {
    res.writeHead(405, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "Method not allowed" }));
    return;
  }

  const body = await new Promise<string>((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => {
      data += chunk;
    });
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });

  try {
    const payload = JSON.parse(body) as JsonRpcRequest;
    const authHeader = Array.isArray(req.headers.authorization) ? req.headers.authorization[0] : req.headers.authorization;
    const apiKeyHeader = Array.isArray(req.headers["x-api-key"]) ? req.headers["x-api-key"][0] : req.headers["x-api-key"];
    const bearer = typeof authHeader === "string" ? authHeader.match(/^Bearer\s+(.+)$/i)?.[1]?.trim() : "";
    const apiKey = (typeof apiKeyHeader === "string" && apiKeyHeader.trim()) || bearer || undefined;

    const result = await handleRpc(payload, { apiKey });
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify(rpcResult(payload.id, result)));
  } catch (error) {
    const msg = error instanceof Error ? error.message : String(error);
    let id: JsonRpcRequest["id"] = null;
    try {
      const parsed = JSON.parse(body) as JsonRpcRequest;
      id = parsed.id ?? null;
    } catch {
      id = null;
    }
    res.writeHead(400, { "content-type": "application/json" });
    res.end(JSON.stringify(rpcError(id, -32000, msg)));
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`websites-mcp server listening on http://127.0.0.1:${PORT}`);
});
