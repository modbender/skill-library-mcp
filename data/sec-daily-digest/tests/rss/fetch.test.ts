import { describe, expect, test } from "bun:test";
import { buildFetchHeaders } from "../../src/rss/fetch";

describe("buildFetchHeaders", () => {
  test("contains anti-basic-scraping headers", () => {
    const headers = buildFetchHeaders(0);
    expect(headers["User-Agent"]).toContain("sec-daily-digest");
    expect(headers["Accept"]).toContain("application/rss+xml");
    expect(headers["Accept-Language"]).toContain("en-US");
  });

  test("rotates user agent by seed", () => {
    const a = buildFetchHeaders(0)["User-Agent"];
    const b = buildFetchHeaders(1)["User-Agent"];
    expect(a).not.toBe("");
    expect(b).not.toBe("");
    expect(a).not.toBe(b);
  });
});
