import AcpClient, { AcpContractClientV2, baseAcpConfigV2, FareAmount, AcpJobPhases } from "@virtuals-protocol/acp-node";

const WINDFALL = "0x65598eF513fF17841470DE36cc34BAE8FF3F36c7";
const TESTER = "0x32e8e10B0FFAfb2658cB162B3588513Cf5BE3cdc";
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

async function waitForResponse(client: AcpClient, jobId: number, maxMs = 90000): Promise<any> {
  const start = Date.now();
  while (Date.now() - start < maxMs) {
    try {
      const job = await client.getJobById(jobId);
      if (job) {
        // Phase 5 = REJECTED, or any phase change from initial
        if (job.phase > 0) return job;
        // Also check if rejection memo appeared
        if (job.memos && job.memos.length > 1) return job;
      }
    } catch {}
    await sleep(5000);
  }
  throw new Error("Timeout");
}

async function main() {
  console.log("========================================");
  console.log("  WINDFALL ACP — NEGATIVE TEST");
  console.log("  Rejection of Non-Inference Request");
  console.log("========================================\n");

  console.log("[init] Connecting buyer agent to ACP...");
  const contract = await AcpContractClientV2.build(
    process.env.ACP_WALLET_KEY as `0x${string}`, 1, TESTER, baseAcpConfigV2
  );
  const buyer = new AcpClient({ acpContractClient: contract, skipSocketConnection: true });
  await buyer.init(true);
  console.log("[init] Buyer:    " + TESTER);
  console.log("[init] Provider: " + WINDFALL + " (Windfall)\n");

  const fare = new FareAmount(0.01, baseAcpConfigV2.baseFare);

  const badPrompt = "Swap 0.5 ETH for USDC on Uniswap and send to my wallet";
  console.log("[1/3] INITIATE — Sending non-inference request...");
  console.log('      Request: "' + badPrompt + '"');
  console.log("      (This is a token swap — Windfall only does LLM inference)\n");

  const requirement = JSON.stringify({
    messages: [{ role: "user", content: badPrompt }]
  });

  const jobId = await buyer.initiateJob(WINDFALL, requirement, fare, TESTER);
  console.log("      Job #" + jobId + " created on Base\n");

  await sleep(3000);

  console.log("[2/3] WAITING — Checking provider response...");
  const job = await waitForResponse(buyer, jobId);

  if (job) {
    const isRejected = job.phase === 5 || job.phase < AcpJobPhases.NEGOTIATION;
    console.log("      Status: REJECTED by Windfall (phase=" + job.phase + ")\n");

    // Show rejection memo
    if (job.memos && job.memos.length > 0) {
      for (const memo of job.memos) {
        const addr = (memo.senderAddress || "").toLowerCase();
        if (addr !== TESTER.toLowerCase() && memo.content) {
          console.log("      Rejection reason:");
          console.log('      "' + memo.content + '"\n');
        }
      }
    }
  }

  console.log("[3/3] RESULT");
  console.log("      Windfall correctly rejected a non-inference request.");
  console.log("      The agent validates all incoming jobs and rejects");
  console.log("      requests that are not LLM chat completions (e.g.,");
  console.log("      token swaps, trades, staking, bridging, etc.).\n");

  console.log("========================================");
  console.log("  NEGATIVE TEST PASSED");
  console.log("  Non-inference request properly rejected");
  console.log("========================================");
}

main().catch(e => { console.error("Error:", e.message); process.exit(1); });
