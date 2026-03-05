// ---------------------------------------------------------------------------
// Recall configuration (Phase 3)
// ---------------------------------------------------------------------------

export type RecallConfig = {
  /** Whether to automatically inject recalled facts before each AI turn. Default: true */
  autoRecall: boolean;
  /** Maximum number of facts to inject per turn. Default: 20 */
  maxFacts: number;
  /** Maximum characters for the injected context block. Default: 4000 */
  maxContextChars: number;
  /** Minimum message length (chars) to trigger recall search. Default: 5 */
  minQueryLength: number;
  /** Whether to include shared facts from other agents (master KB). Default: true */
  crossAgentRecall: boolean;
  /**
   * Whether to use LLM-based query planning before retrieval (AMA-Agent inspired).
   * When enabled, calls the LLM to expand the query with synonyms/entities for
   * better FTS matching. Adds a small LLM call overhead per recall. Default: false
   */
  autoQueryPlanning: boolean;
};

export const DEFAULT_RECALL_CONFIG: RecallConfig = {
  autoRecall: true,
  maxFacts: 20,
  maxContextChars: 4000,
  minQueryLength: 5,
  crossAgentRecall: true,
  autoQueryPlanning: false,
};

// ---------------------------------------------------------------------------
// Extraction configuration (Phase 2)
// ---------------------------------------------------------------------------

export type ExtractionConfig = {
  /** Minimum number of turns in a segment before extraction is attempted. Default: 3 */
  minTurnsForExtraction: number;
  /** Max LLM extraction calls per minute (rate limiting). Default: 10 */
  maxExtractionsPerMinute: number;
  /** How many existing facts to include in the extraction prompt for dedup context. Default: 50 */
  includeExistingFactsCount: number;
  /** Whether to automatically extract facts after each segment capture. Default: true */
  autoExtract: boolean;
};

export const DEFAULT_EXTRACTION_CONFIG: ExtractionConfig = {
  minTurnsForExtraction: 3,
  maxExtractionsPerMinute: 10,
  includeExistingFactsCount: 50,
  autoExtract: false, // Opt-in: enabling this sends conversation text to your configured LLM provider
};

// ---------------------------------------------------------------------------
// Top-level plugin configuration
// ---------------------------------------------------------------------------

export type PluginConfig = {
  /** Idle time (ms) before flushing a conversation segment. Default: 5 min */
  pauseTimeoutMs: number;
  /** Maximum message turns before auto-flush. Default: 50 */
  maxBufferTurns: number;
  /** Whether to automatically capture all conversation messages. Default: true */
  autoCapture: boolean;
  /** Directory for storing data, relative to workspace. Default: .engram */
  dataDir: string;
  /**
   * LLM model for fact extraction. Default: "anthropic/claude-sonnet-4-6"
   *
   * Supported provider prefixes — use whichever you have an API key for:
   *   - "anthropic/<model>"  e.g. "anthropic/claude-sonnet-4-6"
   *   - "openai/<model>"     e.g. "openai/gpt-4o"
   *   - "mistral/<model>"    e.g. "mistral/mistral-large-latest"
   *   - "ollama/<model>"     e.g. "ollama/llama3" (local, no key required)
   *   - Any other string is tried as an OpenAI-compatible endpoint (fallback).
   *
   * Credentials are resolved from environment variables:
   *   ANTHROPIC_API_KEY | OPENAI_API_KEY | MISTRAL_API_KEY | MEMENTO_API_KEY
   */
  extractionModel: string;
  /** Local embedding model for semantic search (Phase 5) */
  embeddingModel: string;
  /**
   * Human-readable display names for agents shown in cross-agent recall context.
   * Map of agentId → display name. Defaults to showing the raw agentId.
   * Example: { "main": "Assistant", "medbot": "Medical Assistant" }
   */
  agentDisplay: Record<string, string>;
  /** Extraction engine configuration (Phase 2) */
  extraction: ExtractionConfig;
  /** Recall / auto-inject configuration (Phase 3) */
  recall: RecallConfig;
};

