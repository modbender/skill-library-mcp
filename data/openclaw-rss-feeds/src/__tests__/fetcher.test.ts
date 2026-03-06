import { describe, it, expect, vi, beforeEach } from 'vitest';

const parseURLMock = vi.fn();

vi.mock('rss-parser', () => {
  return {
    default: vi.fn().mockImplementation(() => ({
      parseURL: parseURLMock,
    })),
  };
});

import { fetchFeed } from '../fetcher';
import type { FeedConfig, RetryConfig } from '../types';

const baseFeed: FeedConfig = {
  id: 'test',
  name: 'Test Feed',
  url: 'https://example.com/rss.xml',
};
const startDate = new Date('2026-02-01T00:00:00.000Z');
const endDate = new Date('2026-03-01T00:00:00.000Z');

describe('fetchFeed', () => {
  beforeEach(() => {
    parseURLMock.mockReset();
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  it('filters by date and keywords, deduplicates, and builds firmware/docs metadata', async () => {
    parseURLMock.mockResolvedValue({
      items: [
        {
          title: 'FortiGate 7.4.2 release notes',
          link: 'https://example.com/a',
          isoDate: '2026-02-10T10:00:00.000Z',
          contentSnippet: 'critical security fix',
        },
        {
          title: 'FortiGate 7.4.2 release notes',
          link: 'https://example.com/a',
          isoDate: '2026-02-10T10:00:00.000Z',
          contentSnippet: 'critical security fix',
        },
        {
          title: 'FortiGate 7.4.4 release notes',
          link: 'https://example.com/b',
          isoDate: '2026-02-12T10:00:00.000Z',
          contentSnippet: 'critical patch release',
        },
        {
          title: 'FortiAnalyzer 7.0.0 release notes',
          link: 'https://example.com/c',
          isoDate: '2026-01-01T10:00:00.000Z',
          contentSnippet: 'critical but too old',
        },
        {
          title: 'General advisory',
          link: 'https://example.com/d',
          isoDate: '2026-02-11T10:00:00.000Z',
          contentSnippet: 'informational only',
        },
      ],
    });

    const feed: FeedConfig = {
      id: 'fortinet',
      name: 'Fortinet',
      url: 'https://example.com/rss.xml',
      keywords: ['critical'],
      docsUrlTemplate: 'https://docs.example.com/{product}/{version}',
    };

    const startDate = new Date('2026-02-01T00:00:00.000Z');
    const endDate = new Date('2026-03-01T00:00:00.000Z');

    const result = await fetchFeed(feed, startDate, endDate);

    expect(result.items).toHaveLength(2);
    expect(result.items.map(i => i.link)).toEqual([
      'https://example.com/a',
      'https://example.com/b',
    ]);

    expect(result.firmware).toHaveLength(2);
    expect(result.firmware[0]).toMatchObject({
      product: 'FORTIGATE',
      version: '7.4.4',
      type: 'Feature',
      docsUrl: 'https://docs.example.com/fortigate/7.4.4',
    });
    expect(result.firmware[1]).toMatchObject({
      product: 'FORTIGATE',
      version: '7.4.2',
      type: 'Feature',
      docsUrl: 'https://docs.example.com/fortigate/7.4.2',
    });

    expect(parseURLMock).toHaveBeenCalledWith('https://example.com/rss.xml');
  });

  it('returns empty arrays for empty feeds', async () => {
    parseURLMock.mockResolvedValue({ items: [] });

    const result = await fetchFeed(
      {
        id: 'empty',
        name: 'Empty Feed',
        url: 'https://example.com/empty.xml',
      },
      startDate,
      endDate
    );

    expect(result.items).toEqual([]);
    expect(result.firmware).toEqual([]);
  });
});

describe('fetchFeed retry/backoff', () => {
  beforeEach(() => {
    parseURLMock.mockReset();
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  it('retries on failure and succeeds on a later attempt', async () => {
    parseURLMock
      .mockRejectedValueOnce(new Error('Network error'))
      .mockRejectedValueOnce(new Error('Timeout'))
      .mockResolvedValueOnce({
        items: [
          {
            title: 'Item 1',
            link: 'https://example.com/1',
            isoDate: '2026-02-10T10:00:00.000Z',
            contentSnippet: 'test',
          },
        ],
      });

    const retry: RetryConfig = { maxRetries: 3, initialDelayMs: 100, backoffMultiplier: 2 };
    const result = await fetchFeed(baseFeed, startDate, endDate, retry);

    expect(parseURLMock).toHaveBeenCalledTimes(3);
    expect(result.items).toHaveLength(1);
    expect(result.items[0].title).toBe('Item 1');
  });

  it('throws after exhausting all retries', async () => {
    parseURLMock.mockRejectedValue(new Error('Persistent failure'));

    const retry: RetryConfig = { maxRetries: 2, initialDelayMs: 50, backoffMultiplier: 2 };

    await expect(fetchFeed(baseFeed, startDate, endDate, retry)).rejects.toThrow(
      'Persistent failure'
    );

    // initial attempt + 2 retries = 3 calls
    expect(parseURLMock).toHaveBeenCalledTimes(3);
  });

  it('succeeds immediately with no retries when fetch works on first attempt', async () => {
    parseURLMock.mockResolvedValue({ items: [] });

    const retry: RetryConfig = { maxRetries: 3, initialDelayMs: 100, backoffMultiplier: 2 };
    const result = await fetchFeed(baseFeed, startDate, endDate, retry);

    expect(parseURLMock).toHaveBeenCalledTimes(1);
    expect(result.items).toEqual([]);
  });

  it('uses default retry config when retry is undefined', async () => {
    parseURLMock
      .mockRejectedValueOnce(new Error('Transient'))
      .mockResolvedValueOnce({ items: [] });

    const result = await fetchFeed(baseFeed, startDate, endDate, undefined);

    // With default config (maxRetries=3), a single failure followed by success should work
    expect(parseURLMock).toHaveBeenCalledTimes(2);
    expect(result.items).toEqual([]);
  });

  it('does not retry when maxRetries is 0', async () => {
    parseURLMock.mockRejectedValue(new Error('Immediate failure'));

    const retry: RetryConfig = { maxRetries: 0 };

    await expect(fetchFeed(baseFeed, startDate, endDate, retry)).rejects.toThrow(
      'Immediate failure'
    );

    expect(parseURLMock).toHaveBeenCalledTimes(1);
  });
});
