import { describe, it, expect } from "vitest";
import { HashEmbedder, cosine, createEmbedder } from "../src/embedding.js";
import type { Embedder } from "../src/types.js";

describe("HashEmbedder", () => {
  it("produces a vector with the configured number of dimensions", async () => {
    const embedder = new HashEmbedder(128);
    const vec = await embedder.embed("hello world");
    expect(vec.length).toBe(128);
  });

  it("defaults to 256 dimensions", async () => {
    const embedder = new HashEmbedder();
    expect(embedder.dims).toBe(256);
    const vec = await embedder.embed("test");
    expect(vec.length).toBe(256);
  });

  it("returns an L2-normalized vector (unit length)", async () => {
    const embedder = new HashEmbedder(64);
    const vec = await embedder.embed("some text with multiple tokens for hashing");
    const magnitude = Math.sqrt(vec.reduce((s, x) => s + x * x, 0));
    expect(magnitude).toBeCloseTo(1.0, 5);
  });

  it("returns a zero-magnitude-safe vector for empty string", async () => {
    const embedder = new HashEmbedder(64);
    const vec = await embedder.embed("");
    // All zeros divided by norm=1 should yield all zeros
    expect(vec.length).toBe(64);
    expect(vec.every((x) => x === 0)).toBe(true);
  });

  it("produces deterministic output for the same input", async () => {
    const embedder = new HashEmbedder(64);
    const a = await embedder.embed("deterministic test");
    const b = await embedder.embed("deterministic test");
    expect(a).toEqual(b);
  });

  it("produces different vectors for different inputs", async () => {
    const embedder = new HashEmbedder(64);
    const a = await embedder.embed("cat");
    const b = await embedder.embed("astrophysics");
    // Vectors should not be identical
    const identical = a.every((v, i) => v === b[i]);
    expect(identical).toBe(false);
  });

  it("is case-insensitive", async () => {
    const embedder = new HashEmbedder(64);
    const a = await embedder.embed("Hello World");
    const b = await embedder.embed("hello world");
    expect(a).toEqual(b);
  });

  it("strips punctuation before hashing", async () => {
    const embedder = new HashEmbedder(64);
    const a = await embedder.embed("hello, world!");
    const b = await embedder.embed("hello world");
    expect(a).toEqual(b);
  });

  it("has the correct id property", () => {
    const embedder = new HashEmbedder();
    expect(embedder.id).toBe("hash-embedder-v1");
  });

  it("gives high similarity for identical text", async () => {
    const embedder = new HashEmbedder(128);
    const v = await embedder.embed("identical text");
    const sim = cosine(v, v);
    expect(sim).toBeCloseTo(1.0, 5);
  });

  it("gives higher similarity for related text than unrelated text", async () => {
    const embedder = new HashEmbedder(128);
    const base = await embedder.embed("programming language typescript javascript");
    const related = await embedder.embed("typescript programming language");
    const unrelated = await embedder.embed("banana strawberry fruit smoothie");
    const simRelated = cosine(base, related);
    const simUnrelated = cosine(base, unrelated);
    expect(simRelated).toBeGreaterThan(simUnrelated);
  });

  it("works with dim=1 (minimal dimension)", async () => {
    const embedder = new HashEmbedder(1);
    const vec = await embedder.embed("hello");
    expect(vec.length).toBe(1);
    // With only one bucket, the magnitude should be 1 or 0
    expect(Math.abs(vec[0]!)).toBeCloseTo(1.0, 5);
  });

  it("handles numeric-only tokens", async () => {
    const embedder = new HashEmbedder(64);
    const vec = await embedder.embed("123 456 789");
    const magnitude = Math.sqrt(vec.reduce((s, x) => s + x * x, 0));
    expect(magnitude).toBeCloseTo(1.0, 5);
  });

  it("handles text with excessive whitespace", async () => {
    const embedder = new HashEmbedder(64);
    const a = await embedder.embed("hello   world");
    const b = await embedder.embed("hello world");
    // Whitespace variations should produce the same embedding
    expect(a).toEqual(b);
  });

  it("handles single-character token", async () => {
    const embedder = new HashEmbedder(64);
    const vec = await embedder.embed("a");
    expect(vec.length).toBe(64);
    const magnitude = Math.sqrt(vec.reduce((s, x) => s + x * x, 0));
    expect(magnitude).toBeCloseTo(1.0, 5);
  });

  it("handles very long input without error", async () => {
    const embedder = new HashEmbedder(64);
    const longText = Array.from({ length: 10000 }, (_, i) => `word${i}`).join(" ");
    const vec = await embedder.embed(longText);
    expect(vec.length).toBe(64);
    const magnitude = Math.sqrt(vec.reduce((s, x) => s + x * x, 0));
    expect(magnitude).toBeCloseTo(1.0, 5);
  });
});

