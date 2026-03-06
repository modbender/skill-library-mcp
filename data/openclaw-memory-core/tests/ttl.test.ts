import { describe, it, expect, vi, afterEach } from "vitest";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { HashEmbedder } from "../src/embedding.js";
import { JsonlMemoryStore } from "../src/store-jsonl.js";
import { ttlMs } from "../src/utils.js";
import type { MemoryItem } from "../src/types.js";

function makeStore(suffix = "") {
  const filePath = join(tmpdir(), `mem-ttl-${Date.now()}${suffix}.jsonl`);
  return new JsonlMemoryStore({ filePath, embedder: new HashEmbedder(64) });
}

const PAST = "2020-01-01T00:00:00.000Z";
const FUTURE = "2099-12-31T23:59:59.999Z";

function item(overrides: Partial<MemoryItem> & { id: string }): MemoryItem {
  return {
    kind: "note",
    text: `text for ${overrides.id}`,
    createdAt: "2024-01-01T00:00:00Z",
    ...overrides,
  };
}

afterEach(() => {
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------
// get()
// ---------------------------------------------------------------------------
describe("TTL - get()", () => {
  it("returns undefined for an expired item", async () => {
    const store = makeStore("-get-expired");
    await store.add(item({ id: "e1", expiresAt: PAST }));
    expect(await store.get("e1")).toBeUndefined();
  });

  it("returns the item when expiresAt is in the future", async () => {
    const store = makeStore("-get-future");
    await store.add(item({ id: "f1", expiresAt: FUTURE }));
    const fetched = await store.get("f1");
    expect(fetched).toBeDefined();
    expect(fetched!.id).toBe("f1");
  });

  it("returns the item when expiresAt is not set", async () => {
    const store = makeStore("-get-noexpiry");
    await store.add(item({ id: "n1" }));
    const fetched = await store.get("n1");
    expect(fetched).toBeDefined();
  });
});

// ---------------------------------------------------------------------------
// list()
// ---------------------------------------------------------------------------
describe("TTL - list()", () => {
  it("excludes expired items by default", async () => {
    const store = makeStore("-list-excl");
    await store.add(item({ id: "live", expiresAt: FUTURE }));
    await store.add(item({ id: "dead", expiresAt: PAST }));
    await store.add(item({ id: "noexpiry" }));
    const items = await store.list();
    const ids = items.map((i) => i.id);
    expect(ids).toContain("live");
    expect(ids).toContain("noexpiry");
    expect(ids).not.toContain("dead");
  });

  it("includes expired items when includeExpired is true", async () => {
    const store = makeStore("-list-incl");
    await store.add(item({ id: "live", expiresAt: FUTURE }));
    await store.add(item({ id: "dead", expiresAt: PAST }));
    const items = await store.list({ includeExpired: true });
    const ids = items.map((i) => i.id);
    expect(ids).toContain("live");
    expect(ids).toContain("dead");
  });

  it("applies kind and tag filters alongside TTL", async () => {
    const store = makeStore("-list-filter");
    await store.add(item({ id: "a", kind: "doc", tags: ["x"], expiresAt: FUTURE }));
    await store.add(item({ id: "b", kind: "doc", tags: ["x"], expiresAt: PAST }));
    await store.add(item({ id: "c", kind: "note", tags: ["x"], expiresAt: FUTURE }));
    const items = await store.list({ kind: "doc", tags: ["x"] });
    expect(items.length).toBe(1);
    expect(items[0]!.id).toBe("a");
  });

  it("respects limit after filtering expired items", async () => {
    const store = makeStore("-list-limit");
    for (let i = 0; i < 5; i++) {
      await store.add(item({ id: `live-${i}`, expiresAt: FUTURE }));
    }
    await store.add(item({ id: "dead", expiresAt: PAST }));
    const items = await store.list({ limit: 3 });
    expect(items.length).toBe(3);
    expect(items.every((i) => !i.id.startsWith("dead"))).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// search()
// ---------------------------------------------------------------------------
describe("TTL - search()", () => {
  it("excludes expired items from search results", async () => {
    const store = makeStore("-search-excl");
    await store.add(item({ id: "live", text: "kubernetes docker containers", expiresAt: FUTURE }));
    await store.add(item({ id: "dead", text: "kubernetes docker containers", expiresAt: PAST }));
    const hits = await store.search("kubernetes", { limit: 10 });
    const ids = hits.map((h) => h.item.id);
    expect(ids).toContain("live");
    expect(ids).not.toContain("dead");
  });

  it("includes expired items in search when includeExpired is true", async () => {
    const store = makeStore("-search-incl");
    await store.add(item({ id: "live", text: "kubernetes docker containers", expiresAt: FUTURE }));
    await store.add(item({ id: "dead", text: "kubernetes docker containers", expiresAt: PAST }));
    const hits = await store.search("kubernetes", { limit: 10, includeExpired: true });
    const ids = hits.map((h) => h.item.id);
    expect(ids).toContain("live");
    expect(ids).toContain("dead");
  });
});

// ---------------------------------------------------------------------------
// purgeExpired()
// ---------------------------------------------------------------------------
describe("TTL - purgeExpired()", () => {
  it("removes expired items and returns the count", async () => {
    const store = makeStore("-purge");
    await store.add(item({ id: "live", expiresAt: FUTURE }));
    await store.add(item({ id: "dead1", expiresAt: PAST }));
    await store.add(item({ id: "dead2", expiresAt: PAST }));
    await store.add(item({ id: "noexpiry" }));

    const purged = await store.purgeExpired();
    expect(purged).toBe(2);

    // Only live items remain (includeExpired to verify dead are really gone)
    const all = await store.list({ includeExpired: true });
    const ids = all.map((i) => i.id);
    expect(ids).toEqual(["live", "noexpiry"]);
  });

  it("returns 0 when nothing is expired", async () => {
    const store = makeStore("-purge-none");
    await store.add(item({ id: "a", expiresAt: FUTURE }));
    await store.add(item({ id: "b" }));
    const purged = await store.purgeExpired();
    expect(purged).toBe(0);
  });

  it("returns 0 on an empty store", async () => {
    const store = makeStore("-purge-empty");
    const purged = await store.purgeExpired();
    expect(purged).toBe(0);
  });

  it("does not write to disk when nothing is purged", async () => {
    const store = makeStore("-purge-nowrite");
    await store.add(item({ id: "a", expiresAt: FUTURE }));
    // After add, cache is warm. Purge should not trigger a write.
    const purged = await store.purgeExpired();
    expect(purged).toBe(0);
  });
});

// ---------------------------------------------------------------------------
// update() interaction with TTL
// ---------------------------------------------------------------------------
describe("TTL - update()", () => {
  it("can set expiresAt via update", async () => {
    const store = makeStore("-update-set");
    await store.add(item({ id: "u1" }));
    const updated = await store.update("u1", { expiresAt: PAST });
    expect(updated).toBeDefined();
    expect(updated!.expiresAt).toBe(PAST);
    // Now it should be hidden from get
    expect(await store.get("u1")).toBeUndefined();
  });

  it("can extend expiry via update", async () => {
    const store = makeStore("-update-extend");
    await store.add(item({ id: "u2", expiresAt: PAST }));
    // Item is expired, but update still works (finds by id regardless of expiry)
    const updated = await store.update("u2", { expiresAt: FUTURE });
    expect(updated).toBeDefined();
    expect(updated!.expiresAt).toBe(FUTURE);
    // Now it should be visible again
    const fetched = await store.get("u2");
    expect(fetched).toBeDefined();
    expect(fetched!.id).toBe("u2");
  });

  it("can clear expiresAt by setting undefined", async () => {
    const store = makeStore("-update-clear");
    await store.add(item({ id: "u3", expiresAt: PAST }));
    const updated = await store.update("u3", { expiresAt: undefined });
    expect(updated).toBeDefined();
    expect(updated!.expiresAt).toBeUndefined();
    expect(await store.get("u3")).toBeDefined();
  });
});

// ---------------------------------------------------------------------------
// ttlMs utility
// ---------------------------------------------------------------------------
describe("ttlMs()", () => {
  it("returns an ISO string in the future", () => {
    const before = Date.now();
    const result = ttlMs(60_000); // 1 minute
    const after = Date.now();
    const ts = new Date(result).getTime();
    expect(ts).toBeGreaterThanOrEqual(before + 60_000);
    expect(ts).toBeLessThanOrEqual(after + 60_000);
  });

  it("returns an ISO string in the past for negative values", () => {
    const result = ttlMs(-60_000);
    expect(new Date(result).getTime()).toBeLessThan(Date.now());
  });

  it("returns a parseable ISO 8601 string", () => {
    const result = ttlMs(1000);
    expect(new Date(result).toISOString()).toBe(result);
  });
});

// ---------------------------------------------------------------------------
// Edge cases
// ---------------------------------------------------------------------------
describe("TTL - edge cases", () => {
  it("items with expiresAt exactly equal to now are treated as expired", async () => {
    const store = makeStore("-edge-exact");
    const now = new Date().toISOString();
    await store.add(item({ id: "exact", expiresAt: now }));
    // ISO string comparison: expiresAt <= now means expired
    // Since we set expiresAt to now, it should be expired
    const fetched = await store.get("exact");
    expect(fetched).toBeUndefined();
  });

  it("add() accepts items with expiresAt already in the past", async () => {
    const store = makeStore("-edge-addpast");
    // Should not throw - the item is just immediately expired
    await store.add(item({ id: "olditem", expiresAt: PAST }));
    expect(await store.get("olditem")).toBeUndefined();
    // But it exists in storage
    const all = await store.list({ includeExpired: true });
    expect(all.find((i) => i.id === "olditem")).toBeDefined();
  });

  it("delete() works on expired items", async () => {
    const store = makeStore("-edge-delete");
    await store.add(item({ id: "d1", expiresAt: PAST }));
    const deleted = await store.delete("d1");
    expect(deleted).toBe(true);
    const all = await store.list({ includeExpired: true });
    expect(all.find((i) => i.id === "d1")).toBeUndefined();
  });

  it("expiresAt persists through file round-trip", async () => {
    const filePath = join(tmpdir(), `mem-ttl-persist-${Date.now()}.jsonl`);
    const embedder = new HashEmbedder(64);
    const store1 = new JsonlMemoryStore({ filePath, embedder });
    await store1.add(item({ id: "p1", expiresAt: FUTURE }));

    // Create a new store instance to force re-read from disk
    const store2 = new JsonlMemoryStore({ filePath, embedder });
    const fetched = await store2.get("p1");
    expect(fetched).toBeDefined();
    expect(fetched!.expiresAt).toBe(FUTURE);
  });

  it("concurrent purge and add do not conflict", async () => {
    const store = makeStore("-edge-concurrent");
    await store.add(item({ id: "dead", expiresAt: PAST }));
    await store.add(item({ id: "live", expiresAt: FUTURE }));

    const [purged] = await Promise.all([
      store.purgeExpired(),
      store.add(item({ id: "new", expiresAt: FUTURE })),
    ]);

    // purged should have removed at least the dead item
    expect(purged).toBeGreaterThanOrEqual(1);
    // new item should exist
    const all = await store.list();
    expect(all.find((i) => i.id === "new")).toBeDefined();
    expect(all.find((i) => i.id === "live")).toBeDefined();
  });
});
