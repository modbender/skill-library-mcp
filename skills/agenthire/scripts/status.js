#!/usr/bin/env node
// agenthire_status — Check job status
require("dotenv").config({ path: __dirname + "/../.env" });
const { ethers } = require("ethers");
const escrowAbi = require("./JobEscrow.abi.json");

async function main() {
    const jobId = parseInt(process.argv[2]);
    if (!jobId) {
        console.log("Usage: node status.js <jobId>");
        process.exit(1);
    }

    const provider = new ethers.JsonRpcProvider(process.env.AGENTHIRE_RPC_URL);
    const escrow = new ethers.Contract(process.env.AGENTHIRE_ESCROW, escrowAbi, provider);

    const job = await escrow.getJob(jobId);
    const status = Number(job[7]);
    const amount = ethers.formatEther(job[4]);
    const task = job[5];
    const result = job[6];
    const rating = Number(job[8]);

    const statusMap = {
        0: "⏳ Created (waiting for provider)",
        1: "📤 Submitted (result ready)",
        2: "✅ Completed",
        3: "❌ Cancelled",
    };

    console.log(`Job #${jobId}:`);
    console.log(`  Status: ${statusMap[status] || "Unknown"}`);
    console.log(`  Amount: ${amount} ETH`);
    console.log(`  Task: ${task}`);
    if (result) console.log(`  Result: ${result}`);
    if (rating > 0) console.log(`  Rating: ${rating}/5 ⭐`);
}

main().catch(err => { console.error("Error:", err.message); process.exit(1); });
