export interface Article {
  title: string;
  link: string;
  pubDate: Date;
  description: string;
  sourceName: string;
  sourceUrl: string;
}

function stripHtml(input: string): string {
  return input
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, "\"")
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

function getTag(xml: string, tagName: string): string {
  const match = xml.match(new RegExp(`<${tagName}[^>]*>([\\s\\S]*?)</${tagName}>`, "i"));
  return match?.[1]?.trim() ?? "";
}

function getAttr(xml: string, tagName: string, attrName: string): string {
  const match = xml.match(new RegExp(`<${tagName}[^>]*\\b${attrName}="([^"]+)"[^>]*>`, "i"));
  return match?.[1]?.trim() ?? "";
}

function parseDate(input: string): Date {
  const d = new Date(input);
  return Number.isNaN(d.getTime()) ? new Date(0) : d;
}

function parseRss(xml: string, sourceName: string, sourceUrl: string): Article[] {
  const items = [...xml.matchAll(/<item\b[\s\S]*?<\/item>/gi)];
  return items
    .map((m) => m[0])
    .map((item): Article => ({
      title: stripHtml(getTag(item, "title")),
      link: getTag(item, "link") || getTag(item, "guid"),
      pubDate: parseDate(getTag(item, "pubDate") || getTag(item, "dc:date") || getTag(item, "date")),
      description: stripHtml(getTag(item, "description") || getTag(item, "content:encoded")),
      sourceName,
      sourceUrl,
    }))
    .filter((article) => article.title.length > 0 || article.link.length > 0);
}

function parseAtom(xml: string, sourceName: string, sourceUrl: string): Article[] {
  const entries = [...xml.matchAll(/<entry\b[\s\S]*?<\/entry>/gi)];
  return entries
    .map((m) => m[0])
    .map((entry): Article => ({
      title: stripHtml(getTag(entry, "title")),
      link: getAttr(entry, "link", "href"),
      pubDate: parseDate(getTag(entry, "published") || getTag(entry, "updated")),
      description: stripHtml(getTag(entry, "summary") || getTag(entry, "content")),
      sourceName,
      sourceUrl,
    }))
    .filter((article) => article.title.length > 0 || article.link.length > 0);
}

export function parseFeedItems(xml: string, sourceName: string, sourceUrl: string): Article[] {
  const normalized = xml.trim();
  const isAtom = normalized.includes("<feed");
  return isAtom ? parseAtom(normalized, sourceName, sourceUrl) : parseRss(normalized, sourceName, sourceUrl);
}
