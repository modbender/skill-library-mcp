import { beforeEach, describe, expect, it, vi } from 'vitest';
import fetch from 'node-fetch';
import {
  near_content_news,
  near_content_thread,
  near_content_tutorial,
  near_content_update
} from '../content-creator.js';

vi.mock('node-fetch', () => ({
  default: vi.fn()
}));

const mockedFetch = vi.mocked(fetch);

function jsonResponse(body: unknown): any {
  return {
    ok: true,
    json: async () => body,
    text: async () => JSON.stringify(body)
  };
}

function textResponse(body: string): any {
  return {
    ok: true,
    json: async () => ({}),
    text: async () => body
  };
}

describe('near content creator', () => {
  beforeEach(() => {
    mockedFetch.mockReset();
    mockedFetch.mockImplementation(async (url: any) => {
      const target = String(url);

      if (target.includes('coingecko')) {
        return jsonResponse({
          near: {
            usd: 4.2,
            usd_24h_change: 2.5,
            usd_market_cap: 5000000000,
            usd_24h_vol: 350000000
          }
        });
      }

      if (target.includes('rpc.mainnet.near.org')) {
        return jsonResponse({
          result: {
            chain_id: 'mainnet',
            sync_info: { latest_block_height: 123456789 }
          }
        });
      }

      if (target.includes('nearblocks.io/v1/stats')) {
        return jsonResponse({
          stats: [{ active_accounts_24h: 76543 }]
        });
      }

      if (target.includes('near.org/blog/rss.xml')) {
        return textResponse(`
          <rss><channel>
            <item>
              <title>NEAR ecosystem update</title>
              <link>https://near.org/blog/ecosystem-update</link>
              <pubDate>Fri, 20 Feb 2026 10:00:00 GMT</pubDate>
              <description>Major ecosystem progress and updates.</description>
            </item>
            <item>
              <title>NEAR ecosystem update</title>
              <link>https://near.org/blog/ecosystem-update</link>
              <pubDate>Fri, 20 Feb 2026 09:00:00 GMT</pubDate>
              <description>Duplicate item for dedupe test.</description>
            </item>
          </channel></rss>
        `);
      }

      if (target.includes('api.github.com/repos/near/nearcore/releases')) {
        return jsonResponse([
          {
            name: 'nearcore v2.2.0',
            html_url: 'https://github.com/near/nearcore/releases/tag/v2.2.0',
            published_at: '2026-02-19T10:00:00Z',
            body: 'Performance and reliability improvements'
          }
        ]);
      }

      if (target.includes('api.github.com/repos/near/near-api-js/releases')) {
        return jsonResponse([
          {
            name: 'near-api-js v4.1.0',
            html_url: 'https://github.com/near/near-api-js/releases/tag/v4.1.0',
            published_at: '2026-02-18T10:00:00Z',
            body: 'DX updates and fixes'
          }
        ]);
      }

      return {
        ok: false,
        json: async () => ({}),
        text: async () => ''
      } as any;
    });
  });

  it('creates thread format', async () => {
    const out = await near_content_thread('NEAR developer onboarding '.repeat(20));
    expect(out).toHaveLength(8);
    out.forEach((line, i) => {
      expect(line.startsWith(`${i + 1}/8 `)).toBe(true);
      expect(line.length).toBeLessThanOrEqual(280);
    });
  });

  it('creates market update text', async () => {
    const out = await near_content_update();
    expect(out).toContain('NEAR Daily Market Update');
    expect(out).toContain('Price: $4.2');
    expect(out).toContain('Data Quality:');
  });

  it('creates news list', async () => {
    const out = await near_content_news();
    expect(out.length).toBeGreaterThan(0);
    const urls = out.map((i) => i.url);
    expect(new Set(urls).size).toEqual(urls.length);
    expect(urls.some((u) => u.includes('near.org') || u.includes('github.com/near/nearcore'))).toBe(true);
  });

  it('creates tutorial text', async () => {
    const out = await near_content_tutorial('smart contract basics');
    expect(out).toContain('NEAR Tutorial');
    expect(out).toContain('smart contract basics');
  });

  it('returns fallback news when sources are unavailable', async () => {
    mockedFetch.mockImplementation(async () => {
      return {
        ok: false,
        json: async () => ({}),
        text: async () => ''
      } as any;
    });

    const out = await near_content_news();
    expect(out.length).toBeGreaterThan(0);
    expect(out[0].source).toBe('Fallback');
  });
});