describe("cosine", () => {
  it("returns 1.0 for identical unit vectors", () => {
    const v = [1, 0, 0];
    expect(cosine(v, v)).toBeCloseTo(1.0, 10);
  });

  it("returns 0 for orthogonal vectors", () => {
    const a = [1, 0, 0];
    const b = [0, 1, 0];
    expect(cosine(a, b)).toBeCloseTo(0, 10);
  });

  it("returns -1 for opposite vectors", () => {
    const a = [1, 0, 0];
    const b = [-1, 0, 0];
    expect(cosine(a, b)).toBeCloseTo(-1.0, 10);
  });

  it("handles vectors of different lengths by using the shorter", () => {
    const a = [1, 0, 0, 999];
    const b = [1, 0, 0];
    // Should only use the first 3 elements
    expect(cosine(a, b)).toBeCloseTo(1.0, 10);
  });

  it("returns 0 for zero vectors", () => {
    const a = [0, 0, 0];
    const b = [0, 0, 0];
    expect(cosine(a, b)).toBe(0);
  });

  it("handles single-element vectors", () => {
    expect(cosine([3], [4])).toBe(12);
    expect(cosine([-1], [1])).toBe(-1);
  });

  it("computes correct dot product for non-unit vectors", () => {
    const a = [2, 0];
    const b = [3, 0];
    // cosine here computes raw dot product (no normalization in the function)
    expect(cosine(a, b)).toBe(6);
  });

  it("handles empty vectors", () => {
    expect(cosine([], [])).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// createEmbedder() factory (issue #1 - provider pattern)
// ---------------------------------------------------------------------------
describe("createEmbedder", () => {
  it("returns a HashEmbedder by default", () => {
    const embedder = createEmbedder();
    expect(embedder).toBeInstanceOf(HashEmbedder);
    expect(embedder.id).toBe("hash-embedder-v1");
    expect(embedder.dims).toBe(256);
  });

  it("respects custom dims for the default HashEmbedder", () => {
    const embedder = createEmbedder({ dims: 128 });
    expect(embedder).toBeInstanceOf(HashEmbedder);
    expect(embedder.dims).toBe(128);
  });

  it("returns a custom embedder when provided", async () => {
    const custom: Embedder = {
      id: "mock-embedder",
      dims: 3,
      async embed(_text: string) {
        return [0.1, 0.2, 0.3];
      },
    };
    const embedder = createEmbedder({ custom });
    expect(embedder).toBe(custom);
    expect(embedder.id).toBe("mock-embedder");
    expect(embedder.dims).toBe(3);
    const vec = await embedder.embed("anything");
    expect(vec).toEqual([0.1, 0.2, 0.3]);
  });

  it("ignores dims when a custom embedder is provided", () => {
    const custom: Embedder = {
      id: "custom",
      dims: 42,
      async embed() { return new Array(42).fill(0); },
    };
    const embedder = createEmbedder({ custom, dims: 999 });
    expect(embedder.dims).toBe(42);
    expect(embedder).toBe(custom);
  });

  it("returned embedder satisfies the Embedder interface", async () => {
    const embedder = createEmbedder();
    expect(typeof embedder.id).toBe("string");
    expect(typeof embedder.dims).toBe("number");
    const vec = await embedder.embed("test");
    expect(Array.isArray(vec)).toBe(true);
    expect(vec.length).toBe(embedder.dims);
  });
});
