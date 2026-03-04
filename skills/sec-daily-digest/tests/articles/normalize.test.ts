import { describe, expect, test } from "bun:test";
import { dedupeByUrl, filterByHours, normalizeUrl } from "../../src/articles/normalize";

describe("normalize helpers", () => {
  test("normalizeUrl strips utm_* parameters", () => {
    const normalized = normalizeUrl("https://example.com/a?utm_source=rss&a=1&utm_medium=email");
    expect(normalized).toContain("a=1");
    expect(normalized.includes("utm_")).toBe(false);
  });

  test("dedupeByUrl keeps first unique normalized url", () => {
    const items = dedupeByUrl([
      { link: "https://example.com/a?utm_source=rss", title: "one" },
      { link: "https://example.com/a", title: "two" },
      { link: "https://example.com/b", title: "three" },
    ]);
    expect(items.length).toBe(2);
    expect(items[0]?.title).toBe("one");
  });

  test("filterByHours keeps recent entries", () => {
    const now = new Date("2026-02-27T12:00:00.000Z");
    const data = [
      { pubDate: new Date("2026-02-27T10:00:00.000Z"), id: 1 },
      { pubDate: new Date("2026-02-25T10:00:00.000Z"), id: 2 },
    ];
    const kept = filterByHours(data, 24, now);
    expect(kept.length).toBe(1);
    expect(kept[0]?.id).toBe(1);
  });
});
