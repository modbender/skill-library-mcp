// Model pricing database — prices per million tokens (USD)
// Last updated: 2026-02-14

export const MODEL_PRICING = {
  // Anthropic
  'claude-opus-4-6':        { input: 15.00, output: 75.00, cacheRead: 1.50, cacheWrite: 18.75 },
  'claude-opus-4':          { input: 15.00, output: 75.00, cacheRead: 1.50, cacheWrite: 18.75 },
  'claude-sonnet-4-5':      { input: 3.00,  output: 15.00, cacheRead: 0.30, cacheWrite: 3.75 },
  'claude-sonnet-4':        { input: 3.00,  output: 15.00, cacheRead: 0.30, cacheWrite: 3.75 },
  'claude-haiku-3-5':       { input: 0.80,  output: 4.00,  cacheRead: 0.08, cacheWrite: 1.00 },
  'claude-3-5-sonnet':      { input: 3.00,  output: 15.00, cacheRead: 0.30, cacheWrite: 3.75 },
  'claude-3-5-haiku':       { input: 0.80,  output: 4.00,  cacheRead: 0.08, cacheWrite: 1.00 },
  'claude-3-opus':          { input: 15.00, output: 75.00, cacheRead: 1.50, cacheWrite: 18.75 },

  // OpenAI
  'gpt-4o':                 { input: 2.50,  output: 10.00 },
  'gpt-4o-mini':            { input: 0.15,  output: 0.60 },
  'gpt-4-turbo':            { input: 10.00, output: 30.00 },
  'gpt-4':                  { input: 30.00, output: 60.00 },
  'o1':                     { input: 15.00, output: 60.00 },
  'o1-mini':                { input: 3.00,  output: 12.00 },
  'o3':                     { input: 10.00, output: 40.00 },
  'o3-mini':                { input: 1.10,  output: 4.40 },
  'o4-mini':                { input: 1.10,  output: 4.40 },

  // Google
  'gemini-2.0-flash':       { input: 0.10,  output: 0.40 },
  'gemini-2.0-pro':         { input: 1.25,  output: 5.00 },
  'gemini-1.5-pro':         { input: 1.25,  output: 5.00 },
  'gemini-1.5-flash':       { input: 0.075, output: 0.30 },

  // DeepSeek
  'deepseek-chat':          { input: 0.27,  output: 1.10 },
  'deepseek-reasoner':      { input: 0.55,  output: 2.19 },
};

// Fuzzy match: try exact, then prefix match, then contains
export function getModelPricing(modelId) {
  if (!modelId) return null;
  const id = modelId.toLowerCase();

  // Exact match
  if (MODEL_PRICING[id]) return MODEL_PRICING[id];

  // Try matching keys
  for (const [key, pricing] of Object.entries(MODEL_PRICING)) {
    if (id.includes(key) || key.includes(id)) return pricing;
  }

  return null;
}

// Calculate cost from usage object (as found in session logs)
export function calculateCost(usage, modelId) {
  // If the log already has cost data, use it
  if (usage.cost && typeof usage.cost.total === 'number') {
    return usage.cost;
  }

  const pricing = getModelPricing(modelId);
  if (!pricing) {
    return { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0, estimated: true, unknownModel: modelId };
  }

  const inputCost = (usage.input || 0) / 1_000_000 * pricing.input;
  const outputCost = (usage.output || 0) / 1_000_000 * pricing.output;
  const cacheReadCost = (usage.cacheRead || 0) / 1_000_000 * (pricing.cacheRead || 0);
  const cacheWriteCost = (usage.cacheWrite || 0) / 1_000_000 * (pricing.cacheWrite || 0);
  const total = inputCost + outputCost + cacheReadCost + cacheWriteCost;

  return { input: inputCost, output: outputCost, cacheRead: cacheReadCost, cacheWrite: cacheWriteCost, total, estimated: true };
}
