import { Command } from 'commander';
import type { Hex } from 'viem';
import {
  createJob,
  acceptJob,
  submitDeliverable,
  evaluate,
  settle,
  cancelJob,
  getJob,
  getAgent,
  getOffering,
  createJobTerms,
  deployRequirements,
  deployDeliverable,
  readRequirements,
  readDeliverable,
  IndexerClient,
  JobStatus,
  formatUsdm,
  DEFAULT_SCHEMAS,
  validateAgainstSchema,
  type OfferingSchema,
  type JsonSchema,
} from '@pulseai/sdk';
import type { Address } from 'viem';
import { getClient, getReadClient, getAddress } from '../config.js';
import { output, success, info, error, isJsonMode } from '../lib/output.js';

const STATUS_NAMES: Record<number, string> = {
  0: 'Created',
  1: 'Accepted',
  2: 'InProgress',
  3: 'Delivered',
  4: 'Evaluated',
  5: 'Completed',
  6: 'Disputed',
  7: 'Cancelled',
};

export const jobCommand = new Command('job').description('Job lifecycle commands');

jobCommand
  .command('create')
  .description('Create a new job (auto-approves USDm, deploys WARREN terms)')
  .requiredOption('--offering <id>', 'Offering ID')
  .requiredOption('--agent-id <id>', 'Your (buyer) agent ID')
  .option('--requirements <json>', 'JSON requirements to attach')
  .option('--json', 'Output as JSON')
  .action(async (opts) => {
    try {
      const client = getClient();
      const offeringId = BigInt(opts.offering);
      const buyerAgentId = BigInt(opts.agentId);

      info('Fetching offering details...');
      const offering = await getOffering(client, offeringId);

      let parsedRequirements: Record<string, unknown> | undefined;
      if (opts.requirements) {
        parsedRequirements = parseRequirementsJson(opts.requirements);
        const schema = await resolveRequirementsSchema(
          Number(offering.serviceType),
          offering.requirementsSchemaURI,
        );
        if (schema) {
          const validation = validateAgainstSchema(
            parsedRequirements,
            schema.serviceRequirements,
          );
          if (!validation.valid) {
            throw new Error(
              `Requirements preflight validation failed: ${validation.reason}\nExpected serviceRequirements schema: ${JSON.stringify(schema.serviceRequirements, null, 2)}`,
            );
          }
        }
      }

      info(`Offering: ${offering.description} — ${formatUsdm(offering.priceUSDm)} USDm`);
      info('Creating WARREN job terms hash...');

      const buyerAddress = getAddress();
      const providerData = await getAgent(client, offering.agentId);

      const terms = createJobTerms({
        jobId: 0n, // placeholder — jobId not yet known
        offeringId,
        agreedPrice: offering.priceUSDm,
        slaMinutes: offering.slaMinutes,
        qualityCriteria: offering.description,
        buyerAgent: buyerAddress,
        providerAgent: providerData.owner as Address,
      });

      info('Creating job (includes USDm approval)...');
      const result = await createJob(client, {
        offeringId,
        buyerAgentId,
        warrenTermsHash: terms.hash,
      });

      // Deploy requirements if provided
      if (parsedRequirements) {
        info('Deploying requirements...');
        try {
          await deployRequirements(
            client,
            buyerAgentId,
            result.jobId,
            {
              jobId: result.jobId,
              offeringId,
              requirements: parsedRequirements,
            },
            client.indexerUrl,
          );
        } catch (e) {
          info(`Warning: requirements deployment failed: ${e instanceof Error ? e.message : e}`);
        }
      }

      output({
        jobId: result.jobId,
        offeringId: Number(offeringId),
        price: formatUsdm(offering.priceUSDm) + ' USDm',
        termsHash: terms.hash,
        txHash: result.txHash,
      });
      success(`Job created with ID: ${result.jobId}`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

jobCommand
  .command('status')
  .description('Get job status (optionally poll until done)')
  .argument('<jobId>', 'Job ID')
  .option('--wait', 'Poll until job reaches a terminal state', false)
  .option('--poll-interval <ms>', 'Poll interval in milliseconds', '5000')
  .option('--json', 'Output as JSON')
  .action(async (jobIdStr, opts) => {
    try {
      const client = getReadClient();
      const indexer = new IndexerClient({ baseUrl: client.indexerUrl });
      const jobId = Number(jobIdStr);

      if (opts.wait) {
        info(`Polling job #${jobId} until completion...`);
        const interval = Number(opts.pollInterval);

        while (true) {
          const job = await indexer.getJob(jobId);
          const statusName = STATUS_NAMES[job.status] ?? String(job.status);

          info(`Status: ${statusName}`);

          // Terminal states: Completed(5), Disputed(6), Cancelled(7)
          if (job.status >= 5) {
            outputJobDetails(job);
            return;
          }

          await sleep(interval);
        }
      } else {
        const job = await indexer.getJob(jobId);
        outputJobDetails(job);
      }
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

jobCommand
  .command('accept')
  .description('Accept a job as provider')
  .argument('<jobId>', 'Job ID')
  .option('--json', 'Output as JSON')
  .action(async (jobIdStr) => {
    try {
      const client = getClient();
      const jobId = BigInt(jobIdStr);

      info('Fetching job details...');
      const job = await getJob(client, jobId);

      const txHash = await acceptJob(client, jobId, job.warrenTermsHash);
      output({ jobId: jobIdStr, txHash });
      success(`Job ${jobIdStr} accepted`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

jobCommand
  .command('deliver')
  .description('Submit a deliverable for a job')
  .argument('<jobId>', 'Job ID')
  .option('--hash <hex>', 'Deliverable hash (bytes32) — legacy mode')
  .option('--content <json>', 'Deliverable content as JSON string')
  .option('--file <path>', 'Path to deliverable JSON file')
  .option('--agent-id <id>', 'Provider agent ID')
  .option('--json', 'Output as JSON')
  .action(async (jobIdStr, opts) => {
    try {
      const client = getClient();
      const jobId = BigInt(jobIdStr);

      if (opts.hash && (opts.content || opts.file)) {
        error('Cannot combine --hash with --content/--file');
      }

      // Backward-compatible hash-only mode
      if (opts.hash && !opts.content && !opts.file) {
        const txHash = await submitDeliverable(client, jobId, opts.hash as Hex);
        output({ jobId: jobIdStr, txHash });
        success('Deliverable submitted');
        return;
      }

      if (opts.content && opts.file) {
        error('Cannot use both --content and --file');
      }
      if (!opts.content && !opts.file) {
        error('Must specify --hash, --content, or --file');
      }
      if (!opts.agentId) {
        error('--agent-id is required when using --content or --file');
      }

      const agentId = Number(opts.agentId);
      if (!Number.isFinite(agentId) || !Number.isInteger(agentId) || agentId <= 0) {
        error('Invalid --agent-id (must be a positive integer)');
      }

      let contentStr: string;
      if (opts.content) {
        contentStr = opts.content as string;
      } else {
        const fs = await import('node:fs');
        contentStr = fs.readFileSync(opts.file as string, 'utf8');
      }

      info('Running preflight checks...');
      const indexer = new IndexerClient({ baseUrl: client.indexerUrl });
      const job = await indexer.getJob(Number(jobIdStr));

      if (job.status !== 2) {
        error(
          `Job is not InProgress (status=${STATUS_NAMES[job.status] ?? String(job.status)}). Cannot deliver.`,
        );
      }
      if (job.providerAgentId !== agentId) {
        error(`You are not the provider for this job (provider agent: ${job.providerAgentId})`);
      }

      if (job.acceptedAt && job.slaMinutes) {
        const deadlineMs = (job.acceptedAt + job.slaMinutes * 60) * 1000;
        const remainingMs = deadlineMs - Date.now();
        if (remainingMs < 10 * 60 * 1000) {
          info('Warning: less than 10 minutes remaining on SLA deadline');
        }
      }

      info('Submitting deliverable on-chain...');
      const result = await deployDeliverable(
        client,
        jobId,
        {
          jobId,
          type: 'inline',
          content: contentStr,
          mimeType: 'application/json',
        },
        client.indexerUrl,
      );

      output({
        jobId: jobIdStr,
        hash: result.hash,
        txHash: result.txHash,
      });
      success('Deliverable submitted');
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

jobCommand
  .command('evaluate')
  .description('Evaluate a delivered job')
  .argument('<jobId>', 'Job ID')
  .option('--approve', 'Approve the deliverable', false)
  .option('--reject', 'Reject the deliverable', false)
  .option('--feedback <text>', 'Feedback text', '')
  .option('--json', 'Output as JSON')
  .action(async (jobIdStr, opts) => {
    try {
      if (!opts.approve && !opts.reject) {
        error('Must specify --approve or --reject');
      }
      const client = getClient();
      const txHash = await evaluate(client, BigInt(jobIdStr), !!opts.approve, opts.feedback);
      output({ jobId: jobIdStr, approved: !!opts.approve, txHash });
      success(`Job ${jobIdStr} evaluated: ${opts.approve ? 'approved' : 'rejected'}`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

jobCommand
  .command('settle')
  .description('Settle an evaluated job (release payment)')
  .argument('<jobId>', 'Job ID')
  .option('--json', 'Output as JSON')
  .action(async (jobIdStr) => {
    try {
      const client = getClient();
      const txHash = await settle(client, BigInt(jobIdStr));
      output({ jobId: jobIdStr, txHash });
      success(`Job ${jobIdStr} settled`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

jobCommand
  .command('result')
  .description('View job deliverable result')
  .argument('<jobId>', 'Job ID')
  .option('--json', 'Output as JSON')
  .action(async (jobIdStr) => {
    try {
      const client = getReadClient();
      const indexer = new IndexerClient({ baseUrl: client.indexerUrl });
      const jobId = Number(jobIdStr);

      info('Fetching job details...');
      const job = await indexer.getJob(jobId);
      const statusName = STATUS_NAMES[job.status] ?? String(job.status);

      if (job.status < 3) {
        error(`Job #${jobId} has not been delivered yet (status: ${statusName})`);
        return;
      }

      info(`Job #${jobId} — status: ${statusName}, deliverableHash: ${job.deliverableHash}`);
      info('Reading deliverable from indexer...');

      try {
        const deliverable = await readDeliverable(BigInt(jobId), client.indexerUrl);
        output({
          jobId,
          status: statusName,
          deliverableHash: job.deliverableHash,
          type: deliverable.type,
          content: deliverable.content ?? null,
          url: deliverable.url ?? null,
          mimeType: deliverable.mimeType ?? 'application/json',
          size: deliverable.size,
          timestamp: new Date(deliverable.timestamp).toISOString(),
        });
        success(`Deliverable retrieved for job #${jobId}`);
      } catch {
        info('Deliverable content not available in indexer. Showing on-chain data only.');
        output({
          jobId,
          status: statusName,
          deliverableHash: job.deliverableHash,
          deliveredAt: job.deliveredAt ? new Date(job.deliveredAt * 1000).toISOString() : null,
          note: 'Deliverable hash exists on-chain but content was not stored in indexer.',
        });
      }
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

jobCommand
  .command('cancel')
  .description('Cancel a job')
  .argument('<jobId>', 'Job ID')
  .option('--json', 'Output as JSON')
  .action(async (jobIdStr) => {
    try {
      const client = getClient();
      const txHash = await cancelJob(client, BigInt(jobIdStr));
      output({ jobId: jobIdStr, txHash });
      success(`Job ${jobIdStr} cancelled`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

jobCommand
  .command('pending')
  .description('List pending jobs for a provider agent')
  .requiredOption('--agent-id <id>', 'Provider agent ID')
  .option('--json', 'Output as JSON')
  .action(async (opts) => {
    try {
      const client = getReadClient();
      const indexer = new IndexerClient({ baseUrl: client.indexerUrl });
      const agentId = Number(opts.agentId);

      if (!Number.isFinite(agentId) || !Number.isInteger(agentId) || agentId <= 0) {
        error('Invalid --agent-id (must be a positive integer)');
      }

      info('Fetching pending jobs...');
      const jobs = await indexer.getJobs({ status: 0, agentId });
      const pendingJobs = jobs.filter((job) => job.providerAgentId === agentId);

      if (pendingJobs.length === 0) {
        info('No pending jobs found.');
        output([]);
        return;
      }

      output(
        pendingJobs.map((job) => ({
          jobId: job.jobId,
          offeringId: job.offeringId,
          buyerAgentId: job.buyerAgentId,
          price: formatUsdm(BigInt(job.priceUsdm)) + ' USDm',
          slaMinutes: job.slaMinutes,
          createdAt: job.createdAt ? new Date(job.createdAt * 1000).toISOString() : null,
        })),
      );
      success(`${pendingJobs.length} pending job(s) found`);
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

jobCommand
  .command('requirements')
  .description('View job requirements')
  .argument('<jobId>', 'Job ID')
  .option('--json', 'Output as JSON')
  .action(async (jobIdStr) => {
    try {
      const client = getReadClient();
      const jobId = Number(jobIdStr);
      if (!Number.isFinite(jobId) || !Number.isInteger(jobId) || jobId < 0) {
        error('Invalid <jobId>');
      }

      info('Fetching job requirements...');

      const warrenRequirements = await readRequirements(client, BigInt(jobId), client.indexerUrl);
      if (warrenRequirements) {
        output(warrenRequirements);
        success('Requirements retrieved from WARREN (verified)');
        return;
      }

      const baseUrl = client.indexerUrl.replace(/\/$/, '');
      const response = await fetch(`${baseUrl}/jobs/${jobId}`);
      if (!response.ok) {
        error(`Failed to fetch job from indexer: ${response.status}`);
      }

      const payload = await response.json() as { data?: Record<string, unknown> };
      const job = payload.data;
      if (!job) {
        error('Invalid indexer response: missing job payload');
      }

      const requirementsContent = job.requirements_content;
      if (typeof requirementsContent === 'string' && requirementsContent.length > 0) {
        try {
          const parsed = JSON.parse(requirementsContent) as unknown;
          output(parsed);
          success('Requirements retrieved from indexer');
          return;
        } catch {
          output({ raw: requirementsContent });
          return;
        }
      }

      info('No requirements found for this job.');
      output({ jobId, requirements: null });
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

function outputJobDetails(job: { jobId: number; offeringId: number; buyerAgentId: number; providerAgentId: number; priceUsdm: string; status: number; slaMinutes: number | null; createdAt: number | null; acceptedAt: number | null; deliveredAt: number | null; evaluatedAt: number | null; settledAt: number | null }) {
  output({
    jobId: job.jobId,
    offeringId: job.offeringId,
    buyerAgentId: job.buyerAgentId,
    providerAgentId: job.providerAgentId,
    price: formatUsdm(BigInt(job.priceUsdm)) + ' USDm',
    status: STATUS_NAMES[job.status] ?? String(job.status),
    slaMinutes: job.slaMinutes,
    createdAt: job.createdAt ? new Date(job.createdAt * 1000).toISOString() : null,
    acceptedAt: job.acceptedAt ? new Date(job.acceptedAt * 1000).toISOString() : null,
    deliveredAt: job.deliveredAt ? new Date(job.deliveredAt * 1000).toISOString() : null,
    evaluatedAt: job.evaluatedAt ? new Date(job.evaluatedAt * 1000).toISOString() : null,
    settledAt: job.settledAt ? new Date(job.settledAt * 1000).toISOString() : null,
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseRequirementsJson(rawRequirements: string): Record<string, unknown> {
  let parsed: unknown;
  try {
    parsed = JSON.parse(rawRequirements);
  } catch {
    throw new Error('--requirements must be valid JSON');
  }

  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    throw new Error('--requirements must be a JSON object');
  }

  return parsed as Record<string, unknown>;
}

async function resolveRequirementsSchema(
  serviceType: number,
  requirementsSchemaUri?: string,
): Promise<OfferingSchema | undefined> {
  if (requirementsSchemaUri && requirementsSchemaUri.trim().length > 0) {
    const fromUri = await loadOfferingSchemaFromUri(requirementsSchemaUri.trim());
    if (!fromUri) {
      throw new Error(
        `Unsupported requirementsSchemaURI format: ${requirementsSchemaUri}. Use http(s), data: URI, or inline JSON.`,
      );
    }
    return fromUri;
  }

  return DEFAULT_SCHEMAS[serviceType] as (typeof DEFAULT_SCHEMAS)[number] | undefined;
}

async function loadOfferingSchemaFromUri(schemaUri: string): Promise<OfferingSchema | null> {
  let schemaPayload: unknown;
  if (schemaUri.startsWith('data:')) {
    schemaPayload = parseDataUriJson(schemaUri);
  } else if (schemaUri.startsWith('http://') || schemaUri.startsWith('https://')) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30_000);
    try {
      const response = await fetch(schemaUri, { signal: controller.signal });
      if (!response.ok) {
        throw new Error(`Failed to fetch requirements schema URI (${response.status} ${response.statusText})`);
      }
      const buf = await response.arrayBuffer();
      if (buf.byteLength > 1_048_576) {
        throw new Error(`Schema too large (${buf.byteLength} bytes). Limit is 1MB`);
      }
      schemaPayload = JSON.parse(new TextDecoder().decode(buf));
    } finally {
      clearTimeout(timeoutId);
    }
  } else if (schemaUri.trim().startsWith('{')) {
    schemaPayload = JSON.parse(schemaUri);
  } else {
    return null;
  }

  if (!isOfferingSchema(schemaPayload)) {
    throw new Error('requirementsSchemaURI did not resolve to a valid OfferingSchema document');
  }
  return schemaPayload;
}

function parseDataUriJson(dataUri: string): unknown {
  const commaIndex = dataUri.indexOf(',');
  if (commaIndex < 0) {
    throw new Error('Invalid data URI schema format');
  }

  const metadata = dataUri.slice(5, commaIndex);
  const payload = dataUri.slice(commaIndex + 1);
  const decoded = metadata.includes(';base64')
    ? new TextDecoder().decode(Uint8Array.from(atob(payload), (char) => char.charCodeAt(0)))
    : decodeURIComponent(payload);

  return JSON.parse(decoded);
}

function isOfferingSchema(value: unknown): value is OfferingSchema {
  if (typeof value !== 'object' || value === null) return false;
  const candidate = value as Partial<OfferingSchema>;
  return (
    typeof candidate.version === 'number' &&
    isJsonSchema(candidate.serviceRequirements) &&
    isJsonSchema(candidate.deliverableRequirements)
  );
}

function isJsonSchema(value: unknown): value is JsonSchema {
  if (typeof value !== 'object' || value === null) return false;
  const candidate = value as Partial<JsonSchema>;
  return (
    candidate.type === 'object' &&
    typeof candidate.properties === 'object' &&
    candidate.properties !== null
  );
}
