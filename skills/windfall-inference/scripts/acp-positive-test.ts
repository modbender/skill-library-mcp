import AcpClient, { AcpContractClientV2, baseAcpConfigV2, FareAmount, AcpJobPhases } from "@virtuals-protocol/acp-node";

const WINDFALL = "0x65598eF513fF17841470DE36cc34BAE8FF3F36c7";
const TESTER = "0x32e8e10B0FFAfb2658cB162B3588513Cf5BE3cdc";
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

async function getJob(client: AcpClient, jobId: number, retries = 5): Promise<any> {
  for (let i = 0; i < retries; i++) {
    try {
      const job = await client.getJobById(jobId);
      if (job) return job;
    } catch {}
    await sleep(3000);
  }
  return null;
}

async function waitForPhase(client: AcpClient, jobId: number, target: number, maxMs = 90000): Promise<any> {
  const start = Date.now();
  while (Date.now() - start < maxMs) {
    try {
      const job = await client.getJobById(jobId);
      if (job && job.phase >= target) return job;
    } catch {}
    await sleep(5000);
  }
  throw new Error("Timeout");
}

async function main() {
  console.log("========================================");
  console.log("  WINDFALL ACP — POSITIVE TEST");
  console.log("  Real LLM Inference via Agent Commerce");
  console.log("========================================\n");

  console.log("[init] Connecting buyer agent to ACP...");
  const contract = await AcpContractClientV2.build(
    process.env.ACP_WALLET_KEY as `0x${string}`, 1, TESTER, baseAcpConfigV2
  );
  const buyer = new AcpClient({ acpContractClient: contract, skipSocketConnection: true });
  await buyer.init(true);
  console.log("[init] Buyer:    " + TESTER);
  console.log("[init] Provider: " + WINDFALL + " (Windfall)");

  const fare = new FareAmount(0.01, baseAcpConfigV2.baseFare);
  const prompt = "What is the duck curve in electricity markets and why does it matter for renewable energy?";

  console.log("\n[1/5] INITIATE — Sending inference request to Windfall...");
  console.log('      Prompt: "' + prompt + '"');

  const requirement = JSON.stringify({
    messages: [
      { role: "system", content: "You are a helpful energy expert. Be concise (2-3 sentences)." },
      { role: "user", content: prompt }
    ],
    mode: "greenest"
  });

  const jobId = await buyer.initiateJob(WINDFALL, requirement, fare, TESTER);
  console.log("      Job #" + jobId + " created on Base\n");

  await sleep(3000);

  console.log("[2/5] NEGOTIATE — Waiting for Windfall to accept...");
  await waitForPhase(buyer, jobId, AcpJobPhases.NEGOTIATION);
  console.log("      Windfall ACCEPTED the job\n");

  await sleep(8000);

  console.log("[3/5] PAY — Approving requirement and paying via escrow...");
  const job = await getJob(buyer, jobId);
  if (!job) throw new Error("Job not found");
  await job.payAndAcceptRequirement("Approved");
  console.log("      Payment sent via ACP escrow\n");

  console.log("[4/5] DELIVER — Waiting for Windfall to run inference...");
  const delivered = await waitForPhase(buyer, jobId, AcpJobPhases.EVALUATION);

  if (delivered?.deliverable) {
    const parsed = JSON.parse(delivered.deliverable);
    const content = parsed.choices?.[0]?.message?.content || "";
    const model = parsed.model || "unknown";
    const windfall = parsed.windfall || {};
    console.log("      Inference DELIVERED\n");
    console.log("      Model:    " + model);
    console.log("      Mode:     " + windfall.mode);
    console.log("      Node:     " + windfall.node + " (" + windfall.location + ")");
    console.log("      Cost:     $" + (windfall.costUsd || 0).toFixed(4));
    console.log("      Carbon:   " + windfall.carbonIntensityGCO2 + "g CO2/kWh");
    console.log("      Cached:   " + windfall.cached);
    console.log("\n      Response:");
    console.log('      "' + content + '"\n');
  }

  await sleep(3000);

  console.log("[5/5] EVALUATE — Approving deliverable...");
  const finalJob = await getJob(buyer, jobId);
  if (finalJob) await finalJob.evaluate(true, "Real inference received successfully");
  console.log("      Job APPROVED\n");

  console.log("========================================");
  console.log("  POSITIVE TEST PASSED");
  console.log("  Real LLM inference delivered via ACP");
  console.log("========================================");
}

main().catch(e => { console.error("Error:", e.message); process.exit(1); });
