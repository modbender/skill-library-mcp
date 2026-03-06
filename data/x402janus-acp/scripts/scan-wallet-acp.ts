#!/usr/bin/env tsx
/**
 * scan-wallet-acp.ts
 *
 * Hires x402janus via the Virtuals ACP marketplace to scan a wallet for
 * risky token approvals, drainer patterns, and on-chain threats. Uses the
 * ACP job system: create job → submit wallet → poll for deliverable.
 *
 * Usage:
 *   npx tsx scripts/scan-wallet-acp.ts <walletAddress> [options]
 *   npx tsx scripts/scan-wallet-acp.ts --job-id <id>   (poll existing job)
 *
 * Options:
 *   --timeout <seconds>       Max time to wait for job completion (default: 120)
 *   --poll-interval <seconds> How often to check job status (default: 5)
 *   --offering <name>         Specific offering name to use
 *   --json                    Output raw JSON result
 *   --job-id <id>             Skip creation, poll an existing job
 *   -h, --help                Show this help
 *
 * Environment:
 *   ACP_API_KEY          — Virtuals ACP API key (required)
 *   ACP_AGENT_WALLET     — Your agent's wallet address on Base (optional)
 *   ACP_BASE_URL         — ACP base URL (default: https://claw-api.virtuals.io)
 *   JANUS_OFFERING_NAME  — Default offering name to use (optional)
 */

import axios, { AxiosInstance } from "axios";
import dotenv from "dotenv";

dotenv.config();

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** ACP job phases as returned by the marketplace API. */
type JobPhase =
  | "pending"
  | "negotiation"
  | "transaction"
  | "completed"
  | "rejected"
  | "expired"
  | string;

/** A single memo/history entry from the job. */
interface JobMemo {
  nextPhase: string;
  content: string;
  createdAt: string;
  status: string;
}

/** Full ACP job state from GET /acp/jobs/:id */
interface AcpJob {
  id: number | string;
  phase: JobPhase;
  providerName?: string;
  providerAddress?: string;
  clientName?: string;
  clientAddress?: string;
  deliverable?: string | null;
  memos?: JobMemo[];
}

/** ACP agent offering used when discovering x402janus. */
interface JobOffering {
  name: string;
  price: number;
  priceType: string;
  requirement: string;
}

interface AcpAgent {
  id: string;
  name: string;
  walletAddress: string;
  description: string;
  jobOfferings: JobOffering[];
}

/** Parsed scan result extracted from the job deliverable. */
export interface ScanResult {
  jobId: number | string;
  walletAddress: string;
  phase: JobPhase;
  deliverable: string | null;
  /** Parsed JSON deliverable (if the provider returned structured data). */
  data?: unknown;
  memos: JobMemo[];
}

