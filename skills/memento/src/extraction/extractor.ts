/**
 * Fact Extractor — Provider-Agnostic
 *
 * Calls the configured LLM provider (Anthropic, OpenAI, Mistral, Ollama, or any
 * OpenAI-compatible endpoint) with a structured extraction prompt, then parses the
 * JSON response into typed ExtractedFact objects.
 *
 * The LLM is instructed to:
 *   - Return facts as a JSON array
 *   - Flag duplicates (duplicate_of + increment_occurrence)
 *   - Flag updates to existing facts (supersedes)
 *   - Assign visibility and sentiment
 *
 * Supported provider prefixes in the model string:
 *   - anthropic/<model>  → https://api.anthropic.com/v1/messages   (Anthropic format)
 *   - openai/<model>     → https://api.openai.com/v1/chat/completions (OpenAI format)
 *   - mistral/<model>    → https://api.mistral.ai/v1/chat/completions (OpenAI format)
 *   - ollama/<model>     → http://localhost:11434/api/chat           (Ollama format)
 *   - anything else      → OpenAI-compatible format (fallback)
 *
 * Credential resolution (in order):
 *   1. ANTHROPIC_API_KEY / OPENAI_API_KEY / MISTRAL_API_KEY / OLLAMA_API_KEY env vars
 *   2. Generic MEMENTO_API_KEY env var (for custom endpoints)
 *   Ollama requires no key (local model server).
 *
 * All API calls are best-effort: errors are returned, never thrown.
 */

import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { classifyVisibility } from "./classifier.js";
import { runViaOpenClaw } from "./embedded-runner.js";
import type { OpenClawConfig } from "./embedded-runner.js";
import type { FactRow, ConversationRow } from "../storage/schema.js";
import type { PluginLogger } from "../types.js";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export type ExtractedFactRelation = {
  /** ID of the related existing fact */
  target_id: string;
  /** Type of relation */
  relation_type: string; // 'related_to' | 'elaborates' | 'contradicts' | 'supports' | 'caused_by' | 'part_of' | 'precondition_of'
  /** Edge strength 0.0–1.0 (default 0.8) */
  strength: number;
};

export type ExtractedFact = {
  category: string;
  content: string;
  summary: string;
  visibility: string;
  confidence: number;
  sentiment: string;
  /** Set if this fact supersedes an existing one (its ID) */
  supersedes?: string;
  /** Set if this is a duplicate of an existing fact (its ID) */
  duplicate_of?: string;
  /** true when duplicate_of is set and occurrence should be incremented */
  increment_occurrence?: boolean;
  /** Relations to existing facts identified during extraction */
  relations?: ExtractedFactRelation[];
};

export type ExtractionResult = {
  facts: ExtractedFact[];
  modelUsed: string;
  error?: string;
};

// ---------------------------------------------------------------------------
// Extraction prompt — loaded from prompts/extraction.md at runtime
// Edit that file to tune extraction quality without recompiling.
// ---------------------------------------------------------------------------

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

function loadExtractionPrompt(): string {
  const promptPath = join(__dirname, '..', '..', 'prompts', 'extraction.md')
  try {
    const raw = readFileSync(promptPath, 'utf-8')
    // Extract the content between "## Prompt" and the trailing "## Conversation" section
    const match = raw.match(/## Prompt\n\n([\s\S]+?)\n---\n\n## Conversation/m)
    if (match) return match[1].trim() + '\n\nCONVERSATION:\n{{conversation}}'
    return raw
  } catch {
    throw new Error(`Extraction prompt not found at ${promptPath}`)
  }
}

const EXTRACTION_PROMPT = loadExtractionPrompt()


// ---------------------------------------------------------------------------
// Token budget helpers
// ---------------------------------------------------------------------------

/** Rough token estimate: ~4 chars per token (good enough for budget checks). */
function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4);
}

/**
 * Truncate a string to approximately `maxTokens` worth of content.
 * Truncates at a newline boundary to avoid cutting mid-sentence.
 */
function truncateToTokenBudget(text: string, maxTokens: number): string {
  const maxChars = maxTokens * 4;
  if (text.length <= maxChars) return text;
  const truncated = text.slice(0, maxChars);
  const lastNewline = truncated.lastIndexOf("\n");
  const cut = lastNewline > maxChars * 0.8 ? lastNewline : maxChars;
  return text.slice(0, cut) + "\n\n[... truncated for token budget ...]";
}

// ---------------------------------------------------------------------------
// Provider detection
// ---------------------------------------------------------------------------

type Provider = "anthropic" | "openai" | "mistral" | "ollama" | "openai-compat";

interface ProviderInfo {
  provider: Provider;
  /** Model name without the provider prefix */
  modelName: string;
  /** API endpoint URL */
  endpoint: string;
  /** ENV var name to look up for the API key */
  apiKeyEnv: string;
}

function detectProvider(model: string): ProviderInfo {
  const slashIdx = model.indexOf("/");
  const prefix = slashIdx !== -1 ? model.slice(0, slashIdx).toLowerCase() : "";
  const modelName = slashIdx !== -1 ? model.slice(slashIdx + 1) : model;

  switch (prefix) {
    case "anthropic":
      return {
        provider: "anthropic",
        modelName,
        endpoint: "https://api.anthropic.com/v1/messages",
        apiKeyEnv: "CLAUDE_CODE_OAUTH_TOKEN",
      };
    case "openai":
      return {
        provider: "openai",
        modelName,
        endpoint: "https://api.openai.com/v1/chat/completions",
        apiKeyEnv: "OPENAI_API_KEY",
      };
    case "mistral":
      return {
        provider: "mistral",
        modelName,
        endpoint: "https://api.mistral.ai/v1/chat/completions",
        apiKeyEnv: "MISTRAL_API_KEY",
      };
    case "ollama":
      return {
        provider: "ollama",
        modelName,
        // Ollama runs locally; no API key required
        endpoint: process.env.OLLAMA_BASE_URL ?? "http://localhost:11434/api/chat",
        apiKeyEnv: "OLLAMA_API_KEY", // optional; Ollama doesn't require one
      };
    default:
      // Unknown prefix — try OpenAI-compatible format as fallback
      return {
        provider: "openai-compat",
        modelName: model, // keep full string — user may know what endpoint expects
        endpoint: process.env.OPENAI_BASE_URL ?? "https://api.openai.com/v1/chat/completions",
        apiKeyEnv: "OPENAI_API_KEY",
      };
  }
}

// ---------------------------------------------------------------------------
// Credential resolution (no filesystem snooping)
// ---------------------------------------------------------------------------

/**
 * Resolve an API key for the given provider by checking environment variables.
 *
 * Priority:
 *   1. Provider-specific env var (e.g. ANTHROPIC_API_KEY)
 *   2. Generic MEMENTO_API_KEY fallback
 *   3. null — let the caller decide (Ollama doesn't need a key)
 */
function resolveApiKey(apiKeyEnv: string): string | null {
  return (
    process.env[apiKeyEnv] ||
    process.env.MEMENTO_API_KEY ||
    null
  );
}

// ---------------------------------------------------------------------------
// Provider-specific API callers
// ---------------------------------------------------------------------------

