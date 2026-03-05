/**
 * Maps between OpenClaw model references ("provider/model") and
 * Kalibr model IDs (just the model slug, e.g. "claude-sonnet-4-5").
 *
 * Kalibr's decide() returns model_id without a provider prefix.
 * OpenClaw's modelOverride wants the model slug, providerOverride
 * wants the provider name. So we need to infer provider from model_id.
 */

// ── Provider inference from model name patterns ────────────
// Order matters: more specific patterns first.

const PROVIDER_PATTERNS: Array<{ prefix: string; provider: string }> = [
  { prefix: "claude-", provider: "anthropic" },
  { prefix: "gpt-", provider: "openai" },
  { prefix: "o1-", provider: "openai" },
  { prefix: "o3-", provider: "openai" },
  { prefix: "o4-", provider: "openai" },
  { prefix: "chatgpt-", provider: "openai" },
  { prefix: "gemini-", provider: "google" },
  { prefix: "gemma-", provider: "google" },
  { prefix: "mistral-", provider: "mistral" },
  { prefix: "mixtral-", provider: "mistral" },
  { prefix: "codestral-", provider: "mistral" },
  { prefix: "llama", provider: "meta" },
  { prefix: "command-", provider: "cohere" },
  { prefix: "deepseek-", provider: "deepseek" },
];

/**
 * Infer the provider from a Kalibr model_id based on known naming patterns.
 * Returns null if no pattern matches.
 */
export function inferProvider(modelId: string): string | null {
  const lower = modelId.toLowerCase();
  for (const { prefix, provider } of PROVIDER_PATTERNS) {
    if (lower.startsWith(prefix)) return provider;
  }
  return null;
}

// ── Explicit lookup table for known mappings ───────────────

const OPENCLAW_TO_KALIBR: Record<string, string> = {
  "anthropic/claude-opus-4-6": "claude-opus-4-6",
  "anthropic/claude-sonnet-4-5": "claude-sonnet-4-5",
  "openai/gpt-5.2": "gpt-5.2",
  "openai/gpt-5.2-mini": "gpt-5.2-mini",
  "openai/gpt-5.1-codex": "gpt-5.1-codex",
};

const KALIBR_TO_OPENCLAW = Object.fromEntries(
  Object.entries(OPENCLAW_TO_KALIBR).map(([k, v]) => [v, k]),
);

/**
 * Convert an OpenClaw model reference ("provider/model") to a Kalibr model ID.
 * Known models are mapped explicitly; unknown models strip the provider prefix.
 */
export function openClawToKalibr(openClawRef: string): string {
  if (OPENCLAW_TO_KALIBR[openClawRef]) return OPENCLAW_TO_KALIBR[openClawRef];
  const parts = openClawRef.split("/");
  return parts.length > 1 ? parts.slice(1).join("/") : openClawRef;
}

/**
 * Convert a Kalibr model_id to { provider, model } for OpenClaw overrides.
 *
 * Resolution order:
 * 1. Explicit lookup table (exact match)
 * 2. If model_id already contains "/" — split directly
 * 3. Infer provider from model name patterns
 * 4. Return null if provider cannot be determined
 */
export function kalibrToOpenClaw(kalibrModelId: string): { provider: string; model: string } | null {
  // 1. Explicit lookup
  const explicit = KALIBR_TO_OPENCLAW[kalibrModelId];
  if (explicit) {
    const [provider, ...modelParts] = explicit.split("/");
    return { provider, model: modelParts.join("/") };
  }

  // 2. Already has provider prefix
  if (kalibrModelId.includes("/")) {
    const [provider, ...modelParts] = kalibrModelId.split("/");
    return { provider, model: modelParts.join("/") };
  }

  // 3. Infer provider from naming pattern
  const provider = inferProvider(kalibrModelId);
  if (provider) {
    return { provider, model: kalibrModelId };
  }

  // 4. Unknown
  return null;
}
