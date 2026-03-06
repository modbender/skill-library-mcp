// @elvatis/openclaw-rss-feeds - NVD CVE API v2.0 fetcher
import type { CveEntry } from './types';

const NVD_API_BASE = 'https://services.nvd.nist.gov/rest/json/cves/2.0';

// Sleep helper for rate limiting
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Format a Date for NVD API: "YYYY-MM-DDTHH:mm:ss.sss"
function toNvdDate(d: Date): string {
  return d.toISOString().replace('Z', '');
}

interface NvdVulnerability {
  cve: {
    id: string;
    descriptions: Array<{ lang: string; value: string }>;
    metrics?: {
      cvssMetricV31?: Array<{ cvssData: { baseScore: number } }>;
      cvssMetricV30?: Array<{ cvssData: { baseScore: number } }>;
      cvssMetricV2?: Array<{ cvssData: { baseScore: number } }>;
    };
    configurations?: Array<{
      nodes: Array<{
        cpeMatch?: Array<{ criteria?: string }>;
      }>;
    }>;
  };
}

interface NvdApiResponse {
  vulnerabilities?: NvdVulnerability[];
  totalResults?: number;
  resultsPerPage?: number;
  startIndex?: number;
}

function extractScore(vuln: NvdVulnerability): number | undefined {
  const metrics = vuln.cve.metrics;
  if (!metrics) return undefined;

  if (metrics.cvssMetricV31 && metrics.cvssMetricV31.length > 0) {
    return metrics.cvssMetricV31[0].cvssData.baseScore;
  }
  if (metrics.cvssMetricV30 && metrics.cvssMetricV30.length > 0) {
    return metrics.cvssMetricV30[0].cvssData.baseScore;
  }
  if (metrics.cvssMetricV2 && metrics.cvssMetricV2.length > 0) {
    return metrics.cvssMetricV2[0].cvssData.baseScore;
  }
  return undefined;
}

function isVendorMatch(vuln: NvdVulnerability, keywords: string[]): boolean {
  const cve = vuln.cve;
  const desc = cve.descriptions.find(d => d.lang === 'en')?.value ?? '';

  // Check description
  for (const kw of keywords) {
    if (desc.toLowerCase().includes(kw.toLowerCase())) return true;
  }

  // Check CPE configurations
  for (const cfg of cve.configurations ?? []) {
    for (const node of cfg.nodes) {
      for (const cpe of node.cpeMatch ?? []) {
        const criteria = cpe.criteria ?? '';
        for (const kw of keywords) {
          if (criteria.toLowerCase().includes(`:${kw.toLowerCase()}:`)) return true;
        }
      }
    }
  }

  return false;
}

export async function fetchCves(
  keywords: string[],
  startDate: Date,
  endDate: Date,
  cvssThreshold: number,
  feedId: string,
  apiKey?: string
): Promise<CveEntry[]> {
  if (!keywords || keywords.length === 0) return [];

  const cves: CveEntry[] = [];
  const seen = new Set<string>();

  for (const keyword of keywords) {
    try {
      const params = new URLSearchParams({
        keywordSearch: keyword,
        pubStartDate: toNvdDate(startDate),
        pubEndDate: toNvdDate(endDate),
      });

      const url = `${NVD_API_BASE}?${params.toString()}`;
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (apiKey) {
        headers['apiKey'] = apiKey;
      }

      const response = await fetch(url, {
        headers,
        signal: AbortSignal.timeout(30000),
      });

      if (!response.ok) {
        console.warn(`[cveFetcher] NVD API returned ${response.status} for keyword "${keyword}"`);
        // Still sleep to respect rate limits
        await sleep(6000);
        continue;
      }

      const data = (await response.json()) as NvdApiResponse;
      const vulns = data.vulnerabilities ?? [];

      for (const vuln of vulns) {
        const cveId = vuln.cve.id;
        if (seen.has(cveId)) continue;

        const score = extractScore(vuln);
        if (score === undefined || score < cvssThreshold) continue;

        // Vendor/keyword matching via description OR CPE
        if (!isVendorMatch(vuln, keywords)) continue;

        seen.add(cveId);

        const description =
          vuln.cve.descriptions.find(d => d.lang === 'en')?.value ?? '';

        cves.push({
          id: cveId,
          score,
          description,
          url: `https://nvd.nist.gov/vuln/detail/${cveId}`,
          feedId,
        });
      }

      // Rate limit: 6s between requests (NVD recommendation)
      await sleep(6000);
    } catch (err) {
      // Non-fatal: log and continue
      console.warn(`[cveFetcher] Failed to fetch CVEs for keyword "${keyword}":`, err);
      // Still sleep to avoid hammering NVD on retry scenarios
      await sleep(6000);
    }
  }

  // Sort by score descending
  cves.sort((a, b) => b.score - a.score);

  return cves;
}
