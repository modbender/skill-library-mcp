/**
 * ACP Graduation Script (buyer-only)
 *
 * Runs 10 successful jobs as a buyer against Windfall's ACP handler.
 * The server's acp-handler.ts handles the provider side (accept, requirement, deliver)
 * via WebSocket — this script only acts as the buyer.
 *
 * Lifecycle per job:
 *   1. Buyer initiates with real inference requirement (JSON messages)
 *   2. Wait for provider to accept + create requirement (server handler)
 *   3. Buyer pays and accepts requirement
 *   4. Wait for provider to deliver real inference (server handler)
 *   5. Buyer evaluates deliverable
 *
 * Usage: ACP_WALLET_KEY=0x... npx ts-node scripts/graduate.ts
 */

import AcpClient, {
  AcpContractClientV2,
  baseAcpConfigV2,
  FareAmount,
  AcpJobPhases,
} from '@virtuals-protocol/acp-node';

const WALLET_KEY = process.env.ACP_WALLET_KEY;
if (!WALLET_KEY) {
  console.error('Set ACP_WALLET_KEY env var (0x-prefixed private key)');
  process.exit(1);
}

const WINDFALL_AGENT = '0x65598eF513fF17841470DE36cc34BAE8FF3F36c7' as const;
const TESTER_AGENT = '0x32e8e10B0FFAfb2658cB162B3588513Cf5BE3cdc' as const;
const TESTER_ENTITY_ID = 1;
const TOTAL_JOBS = 10;

// Real inference prompts — varied to avoid cache hits across jobs
const PROMPTS = [
  'What are three key advantages of distributed energy resources for grid resilience?',
  'In two sentences, explain how a power purchase agreement works.',
  'How do virtual power plants aggregate distributed energy?',
  'What is the duck curve and why is it a challenge for grid operators?',
  'Describe the role of pumped hydro storage in renewable energy systems.',
  'How does time-of-use pricing encourage demand flexibility?',
  'What is the difference between capacity markets and energy markets?',
  'Explain how offshore wind farms connect to onshore grids.',
  'What are renewable energy certificates and how do they work?',
  'How does vehicle-to-grid technology support renewable integration?',
];

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function waitForPhase(
  client: AcpClient,
  jobId: number,
  targetPhase: number,
  label: string,
  maxWaitMs = 90000,
): Promise<any> {
  const start = Date.now();
  while (Date.now() - start < maxWaitMs) {
    try {
      const job = await client.getJobById(jobId);
      if (job) {
        console.log(`    [${label}] phase=${job.phase}, memos=${job.memos?.length || 0}`);
        if (job.phase >= targetPhase) return job;
      } else {
        console.log(`    [${label}] job not indexed yet, retrying...`);
      }
    } catch {
      // SDK beta.30 throws "Job not found" instead of returning null when not yet indexed
      console.log(`    [${label}] job not indexed yet, retrying...`);
    }
    await sleep(5000);
  }
  throw new Error(`Timeout waiting for phase ${targetPhase} (${label})`);
}

async function main() {
  console.log('Initializing ACP buyer client...');

  const buyerContract = await AcpContractClientV2.build(
    WALLET_KEY as `0x${string}`,
    TESTER_ENTITY_ID,
    TESTER_AGENT,
    baseAcpConfigV2,
  );

  const buyer = new AcpClient({
    acpContractClient: buyerContract,
    skipSocketConnection: true,
  });
  await buyer.init(true);

  console.log(`Buyer: ${buyer.walletAddress}`);
  console.log(`Provider (Windfall): ${WINDFALL_AGENT}`);
  console.log(`Jobs to run: ${TOTAL_JOBS}\n`);

  const fare = new FareAmount(0.01, baseAcpConfigV2.baseFare);

  let successCount = 0;

  for (let i = 1; i <= TOTAL_JOBS; i++) {
    const prompt = PROMPTS[(i - 1) % PROMPTS.length];
    console.log(`\n--- Job ${i}/${TOTAL_JOBS} ---`);
    console.log(`  Prompt: "${prompt.slice(0, 60)}..."`);

    try {
      // 1. Buyer initiates job with real inference requirement
      console.log('  [1/4] Initiating job...');
      const requirement = JSON.stringify({
        messages: [
          { role: 'system', content: 'You are a helpful energy and sustainability expert. Be concise.' },
          { role: 'user', content: prompt },
        ],
        mode: 'greenest',
      });

      const jobId = await buyer.initiateJob(
        WINDFALL_AGENT,
        requirement,
        fare,
        TESTER_AGENT,
      );
      console.log(`  Job #${jobId} created`);

      // Brief pause for job indexing before polling
      await sleep(3000);

      // 2. Wait for provider to accept + create requirement (server acp-handler)
      console.log('  [2/4] Waiting for provider to accept...');
      await waitForPhase(buyer, jobId, AcpJobPhases.NEGOTIATION, 'negotiation');

      // Need to wait for the requirement memo to appear
      await sleep(8000);

      // 3. Buyer pays and accepts requirement
      console.log('  [3/4] Paying and accepting...');
      let buyerJob: any = null;
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          buyerJob = await buyer.getJobById(jobId);
          if (buyerJob) break;
        } catch { /* retry */ }
        await sleep(3000);
      }
      if (!buyerJob) throw new Error(`Job ${jobId} not found by buyer`);
      console.log(`    phase=${buyerJob.phase}, memos=${buyerJob.memos?.length}`);
      await buyerJob.payAndAcceptRequirement('Approved');
      console.log('  Paid');

      // 4. Wait for provider to deliver real inference (server acp-handler)
      console.log('  [4/4] Waiting for delivery...');
      buyerJob = await waitForPhase(buyer, jobId, AcpJobPhases.EVALUATION, 'delivery');

      // Parse and display the deliverable
      const deliverable = buyerJob?.deliverable;
      if (deliverable) {
        try {
          const parsed = JSON.parse(deliverable);
          const content = parsed.choices?.[0]?.message?.content;
          const model = parsed.model || parsed.windfall?.model || 'unknown';
          const cached = parsed.windfall?.cached ? ' (cached)' : '';
          console.log(`  Model: ${model}${cached}`);
          console.log(`  Response: "${(content || '').slice(0, 120)}..."`);
        } catch {
          console.log(`  Deliverable (raw): ${deliverable.slice(0, 200)}`);
        }
      }

      await sleep(3000);

      // 5. Buyer evaluates
      console.log('  Evaluating...');
      try {
        buyerJob = await buyer.getJobById(jobId);
      } catch {
        await sleep(3000);
        buyerJob = await buyer.getJobById(jobId);
      }
      if (!buyerJob) throw new Error(`Job ${jobId} not found`);
      await buyerJob.evaluate(true, 'Real inference received successfully');
      console.log('  APPROVED');

      successCount++;
      console.log(`  Job ${i} DONE (${successCount}/${TOTAL_JOBS})`);

      if (i < TOTAL_JOBS) await sleep(3000);
    } catch (err: any) {
      console.error(`  Job ${i} failed: ${err.message}`);
      let inner = err.cause || err.innerError || err.error;
      let depth = 0;
      while (inner && depth < 3) {
        console.error(`  Cause [${depth}]:`, (inner.message || inner.toString()).slice(0, 500));
        inner = inner.cause || inner.innerError || inner.error;
        depth++;
      }
      console.log('  Continuing...');
      await sleep(5000);
    }
  }

  console.log(`\n${'='.repeat(50)}`);
  console.log(`Completed: ${successCount}/${TOTAL_JOBS} successful jobs`);
  if (successCount >= 10) {
    console.log('Graduation criteria met!');
  } else {
    console.log(`Need ${10 - successCount} more. Re-run to continue.`);
  }
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
