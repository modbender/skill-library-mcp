import { describe, expect, test } from "bun:test";
import { parseOpmlFeeds } from "../../src/opml/parse";

describe("parseOpmlFeeds", () => {
  test("extracts feed entries from opml outline nodes", () => {
    const xml = `
<opml version="1.0">
  <body>
    <outline text="Feed A" xmlUrl="https://example.com/a.xml" htmlUrl="https://example.com/a"/>
    <outline title="Feed B" xmlUrl="https://example.com/b.xml" htmlUrl="https://example.com/b"/>
  </body>
</opml>`;

    const feeds = parseOpmlFeeds(xml);
    expect(feeds.length).toBe(2);
    expect(feeds[0]?.name).toBe("Feed A");
    expect(feeds[0]?.xmlUrl).toBe("https://example.com/a.xml");
    expect(feeds[1]?.name).toBe("Feed B");
  });

  test("ignores outlines without xmlUrl", () => {
    const xml = `
<opml>
  <body>
    <outline text="folder">
      <outline text="Feed X" xmlUrl="https://example.com/x.xml" />
    </outline>
  </body>
</opml>`;
    const feeds = parseOpmlFeeds(xml);
    expect(feeds.length).toBe(1);
    expect(feeds[0]?.xmlUrl).toBe("https://example.com/x.xml");
  });
});
