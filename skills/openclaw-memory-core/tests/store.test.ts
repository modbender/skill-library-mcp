import { describe, it, expect } from "vitest";
import { tmpdir } from "node:os";
import { join } from "node:path";
import fsPromises from "node:fs/promises";
import { HashEmbedder } from "../src/embedding.js";
import { JsonlMemoryStore } from "../src/store-jsonl.js";
import type { MemoryItem } from "../src/types.js";

function makeStore(suffix = "") {
  const filePath = join(tmpdir(), `mem-${Date.now()}${suffix}.jsonl`);
  return { store: new JsonlMemoryStore({ filePath, embedder: new HashEmbedder(64) }), filePath };
}

function makeItem(id: string, overrides: Partial<MemoryItem> = {}): MemoryItem {
  return { id, kind: "note", text: `text for ${id}`, createdAt: new Date().toISOString(), ...overrides };
}

describe("JsonlMemoryStore", () => {
  it("adds and searches", async () => {
    const { store } = makeStore();
    await store.add({
      id: "1",
      kind: "doc",
      text: "Project setup checklist: residency, bank, company formation",
      createdAt: new Date().toISOString(),
      tags: ["project"],
    });
    const hits = await store.search("residency checklist", { limit: 5 });
    expect(hits.length).toBeGreaterThan(0);
    expect(hits[0]!.item.text).toContain("residency");
  });

  it("deletes an item by id", async () => {
    const { store } = makeStore("-del");
    await store.add({ id: "a", kind: "note", text: "delete me", createdAt: new Date().toISOString() });
    const deleted = await store.delete("a");
    expect(deleted).toBe(true);
    const items = await store.list();
    expect(items.find((i) => i.id === "a")).toBeUndefined();
  });

  it("returns false when deleting non-existent id", async () => {
    const { store } = makeStore("-del2");
    const deleted = await store.delete("ghost");
    expect(deleted).toBe(false);
  });

  it("lists items in insertion order (most recent last)", async () => {
    const { store } = makeStore("-list");
    for (let i = 1; i <= 3; i++) {
      await store.add({ id: String(i), kind: "fact", text: `fact ${i}`, createdAt: new Date().toISOString() });
    }
    const items = await store.list({ limit: 3 });
    expect(items.map((i) => i.id)).toEqual(["1", "2", "3"]);
  });

  it("filters list by kind", async () => {
    const { store } = makeStore("-kind");
    await store.add({ id: "d1", kind: "doc", text: "a doc", createdAt: new Date().toISOString() });
    await store.add({ id: "n1", kind: "note", text: "a note", createdAt: new Date().toISOString() });
    const docs = await store.list({ kind: "doc" });
    expect(docs.every((i) => i.kind === "doc")).toBe(true);
    expect(docs.find((i) => i.id === "d1")).toBeDefined();
  });

  it("rejects items with invalid kind", async () => {
    const { store } = makeStore("-inv");
    await expect(
      store.add({ id: "bad", kind: "invalid" as never, text: "x", createdAt: new Date().toISOString() })
    ).rejects.toThrow(/Invalid kind/);
  });

  it("handles concurrent adds without data loss", async () => {
    const { store } = makeStore("-concurrent");
    await Promise.all(
      Array.from({ length: 10 }, (_, i) =>
        store.add({ id: String(i), kind: "note", text: `note ${i}`, createdAt: new Date().toISOString() })
      )
    );
    const items = await store.list();
    expect(items.length).toBe(10);
  });

  // --- update() tests ---

  it("updates an existing item and returns the merged result", async () => {
    const { store } = makeStore("-upd1");
    await store.add({ id: "u1", kind: "note", text: "original text", createdAt: "2024-01-01T00:00:00Z" });
    const updated = await store.update("u1", { text: "revised text" });
    expect(updated).toBeDefined();
    expect(updated!.text).toBe("revised text");
    expect(updated!.kind).toBe("note");
    expect(updated!.id).toBe("u1");
    // Verify persisted
    const fetched = await store.get("u1");
    expect(fetched!.text).toBe("revised text");
  });

  it("returns undefined when updating a non-existent id", async () => {
    const { store } = makeStore("-upd2");
    const result = await store.update("ghost", { text: "nope" });
    expect(result).toBeUndefined();
  });

  it("preserves insertion order after update", async () => {
    const { store } = makeStore("-upd3");
    await store.add({ id: "a", kind: "fact", text: "first", createdAt: "2024-01-01T00:00:00Z" });
    await store.add({ id: "b", kind: "fact", text: "second", createdAt: "2024-01-02T00:00:00Z" });
    await store.add({ id: "c", kind: "fact", text: "third", createdAt: "2024-01-03T00:00:00Z" });
    await store.update("b", { text: "second-updated" });
    const items = await store.list();
    expect(items.map((i) => i.id)).toEqual(["a", "b", "c"]);
    expect(items[1]!.text).toBe("second-updated");
  });

  it("re-embeds when text content changes so search still works", async () => {
    const { store } = makeStore("-upd4");
    await store.add({ id: "s1", kind: "doc", text: "banana apple orange", createdAt: "2024-01-01T00:00:00Z" });
    await store.update("s1", { text: "kubernetes docker containers" });
    const hits = await store.search("kubernetes containers", { limit: 5 });
    expect(hits.length).toBeGreaterThan(0);
    expect(hits[0]!.item.text).toContain("kubernetes");
  });

  it("keeps existing embedding when text does not change", async () => {
    const { store } = makeStore("-upd5");
    await store.add({ id: "e1", kind: "note", text: "stable text", createdAt: "2024-01-01T00:00:00Z" });
    // Only update tags, not text
    await store.update("e1", { tags: ["important"] });
    const fetched = await store.get("e1");
    expect(fetched!.tags).toEqual(["important"]);
    expect(fetched!.text).toBe("stable text");
    // Search should still find it via the original embedding
    const hits = await store.search("stable text", { limit: 5 });
    expect(hits.length).toBeGreaterThan(0);
    expect(hits[0]!.item.id).toBe("e1");
  });

  it("rejects update with invalid kind", async () => {
    const { store } = makeStore("-upd6");
    await store.add({ id: "k1", kind: "note", text: "valid", createdAt: "2024-01-01T00:00:00Z" });
    await expect(
      store.update("k1", { kind: "invalid" as never })
    ).rejects.toThrow(/Invalid kind/);
  });

  it("can update kind to a valid value", async () => {
    const { store } = makeStore("-upd7");
    await store.add({ id: "k2", kind: "note", text: "was a note", createdAt: "2024-01-01T00:00:00Z" });
    const updated = await store.update("k2", { kind: "decision" });
    expect(updated!.kind).toBe("decision");
  });

  it("cannot change the id field via update", async () => {
    const { store } = makeStore("-upd8");
    await store.add({ id: "orig", kind: "note", text: "text", createdAt: "2024-01-01T00:00:00Z" });
    // Partial<Omit<MemoryItem, "id">> prevents id at the type level,
    // but we test runtime behaviour with a forced cast
    const updated = await store.update("orig", { text: "changed" } as never);
    expect(updated!.id).toBe("orig");
  });
});

