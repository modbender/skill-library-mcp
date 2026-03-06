import { describe, it, expect } from 'vitest';
import { formatDigestBody } from '../formatter';
import type { FeedResult } from '../types';

describe('formatDigestBody', () => {
  it('renders feed sections, escapes html, and includes combined CVE section', () => {
    const feedResults: FeedResult[] = [
      {
        feedId: 'f1',
        feedName: 'Fortinet <Feed>',
        enrichCve: true,
        productHighlightPattern: 'FortiGate',
        items: [
          {
            title: 'General <News>',
            link: 'https://example.com/news',
            pubDate: new Date('2026-02-10T10:00:00.000Z'),
            feedId: 'f1',
            feedName: 'Fortinet <Feed>',
          },
        ],
        firmware: [
          {
            product: 'FORTIGATE',
            version: '7.4.2',
            type: 'Feature',
            pubDate: '2026-02-10T10:00:00.000Z',
            docsUrl: 'https://docs.example.com/fortigate/7.4.2',
            feedId: 'f1',
            feedName: 'Fortinet <Feed>',
          },
        ],
        cves: [
          {
            id: 'CVE-2026-1111',
            score: 9.2,
            description: 'FortiGate allows remote attacker to execute code <script>',
            url: 'https://nvd.nist.gov/vuln/detail/CVE-2026-1111',
            feedId: 'f1',
          },
        ],
      },
      {
        feedId: 'f2',
        feedName: 'BSI',
        items: [],
        firmware: [],
        cves: [
          {
            id: 'CVE-2026-2222',
            score: 7.5,
            description: 'BSI related issue',
            url: 'https://nvd.nist.gov/vuln/detail/CVE-2026-2222',
            feedId: 'f2',
          },
        ],
      },
    ];

    const html = formatDigestBody(feedResults, {
      startDate: new Date('2026-02-01T00:00:00.000Z'),
      endDate: new Date('2026-03-01T00:00:00.000Z'),
      generatedAt: new Date('2026-03-01T09:00:00.000Z'),
    });

    expect(html).toContain('Digest Summary');
    expect(html).toContain('Feeds monitored: <strong>2</strong>');
    expect(html).toContain('Fortinet &lt;Feed&gt;');
    expect(html).toContain('General &lt;News&gt;');
    expect(html).toContain('Documentation');
    expect(html).toContain('CVE-2026-1111');
    expect(html).toContain('All CVEs - Combined View');

    expect(html).not.toContain('<script>');
    expect(html).toContain('&lt;script&gt;');
  });
});
