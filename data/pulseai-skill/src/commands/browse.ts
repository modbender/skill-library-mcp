import { Command } from 'commander';
import { DEFAULT_SCHEMAS, IndexerClient, ServiceType, formatUsdm } from '@pulseai/sdk';
import { getReadClient } from '../config.js';
import { output, info, error, isJsonMode } from '../lib/output.js';

const SERVICE_TYPE_NAMES: Record<number, string> = {
  0: 'TextGeneration',
  1: 'ImageGeneration',
  2: 'DataAnalysis',
  3: 'CodeGeneration',
  4: 'Translation',
  5: 'Custom',
};

export const browseCommand = new Command('browse')
  .description('Browse available offerings on the Pulse marketplace')
  .argument('[query]', 'Search query (filters by description)')
  .option('--type <serviceType>', 'Filter by service type (0-5 or name)')
  .option('--max-price <usdm>', 'Maximum price in USDm (e.g. "10.0")')
  .option('--agent-id <id>', 'Filter by provider agent ID')
  .option('--json', 'Output as JSON')
  .action(async (query, opts) => {
    try {
      const client = getReadClient();
      const indexer = new IndexerClient({ baseUrl: client.indexerUrl });

      const filter: { serviceType?: number; active?: boolean; agentId?: number } = {
        active: true,
      };

      if (opts.type !== undefined) {
        filter.serviceType = parseServiceType(opts.type);
      }

      if (opts.agentId !== undefined) {
        filter.agentId = Number(opts.agentId);
      }

      info('Searching Pulse marketplace...');

      let offerings = await indexer.getOfferings(filter);

      // Filter by max price
      if (opts.maxPrice) {
        const maxPrice = parseFloat(opts.maxPrice);
        offerings = offerings.filter((o) => {
          const price = parseFloat(formatUsdm(BigInt(o.priceUsdm)));
          return price <= maxPrice;
        });
      }

      // Filter by query (description match)
      if (query) {
        const q = query.toLowerCase();
        offerings = offerings.filter(
          (o) => o.description?.toLowerCase().includes(q),
        );
      }

      if (offerings.length === 0) {
        if (isJsonMode()) {
          output({ offerings: [], count: 0 });
        } else {
          info('No offerings found matching your criteria.');
        }
        return;
      }

      if (isJsonMode()) {
        output({
          offerings: offerings.map((o) => ({
            offeringId: o.offeringId,
            agentId: o.agentId,
            serviceType: SERVICE_TYPE_NAMES[o.serviceType] ?? String(o.serviceType),
            priceUsdm: formatUsdm(BigInt(o.priceUsdm)),
            slaMinutes: o.slaMinutes,
            description: o.description,
            requirementsSchemaUri: o.requirementsSchemaUri ?? null,
            fallbackSchema: o.requirementsSchemaUri
              ? null
              : (DEFAULT_SCHEMAS[o.serviceType] as (typeof DEFAULT_SCHEMAS)[number] | undefined) ?? null,
          })),
          count: offerings.length,
        });
      } else {
        output(
          offerings.map((o) => ({
            id: o.offeringId,
            agent: o.agentId,
            type: SERVICE_TYPE_NAMES[o.serviceType] ?? String(o.serviceType),
            price: formatUsdm(BigInt(o.priceUsdm)) + ' USDm',
            sla: o.slaMinutes ? `${o.slaMinutes}m` : '—',
            description: truncate(o.description ?? '', 50),
          })),
        );
      }
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 1) + '…' : s;
}

function parseServiceType(val: string): number {
  const num = Number(val);
  if (!isNaN(num) && num >= 0 && num <= 5) return num;
  const key = val as keyof typeof ServiceType;
  if (key in ServiceType) return ServiceType[key];
  throw new Error(
    `Invalid service type: ${val}. Use 0-5 or name (TextGeneration, ImageGeneration, DataAnalysis, CodeGeneration, Translation, Custom)`,
  );
}
