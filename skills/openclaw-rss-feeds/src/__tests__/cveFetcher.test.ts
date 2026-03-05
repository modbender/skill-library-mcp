import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchCves } from '../cveFetcher';

describe('fetchCves', () => {
  const originalFetch = global.fetch;
  const originalSetTimeout = global.setTimeout;

  beforeEach(() => {
    vi.restoreAllMocks();
    global.setTimeout = ((cb: (...args: unknown[]) => void) => {
      cb();
      return 0 as unknown as NodeJS.Timeout;
    }) as typeof setTimeout;
  });

  afterEach(() => {
    global.fetch = originalFetch;
    global.setTimeout = originalSetTimeout;
  });

  it('filters by CVSS threshold, vendor match, and deduplicates across keywords', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        vulnerabilities: [
          {
            cve: {
              id: 'CVE-2026-0001',
              descriptions: [{ lang: 'en', value: 'Fortinet product allows remote attacker.' }],
              metrics: { cvssMetricV31: [{ cvssData: { baseScore: 9.1 } }] },
              configurations: [{ nodes: [{ cpeMatch: [{ criteria: 'cpe:2.3:a:fortinet:fortios:*:*:*:*:*:*:*:*' }] }] }],
            },
          },
          {
            cve: {
              id: 'CVE-2026-0002',
              descriptions: [{ lang: 'en', value: 'Fortinet info leak.' }],
              metrics: { cvssMetricV31: [{ cvssData: { baseScore: 5.0 } }] },
            },
          },
          {
            cve: {
              id: 'CVE-2026-0003',
              descriptions: [{ lang: 'en', value: 'Unrelated vendor issue.' }],
              metrics: { cvssMetricV31: [{ cvssData: { baseScore: 9.8 } }] },
            },
          },
          {
            cve: {
              id: 'CVE-2026-0001',
              descriptions: [{ lang: 'en', value: 'Duplicate entry should be deduped.' }],
              metrics: { cvssMetricV31: [{ cvssData: { baseScore: 9.1 } }] },
            },
          },
        ],
      }),
    } as Response);

    const results = await fetchCves(
      ['fortinet', 'fortios'],
      new Date('2026-02-01T00:00:00.000Z'),
      new Date('2026-03-01T00:00:00.000Z'),
      7.0,
      'fortinet-feed',
      'test-api-key'
    );

    expect(results).toHaveLength(1);
    expect(results[0]).toMatchObject({
      id: 'CVE-2026-0001',
      score: 9.1,
      feedId: 'fortinet-feed',
      url: 'https://nvd.nist.gov/vuln/detail/CVE-2026-0001',
    });

    expect(global.fetch).toHaveBeenCalledTimes(2);
    const callUrl = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
    expect(callUrl).toContain('keywordSearch=fortinet');
    const firstOptions = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0][1] as RequestInit;
    expect((firstOptions.headers as Record<string, string>).apiKey).toBe('test-api-key');
  });

  it('continues on NVD API errors and returns partial results', async () => {
    global.fetch = vi
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 503 } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          vulnerabilities: [
            {
              cve: {
                id: 'CVE-2026-0100',
                descriptions: [{ lang: 'en', value: 'Microsoft product vulnerability.' }],
                metrics: { cvssMetricV30: [{ cvssData: { baseScore: 8.0 } }] },
              },
            },
          ],
        }),
      } as Response);

    const results = await fetchCves(
      ['fortinet', 'microsoft'],
      new Date('2026-02-01T00:00:00.000Z'),
      new Date('2026-03-01T00:00:00.000Z'),
      7.0,
      'mixed-feed'
    );

    expect(results).toHaveLength(1);
    expect(results[0].id).toBe('CVE-2026-0100');
  });
});
