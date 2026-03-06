// scripts/embedding-demo.ts
// Minimal TypeScript demo for a skill that exposes an embedding-like function.
// This is intentionally simple and deterministic so it can be used in tests and examples.

export type Embedding = number[];

/**
 * generateFakeEmbedding
 *
 * Deterministic, cheap "embedding" implementation:
 * - converts each character to its char code
 * - normalizes to [0, 1]
 * - pads/truncates to a fixed length
 *
 * This is NOT suitable for production semantic search, but is useful
 * as a drop-in demo implementation for wiring, testing, and examples.
 */
export function generateFakeEmbedding(text: string, dim: number = 32): Embedding {
  const chars = Array.from(text || "");

  // Map characters to [0, 1]
  const raw = chars.map((ch) => {
    const code = ch.charCodeAt(0);
    return (code % 256) / 255; // normalize
  });

  const result: number[] = new Array(dim).fill(0);

  // Simple deterministic folding into fixed-size vector
  for (let i = 0; i < raw.length; i++) {
    const idx = i % dim;
    result[idx] += raw[i];
  }

  // Normalize again to keep values in [0, 1]
  const maxVal = Math.max(1e-9, ...result.map((v) => Math.abs(v)));
  return result.map((v) => v / maxVal);
}

/**
 * cosineSimilarity
 *
 * Utility to compare two embeddings; useful for tests and examples.
 */
export function cosineSimilarity(a: Embedding, b: Embedding): number {
  if (a.length !== b.length) {
    throw new Error("Embedding dimension mismatch");
  }

  let dot = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  const denom = Math.sqrt(normA) * Math.sqrt(normB) || 1e-9;
  return dot / denom;
}

// Example usage (for docs/tests only; not executed by default):
// const v1 = generateFakeEmbedding("hello world");
// const v2 = generateFakeEmbedding("hello there");
// console.log("cosine:", cosineSimilarity(v1, v2));
