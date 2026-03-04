export type MemoryKind = "fact" | "decision" | "doc" | "note";

export interface MemoryItem {
  id: string;
  kind: MemoryKind;
  text: string;
  createdAt: string; // ISO
  /** Optional expiry timestamp (ISO 8601). Items past this time are excluded from reads by default. */
  expiresAt?: string;
  source?: {
    channel?: string;
    from?: string;
    conversationId?: string;
    messageId?: string;
  };
  tags?: string[];
  meta?: Record<string, unknown>;
}

export interface SearchHit {
  item: MemoryItem;
  score: number; // 0..1
}

export interface SearchOpts {
  limit?: number;
  kind?: MemoryKind;
  tags?: string[];
  /** When true, include items that have passed their expiresAt. Default: false. */
  includeExpired?: boolean;
}

export interface ListOpts {
  limit?: number;
  kind?: MemoryKind;
  tags?: string[];
  /** When true, include items that have passed their expiresAt. Default: false. */
  includeExpired?: boolean;
}

export interface MemoryStore {
  add(item: MemoryItem): Promise<void>;
  /** Add multiple items in a single operation. More efficient than calling add() in a loop. */
  addMany(items: MemoryItem[]): Promise<void>;
  get(id: string): Promise<MemoryItem | undefined>;
  /** Update an existing item by merging partial fields. Returns the updated item, or undefined if not found. */
  update(id: string, partial: Partial<Omit<MemoryItem, "id">>): Promise<MemoryItem | undefined>;
  delete(id: string): Promise<boolean>;
  search(query: string, opts?: SearchOpts): Promise<SearchHit[]>;
  list(opts?: ListOpts): Promise<MemoryItem[]>;
  /** Remove all items whose expiresAt is in the past. Returns the number of purged items. */
  purgeExpired(): Promise<number>;
}

export interface RedactionResult {
  redactedText: string;
  hadSecrets: boolean;
  /** Stores only which rule fired and how many times - never the actual matched text. */
  matches: Array<{ rule: string; count: number }>;
}

export interface Redactor {
  redact(text: string): RedactionResult;
}

/**
 * Pluggable embeddings backend. The default implementation is HashEmbedder
 * (deterministic, local, zero-dependency). Swap in any provider that
 * satisfies this interface - for example an OpenAI, Cohere, or local-model
 * adapter.
 *
 * ```ts
 * const myEmbedder: Embedder = {
 *   id: "openai-text-embedding-3-small",
 *   dims: 1536,
 *   async embed(text) { return callOpenAI(text); },
 * };
 * const store = new JsonlMemoryStore({ filePath, embedder: myEmbedder });
 * ```
 */
export interface Embedder {
  /** Generate a numeric embedding vector for the given text. */
  embed(text: string): Promise<number[]>;
  /** Number of dimensions the embedder produces. */
  dims: number;
  /** Unique identifier for this embedder implementation. */
  id: string;
}

/**
 * Options accepted by `createEmbedder()`. When no custom embedder is
 * supplied, a HashEmbedder with the specified dimensions is used.
 */
export interface EmbedderOptions {
  /** Supply a custom Embedder implementation to override the default HashEmbedder. */
  custom?: Embedder;
  /** Dimensions for the default HashEmbedder (ignored when `custom` is set). Default: 256. */
  dims?: number;
}

// ---------------------------------------------------------------------------
// Plugin API contract (used by openclaw-memory-brain, openclaw-memory-docs)
// ---------------------------------------------------------------------------

export interface PluginLogger {
  info?(msg: string): void;
  warn?(msg: string): void;
  error?(msg: string): void;
}

export interface CommandContext {
  args?: string;
  channel?: string;
  from?: string;
  conversationId?: string;
  messageId?: string;
}

export interface MessageEvent {
  content?: string;
  from?: string;
}

export interface MessageEventContext {
  messageProvider?: string;
  sessionId?: string;
}

export interface ToolCallParams {
  [key: string]: unknown;
}

export interface CommandDefinition {
  name: string;
  description: string;
  usage: string;
  requireAuth: boolean;
  acceptsArgs: boolean;
  handler: (ctx: CommandContext) => Promise<{ text: string }>;
}

export interface ToolDefinition {
  name: string;
  description: string;
  /** JSON Schema for the tool's input parameters. Used by OpenClaw to describe the tool to the AI. */
  parameters?: Record<string, unknown>;
  execute(params: ToolCallParams): Promise<unknown>;
}

export interface PluginApi {
  pluginConfig?: Record<string, unknown>;
  logger?: PluginLogger;
  registerCommand(def: CommandDefinition): void;
  registerTool(def: ToolDefinition): void;
  on(event: 'message_received', handler: (event: MessageEvent, ctx: MessageEventContext) => Promise<void>): void;
}
