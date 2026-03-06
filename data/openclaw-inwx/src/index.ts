import pluginManifest from "../openclaw.plugin.json";
import { createTools } from "./tools";
import { JsonMap, OpenClawRuntimeLike, PluginConfig } from "./types";

export {
  provisionDomainWithHosting,
  ExternalBoundTool,
  ProvisionDomainHostingParams,
  ProvisioningResult,
  ProvisioningStep,
} from "./provisioning";

function ensureConfig(config: Partial<PluginConfig>): PluginConfig {
  if (!config.username || !config.password) {
    throw new Error("Missing required config: username, password");
  }

  return {
    username: config.username,
    password: config.password,
    otpSecret: config.otpSecret,
    environment: config.environment ?? "production",
    readOnly: config.readOnly ?? false,
    allowedOperations: config.allowedOperations ?? [],
  };
}

export interface BoundTool {
  name: string;
  description: string;
  run: (params: JsonMap) => Promise<unknown>;
}

export function buildToolset(config: Partial<PluginConfig>): BoundTool[] {
  const safeConfig = ensureConfig(config);
  const context = { config: safeConfig };
  return createTools().map((tool) => ({
    name: tool.name,
    description: tool.description,
    run: (params: JsonMap) => tool.run(params, context),
  }));
}

export function registerAllTools(runtime: OpenClawRuntimeLike, config: Partial<PluginConfig>): void {
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