/** Configuration for a scan operation. */
interface ScanOptions {
  /** Wallet address to scan. */
  walletAddress: string;
  /** Override API key (default: ACP_API_KEY). */
  apiKey?: string;
  /** Override base URL (default: ACP_BASE_URL or production). */
  baseUrl?: string;
  /** Specific ACP offering name to use. */
  offeringName?: string;
  /** Caller's agent wallet address (optional, required by some offerings). */
  agentWallet?: string;
  /** Max seconds to wait for job completion (default: 120). */
  timeoutSeconds?: number;
  /** Seconds between status polls (default: 5). */
  pollIntervalSeconds?: number;
  /** Output raw JSON to stdout. */
  json?: boolean;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const DEFAULT_BASE_URL = "https://claw-api.virtuals.io";
const DEFAULT_TIMEOUT_SECONDS = 120;
const DEFAULT_POLL_INTERVAL_SECONDS = 5;
const TERMINAL_PHASES: JobPhase[] = ["completed", "rejected", "expired"];
const JANUS_SEARCH_QUERY = "x402janus";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Builds an Axios instance pre-configured for the ACP API.
 */
function buildClient(apiKey: string, baseUrl: string): AxiosInstance {
  return axios.create({
    baseURL: baseUrl,
    headers: { "x-api-key": apiKey },
    timeout: 15_000,
  });
}

/**
 * Validates an Ethereum address (basic hex format check).
 *
 * @param address - The address string to validate.
 * @returns true if it looks like a valid EVM address.
 */
function isValidAddress(address: string): boolean {
  return /^0x[0-9a-fA-F]{40}$/.test(address);
}

/**
 * Sleeps for the given number of milliseconds.
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Fetches agents from ACP matching the given query.
 *
 * @param client - Configured Axios instance.
 * @param query  - Search term.
 * @throws If the HTTP request fails.
 */
async function fetchAgents(
  client: AxiosInstance,
  query: string
): Promise<AcpAgent[]> {
  const res = await client.get<{ data: AcpAgent[] }>(
    `/acp/agents?query=${encodeURIComponent(query)}`
  );
  return res.data.data ?? [];
}

/**
 * Finds the x402janus agent and the target offering on the ACP marketplace.
 *
 * @param client       - Configured Axios instance.
 * @param offeringName - Preferred offering name. Uses first available if null.
 * @returns { agent, offering } — the matched agent and its offering.
 * @throws If no x402janus agent or matching offering is found.
 */
async function resolveJanusOffering(
  client: AxiosInstance,
  offeringName: string | null
): Promise<{ agent: AcpAgent; offering: JobOffering }> {
  const agents = await fetchAgents(client, JANUS_SEARCH_QUERY);

  if (agents.length === 0) {
    throw new Error(
      `No agents found matching "${JANUS_SEARCH_QUERY}" on ACP marketplace. ` +
      "x402janus may not be registered yet. Check https://claw-api.virtuals.io"
    );
  }

  // Prefer an agent named exactly "x402janus"
  const janusAgent =
    agents.find((a) => a.name.toLowerCase() === "x402janus") ?? agents[0];

  const offerings = janusAgent.jobOfferings ?? [];
  if (offerings.length === 0) {
    throw new Error(
      `x402janus agent (${janusAgent.name}) has no job offerings registered.`
    );
  }

  let offering: JobOffering | undefined;
  if (offeringName) {
    offering = offerings.find(
      (o) => o.name.toLowerCase() === offeringName.toLowerCase()
    );
    if (!offering) {
      const names = offerings.map((o) => `"${o.name}"`).join(", ");
      throw new Error(
        `Offering "${offeringName}" not found. Available: ${names}`
      );
    }
  } else {
    // Default: use the first available offering
    offering = offerings[0];
  }

  return { agent: janusAgent, offering };
}

/**
 * Creates an ACP job, targeting x402janus for a wallet scan.
 *
 * @param client           - Configured Axios instance.
 * @param providerWallet   - x402janus agent wallet address.
 * @param offeringName     - The offering name to purchase.
 * @param walletToScan     - The wallet address to submit for scanning.
 * @param agentWallet      - Caller's agent wallet (optional).
 * @returns The created job's numeric ID.
 * @throws If job creation fails.
 */
async function createScanJob(
  client: AxiosInstance,
  providerWallet: string,
  offeringName: string,
  walletToScan: string,
  agentWallet?: string
): Promise<number> {
  const serviceRequirements: Record<string, string> = {
    walletAddress: walletToScan,
  };

  if (agentWallet) {
    serviceRequirements.clientWalletAddress = agentWallet;
  }

  const res = await client.post<{ data: { jobId: number } }>("/acp/jobs", {
    providerWalletAddress: providerWallet,
    jobOfferingName: offeringName,
    serviceRequirements,
  });

  const jobId = res.data?.data?.jobId;
  if (!jobId) {
    throw new Error(
      `Unexpected response from job creation: ${JSON.stringify(res.data)}`
    );
  }

  return jobId;
}

/**
 * Fetches the current state of an ACP job by ID.
 *
 * @param client - Configured Axios instance.
 * @param jobId  - Numeric ACP job ID.
 * @returns Raw ACP job data.
 * @throws If the job is not found or the request fails.
 */
async function fetchJobStatus(
  client: AxiosInstance,
  jobId: number | string
): Promise<AcpJob> {
  const res = await client.get<{ data: AcpJob }>(`/acp/jobs/${jobId}`);
  const data = res.data?.data;
  if (!data) {
    throw new Error(`Job ${jobId} not found or empty response.`);
  }
  return data;
}

/**
 * Polls an ACP job until it reaches a terminal phase or times out.
 *
 * @param client          - Configured Axios instance.
 * @param jobId           - Job to poll.
 * @param timeoutMs       - Max milliseconds to wait.
 * @param pollIntervalMs  - Milliseconds between polls.
 * @param verbose         - Print phase updates to stderr.
 * @returns Final ACP job state.
 * @throws If the job times out before completing.
 */
async function pollJobToCompletion(
  client: AxiosInstance,
  jobId: number | string,
  timeoutMs: number,
  pollIntervalMs: number,
  verbose = true
): Promise<AcpJob> {
  const deadline = Date.now() + timeoutMs;
  let lastPhase = "";

  while (Date.now() < deadline) {
    const job = await fetchJobStatus(client, jobId);

    if (verbose && job.phase !== lastPhase) {
      process.stderr.write(`  [job ${jobId}] phase: ${job.phase}\n`);
      lastPhase = job.phase;
    }

    if (TERMINAL_PHASES.includes(job.phase)) {
      return job;
    }

    const remaining = deadline - Date.now();
    if (remaining <= 0) break;

    await sleep(Math.min(pollIntervalMs, remaining));
  }

  throw new Error(
    `Job ${jobId} did not complete within ${timeoutMs / 1000}s. ` +
    "Use --job-id to resume polling later."
  );
}

/**
 * Attempts to parse the job deliverable as JSON.
 *
 * @param deliverable - Raw deliverable string from the job.
 * @returns Parsed object, or undefined if not valid JSON.
 */
function parseDeliverable(deliverable: string | null | undefined): unknown {
  if (!deliverable) return undefined;
  try {
    return JSON.parse(deliverable);
  } catch {
    return undefined;
  }
}

// ---------------------------------------------------------------------------
// Main exported function
// ---------------------------------------------------------------------------

/**
 * Scans a wallet via the x402janus ACP marketplace offering.
 *
 * Flow:
 *   1. Resolve x402janus agent + target offering on the marketplace.
 *   2. Create an ACP job with the wallet address as the service requirement.
 *   3. Poll the job until it reaches a terminal phase (completed/rejected/expired).
 *   4. Return structured scan results from the deliverable.
 *
 * @param options - Scan configuration.
 * @returns Structured scan result with risk data.
 *
 * @example
 * const result = await scanWalletAcp({
 *   walletAddress: "0xYourWalletAddress",
 *   timeoutSeconds: 90,
 * });
 * console.log(result.data); // parsed risk report
 */
export async function scanWalletAcp(options: ScanOptions): Promise<ScanResult> {
  const {
    walletAddress,
    timeoutSeconds = DEFAULT_TIMEOUT_SECONDS,
    pollIntervalSeconds = DEFAULT_POLL_INTERVAL_SECONDS,
    json = false,
  } = options;

  // Validate inputs
  if (!isValidAddress(walletAddress)) {
    throw new Error(
      `Invalid wallet address: "${walletAddress}". Must be a 0x-prefixed 40-char hex address.`
    );
  }

  const apiKey = options.apiKey ?? process.env.ACP_API_KEY;
  if (!apiKey) {
    throw new Error(
      "ACP_API_KEY environment variable is not set. " +
      "Get your key at https://claw-api.virtuals.io"
    );
  }

  const baseUrl = options.baseUrl ?? process.env.ACP_BASE_URL ?? DEFAULT_BASE_URL;
  const agentWallet = options.agentWallet ?? process.env.ACP_AGENT_WALLET;
  const offeringName =
    options.offeringName ?? process.env.JANUS_OFFERING_NAME ?? null;

  const client = buildClient(apiKey, baseUrl);

  if (!json) {
    process.stderr.write(`\n  Resolving x402janus on ACP marketplace…\n`);
  }

  // Step 1: Find x402janus + the target offering
  const { agent, offering } = await resolveJanusOffering(client, offeringName);

  if (!json) {
    process.stderr.write(
      `  Found: ${agent.name} — offering "${offering.name}" @ ${offering.price} ${offering.priceType}\n`
    );
    process.stderr.write(`  Creating ACP job for wallet: ${walletAddress}\n`);
  }

  // Step 2: Create the job
  const jobId = await createScanJob(
    client,
    agent.walletAddress,
    offering.name,
    walletAddress,
    agentWallet
  );

  if (!json) {
    process.stderr.write(
      `  Job created: #${jobId} — polling for up to ${timeoutSeconds}s…\n\n`
    );
  }

  // Step 3: Poll to completion
  const finalJob = await pollJobToCompletion(
    client,
    jobId,
    timeoutSeconds * 1000,
    pollIntervalSeconds * 1000,
    !json
  );

  const result: ScanResult = {
    jobId: finalJob.id,
    walletAddress,
    phase: finalJob.phase,
    deliverable: finalJob.deliverable ?? null,
    data: parseDeliverable(finalJob.deliverable),
    memos: finalJob.memos ?? [],
  };

  return result;
}

// ---------------------------------------------------------------------------
// CLI entrypoint
// ---------------------------------------------------------------------------

function printHelp(): void {
  console.log(`
scan-wallet-acp — Hire x402janus via ACP marketplace for wallet scans

Usage:
  npx tsx scripts/scan-wallet-acp.ts <walletAddress> [options]
  npx tsx scripts/scan-wallet-acp.ts --job-id <id> [options]

Options:
  --timeout <seconds>       Max seconds to wait for completion (default: ${DEFAULT_TIMEOUT_SECONDS})
  --poll-interval <seconds> Seconds between status checks (default: ${DEFAULT_POLL_INTERVAL_SECONDS})
  --offering <name>         Specific x402janus offering name to use
  --json                    Output raw JSON result only (no progress messages)
  --job-id <id>             Skip creation; poll an existing job by ID
  -h, --help                Show this help

Environment variables:
  ACP_API_KEY          — Virtuals ACP API key (required)
  ACP_AGENT_WALLET     — Your agent's wallet address (optional)
  ACP_BASE_URL         — ACP base URL (default: https://claw-api.virtuals.io)
  JANUS_OFFERING_NAME  — Default offering name (optional)

Examples:
  npx tsx scripts/scan-wallet-acp.ts 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
  npx tsx scripts/scan-wallet-acp.ts 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --json
  npx tsx scripts/scan-wallet-acp.ts 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --timeout 180
  npx tsx scripts/scan-wallet-acp.ts --job-id 42
`);
}

function parseArgs(argv: string[]): {
  walletAddress?: string;
  jobId?: string;
  timeoutSeconds: number;
  pollIntervalSeconds: number;
  offeringName?: string;
  json: boolean;
} {
  const args = argv.slice(2);
  let walletAddress: string | undefined;
  let jobId: string | undefined;
  let timeoutSeconds = DEFAULT_TIMEOUT_SECONDS;
  let pollIntervalSeconds = DEFAULT_POLL_INTERVAL_SECONDS;
  let offeringName: string | undefined;
  let json = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "-h" || arg === "--help") {
      printHelp();
      process.exit(0);
    } else if (arg === "--json") {
      json = true;
    } else if (arg === "--timeout" && args[i + 1]) {
      timeoutSeconds = parseInt(args[++i], 10);
      if (isNaN(timeoutSeconds) || timeoutSeconds <= 0) {
        console.error("Error: --timeout must be a positive integer.");
        process.exit(1);
      }
    } else if (arg === "--poll-interval" && args[i + 1]) {
      pollIntervalSeconds = parseInt(args[++i], 10);
      if (isNaN(pollIntervalSeconds) || pollIntervalSeconds <= 0) {
        console.error("Error: --poll-interval must be a positive integer.");
        process.exit(1);
      }
    } else if (arg === "--offering" && args[i + 1]) {
      offeringName = args[++i];
    } else if (arg === "--job-id" && args[i + 1]) {
      jobId = args[++i];
    } else if (!arg.startsWith("--") && !walletAddress) {
      walletAddress = arg;
    }
  }

  return {
    walletAddress,
    jobId,
    timeoutSeconds,
    pollIntervalSeconds,
    offeringName,
    json,
  };
}

