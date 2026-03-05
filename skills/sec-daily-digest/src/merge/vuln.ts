export interface VulnerabilityItemInput {
  title: string;
  summary: string;
  link: string;
  source: string;
}

export interface VulnerabilityEvent {
  key: string;
  title: string;
  summary: string;
  cves: string[];
  references: Array<{ link: string; source: string }>;
}

const CVE_RE = /CVE-\d{4}-\d{4,7}/gi;
const STOP_WORDS = new Set([
  "the",
  "and",
  "for",
  "with",
  "that",
  "this",
  "from",
  "same",
  "details",
  "published",
  "release",
  "released",
  "researchers",
  "critical",
]);

function extractCves(input: string): string[] {
  return [...new Set((input.match(CVE_RE) ?? []).map((m) => m.toUpperCase()))];
}

function tokenize(input: string): Set<string> {
  return new Set(
    input
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, " ")
      .split(/\s+/)
      .map((token) => token.trim())
      .filter((token) => token.length >= 3 && !STOP_WORDS.has(token)),
  );
}

function jaccard(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 && b.size === 0) {
    return 1;
  }
  let intersection = 0;
  for (const token of a) {
    if (b.has(token)) {
      intersection += 1;
    }
  }
  const union = a.size + b.size - intersection;
  return union === 0 ? 0 : intersection / union;
}

function buildSemanticKey(title: string, summary: string): string {
  const tokens = [...tokenize(`${title} ${summary}`)].slice(0, 6).sort();
  return `semantic:${tokens.join("-") || "unknown"}`;
}

export function mergeVulnerabilityItems(items: VulnerabilityItemInput[]): VulnerabilityEvent[] {
  const byKey = new Map<string, VulnerabilityEvent>();

  for (const item of items) {
    const fullText = `${item.title} ${item.summary}`;
    const cves = extractCves(fullText);
    let key = cves[0];

    if (!key) {
      const tokens = tokenize(fullText);
      let bestKey = "";
      let bestScore = 0;

      for (const [existingKey, event] of byKey.entries()) {
        if (!existingKey.startsWith("semantic:")) {
          continue;
        }
        const score = jaccard(tokens, tokenize(`${event.title} ${event.summary}`));
        if (score > bestScore) {
          bestScore = score;
          bestKey = existingKey;
        }
      }

      key = bestScore >= 0.3 ? bestKey : buildSemanticKey(item.title, item.summary);
    }

    const current = byKey.get(key);
    if (!current) {
      byKey.set(key, {
        key,
        title: item.title,
        summary: item.summary,
        cves,
        references: [{ link: item.link, source: item.source }],
      });
      continue;
    }

    const refExists = current.references.some((ref) => ref.link === item.link);
    if (!refExists) {
      current.references.push({ link: item.link, source: item.source });
    }

    current.cves = [...new Set([...current.cves, ...cves])];
  }

  return [...byKey.values()].sort((a, b) => b.references.length - a.references.length);
}