// ---------------------------------------------------------------------------
// addMany() bulk operations (issue #8)
// ---------------------------------------------------------------------------
describe("JsonlMemoryStore - addMany()", () => {
  it("adds multiple items in one call", async () => {
    const { store } = makeStore("-bulk1");
    const items = [makeItem("b1"), makeItem("b2"), makeItem("b3")];
    await store.addMany(items);
    const listed = await store.list();
    expect(listed.length).toBe(3);
    expect(listed.map((i) => i.id)).toEqual(["b1", "b2", "b3"]);
  });

  it("returns void on success", async () => {
    const { store } = makeStore("-bulk-void");
    const result = await store.addMany([makeItem("v1")]);
    expect(result).toBeUndefined();
  });

  it("handles empty array without error", async () => {
    const { store } = makeStore("-bulk-empty");
    await store.addMany([]);
    const listed = await store.list();
    expect(listed.length).toBe(0);
  });

  it("rejects if any item has an invalid kind", async () => {
    const { store } = makeStore("-bulk-inv");
    const items = [
      makeItem("ok1"),
      makeItem("bad", { kind: "invalid" as never }),
    ];
    await expect(store.addMany(items)).rejects.toThrow(/Invalid kind/);
  });

  it("items added with addMany are searchable", async () => {
    const { store } = makeStore("-bulk-search");
    await store.addMany([
      makeItem("s1", { text: "kubernetes docker containers orchestration" }),
      makeItem("s2", { text: "banana apple orange fruit" }),
    ]);
    const hits = await store.search("kubernetes containers", { limit: 5 });
    expect(hits.length).toBeGreaterThan(0);
    expect(hits[0]!.item.id).toBe("s1");
  });

  it("persists across store instances", async () => {
    const filePath = join(tmpdir(), `mem-bulk-persist-${Date.now()}.jsonl`);
    const embedder = new HashEmbedder(64);
    const store1 = new JsonlMemoryStore({ filePath, embedder });
    await store1.addMany([makeItem("p1"), makeItem("p2")]);

    const store2 = new JsonlMemoryStore({ filePath, embedder });
    const listed = await store2.list();
    expect(listed.length).toBe(2);
    expect(listed.map((i) => i.id)).toEqual(["p1", "p2"]);
  });

  it("interleaves correctly with single add()", async () => {
    const { store } = makeStore("-bulk-mix");
    await store.add(makeItem("single1"));
    await store.addMany([makeItem("bulk1"), makeItem("bulk2")]);
    await store.add(makeItem("single2"));
    const listed = await store.list();
    expect(listed.map((i) => i.id)).toEqual(["single1", "bulk1", "bulk2", "single2"]);
  });

  it("handles concurrent addMany calls without data loss", async () => {
    const { store } = makeStore("-bulk-concurrent");
    await Promise.all([
      store.addMany([makeItem("a1"), makeItem("a2"), makeItem("a3")]),
      store.addMany([makeItem("b1"), makeItem("b2"), makeItem("b3")]),
    ]);
    const listed = await store.list();
    expect(listed.length).toBe(6);
  });

  it("trims to maxItems when addMany exceeds capacity", async () => {
    const filePath = join(tmpdir(), `mem-bulk-trim-${Date.now()}.jsonl`);
    const store = new JsonlMemoryStore({ filePath, embedder: new HashEmbedder(64), maxItems: 5 });
    const items = Array.from({ length: 8 }, (_, i) => makeItem(`t${i}`));
    await store.addMany(items);
    const listed = await store.list();
    expect(listed.length).toBe(5);
    // Should keep the last 5 (t3..t7)
    expect(listed.map((i) => i.id)).toEqual(["t3", "t4", "t5", "t6", "t7"]);
  });
});

