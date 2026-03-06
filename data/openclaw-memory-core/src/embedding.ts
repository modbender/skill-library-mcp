import type { Embedder, EmbedderOptions } from "./types.js";

// Deterministic, local, dependency-free embedder.
// Not SOTA semantics, but stable and safe for offline vector search.
export class HashEmbedder implements Embedder {
  id = "hash-embedder-v1";
  dims: number;

  constructor(dims = 256) {
    this.dims = dims;
  }

  async embed(text: string): Promise<number[]> {
    const vec = new Array(this.dims).fill(0);
    const tokens = text
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter(Boolean);

    for (const t of tokens) {
      const h = fnv1a32(t);
      const idx = h % this.dims;
      const sign = (h & 1) === 0 ? 1 : -1;
      vec[idx] += sign;
    }

    return l2Normalize(vec);
  }
}

/**
 * Factory that returns an Embedder. Pass `{ custom: myEmbedder }` to use a
 * real semantic backend, or omit it to get the default HashEmbedder.
 *
 * ```ts
 * // Default (local, deterministic)
 * const embedder = createEmbedder();
 *
 * // Custom provider
 * const embedder = createEmbedder({ custom: myOpenAIEmbedder });
 * ```
 */
export function createEmbedder(opts?: EmbedderOptions): Embedder {
  if (opts?.custom) return opts.custom;
  return new HashEmbedder(opts?.dims);
}

export function cosine(a: number[], b: number[]): number {
  const n = Math.min(a.length, b.length);
  let dot = 0;
  for (let i = 0; i < n; i++) dot += a[i] * b[i];
  return dot;
}

function l2Normalize(v: number[]): number[] {
  let sum = 0;
  for (const x of v) sum += x * x;
  const norm = Math.sqrt(sum) || 1;
  return v.map((x) => x / norm);
}

function fnv1a32(str: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
  }
  return h >>> 0;
}
