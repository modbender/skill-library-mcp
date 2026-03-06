export interface OpmlFeed {
  name: string;
  xmlUrl: string;
  htmlUrl: string;
}

function pickAttr(tag: string, names: string[]): string {
  for (const name of names) {
    const match = tag.match(new RegExp(`${name}="([^"]+)"`, "i"));
    if (match?.[1]) {
      return match[1].trim();
    }
  }
  return "";
}

export function parseOpmlFeeds(xml: string): OpmlFeed[] {
  const tags = [...xml.matchAll(/<outline\b[^>]*>/gi)].map((m) => m[0]);

  return tags
    .map((tag): OpmlFeed => ({
      name: pickAttr(tag, ["text", "title"]) || "unknown",
      xmlUrl: pickAttr(tag, ["xmlUrl"]),
      htmlUrl: pickAttr(tag, ["htmlUrl"]),
    }))
    .filter((feed) => feed.xmlUrl.length > 0);
}
