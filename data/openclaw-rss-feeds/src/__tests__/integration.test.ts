/**
 * Integration test for the full rss_run_digest flow.
 *
 * Mocks the data-layer modules (fetcher, cveFetcher, ghostPublisher, notifier)
 * and exercises the orchestration logic in index.ts: date-range resolution,
 * sequential feed processing, CVE enrichment, HTML formatting, Ghost publish,
 * notification dispatch, result aggregation, and error handling.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import type {
  PluginApi,
  PluginConfig,
  PluginTool,
  PluginService,
  FeedItem,
  FirmwareEntry,
  CveEntry,
} from '../types';

// ---------------------------------------------------------------------------
// Module-level mocks - intercept the modules index.ts imports directly
// ---------------------------------------------------------------------------

const fetchFeedMock = vi.fn();
vi.mock('../fetcher', () => ({
  fetchFeed: (...args: unknown[]) => fetchFeedMock(...args),
}));

const fetchCvesMock = vi.fn();
vi.mock('../cveFetcher', () => ({
  fetchCves: (...args: unknown[]) => fetchCvesMock(...args),
}));

const publishDraftMock = vi.fn();
vi.mock('../ghostPublisher', () => ({
  publishDraft: (...args: unknown[]) => publishDraftMock(...args),
}));

const notifyMock = vi.fn();
const buildDigestNotificationMock = vi.fn();
vi.mock('../notifier', () => ({
  notify: (...args: unknown[]) => notifyMock(...args),
  buildDigestNotification: (...args: unknown[]) => buildDigestNotificationMock(...args),
}));

// Import plugin entry after mocks are wired
import pluginInit from '../index';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeApi(configOverrides: Partial<PluginConfig> = {}): {
  api: PluginApi;
  tools: PluginTool[];
  services: PluginService[];
  logs: { info: string[]; warn: string[]; error: string[] };
} {
  const tools: PluginTool[] = [];
  const services: PluginService[] = [];
  const logs = { info: [] as string[], warn: [] as string[], error: [] as string[] };

  const config: PluginConfig = {
    feeds: [],
    lookbackDays: 31,
    ...configOverrides,
  };

  const api: PluginApi = {
    config,
    logger: {
      info: (msg: string) => logs.info.push(msg),
      warn: (msg: string) => logs.warn.push(msg),
      error: (msg: string) => logs.error.push(msg),
    },
    registerService(service: PluginService) {
      services.push(service);
    },
    registerTool(tool: PluginTool) {
      tools.push(tool);
    },
  };

  return { api, tools, services, logs };
}

function findTool(tools: PluginTool[], name: string): PluginTool {
  const tool = tools.find(t => t.name === name);
  if (!tool) throw new Error(`Tool "${name}" not registered`);
  return tool;
}

// Stable test dates
const twoDaysAgo = new Date();
twoDaysAgo.setDate(twoDaysAgo.getDate() - 2);

function makeFeedItems(feedId: string, feedName: string): FeedItem[] {
  return [
    {
      title: 'FortiGate 7.4.2 release notes',
      link: 'https://example.com/a',
      pubDate: twoDaysAgo,
      version: '7.4.2',
      product: 'fortigate',
      content: 'critical security patch',
      feedId,
      feedName,
    },
    {
      title: 'FortiAnalyzer 7.6.0 release notes',
      link: 'https://example.com/b',
      pubDate: twoDaysAgo,
      version: '7.6.0',
      product: 'fortianalyzer',
      content: 'major release',
      feedId,
      feedName,
    },
  ];
}

function makeFirmwareEntries(feedId: string, feedName: string): FirmwareEntry[] {
  return [
    {
      product: 'FORTIGATE',
      version: '7.4.2',
      type: 'Feature',
      pubDate: twoDaysAgo.toISOString(),
      feedId,
      feedName,
    },
    {
      product: 'FORTIANALYZER',
      version: '7.6.0',
      type: 'Major',
      pubDate: twoDaysAgo.toISOString(),
      feedId,
      feedName,
    },
  ];
}

function makeCveEntries(feedId: string): CveEntry[] {
  return [
    {
      id: 'CVE-2026-1001',
      score: 9.8,
      description: 'Fortinet FortiOS remote code execution.',
      url: 'https://nvd.nist.gov/vuln/detail/CVE-2026-1001',
      feedId,
    },
  ];
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

describe('rss_run_digest integration', () => {
  beforeEach(() => {
    fetchFeedMock.mockReset();
    fetchCvesMock.mockReset();
    publishDraftMock.mockReset();
    notifyMock.mockReset();
    buildDigestNotificationMock.mockReset();
  });

  it('runs full digest: fetch feeds, enrich CVEs, publish Ghost draft, send notifications', async () => {
    // Feed 1: Fortinet (with CVE enrichment)
    fetchFeedMock
      .mockResolvedValueOnce({
        items: makeFeedItems('fortinet', 'Fortinet'),
        firmware: makeFirmwareEntries('fortinet', 'Fortinet'),
      })
      // Feed 2: BSI (no CVE enrichment)
      .mockResolvedValueOnce({
        items: [
          {
            title: 'BSI Advisory 2026-001',
            link: 'https://bsi.example.com/advisory-1',
            pubDate: twoDaysAgo,
            content: 'security advisory',
            feedId: 'bsi',
            feedName: 'BSI',
          },
        ],
        firmware: [],
      });

    // CVE enrichment for Fortinet feed
    fetchCvesMock.mockResolvedValueOnce(makeCveEntries('fortinet'));

    // Ghost publish
    publishDraftMock.mockResolvedValueOnce({
      success: true,
      postId: 'ghost-post-1',
      postUrl: 'https://blog.example.com/p/ghost-post-1/',
    });

    // Notification
    buildDigestNotificationMock.mockReturnValueOnce('Digest notification message');
    notifyMock.mockResolvedValueOnce(undefined);

    const ghostKeyId = 'abcd1234';
    const ghostSecret = '00112233445566778899aabbccddeeff';

    const { api, tools } = makeApi({
      feeds: [
        {
          id: 'fortinet',
          name: 'Fortinet',
          url: 'https://fortinet.example.com/rss.xml',
          keywords: ['fortinet', 'fortigate'],
          enrichCve: true,
          cvssThreshold: 7.0,
          tags: ['security', 'fortinet'],
        },
        {
          id: 'bsi',
          name: 'BSI',
          url: 'https://bsi.example.com/rss.xml',
          keywords: ['security'],
          tags: ['security', 'bsi'],
        },
      ],
      ghost: {
        url: 'https://blog.example.com/',
        adminKey: `${ghostKeyId}:${ghostSecret}`,
      },
      notify: ['whatsapp:+491234567890'],
      nvdApiKey: 'test-nvd-key',
      lookbackDays: 31,
      retry: { maxRetries: 0 },
    });

    pluginInit(api);

    const tool = findTool(tools, 'rss_run_digest');
    const result = await tool.execute({}) as Record<string, unknown>;

    // Verify overall success
    expect(result.success).toBe(true);
    expect(result.feedsProcessed).toBe(2);

    // Items: 2 from Fortinet + 1 from BSI = 3
    expect(result.totalItems).toBe(3);

    // CVEs: 1 from Fortinet feed enrichment
    expect(result.totalCves).toBe(1);

    // Firmware: 2 from Fortinet feed
    expect(result.totalFirmware).toBe(2);

    // Ghost draft was published
    expect(result.ghostUrl).toBe('https://blog.example.com/p/ghost-post-1/');
    expect(result.ghostError).toBeNull();

    // Notifications were sent
    expect(result.notified).toBe(true);

    // Verify fetchFeed was called for both feeds with correct args
    expect(fetchFeedMock).toHaveBeenCalledTimes(2);
    expect(fetchFeedMock.mock.calls[0][0]).toMatchObject({
      id: 'fortinet',
      url: 'https://fortinet.example.com/rss.xml',
    });
    expect(fetchFeedMock.mock.calls[1][0]).toMatchObject({
      id: 'bsi',
      url: 'https://bsi.example.com/rss.xml',
    });

    // Verify date range was passed (startDate and endDate are Date objects)
    const startArg = fetchFeedMock.mock.calls[0][1] as Date;
    const endArg = fetchFeedMock.mock.calls[0][2] as Date;
    expect(startArg).toBeInstanceOf(Date);
    expect(endArg).toBeInstanceOf(Date);
    // endDate should be start of today, startDate should be ~31 days before
    const daysBetween = (endArg.getTime() - startArg.getTime()) / (1000 * 60 * 60 * 24);
    expect(daysBetween).toBe(31);

    // Verify CVE fetch was called only for the enrichCve feed
    expect(fetchCvesMock).toHaveBeenCalledTimes(1);
    expect(fetchCvesMock.mock.calls[0][0]).toEqual(['fortinet', 'fortigate']);
    expect(fetchCvesMock.mock.calls[0][3]).toBe(7.0); // cvssThreshold
    expect(fetchCvesMock.mock.calls[0][4]).toBe('fortinet'); // feedId
    expect(fetchCvesMock.mock.calls[0][5]).toBe('test-nvd-key'); // apiKey

    // Verify Ghost publish was called with correct args
    expect(publishDraftMock).toHaveBeenCalledTimes(1);
    const ghostArgs = publishDraftMock.mock.calls[0];
    expect(ghostArgs[0]).toEqual({
      url: 'https://blog.example.com/',
      adminKey: `${ghostKeyId}:${ghostSecret}`,
    });
    expect(ghostArgs[1]).toContain('Fortinet & BSI'); // title contains feed names
    expect(ghostArgs[1]).toContain('Security & Firmware Digest');
    expect(typeof ghostArgs[2]).toBe('string'); // HTML body
    // Tags should be deduplicated union of both feeds
    const tagNames = (ghostArgs[3] as Array<{ name: string }>).map((t: { name: string }) => t.name);
    expect(tagNames).toContain('security');
    expect(tagNames).toContain('fortinet');
    expect(tagNames).toContain('bsi');

    // Verify notification was sent
    expect(buildDigestNotificationMock).toHaveBeenCalledTimes(1);
    expect(notifyMock).toHaveBeenCalledTimes(1);
    expect(notifyMock.mock.calls[0][0]).toEqual(['whatsapp:+491234567890']);
  });

  it('continues processing when one feed fails (non-fatal errors)', async () => {
    // Feed 1: fails
    fetchFeedMock
      .mockRejectedValueOnce(new Error('DNS resolution failed'))
      // Feed 2: succeeds
      .mockResolvedValueOnce({
        items: [
          {
            title: 'Advisory item',
            link: 'https://example.com/item1',
            pubDate: twoDaysAgo,
            content: 'security advisory',
            feedId: 'working-feed',
            feedName: 'Working Feed',
          },
        ],
        firmware: [],
      });

    const { api, tools, logs } = makeApi({
      feeds: [
        {
          id: 'failing-feed',
          name: 'Failing Feed',
          url: 'https://broken.example.com/rss.xml',
        },
        {
          id: 'working-feed',
          name: 'Working Feed',
          url: 'https://example.com/rss.xml',
        },
      ],
    });

    pluginInit(api);

    const tool = findTool(tools, 'rss_run_digest');
    const result = await tool.execute({}) as Record<string, unknown>;

    // Digest still succeeds overall
    expect(result.success).toBe(true);
    expect(result.feedsProcessed).toBe(2);

    // Only the working feed contributed items
    expect(result.totalItems).toBe(1);

    // Error was logged for the failing feed
    expect(logs.error.some(l => l.includes('Failing Feed'))).toBe(true);

    // Ghost and notify were not configured
    expect(result.ghostUrl).toBeNull();
    expect(result.notified).toBe(false);
  });

  it('dry run mode skips Ghost publish and notifications', async () => {
    fetchFeedMock.mockResolvedValueOnce({
      items: [
        {
          title: 'Test item',
          link: 'https://example.com/test',
          pubDate: twoDaysAgo,
          feedId: 'test-feed',
          feedName: 'Test Feed',
        },
      ],
      firmware: [],
    });

    const { api, tools } = makeApi({
      feeds: [
        {
          id: 'test-feed',
          name: 'Test Feed',
          url: 'https://example.com/rss.xml',
        },
      ],
      ghost: {
        url: 'https://blog.example.com/',
        adminKey: 'id:00112233445566778899aabbccddeeff',
      },
      notify: ['telegram:123456'],
    });

    pluginInit(api);

    const tool = findTool(tools, 'rss_run_digest');
    const result = await tool.execute({ dryRun: true }) as Record<string, unknown>;

    expect(result.dryRun).toBe(true);
    expect(result.success).toBe(true);
    expect(result.totalItems).toBe(1);

    // Ghost and notify should NOT have been called
    expect(publishDraftMock).not.toHaveBeenCalled();
    expect(notifyMock).not.toHaveBeenCalled();
  });

  it('handles empty feeds config gracefully', async () => {
    const { api, tools, logs } = makeApi({ feeds: [] });

    pluginInit(api);

    const tool = findTool(tools, 'rss_run_digest');
    const result = await tool.execute({}) as Record<string, unknown>;

    expect(result.success).toBe(true);
    expect(result.feedsProcessed).toBe(0);
    expect(result.totalItems).toBe(0);
    expect(result.totalCves).toBe(0);
    expect(result.totalFirmware).toBe(0);

    // No modules should have been called
    expect(fetchFeedMock).not.toHaveBeenCalled();
    expect(fetchCvesMock).not.toHaveBeenCalled();
    expect(publishDraftMock).not.toHaveBeenCalled();
    expect(notifyMock).not.toHaveBeenCalled();

    // Warning about no feeds should be logged
    expect(logs.warn.some(l => l.includes('No feeds configured'))).toBe(true);
  });

  it('handles Ghost publish failure non-fatally', async () => {
    fetchFeedMock.mockResolvedValueOnce({
      items: [
        {
          title: 'Item 1',
          link: 'https://example.com/1',
          pubDate: twoDaysAgo,
          feedId: 'feed-1',
          feedName: 'Feed One',
        },
      ],
      firmware: [],
    });

    // Ghost returns failure
    publishDraftMock.mockResolvedValueOnce({
      success: false,
      error: 'Internal Server Error',
    });

    const { api, tools, logs } = makeApi({
      feeds: [
        {
          id: 'feed-1',
          name: 'Feed One',
          url: 'https://example.com/rss.xml',
        },
      ],
      ghost: {
        url: 'https://blog.example.com/',
        adminKey: 'keyid:00112233445566778899aabbccddeeff',
      },
    });

    pluginInit(api);

    const tool = findTool(tools, 'rss_run_digest');
    const result = await tool.execute({}) as Record<string, unknown>;

    // Digest still succeeds overall despite Ghost failure
    expect(result.success).toBe(true);
    expect(result.totalItems).toBe(1);
    expect(result.ghostUrl).toBeNull();
    expect(result.ghostError).toBeTruthy();

    // Ghost error was logged
    expect(logs.error.some(l => l.includes('Ghost publish failed'))).toBe(true);
  });
});
