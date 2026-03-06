/**
 * Provider registry and resolver.
 * Supports Kimi, Claude Code, and OpenCode CLIs.
 */

import type { CLIProvider, ProviderId } from "./types.js";
import { kimiProvider } from "./kimi.js";
import { claudeProvider } from "./claude.js";
import { opencodeProvider } from "./opencode.js";
import type { OpenClawConfig } from "../config.js";

/** All valid provider IDs */
export const VALID_PROVIDER_IDS: ProviderId[] = ["kimi", "claude", "opencode"];

/** Map of provider ID to provider instance */
const providerMap: Map<ProviderId, CLIProvider> = new Map([
  ["kimi", kimiProvider as CLIProvider],
  ["claude", claudeProvider as CLIProvider],
  ["opencode", opencodeProvider as CLIProvider],
]);

/**
 * Get a provider by ID.
 * @param id - Provider ID (kimi, claude, opencode)
 * @returns The provider instance
 * @throws Error if provider ID is unknown
 */
export function getProvider(id: ProviderId): CLIProvider {
  const provider = providerMap.get(id);
  if (!provider) {
    throw new Error(
      `Unknown provider: ${id}. Valid providers: ${VALID_PROVIDER_IDS.join(", ")}`
    );
  }
  return provider;
}

/**
 * Check if a string is a valid provider ID.
 * @param id - String to check
 * @returns True if valid provider ID
 */
export function isValidProviderId(id: string): id is ProviderId {
  return VALID_PROVIDER_IDS.includes(id as ProviderId);
}

/**
 * Resolve provider ID from various sources (in order of precedence):
 * 1. CLI flag (--provider)
 * 2. Environment variable (OPENCLAW_CLI_PROVIDER)
 * 3. Config file (cliWorker.provider or skills['cli-worker'].provider)
 * 4. Default (kimi)
 *
 * @param config - OpenClaw configuration object
 * @param cliFlag - Optional --provider value from CLI args
 * @returns Resolved ProviderId
 */
export function resolveProviderId(
  config: OpenClawConfig,
  cliFlag?: string
): ProviderId {
  // 1. CLI flag takes highest precedence
  if (cliFlag && isValidProviderId(cliFlag)) {
    return cliFlag;
  }

  // 2. Environment variable
  const envProvider = process.env.OPENCLAW_CLI_PROVIDER;
  if (envProvider && isValidProviderId(envProvider)) {
    return envProvider;
  }

  // 3. Config file - check both possible locations
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const cliWorkerConfig = (config as any).cliWorker;
  if (
    cliWorkerConfig?.provider &&
    isValidProviderId(cliWorkerConfig.provider)
  ) {
    return cliWorkerConfig.provider;
  }

  // Check skills['cli-worker'] path
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const skillsConfig = (config as any).skills;
  const skillConfig = skillsConfig?.["cli-worker"];
  if (skillConfig?.provider && isValidProviderId(skillConfig.provider)) {
    return skillConfig.provider;
  }

  // 4. Default to kimi
  return "kimi";
}

/**
 * Get a provider resolved from configuration.
 * Convenience function that combines resolveProviderId and getProvider.
 *
 * @param config - OpenClaw configuration object
 * @param cliFlag - Optional --provider value from CLI args
 * @returns The resolved provider instance
 */
export function getProviderFromConfig(
  config: OpenClawConfig,
  cliFlag?: string
): CLIProvider {
  const id = resolveProviderId(config, cliFlag);
  return getProvider(id);
}

export { kimiProvider, claudeProvider, opencodeProvider };
export * from "./types.js";
