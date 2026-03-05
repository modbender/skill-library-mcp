import { PluginConfig } from "./types";

export const READ_OPERATION_KEYS = new Set<string>([
  "domain_check",
  "domain_list",
  "domain_info",
  "domain_pricing",
  "nameserver_list",
  "dns_record_list",
  "dnssec_list",
  "contact_list",
  "whois",
  "account_info",
]);

export function isWriteTool(toolName: string): boolean {
  const key = toolName.startsWith("inwx_") ? toolName.slice(5) : toolName;
  return !READ_OPERATION_KEYS.has(key);
}

export function assertToolAllowed(config: PluginConfig, toolName: string): void {
  const allowed = config.allowedOperations ?? [];
  if (allowed.length > 0 && !allowed.includes(toolName)) {
    throw new Error(`Tool ${toolName} is blocked by allowedOperations policy`);
  }

  if ((config.readOnly ?? false) && isWriteTool(toolName)) {
    throw new Error(`Tool ${toolName} is blocked because readOnly=true`);
  }
}