// Run when called directly
const isMain =
  process.argv[1]?.endsWith("scan-wallet-acp.ts") ||
  process.argv[1]?.endsWith("scan-wallet-acp.js");

if (isMain) {
  const parsed = parseArgs(process.argv);

  if (!parsed.walletAddress && !parsed.jobId) {
    console.error("Error: provide a wallet address or --job-id.");
    printHelp();
    process.exit(1);
  }

  const apiKey = process.env.ACP_API_KEY;
  if (!apiKey) {
    console.error("Error: ACP_API_KEY environment variable is not set.");
    console.error("Get your key at: https://claw-api.virtuals.io");
    process.exit(1);
  }

  const baseUrl = process.env.ACP_BASE_URL ?? DEFAULT_BASE_URL;
  const client = buildClient(apiKey, baseUrl);

  const run = async (): Promise<void> => {
    // Mode: poll existing job
    if (parsed.jobId && !parsed.walletAddress) {
      if (!parsed.json) {
        process.stderr.write(`\n  Polling existing job #${parsed.jobId}…\n\n`);
      }
      const job = await pollJobToCompletion(
        client,
        parsed.jobId,
        parsed.timeoutSeconds * 1000,
        parsed.pollIntervalSeconds * 1000,
        !parsed.json
      );

      const result: ScanResult = {
        jobId: job.id,
        walletAddress: "(from job)",
        phase: job.phase,
        deliverable: job.deliverable ?? null,
        data: parseDeliverable(job.deliverable),
        memos: job.memos ?? [],
      };

      if (parsed.json) {
        console.log(JSON.stringify(result, null, 2));
        return;
      }

      printResultHuman(result);
      return;
    }

    // Mode: full scan
    const result = await scanWalletAcp({
      walletAddress: parsed.walletAddress!,
      offeringName: parsed.offeringName,
      timeoutSeconds: parsed.timeoutSeconds,
      pollIntervalSeconds: parsed.pollIntervalSeconds,
      json: parsed.json,
    });

    if (parsed.json) {
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    printResultHuman(result);
  };

  run().catch((err) => {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`\n  Error: ${msg}\n`);
    process.exit(1);
  });
}

/**
 * Prints a scan result in human-readable format.
 *
 * @param result - Completed scan result.
 */
function printResultHuman(result: ScanResult): void {
  console.log("\n  x402janus ACP Scan Result");
  console.log("  ─────────────────────────");
  console.log(`  Job ID:  ${result.jobId}`);
  console.log(`  Wallet:  ${result.walletAddress}`);
  console.log(`  Status:  ${result.phase}`);
  console.log("");

  if (result.phase === "completed" && result.deliverable) {
    console.log("  Deliverable:");
    if (result.data && typeof result.data === "object") {
      // Pretty-print structured JSON data
      const lines = JSON.stringify(result.data, null, 2).split("\n");
      for (const line of lines) {
        console.log(`    ${line}`);
      }
    } else {
      console.log(`    ${result.deliverable}`);
    }
  } else if (result.phase === "rejected") {
    console.log("  Job was rejected by x402janus.");
    if (result.memos.length > 0) {
      console.log("  Last memo:", result.memos[result.memos.length - 1]?.content ?? "");
    }
  } else if (result.phase === "expired") {
    console.log("  Job expired without completion.");
  }

  if (result.memos.length > 0) {
    console.log("\n  History:");
    for (const m of result.memos) {
      console.log(`    [${m.nextPhase}] ${m.content} (${m.createdAt})`);
    }
  }

  console.log("");
}
