import { Command } from 'commander';
import type { DeliverableParams } from '@pulseai/sdk';
import { HandlerProviderRuntime, ProviderRuntime } from '@pulseai/sdk';
import { getClient } from '../config.js';
import { info, error } from '../lib/output.js';

export const serveCommand = new Command('serve')
  .description('Run provider runtime to handle incoming jobs');

serveCommand
  .command('start')
  .description('Start the provider runtime (poll and handle jobs)')
  .requiredOption('--agent-id <id>', 'Provider agent ID')
  .option('--handler <path>', 'Path to OfferingHandler file (TypeScript/JS)')
  .option('--auto-accept', 'Automatically accept matching jobs', false)
  .option('--auto-deliver', 'Automatically deliver with dummy content', false)
  .option('--poll-interval <ms>', 'Poll interval in milliseconds', '5000')
  .option('--json', 'Output as JSON')
  .action(async (opts) => {
    try {
      const client = getClient();
      const agentId = BigInt(opts.agentId);
      const ts = () => new Date().toISOString();

      if (opts.handler) {
        const { resolve } = await import('node:path');
        const handlerPath = resolve(opts.handler);
        const mod = await import(handlerPath);
        const handler = mod.default ?? mod;

        if (typeof handler.offeringId !== 'number' || typeof handler.executeJob !== 'function') {
          throw new Error(
            `Invalid handler at ${handlerPath}: must export offeringId (number) and executeJob (function)`,
          );
        }

        const runtime = new HandlerProviderRuntime(client, agentId, {
          indexerUrl: client.indexerUrl,
          pollInterval: Number(opts.pollInterval),
        });

        runtime.registerHandler(handler);
        runtime.setErrorHandler((err) => {
          info(`[${ts()}] Error: ${err.message}`);
        });

        info(`Handler loaded for offering #${handler.offeringId}`);
        info('Provider runtime started. Listening for jobs...');
        runtime.start();
        return;
      }

      info(`Provider runtime started for agent ${agentId}`);
      info(`Auto-accept: ${opts.autoAccept} | Auto-deliver: ${opts.autoDeliver}`);
      info('Listening for jobs...\n');

      const runtime = new ProviderRuntime(client, agentId, {
        onJobReceived: async (job) => {
          info(`[${ts()}] New job #${job.jobId} — offering #${job.offeringId}, price: ${job.priceUsdm}`);
          if (opts.autoAccept) {
            info(`[${ts()}] Auto-accepting job #${job.jobId}...`);
            return true;
          }
          info(`[${ts()}] Skipping job #${job.jobId} (auto-accept disabled)`);
          return false;
        },

        onDeliverableRequested: async (job): Promise<DeliverableParams> => {
          info(`[${ts()}] Job #${job.jobId} needs delivery`);
          if (opts.autoDeliver) {
            info(`[${ts()}] Auto-delivering for job #${job.jobId}...`);
            return {
              type: 'inline',
              content: JSON.stringify({ result: `Auto-delivered for job ${job.jobId}`, timestamp: Date.now() }),
              mimeType: 'application/json',
              jobId: BigInt(job.jobId),
            };
          }
          throw new Error('Auto-deliver disabled — provide a --handler file');
        },

        onJobCompleted: (job) => {
          info(`[${ts()}] Job #${job.jobId} completed!`);
        },

        onError: (err) => {
          info(`[${ts()}] Error: ${err.message}`);
        },
      }, {
        indexerUrl: client.indexerUrl,
        pollInterval: Number(opts.pollInterval),
      });

      runtime.start();
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });
