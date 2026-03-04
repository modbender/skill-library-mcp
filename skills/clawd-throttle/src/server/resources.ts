import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { ThrottleConfig } from '../config/types.js';
import type { LogReader } from '../logging/reader.js';
import { computeStats } from '../logging/stats.js';

export function registerResources(
  server: McpServer,
  config: ThrottleConfig,
  logReader: LogReader,
): void {
  server.resource(
    'dashboard',
    'throttle://dashboard',
    {
      description: "Current routing status: active mode, today's stats, model distribution",
      mimeType: 'application/json',
    },
    async () => {
      const todayStart = new Date();
      todayStart.setHours(0, 0, 0, 0);
      const todayEntries = logReader.readSince(todayStart.toISOString());
      const stats = computeStats(todayEntries);

      return {
        contents: [{
          uri: 'throttle://dashboard',
          mimeType: 'application/json',
          text: JSON.stringify({
            currentMode: config.mode,
            todayRequests: stats.totalRequests,
            todayCost: `$${stats.totalCostUsd.toFixed(4)}`,
            todaySavings: `$${stats.estimatedSavingsUsd.toFixed(4)}`,
            modelDistribution: stats.modelDistribution,
          }, null, 2),
        }],
      };
    },
  );
}
