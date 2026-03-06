import { Command } from 'commander';
import {
  listOffering,
  updateOffering,
  updateOfferingSchema,
  getOffering,
  deactivateOffering,
  activateOffering,
  ServiceType,
  parseUsdm,
  formatUsdm,
  IndexerClient,
} from '@pulseai/sdk';
import { getClient, getReadClient } from '../config.js';
import { output, success, info, error, isJsonMode } from '../lib/output.js';

const SERVICE_TYPE_NAMES: Record<number, string> = {
  0: 'TextGeneration',
  1: 'ImageGeneration',
  2: 'DataAnalysis',
  3: 'CodeGeneration',
  4: 'Translation',
  5: 'Custom',
};

export const sellCommand = new Command('sell').description('Create and manage service offerings');

sellCommand
  .command('init')
  .description('Create a new service offering')
  .requiredOption('--agent-id <id>', 'Your agent ID')
  .requiredOption('--type <serviceType>', 'Service type (0-5 or name)')
  .requiredOption('--price <usdm>', 'Price in USDm (e.g. "5.0")')
  .requiredOption('--sla <minutes>', 'SLA in minutes')
  .requiredOption('--name <name>', 'Offering name')
  .requiredOption('--description <desc>', 'Offering description')
  .option('--schema-uri <uri>', 'Requirements schema URI')
  .option('--json', 'Output as JSON')
  .action(async (opts) => {
    try {
      const client = getClient();
      const serviceType = parseServiceType(opts.type);

      info(`Creating offering: ${opts.name}`);
      info(`Type: ${SERVICE_TYPE_NAMES[serviceType]} | Price: ${opts.price} USDm | SLA: ${opts.sla}m`);

      const result = await listOffering(client, {
        agentId: BigInt(opts.agentId),
        serviceType,
        priceUSDm: parseUsdm(opts.price),
        slaMinutes: Number(opts.sla),
        name: opts.name,
        description: opts.description,
        requirementsSchemaURI: opts.schemaUri,
      });

      output({
        offeringId: result.offeringId,
        agentId: Number(opts.agentId),
        serviceType: SERVICE_TYPE_NAMES[serviceType],
        price: opts.price + ' USDm',
        slaMinutes: Number(opts.sla),
        name: opts.name,
        description: opts.description,
        txHash: result.txHash,
      });
      success(`Offering created with ID: ${result.offeringId}`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

sellCommand
  .command('list')
  .description('List your offerings')
  .option('--agent-id <id>', 'Agent ID to list offerings for')
  .option('--json', 'Output as JSON')
  .action(async (opts) => {
    try {
      const client = getReadClient();
      const indexer = new IndexerClient({ baseUrl: client.indexerUrl });

      const filter = opts.agentId ? { agentId: Number(opts.agentId) } : {};
      const offerings = await indexer.getOfferings(filter);

      if (offerings.length === 0) {
        info('No offerings found.');
        if (isJsonMode()) output({ offerings: [], count: 0 });
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
            active: o.active,
          })),
          count: offerings.length,
        });
      } else {
        output(
          offerings.map((o) => ({
            id: o.offeringId,
            type: SERVICE_TYPE_NAMES[o.serviceType] ?? String(o.serviceType),
            price: formatUsdm(BigInt(o.priceUsdm)) + ' USDm',
            sla: o.slaMinutes ? `${o.slaMinutes}m` : '—',
            active: o.active ? 'yes' : 'no',
            description: o.description ?? '',
          })),
        );
      }
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

sellCommand
  .command('deactivate')
  .description('Deactivate an offering')
  .argument('<offeringId>', 'Offering ID')
  .option('--json', 'Output as JSON')
  .action(async (offeringIdStr) => {
    try {
      const client = getClient();
      const txHash = await deactivateOffering(client, BigInt(offeringIdStr));
      output({ offeringId: offeringIdStr, txHash });
      success(`Offering ${offeringIdStr} deactivated`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

sellCommand
  .command('activate')
  .description('Activate a deactivated offering')
  .argument('<offeringId>', 'Offering ID')
  .option('--json', 'Output as JSON')
  .action(async (offeringIdStr) => {
    try {
      const client = getClient();
      const txHash = await activateOffering(client, BigInt(offeringIdStr));
      output({ offeringId: offeringIdStr, txHash });
      success(`Offering ${offeringIdStr} activated`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

sellCommand
  .command('update')
  .description('Update an offering (price, SLA, name, description)')
  .argument('<offeringId>', 'Offering ID')
  .option('--price <usdm>', 'New price in USDm')
  .option('--sla <minutes>', 'New SLA in minutes')
  .option('--name <name>', 'New name')
  .option('--description <desc>', 'New description')
  .option('--json', 'Output as JSON')
  .action(async (offeringIdStr, opts) => {
    try {
      const client = getClient();
      const offeringId = BigInt(offeringIdStr);

      // Fetch current values for fields not specified
      const current = await getOffering(client, offeringId);
      const price = opts.price ? parseUsdm(opts.price) : current.priceUSDm;
      const sla = opts.sla ? Number(opts.sla) : current.slaMinutes;
      const name = opts.name ?? current.name;
      const description = opts.description ?? current.description;

      info(`Updating offering ${offeringIdStr}...`);
      const txHash = await updateOffering(client, offeringId, price, sla, name, description);
      output({ offeringId: offeringIdStr, price: formatUsdm(price) + ' USDm', slaMinutes: sla, name, description, txHash });
      success(`Offering ${offeringIdStr} updated`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

sellCommand
  .command('update-schema')
  .description('Update the requirements schema URI of an offering')
  .argument('<offeringId>', 'Offering ID')
  .requiredOption('--uri <schemaURI>', 'Requirements schema URI')
  .option('--json', 'Output as JSON')
  .action(async (offeringIdStr, opts) => {
    try {
      const client = getClient();
      info(`Updating schema for offering ${offeringIdStr}...`);
      const txHash = await updateOfferingSchema(client, BigInt(offeringIdStr), opts.uri);
      output({ offeringId: offeringIdStr, requirementsSchemaURI: opts.uri, txHash });
      success(`Offering ${offeringIdStr} schema updated`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

sellCommand
  .command('metadata')
  .description('Set OpenClaw usage metadata for an offering')
  .argument('<offeringId>', 'Offering ID')
  .option('--example <cmd>', 'OpenClaw example command (max 500 chars)')
  .option('--usage-url <url>', 'Usage documentation URL (max 2000 chars)')
  .option('--instructions <text>', 'Usage instructions (max 5000 chars)')
  .option('--json', 'Output as JSON')
  .action(async (offeringIdStr, opts) => {
    try {
      const client = getClient();
      if (!client.walletClient?.account) {
        throw new Error('Wallet required to sign metadata update. Set PULSE_PRIVATE_KEY or run `pulse wallet generate`.');
      }

      const offeringId = Number(offeringIdStr);
      const message = `Pulse: Update offering #${offeringId} metadata`;
      const signature = await client.walletClient.signMessage({ message });

      const indexer = new IndexerClient({ baseUrl: client.indexerUrl });
      await indexer.updateOfferingMetadata(offeringId, {
        openclawExample: opts.example,
        usageUrl: opts.usageUrl,
        usageInstructions: opts.instructions,
        signature,
      });

      output({
        offeringId,
        openclawExample: opts.example ?? null,
        usageUrl: opts.usageUrl ?? null,
        usageInstructions: opts.instructions ?? null,
      });
      success(`Metadata updated for offering ${offeringIdStr}`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

function parseServiceType(val: string): ServiceType {
  const num = Number(val);
  if (!isNaN(num) && num >= 0 && num <= 5) return num as ServiceType;
  const key = val as keyof typeof ServiceType;
  if (key in ServiceType) return ServiceType[key];
  throw new Error(
    `Invalid service type: ${val}. Use 0-5 or name (TextGeneration, ImageGeneration, DataAnalysis, CodeGeneration, Translation, Custom)`,
  );
}
