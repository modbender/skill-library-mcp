// @elvatis/openclaw-rss-feeds - Plugin entry point
import cron from 'node-cron';
import { fetchFeed } from './fetcher';
import { fetchCves } from './cveFetcher';
import { formatDigestBody } from './formatter';
import { publishDraft } from './ghostPublisher';
import { notify, buildDigestNotification } from './notifier';
import type {
  PluginApi,
  PluginConfig,
  FeedResult,
  DigestResult,
} from './types';

// Resolve date range from config
function resolveDateRange(config: PluginConfig): { startDate: Date; endDate: Date } {
  const now = new Date();
  const lookbackDays = config.lookbackDays ?? 31;

  const endDate = new Date(now);
  endDate.setHours(0, 0, 0, 0); // Start of today

  const startDate = new Date(endDate);
  startDate.setDate(startDate.getDate() - lookbackDays);

  return { startDate, endDate };
}

// Main digest runner
async function runDigest(api: PluginApi): Promise<DigestResult> {
  const config = api.config;
  const feeds = Array.isArray(config.feeds) ? config.feeds : [];
  const { startDate, endDate } = resolveDateRange(config);

  api.logger.info(
    `[rss-feeds] Running digest for period ${startDate.toISOString()} → ${endDate.toISOString()}`
  );

  const feedResults: FeedResult[] = [];

  // Process each feed sequentially (NVD rate limits require sequential CVE fetches)
  for (const feedConfig of feeds) {
    api.logger.info(`[rss-feeds] Fetching feed: ${feedConfig.name} (${feedConfig.url})`);

    const feedResult: FeedResult = {
      feedId: feedConfig.id,
      feedName: feedConfig.name,
      enrichCve: feedConfig.enrichCve ?? false,
      productHighlightPattern: feedConfig.productHighlightPattern,
      items: [],
      firmware: [],
      cves: [],
    };

    // Fetch RSS/Atom items
    try {
      const { items, firmware } = await fetchFeed(feedConfig, startDate, endDate, config.retry);
      feedResult.items = items;
      feedResult.firmware = firmware;
      api.logger.info(
        `[rss-feeds] Feed "${feedConfig.name}": ${items.length} items, ${firmware.length} firmware entries`
      );
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : String(err);
      api.logger.error(`[rss-feeds] Feed "${feedConfig.name}" fetch failed: ${errMsg}`);
      feedResult.error = errMsg;
      // Continue to next feed - don't abort the whole digest
    }

    // Optionally enrich with CVE data
    if (feedConfig.enrichCve && feedConfig.keywords && feedConfig.keywords.length > 0) {
      api.logger.info(`[rss-feeds] Fetching CVEs for feed "${feedConfig.name}"...`);
      try {
        const cves = await fetchCves(
          feedConfig.keywords,
          startDate,
          endDate,
          feedConfig.cvssThreshold ?? 6.5,
          feedConfig.id,
          config.nvdApiKey
        );
        feedResult.cves = cves;
        api.logger.info(`[rss-feeds] CVEs found for "${feedConfig.name}": ${cves.length}`);
      } catch (err) {
        // NVD failure is non-fatal
        const errMsg = err instanceof Error ? err.message : String(err);
        api.logger.warn(`[rss-feeds] CVE fetch failed for "${feedConfig.name}": ${errMsg}`);
        feedResult.cveError = errMsg;
      }
    }

    feedResults.push(feedResult);
  }

  // Build digest HTML
  const html = formatDigestBody(feedResults, { startDate, endDate, generatedAt: new Date() });

  const totalFirmware = feedResults.reduce((acc, fr) => acc + fr.firmware.length, 0);
  const totalCves = feedResults.reduce((acc, fr) => acc + fr.cves.length, 0);
  const totalItems = feedResults.reduce((acc, fr) => acc + fr.items.length, 0);

  // Build a title
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
  ];
  const period = `${months[startDate.getMonth()]} ${startDate.getFullYear()}`;
  const feedNames = feeds.map(f => f.name).join(' & ');
  const titlePrefix = feedNames || 'Configured Feeds';
  const title = `🛡️ ${titlePrefix} - Security & Firmware Digest | ${period}`;

  let ghostUrl: string | undefined;
  let ghostError: string | undefined;

  // Publish to Ghost (if configured)
  if (config.ghost) {
    api.logger.info(`[rss-feeds] Publishing draft to Ghost: ${config.ghost.url}`);

    try {
      // Collect all tags from all feed configs
      const allTags = Array.from(
        new Set(feeds.flatMap(f => f.tags ?? []))
      ).map(name => ({ name }));

      const result = await publishDraft(
        config.ghost,
        title,
        html,
        allTags,
        `Monthly security digest for ${period}.`
      );

      if (result.success) {
        ghostUrl = result.postUrl;
        api.logger.info(`[rss-feeds] Ghost draft created: ${ghostUrl}`);
      } else {
        ghostError = result.error;
        api.logger.error(`[rss-feeds] Ghost publish failed: ${ghostError}`);
      }
    } catch (err) {
      ghostError = err instanceof Error ? err.message : String(err);
      api.logger.error(`[rss-feeds] Ghost publish crashed: ${ghostError}`);
    }
  } else {
    api.logger.info('[rss-feeds] No Ghost config - skipping draft creation');
  }

  // Send notifications (if configured)
  let notified = false;
  if (config.notify && config.notify.length > 0) {
    const message = buildDigestNotification({
      title,
      firmwareCount: totalFirmware,
      cveCount: totalCves,
      ghostUrl,
      ghostError,
      period,
    });

    try {
      await notify(config.notify, message);
      notified = true;
      api.logger.info(`[rss-feeds] Notifications sent to ${config.notify.length} target(s)`);
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : String(err);
      api.logger.warn(`[rss-feeds] Notification failed: ${errMsg}`);
    }
  }

  const result: DigestResult = {
    success: true,
    feedsProcessed: feedResults.length,
    totalItems,
    totalCves,
    totalFirmware,
    ghostUrl,
    ghostError,
    notified,
    startDate,
    endDate,
    feedResults,
  };

  api.logger.info(
    `[rss-feeds] Digest complete. Feeds: ${result.feedsProcessed}, ` +
    `Items: ${result.totalItems}, Firmware: ${result.totalFirmware}, CVEs: ${result.totalCves}`
  );

  return result;
}