/** Call the Anthropic Messages API (native format). */
async function callAnthropic(
  info: ProviderInfo,
  apiKey: string,
  prompt: string,
): Promise<string> {
  const isOAuth = apiKey.includes("sk-ant-oat");
  const authHeaders: Record<string, string> = isOAuth
    ? {
        "Authorization": `Bearer ${apiKey}`,
        "anthropic-beta": "claude-code-20250219,oauth-2025-04-20",
      }
    : {
        "x-api-key": apiKey,
      };

  const response = await fetch(info.endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "anthropic-version": "2023-06-01",
      ...authHeaders,
    },
    body: JSON.stringify({
      model: info.modelName,
      max_tokens: 4096,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  if (!response.ok) {
    const errText = await response.text().catch(() => "(unreadable)");
    throw new Error(`Anthropic API error ${response.status}: ${errText.slice(0, 300)}`);
  }

  const data = (await response.json()) as any;
  // Anthropic format: { content: [{ type: "text", text: "..." }] }
  return data?.content?.[0]?.text ?? "";
}

/** Call an OpenAI-compatible API (OpenAI, Mistral, openai-compat). */
async function callOpenAICompat(
  info: ProviderInfo,
  apiKey: string | null,
  prompt: string,
): Promise<string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (apiKey) {
    headers["Authorization"] = `Bearer ${apiKey}`;
  }

  const response = await fetch(info.endpoint, {
    method: "POST",
    headers,
    body: JSON.stringify({
      model: info.modelName,
      max_tokens: 4096,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  if (!response.ok) {
    const errText = await response.text().catch(() => "(unreadable)");
    throw new Error(`${info.provider} API error ${response.status}: ${errText.slice(0, 300)}`);
  }

  const data = (await response.json()) as any;
  // OpenAI format: { choices: [{ message: { content: "..." } }] }
  return data?.choices?.[0]?.message?.content ?? "";
}

/** Call Ollama's native chat API. */
async function callOllama(
  info: ProviderInfo,
  prompt: string,
): Promise<string> {
  const response = await fetch(info.endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: info.modelName,
      messages: [{ role: "user", content: prompt }],
      stream: false,
    }),
  });

  if (!response.ok) {
    const errText = await response.text().catch(() => "(unreadable)");
    throw new Error(`Ollama API error ${response.status}: ${errText.slice(0, 300)}`);
  }

  const data = (await response.json()) as any;
  // Ollama format: { message: { content: "..." } }
  return data?.message?.content ?? "";
}

// ---------------------------------------------------------------------------
// Main extractor
// ---------------------------------------------------------------------------

/**
 * Call the configured LLM provider to extract facts from a conversation segment.
 *
 * @param conversation   - The captured conversation row
 * @param existingFacts  - Active facts for the agent (kept for API compatibility; Phase 2 dedup uses embeddings)
 * @param model          - Full model string, e.g. "anthropic/claude-sonnet-4-6"
 * @param logger
 */
export async function extractFacts(
  conversation: ConversationRow,
  _existingFacts: FactRow[], // Phase 2: dedup now handled by embedding similarity, not LLM
  model: string,
  logger: PluginLogger,
  openClawConfig?: OpenClawConfig,
): Promise<ExtractionResult> {

  // Model context window budget (leave headroom for response)
  const MODEL_CONTEXT_TOKENS = 180_000;
  const RESPONSE_HEADROOM_TOKENS = 4_096;
  const PROMPT_TEMPLATE_TOKENS = estimateTokens(EXTRACTION_PROMPT);
  const availableTokens = MODEL_CONTEXT_TOKENS - RESPONSE_HEADROOM_TOKENS - PROMPT_TEMPLATE_TOKENS;

  // Phase 1: history-agnostic extraction.
  // Existing facts are NO LONGER passed to the LLM.
  // Dedup/superseding is handled by Phase 2 (embedding similarity) in deduplicator.ts.
  // This reduces token cost, removes history-quality dependency, and improves extraction focus.
  const conversationText = truncateToTokenBudget(conversation.raw_text, availableTokens);
  const prompt = EXTRACTION_PROMPT.replace("{{conversation}}", conversationText);

  // ── Dispatch: try OpenClaw model routing first, fall back to direct API ──
  let responseText: string;
  let modelUsed = model;
  try {
    // Strategy 1: Use OpenClaw's embedded runner (preferred — inherits agent model config)
    if (openClawConfig) {
      const ocResult = await runViaOpenClaw(prompt, openClawConfig, model);
      if (ocResult) {
        responseText = ocResult.text;
        modelUsed = `${ocResult.provider}/${ocResult.model}`;
        logger.debug?.(`memento: extraction via OpenClaw model routing (${modelUsed})`);
      } else {
        // OpenClaw runner not available — fall through to direct API
        logger.debug?.("memento: OpenClaw runner unavailable, falling back to direct API");
        const info = detectProvider(model);
        const apiKey = resolveApiKey(info.apiKeyEnv);
        if (!apiKey && info.provider !== "ollama") {
          return {
            facts: [],
            modelUsed: model,
            error: `No API key found for provider "${info.provider}". Set the ${info.apiKeyEnv} environment variable (or MEMENTO_API_KEY as a generic fallback).`,
          };
        }
        switch (info.provider) {
          case "anthropic":
            responseText = await callAnthropic(info, apiKey!, prompt);
            break;
          case "ollama":
            responseText = await callOllama(info, prompt);
            break;
          default:
            responseText = await callOpenAICompat(info, apiKey, prompt);
            break;
        }
      }
    } else {
      // Strategy 2: Direct API (CLI mode or no OpenClaw config available)
      const info = detectProvider(model);
      const apiKey = resolveApiKey(info.apiKeyEnv);
      if (!apiKey && info.provider !== "ollama") {
        return {
          facts: [],
          modelUsed: model,
          error: `No API key found for provider "${info.provider}". Set the ${info.apiKeyEnv} environment variable (or MEMENTO_API_KEY as a generic fallback).`,
        };
      }
      switch (info.provider) {
        case "anthropic":
          responseText = await callAnthropic(info, apiKey!, prompt);
          break;
        case "ollama":
          responseText = await callOllama(info, prompt);
          break;
        default:
          responseText = await callOpenAICompat(info, apiKey, prompt);
          break;
      }
    }
  } catch (err) {
    return {
      facts: [],
      modelUsed,
      error: `API call failed: ${String(err)}`,
    };
  }

  // Parse JSON array from the model response
  let rawFacts: any[];
  try {
    const trimmed = responseText.trim();
    // Handle case where model wraps the array in markdown code fences
    const jsonStr = trimmed.startsWith("```")
      ? trimmed.replace(/^```[a-z]*\n?/, "").replace(/\n?```$/, "").trim()
      : trimmed;

    // Find the outermost JSON array
    const arrayStart = jsonStr.indexOf("[");
    const arrayEnd = jsonStr.lastIndexOf("]");
    if (arrayStart === -1 || arrayEnd === -1) {
      return {
        facts: [],
        modelUsed: model,
        error: `No JSON array found in response: ${responseText.slice(0, 200)}`,
      };
    }

    rawFacts = JSON.parse(jsonStr.slice(arrayStart, arrayEnd + 1));
  } catch (parseErr) {
    return {
      facts: [],
      modelUsed: model,
      error: `JSON parse error: ${String(parseErr)} | response: ${responseText.slice(0, 200)}`,
    };
  }

  // Validate, normalize, and apply classifier overrides
  const facts: ExtractedFact[] = [];
  for (const raw of rawFacts) {
    if (typeof raw !== "object" || raw === null) continue;
    if (typeof raw.content !== "string" || !raw.content.trim()) continue;

    const category = typeof raw.category === "string" ? raw.category : "technical";
    const llmVisibility =
      typeof raw.visibility === "string" ? raw.visibility : "shared";

    const fact: ExtractedFact = {
      category,
      content: raw.content.trim(),
      summary:
        typeof raw.summary === "string"
          ? raw.summary.slice(0, 100).trim()
          : raw.content.slice(0, 100).trim(),
      visibility: classifyVisibility(category, raw.content, llmVisibility),
      confidence:
        typeof raw.confidence === "number"
          ? Math.min(1, Math.max(0, raw.confidence))
          : 1.0,
      sentiment:
        typeof raw.sentiment === "string" ? raw.sentiment : "neutral",
    };

    if (typeof raw.supersedes === "string" && raw.supersedes.trim()) {
      fact.supersedes = raw.supersedes.trim();
    }
    if (typeof raw.duplicate_of === "string" && raw.duplicate_of.trim()) {
      fact.duplicate_of = raw.duplicate_of.trim();
      fact.increment_occurrence = raw.increment_occurrence === true;
    }

    // Parse relations to existing facts
    if (Array.isArray(raw.relations) && raw.relations.length > 0) {
      fact.relations = raw.relations
        .filter(
          (r: any) =>
            typeof r === "object" &&
            r !== null &&
            typeof r.target_id === "string" &&
            r.target_id.trim() &&
            typeof r.relation_type === "string" &&
            r.relation_type.trim(),
        )
        .map((r: any) => ({
          target_id: r.target_id.trim(),
          relation_type: r.relation_type.trim(),
          strength:
            typeof r.strength === "number"
              ? Math.min(1, Math.max(0, r.strength))
              : 0.8,
        }));
    }

    // Skip low-confidence inferences (threshold matches prompt instruction of 0.6)
    if (fact.confidence < 0.6) {
      logger.debug?.(
        `memento: skipping low-confidence fact (${fact.confidence}): ${fact.content.slice(0, 60)}`,
      );
      continue;
    }

    facts.push(fact);
  }

  logger.debug?.(
    `memento: extractor parsed ${facts.length} facts from ${rawFacts.length} raw`,
  );

  return { facts, modelUsed: model };
}
