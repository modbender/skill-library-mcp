import { describe, expect, test } from "bun:test";
import { parseFeedItems } from "../../src/rss/parse";

describe("parseFeedItems", () => {
  test("parses RSS 2.0 items", () => {
    const xml = `<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>RSS Title</title>
      <link>https://example.com/rss-1</link>
      <pubDate>Fri, 27 Feb 2026 09:00:00 GMT</pubDate>
      <description>Hello RSS</description>
    </item>
  </channel>
</rss>`;
    const items = parseFeedItems(xml, "feed-a", "https://example.com");
    expect(items.length).toBe(1);
    expect(items[0]?.title).toBe("RSS Title");
    expect(items[0]?.link).toBe("https://example.com/rss-1");
  });

  test("parses Atom entries", () => {
    const xml = `<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Atom Title</title>
    <link href="https://example.com/atom-1" />
    <updated>2026-02-27T09:00:00Z</updated>
    <summary>Hello Atom</summary>
  </entry>
</feed>`;
    const items = parseFeedItems(xml, "feed-b", "https://example.com");
    expect(items.length).toBe(1);
    expect(items[0]?.title).toBe("Atom Title");
    expect(items[0]?.link).toBe("https://example.com/atom-1");
  });
});
