import pluginManifest from "../openclaw.plugin.json";
export { ISPConfigError, ISPConfigErrorCode, normalizeError } from "./errors";
import { createTools } from "./tools";
import { ISPConfigPluginConfig, JsonMap } from "./types";

export interface OpenClawRuntimeLike {
  registerTool: (name: string, definition: { description: string; run: (params: JsonMap) => Promise<unknown> }) => void;
}

function ensureConfig(config: Partial<ISPConfigPluginConfig>): ISPConfigPluginConfig {
  if (!config.apiUrl || !config.username || !config.password) {
    throw new Error("Missing required config: apiUrl, username, password");
  }

  return {
    apiUrl: config.apiUrl,
    username: config.username,
    password: config.password,
    serverId: config.serverId ?? 1,
    defaultServerIp: config.defaultServerIp,
    readOnly: config.readOnly ?? false,
    allowedOperations: config.allowedOperations ?? [],
    verifySsl: config.verifySsl ?? true,
    timeoutMs: config.timeoutMs,
  };
}

export interface BoundTool {
  name: string;
  description: string;
  run: (params: JsonMap) => Promise<unknown>;
}

export function buildToolset(config: Partial<ISPConfigPluginConfig>): BoundTool[] {
  const safeConfig = ensureConfig(config);
  const context = { config: safeConfig };
  return createTools().map((tool) => ({
    name: tool.name,
    description: tool.description,
    run: (params: JsonMap) => tool.run(params, context),
  }));
}

export function registerAllTools(runtime: OpenClawRuntimeLike, config: Partial<ISPConfigPluginConfig>): void {
  const tools = buildToolset(config);
  for (const tool of tools) {
    runtime.registerTool(tool.name, {
      description: tool.description,
      run: (params: JsonMap) => tool.run(params),
    });
  }
}

const plugin = {
  manifest: pluginManifest,
  register: registerAllTools,
};

export default plugin;