export const DEFAULT_CONFIG: PluginConfig = {
  pauseTimeoutMs: 300_000,
  maxBufferTurns: 50,
  autoCapture: true,
  dataDir: ".engram", // Default data directory; existing deployments use this path.
  extractionModel: "anthropic/claude-sonnet-4-6",
  embeddingModel: "hf:BAAI/bge-m3-gguf",
  agentDisplay: {}, // populated via plugin config: { "main": "Main Agent", "medbot": "Medical Bot" }
  extraction: DEFAULT_EXTRACTION_CONFIG,
  recall: DEFAULT_RECALL_CONFIG,
};

export function resolveConfig(raw?: Record<string, unknown>): PluginConfig {
  if (!raw) return { ...DEFAULT_CONFIG, extraction: { ...DEFAULT_EXTRACTION_CONFIG }, recall: { ...DEFAULT_RECALL_CONFIG } };

  const rawExtraction =
    raw.extraction && typeof raw.extraction === "object"
      ? (raw.extraction as Record<string, unknown>)
      : {};

  const rawRecall =
    raw.recall && typeof raw.recall === "object"
      ? (raw.recall as Record<string, unknown>)
      : {};

  return {
    pauseTimeoutMs:
      typeof raw.pauseTimeoutMs === "number"
        ? raw.pauseTimeoutMs
        : DEFAULT_CONFIG.pauseTimeoutMs,
    maxBufferTurns:
      typeof raw.maxBufferTurns === "number"
        ? raw.maxBufferTurns
        : DEFAULT_CONFIG.maxBufferTurns,
    autoCapture:
      typeof raw.autoCapture === "boolean"
        ? raw.autoCapture
        : DEFAULT_CONFIG.autoCapture,
    dataDir:
      typeof raw.dataDir === "string" ? raw.dataDir : DEFAULT_CONFIG.dataDir,
    extractionModel:
      typeof raw.extractionModel === "string"
        ? raw.extractionModel
        : DEFAULT_CONFIG.extractionModel,
    embeddingModel:
      typeof raw.embeddingModel === "string"
        ? raw.embeddingModel
        : DEFAULT_CONFIG.embeddingModel,
    agentDisplay:
      raw.agentDisplay && typeof raw.agentDisplay === "object" && !Array.isArray(raw.agentDisplay)
        ? (raw.agentDisplay as Record<string, string>)
        : DEFAULT_CONFIG.agentDisplay,
    extraction: {
      minTurnsForExtraction:
        typeof rawExtraction.minTurnsForExtraction === "number"
          ? rawExtraction.minTurnsForExtraction
          : DEFAULT_EXTRACTION_CONFIG.minTurnsForExtraction,
      maxExtractionsPerMinute:
        typeof rawExtraction.maxExtractionsPerMinute === "number"
          ? rawExtraction.maxExtractionsPerMinute
          : DEFAULT_EXTRACTION_CONFIG.maxExtractionsPerMinute,
      includeExistingFactsCount:
        typeof rawExtraction.includeExistingFactsCount === "number"
          ? rawExtraction.includeExistingFactsCount
          : DEFAULT_EXTRACTION_CONFIG.includeExistingFactsCount,
      autoExtract:
        typeof rawExtraction.autoExtract === "boolean"
          ? rawExtraction.autoExtract
          : DEFAULT_EXTRACTION_CONFIG.autoExtract,
    },
    recall: {
      autoRecall:
        typeof rawRecall.autoRecall === "boolean"
          ? rawRecall.autoRecall
          : DEFAULT_RECALL_CONFIG.autoRecall,
      maxFacts:
        typeof rawRecall.maxFacts === "number"
          ? rawRecall.maxFacts
          : DEFAULT_RECALL_CONFIG.maxFacts,
      maxContextChars:
        typeof rawRecall.maxContextChars === "number"
          ? rawRecall.maxContextChars
          : DEFAULT_RECALL_CONFIG.maxContextChars,
      minQueryLength:
        typeof rawRecall.minQueryLength === "number"
          ? rawRecall.minQueryLength
          : DEFAULT_RECALL_CONFIG.minQueryLength,
      crossAgentRecall:
        typeof rawRecall.crossAgentRecall === "boolean"
          ? rawRecall.crossAgentRecall
          : DEFAULT_RECALL_CONFIG.crossAgentRecall,
      autoQueryPlanning:
        typeof rawRecall.autoQueryPlanning === "boolean"
          ? rawRecall.autoQueryPlanning
          : DEFAULT_RECALL_CONFIG.autoQueryPlanning,
    },
  };
}