// Plugin entry point
export default function (api: PluginApi): void {
  const config = api.config;
  const feeds = Array.isArray(config.feeds) ? config.feeds : [];

  if (feeds.length === 0) {
    api.logger.warn('[rss-feeds] No feeds configured. The digest will run but produce empty output.');
  }

  // Register scheduled service (if cron schedule is configured)
  if (config.schedule && config.schedule.trim() !== '') {
    let cronTask: ReturnType<typeof cron.schedule> | undefined;

    api.registerService({
      id: 'rss-digest-scheduler',
      start() {
        api.logger.info(`[rss-feeds] Starting scheduled digest service (${config.schedule})`);

        if (!cron.validate(config.schedule!)) {
          api.logger.error(`[rss-feeds] Invalid cron expression: "${config.schedule}"`);
          return;
        }

        cronTask = cron.schedule(config.schedule!, () => {
          api.logger.info('[rss-feeds] Scheduled digest triggered by cron');
          runDigest(api).catch(err => {
            api.logger.error('[rss-feeds] Scheduled digest failed:', err);
          });
        });

        api.logger.info(`[rss-feeds] Digest scheduled: ${config.schedule}`);
      },
      stop() {
        api.logger.info('[rss-feeds] Stopping scheduled digest service');
        cronTask?.stop();
        cronTask = undefined;
      },
    });
  } else {
    api.logger.info('[rss-feeds] No schedule configured - manual trigger only');
  }

  // Register manual tool trigger
  api.registerTool({
    name: 'rss_run_digest',
    description:
      'Manually trigger the RSS feed digest. Fetches configured feeds, ' +
      'optionally enriches with NVD CVE data, publishes to Ghost as draft, ' +
      'and sends notifications.',
    parameters: {
      type: 'object',
      properties: {
        dryRun: {
          type: 'boolean',
          description:
            'If true, fetch and format the digest but skip Ghost publish and notifications.',
        },
      },
      additionalProperties: false,
    },
    async execute(args: Record<string, unknown>) {
      const dryRun = args['dryRun'] === true;

      if (dryRun) {
        api.logger.info('[rss-feeds] Running digest in DRY RUN mode (no publish, no notify)');

        // Temporarily override config to skip publish/notify
        const dryRunApi: PluginApi = {
          ...api,
          config: {
            ...config,
            ghost: undefined,
            notify: [],
          },
        };

        const result = await runDigest(dryRunApi);
        return {
          ...result,
          dryRun: true,
          message: 'Dry run complete - digest generated but not published or notified.',
        };
      }

      const result = await runDigest(api);
      return {
        feedsProcessed: result.feedsProcessed,
        totalItems: result.totalItems,
        totalFirmware: result.totalFirmware,
        totalCves: result.totalCves,
        ghostUrl: result.ghostUrl ?? null,
        ghostError: result.ghostError ?? null,
        notified: result.notified,
        startDate: result.startDate.toISOString(),
        endDate: result.endDate.toISOString(),
        success: result.success,
      };
    },
  });

  api.logger.info(
    `[rss-feeds] Plugin loaded. Feeds: ${feeds.length}. ` +
    `Schedule: ${config.schedule || 'none (manual only)'}.`
  );
}