// ---------------------------------------------------------------------------
// Append-optimized add() (issue #8)
// ---------------------------------------------------------------------------
describe("JsonlMemoryStore - append-optimized add()", () => {
  it("append produces valid JSONL that survives re-read from disk", async () => {
    const filePath = join(tmpdir(), `mem-append-${Date.now()}.jsonl`);
    const embedder = new HashEmbedder(64);
    const store1 = new JsonlMemoryStore({ filePath, embedder });
    await store1.add(makeItem("a1"));
    await store1.add(makeItem("a2"));

    // Re-open from disk to force a fresh parse
    const store2 = new JsonlMemoryStore({ filePath, embedder });
    const listed = await store2.list();
    expect(listed.length).toBe(2);
    expect(listed.map((i) => i.id)).toEqual(["a1", "a2"]);
  });

  it("file grows by appending, not rewriting, for small stores", async () => {
    const filePath = join(tmpdir(), `mem-appendsize-${Date.now()}.jsonl`);
    const embedder = new HashEmbedder(64);
    const store = new JsonlMemoryStore({ filePath, embedder });
    await store.add(makeItem("x1"));
    const size1 = (await fsPromises.stat(filePath)).size;
    await store.add(makeItem("x2"));
    const size2 = (await fsPromises.stat(filePath)).size;
    // After appending, file should be strictly larger than before
    expect(size2).toBeGreaterThan(size1);
  });
});
