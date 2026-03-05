import { Command } from 'commander';
import type { Address } from 'viem';
import { registerAgent, initAgent, getAgent, setOperator, IndexerClient } from '@pulseai/sdk';
import { getClient, getReadClient, getAddress } from '../config.js';
import { output, success, error, info } from '../lib/output.js';

export const agentCommand = new Command('agent').description('Agent registration and info');

agentCommand
  .command('register')
  .description('Register a new agent and initialize it in Pulse')
  .option('--name <name>', 'Agent name (used as URI)', 'pulse-agent')
  .option('--json', 'Output as JSON')
  .action(async (opts) => {
    try {
      const client = getClient();
      const address = getAddress();

      info('Registering agent in ERC-8004 Identity Registry...');
      const result = await registerAgent(client, opts.name);

      info(`Agent ID: ${result.agentId}. Initializing in Pulse...`);
      const initHash = await initAgent(client, result.agentId, address);

      output({
        agentId: result.agentId,
        owner: address,
        operator: address,
        registerTx: result.txHash,
        initTx: initHash,
      });
      success(`Agent registered and initialized with ID: ${result.agentId}`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

agentCommand
  .command('info')
  .description('Get agent information')
  .argument('<agentId>', 'Agent ID')
  .option('--json', 'Output as JSON')
  .action(async (agentIdStr) => {
    try {
      const client = getReadClient();

      // Try on-chain first, fall back to indexer for richer data
      try {
        const data = await getAgent(client, BigInt(agentIdStr));
        output({
          agentId: agentIdStr,
          owner: data.owner,
          operator: data.pulseData.operator,
          warrenContract: data.pulseData.warrenMasterContract,
          registeredAt: data.pulseData.registeredAt,
          active: data.active,
        });
      } catch {
        // Fall back to indexer
        const indexer = new IndexerClient({ baseUrl: client.indexerUrl });
        const agent = await indexer.getAgent(Number(agentIdStr));
        output({
          agentId: agent.agentId,
          owner: agent.owner,
          operator: agent.operator,
          warrenContract: agent.warrenContract,
          registeredAt: agent.registeredAt,
          active: agent.active,
        });
      }
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

agentCommand
  .command('set-operator')
  .description('Set operator for an agent (owner only)')
  .requiredOption('--agent-id <id>', 'Agent ID')
  .requiredOption('--operator <address>', 'Operator address')
  .option('--json', 'Output as JSON')
  .action(async (opts) => {
    try {
      const client = getClient();
      info('Setting operator...');
      const txHash = await setOperator(client, BigInt(opts.agentId), opts.operator as Address);
      output({ agentId: opts.agentId, operator: opts.operator, txHash });
      success('Operator updated');
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });
