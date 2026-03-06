/**
 * Embedding Engine
 *
 * Generates vector embeddings for facts using BGE-M3 (or any GGUF model)
 * via node-llama-cpp. Runs locally on GPU (or CPU fallback).
 *
 * Architecture:
 *   - Lazy-loads the model on first embed request (not at plugin startup)
 *   - Keeps the model + context alive for the plugin lifetime
 *   - Provides batch embedding for migration / backfill
 *   - Cosine similarity search over fact embeddings stored in SQLite
 *
 * The model is resolved from:
 *   1. Plugin config `embeddingModel` (path or hf: URI)
 *   2. Falls back to ~/.node-llama-cpp/models/bge-m3-Q8_0.gguf
 *
 * node-llama-cpp is loaded via createRequire from the OpenClaw gateway's
 * node_modules — it is NOT a direct dependency of this plugin.
 */

import { existsSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";
import type { PluginLogger } from "../types.js";

/** Minimal interface for node-llama-cpp's embedding context */
interface EmbeddingResult {
  vector: number[];
}

// ---------------------------------------------------------------------------
// Model path resolution
// ---------------------------------------------------------------------------

const DEFAULT_MODEL_PATHS = [
  join(homedir(), ".node-llama-cpp", "models", "bge-m3-Q8_0.gguf"),
  join(homedir(), ".node-llama-cpp", "models", "bge-m3-Q4_K_M.gguf"),
];

function resolveModelPath(configPath?: string): string | null {
  // If config specifies an absolute path, use it directly
  if (configPath && !configPath.startsWith("hf:") && existsSync(configPath)) {
    return configPath;
  }

  // Check default locations
  for (const p of DEFAULT_MODEL_PATHS) {
    if (existsSync(p)) return p;
  }

  return null;
}

// ---------------------------------------------------------------------------
// node-llama-cpp loader
// ---------------------------------------------------------------------------

/**
 * Dynamically load node-llama-cpp from the gateway's node_modules.
 * This plugin does NOT bundle node-llama-cpp — it reuses the gateway's copy.
 */
/**
 * Dynamically import node-llama-cpp.
 * The module uses ESM with top-level await, so it MUST be loaded via
 * dynamic import() — createRequire() will not work.
 */
async function loadNodeLlamaCpp(): Promise<any> {
  // Known paths where node-llama-cpp lives
  const candidates = [
    join(
      homedir(),
      ".npm-global",
      "lib",
      "node_modules",
      "openclaw",
      "node_modules",
      "node-llama-cpp",
      "dist",
      "index.js",
    ),
  ];

  for (const candidate of candidates) {
    if (!existsSync(candidate)) continue;
    try {
      // Convert to file:// URL for import()
      const fileUrl = `file://${candidate}`;
      const mod = await import(fileUrl);
      return mod;
    } catch (err) {
      // Try next candidate
      continue;
    }
  }

  // Fallback: try bare specifier (works inside the gateway process where
  // node-llama-cpp is installed as part of openclaw).
  try {
    // @ts-expect-error — runtime-only fallback; module lives in gateway's node_modules
    return await import("node-llama-cpp");
  } catch (_) {
    // Fall through
  }

  throw new Error(
    "memento: could not load node-llama-cpp. " +
      "Ensure OpenClaw is installed globally.",
  );
}

// ---------------------------------------------------------------------------
// EmbeddingEngine
// ---------------------------------------------------------------------------

export class EmbeddingEngine {
  private llama: any = null;
  private model: any = null;
  private ctx: any = null;
  private dimensions: number = 0;
  private ready = false;
  private initializing: Promise<void> | null = null;
  private disposed = false;

  constructor(
    private readonly modelConfigPath: string | undefined,
    private readonly logger: PluginLogger,
  ) {}

  // ---- Public API ---------------------------------------------------------

  /**
   * Returns the embedding dimension count (available after first embed call).
   */
  get embeddingDimensions(): number {
    return this.dimensions;
  }

  /**
   * Returns true if the engine has been initialized and is ready.
   */
  get isReady(): boolean {
    return this.ready;
  }

  /**
   * Generate an embedding vector for a single text.
   * Lazy-initializes the model on first call.
   */
  async embed(text: string): Promise<number[] | null> {
    if (this.disposed) return null;

    try {
      await this.ensureInit();
      if (!this.ctx) return null;

      const result: EmbeddingResult = await this.ctx.getEmbeddingFor(text);
      return result.vector;
    } catch (err) {
      this.logger.warn(`memento: embedding failed: ${String(err)}`);
      return null;
    }
  }

  /**
   * Generate embeddings for multiple texts.
   * Processes sequentially to avoid memory spikes.
   */
  async embedBatch(
    texts: string[],
    onProgress?: (done: number, total: number) => void,
  ): Promise<(number[] | null)[]> {
    if (this.disposed) return texts.map(() => null);

    try {
      await this.ensureInit();
      if (!this.ctx) return texts.map(() => null);
    } catch (_) {
      return texts.map(() => null);
    }

    const results: (number[] | null)[] = [];
    for (let i = 0; i < texts.length; i++) {
      try {
        const result: EmbeddingResult = await this.ctx.getEmbeddingFor(texts[i]);
        results.push(result.vector);
      } catch (err) {
        this.logger.warn(
          `memento: batch embed [${i}/${texts.length}] failed: ${String(err)}`,
        );
        results.push(null);
      }
      onProgress?.(i + 1, texts.length);
    }
    return results;
  }

  /**
   * Compute cosine similarity between two vectors.
   */
  static cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length || a.length === 0) return 0;
    let dot = 0,
      normA = 0,
      normB = 0;
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    const denom = Math.sqrt(normA) * Math.sqrt(normB);
    return denom === 0 ? 0 : dot / denom;
  }

  /**
   * Clean up: dispose context, model, and llama instance.
   */
  async dispose(): Promise<void> {
    this.disposed = true;
    try {
      if (this.ctx) {
        await this.ctx.dispose?.();
        this.ctx = null;
      }
      if (this.model) {
        await this.model.dispose?.();
        this.model = null;
      }
    } catch (err) {
      this.logger.warn(`memento: embedding dispose error: ${String(err)}`);
    }
    this.ready = false;
  }

  // ---- Initialization -----------------------------------------------------

  private async ensureInit(): Promise<void> {
    if (this.ready) return;
    if (this.initializing) return this.initializing;

    this.initializing = this.init();
    try {
      await this.initializing;
    } finally {
      this.initializing = null;
    }
  }

  private async init(): Promise<void> {
    const modelPath = resolveModelPath(this.modelConfigPath);
    if (!modelPath) {
      this.logger.warn(
        "memento: no embedding model found. " +
          "Download BGE-M3: curl -L -o ~/.node-llama-cpp/models/bge-m3-Q8_0.gguf " +
          '"https://huggingface.co/gpustack/bge-m3-GGUF/resolve/main/bge-m3-Q8_0.gguf"',
      );
      return;
    }

    this.logger.info(`memento: loading embedding model from ${modelPath}`);
    const startMs = Date.now();

    try {
      const llamaModule = await loadNodeLlamaCpp();
      const getLlama =
        llamaModule.getLlama ?? llamaModule.default?.getLlama;

      if (!getLlama) {
        throw new Error("getLlama not found in node-llama-cpp module");
      }

      // Try GPU first, fall back to CPU if CUDA driver mismatch
      try {
        this.llama = await getLlama();
      } catch (gpuErr) {
        this.logger.info(
          `memento: GPU init failed (${String(gpuErr).slice(0, 80)}), falling back to CPU`,
        );
        this.llama = await getLlama({ gpu: false });
      }

      this.model = await this.llama.loadModel({
        modelPath,
      });

      this.dimensions = this.model.embeddingSize ?? 0;

      this.ctx = await this.model.createEmbeddingContext();

      this.ready = true;
      const elapsedMs = Date.now() - startMs;
      this.logger.info(
        `memento: embedding model loaded in ${elapsedMs}ms ` +
          `(dims: ${this.dimensions}, model: ${modelPath.split("/").pop()})`,
      );
    } catch (err) {
      this.logger.warn(
        `memento: failed to load embedding model: ${String(err)}. ` +
          "Semantic search will be unavailable; FTS5 keyword search still works.",
      );
      // Don't throw — graceful degradation
    }
  }
}
