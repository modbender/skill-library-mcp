/**
 * Central config from environment.
 * Load dotenv in the app entry (e.g. index.ts) before importing modules that use config.
 */

function env(key: string): string | undefined {
  return process.env[key];
}

function envNum(key: string, defaultVal: number): number {
  const raw = process.env[key];
  if (raw === undefined || raw === "") return defaultVal;
  const n = parseInt(raw, 10);
  return Number.isNaN(n) ? defaultVal : n;
}

/** Server port. */
export const port = envNum("PORT", 3001);

/** OpenAI: API key, optional base URL, model name. */
export const openai = {
  get apiKey(): string | undefined {
    return env("OPENAI_API_KEY");
  },
  get baseURL(): string | undefined {
    return env("OPENAI_BASE_URL");
  },
  get model(): string {
    return env("OPENAI_MODEL") ?? "gpt-4o";
  },
} as const;

/** PICUI image hosting: token for uploads (from https://picui.cn personal center). */
export const picui = {
  get token(): string | undefined {
    return env("PICUI_TOKEN");
  },
  get baseURL(): string {
    return "https://picui.cn/api/v1";
  },
} as const;

/** Agent names for getMaxTokens(); env keys are AGENT_<NAME>_MAX_TOKENS (e.g. AGENT_ORCHESTRATOR_MAX_TOKENS). */
export const AgentName = {
  Canvas: "canvas",
  Design: "design",
  Orchestrator: "orchestrator",
  Verification: "verification",
} as const;

export type AgentName = (typeof AgentName)[keyof typeof AgentName];

/**
 * Agent max_tokens: optional cap per agent or globally.
 * - AGENT_MAX_TOKENS: global default (unset = unlimited).
 * - AGENT_<NAME>_MAX_TOKENS: per-agent override (e.g. AGENT_ORCHESTRATOR_MAX_TOKENS).
 */
export function getMaxTokens(agent?: AgentName | string): number | undefined {
  const agentKey =
    agent && agent.length > 0
      ? `AGENT_${agent.toUpperCase()}_MAX_TOKENS`
      : null;
  const raw =
    (agentKey != null && process.env[agentKey]) || process.env.AGENT_MAX_TOKENS;
  if (raw === undefined || raw === "") return undefined;
  const n = parseInt(raw, 10);
  if (Number.isNaN(n) || n <= 0) return undefined;
  return n;
}
