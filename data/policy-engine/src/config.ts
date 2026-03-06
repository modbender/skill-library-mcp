/**
 * Policy engine configuration types, defaults, and validation.
 */

export type RiskTier = "T0" | "T1" | "T2";

export type RoutingRule = {
  model?: string;
  toolProfile?: string;
};

export type PolicyConfig = {
  enabled: boolean;
  dryRun: boolean;
  dryRunAllowT0: boolean;
  dryRunEssentialTools: string[];
  maxBlockedRetries: number;
  riskTiers: Record<string, RiskTier>;
  denyPatterns: Record<string, string[]>;
  allowlists: Record<string, string[]>;
  routing: Record<string, RoutingRule>;
  pathAllowlists: Record<string, string[]>;
};

/**
 * Essential tools that MUST always work, even in dry-run mode.
 * Without these, the agent cannot communicate or fix its own config.
 * This is the "control plane" — blocking it creates an unrecoverable deadlock.
 */
const DEFAULT_ESSENTIAL_TOOLS: string[] = [
  "message",         // agent must be able to talk to users
  "gateway",         // agent must be able to patch config / restart
  "session_status",  // agent must be able to check its own state
  "sessions_send",   // agent must be able to message other sessions
  "sessions_list",   // agent must be able to list sessions
  "tts",             // voice replies should not be blocked
];

export const DEFAULT_CONFIG: PolicyConfig = {
  enabled: true,
  dryRun: false,
  dryRunAllowT0: true,
  dryRunEssentialTools: DEFAULT_ESSENTIAL_TOOLS,
  maxBlockedRetries: 3,
  riskTiers: {},
  denyPatterns: {},
  allowlists: {},
  routing: {},
  pathAllowlists: {},
};

const VALID_TIERS = new Set<string>(["T0", "T1", "T2"]);

export function resolveConfig(raw: Record<string, unknown> | undefined): PolicyConfig {
  if (!raw) {
    return { ...DEFAULT_CONFIG };
  }

  const config: PolicyConfig = {
    enabled: typeof raw.enabled === "boolean" ? raw.enabled : DEFAULT_CONFIG.enabled,
    dryRun: typeof raw.dryRun === "boolean" ? raw.dryRun : DEFAULT_CONFIG.dryRun,
    dryRunAllowT0:
      typeof raw.dryRunAllowT0 === "boolean" ? raw.dryRunAllowT0 : DEFAULT_CONFIG.dryRunAllowT0,
    dryRunEssentialTools: resolveStringArray(raw.dryRunEssentialTools, DEFAULT_ESSENTIAL_TOOLS),
    maxBlockedRetries:
      typeof raw.maxBlockedRetries === "number" && raw.maxBlockedRetries > 0
        ? raw.maxBlockedRetries
        : DEFAULT_CONFIG.maxBlockedRetries,
    riskTiers: resolveRiskTiers(raw.riskTiers),
    denyPatterns: resolveDenyPatterns(raw.denyPatterns),
    allowlists: resolveAllowlists(raw.allowlists),
    routing: resolveRouting(raw.routing),
    pathAllowlists: resolvePathAllowlists(raw.pathAllowlists),
  };

  return config;
}

function resolveStringArray(raw: unknown, fallback: string[]): string[] {
  if (!Array.isArray(raw)) {
    return [...fallback];
  }
  const filtered = raw.filter((v): v is string => typeof v === "string");
  return filtered.length > 0 ? filtered : [...fallback];
}

function resolveRiskTiers(raw: unknown): Record<string, RiskTier> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return {};
  }
  const result: Record<string, RiskTier> = {};
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    if (typeof value === "string" && VALID_TIERS.has(value)) {
      result[key] = value as RiskTier;
    }
  }
  return result;
}

function resolveDenyPatterns(raw: unknown): Record<string, string[]> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return {};
  }
  const result: Record<string, string[]> = {};
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    if (Array.isArray(value)) {
      result[key] = value.filter((v): v is string => typeof v === "string");
    }
  }
  return result;
}

function resolveAllowlists(raw: unknown): Record<string, string[]> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return {};
  }
  const result: Record<string, string[]> = {};
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    if (Array.isArray(value)) {
      result[key] = value.filter((v): v is string => typeof v === "string");
    }
  }
  return result;
}

function resolvePathAllowlists(raw: unknown): Record<string, string[]> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return {};
  }
  const result: Record<string, string[]> = {};
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    if (Array.isArray(value)) {
      result[key] = value.filter((v): v is string => typeof v === "string");
    }
  }
  return result;
}

function resolveRouting(raw: unknown): Record<string, RoutingRule> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return {};
  }
  const result: Record<string, RoutingRule> = {};
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    if (value && typeof value === "object" && !Array.isArray(value)) {
      const rule = value as Record<string, unknown>;
      const entry: RoutingRule = {};
      if (typeof rule.model === "string") entry.model = rule.model;
      if (typeof rule.toolProfile === "string") entry.toolProfile = rule.toolProfile;
      result[key] = entry;
    }
  }
  return result;
}
