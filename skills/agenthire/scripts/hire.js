#!/usr/bin/env node
// agenthire_hire — Hire an agent from the marketplace
require("dotenv").config({ path: __dirname + "/../.env" });
const { ethers } = require("ethers");
const registryAbi = require("./ServiceRegistry.abi.json");
const escrowAbi = require("./JobEscrow.abi.json");

async function main() {
    const serviceId = parseInt(process.argv[2]);
    const task = process.argv[3];

    if (!serviceId || !task) {
        console.log('Usage: node hire.js <serviceId> "<task description>"');
        process.exit(1);
    }

    const provider = new ethers.JsonRpcProvider(process.env.AGENTHIRE_RPC_URL);
    const wallet = new ethers.Wallet(process.env.AGENTHIRE_PRIVATE_KEY, provider);
    const registry = new ethers.Contract(process.env.AGENTHIRE_REGISTRY, registryAbi, provider);
    const escrow = new ethers.Contract(process.env.AGENTHIRE_ESCROW, escrowAbi, wallet);

    // Get service price
    const s = await registry.getService(serviceId);
    const price = s[5]; // pricePerJob in wei
    const name = s[2];
    console.log(`Hiring ${name} (ID: ${serviceId}) for ${ethers.formatEther(price)} ETH...`);

    // Create job with escrow (explicit nonce for testnet)
    const nonce = await wallet.getNonce("pending");
    const tx = await escrow.createJob(serviceId, task, { value: price, nonce });
    const receipt = await tx.wait();

    // Parse JobCreated event to get jobId
    const event = receipt.logs.find(log => {
        try { return escrow.interface.parseLog(log)?.name === "JobCreated"; }
        catch { return false; }
    });
    const jobId = event ? Number(escrow.interface.parseLog(event).args[0]) : 0;

    console.log(`Job #${jobId} created! Escrow locked. TX: ${tx.hash}`);
    console.log("Waiting for provider to complete (max 120s)...");

    // Poll for result
    const maxWait = 120_000;
    const poll = 5_000;
    let elapsed = 0;

    while (elapsed < maxWait) {
        const job = await escrow.getJob(jobId);
        const status = Number(job[7]); // status field
        const result = job[6]; // result field

        if (status === 1 || status === 2) {
            // Status 1 = Submitted (need to confirm)
            // Status 2 = Already completed
            if (status === 1) {
                console.log("\nProvider delivered! Confirming + rating...");
                try {
                    await new Promise(r => setTimeout(r, 3000));
                    const cNonce = await wallet.getNonce("pending");
                    const confirmTx = await escrow.confirmComplete(jobId, { nonce: cNonce });
                    await confirmTx.wait();
                    console.log("Payment released!");

                    await new Promise(r => setTimeout(r, 3000));
                    const rNonce = await wallet.getNonce("pending");
                    const rateTx = await escrow.rateJob(jobId, 5, { nonce: rNonce });
                    await rateTx.wait();
                    console.log("Rated 5/5 stars.");
                } catch (e) {
                    console.log("Auto-completed by provider.");
                }
            } else {
                console.log("\nJob completed!");
            }

            // Parse result
            try {
                const r = JSON.parse(result);
                if (r.success) {
                    console.log(`\nResult: Swapped ${r.amountIn} ${r.fromToken} → ${r.amountOut} ${r.toToken}`);
                    console.log(`TX Hash: ${r.txHash}`);
                    if (r.basescanUrl) console.log(`Verify: ${r.basescanUrl}`);
                    console.log(`DEX: ${r.dex}`);
                } else {
                    console.log(`\nJob failed: ${r.error}`);
                }
            } catch {
                console.log(`\nResult: ${result}`);
            }
            process.exit(0);
        }

        if (status === 3) {
            console.log(`\nJob #${jobId} was cancelled.`);
            process.exit(1);
        }

        process.stdout.write(".");
        await new Promise(r => setTimeout(r, poll));
        elapsed += poll;
    }

    console.log(`\nTimeout — provider didn't respond in 120s. Job #${jobId} still pending.`);
    console.log("Check later: node status.js " + jobId);
}

main().catch(err => { console.error("Error:", err.message); process.exit(1); });
