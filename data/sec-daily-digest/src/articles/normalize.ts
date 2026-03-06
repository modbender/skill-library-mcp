export function normalizeUrl(input: string): string {
  try {
    const url = new URL(input);
    for (const key of [...url.searchParams.keys()]) {
      if (key.toLowerCase().startsWith("utm_")) {
        url.searchParams.delete(key);
      }
    }
    const search = url.searchParams.toString();
    url.search = search;
    return url.toString();
  } catch {
    return input;
  }
}

export function dedupeByUrl<T extends { link: string }>(items: T[]): T[] {
  const seen = new Set<string>();
  const deduped: T[] = [];
  for (const item of items) {
    const normalized = normalizeUrl(item.link);
    if (seen.has(normalized)) {
      continue;
    }
    seen.add(normalized);
    deduped.push(item);
  }
  return deduped;
}

export function filterByHours<T extends { pubDate: Date }>(items: T[], hours: number, now: Date = new Date()): T[] {
  const cutoff = new Date(now.getTime() - hours * 60 * 60 * 1000);
  return items.filter((item) => item.pubDate.getTime() >= cutoff.getTime());
}
