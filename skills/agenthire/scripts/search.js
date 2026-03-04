#!/usr/bin/env node
// agenthire_search — Search AgentHire marketplace
require("dotenv").config({ path: __dirname + "/../.env" });
const { ethers } = require("ethers");
const registryAbi = require("./ServiceRegistry.abi.json");

async function main() {
    const tag = process.argv[2];
    if (!tag) {
        console.log("Usage: node search.js <skill-tag>");
        console.log("Tags: token-swap, defi, trading, research, translation, coding, analysis");
        process.exit(1);
    }

    const provider = new ethers.JsonRpcProvider(process.env.AGENTHIRE_RPC_URL);
    const registry = new ethers.Contract(process.env.AGENTHIRE_REGISTRY, registryAbi, provider);

    const serviceIds = await registry.findByTag(tag);

    if (serviceIds.length === 0) {
        console.log(`No agents found for "${tag}".`);
        process.exit(0);
    }

    console.log(`Found ${serviceIds.length} agent(s) for "${tag}":\n`);

    for (let i = 0; i < serviceIds.length; i++) {
        const s = await registry.getService(serviceIds[i]);
        const id = Number(s[0]);
        const name = s[2];
        const description = s[3];
        const tags = s[4];
        const price = ethers.formatEther(s[5]);
        const active = s[6];
        const totalJobs = Number(s[7]);
        const totalRating = Number(s[8]);
        const ratingCount = Number(s[9]);
        const avgRating = ratingCount > 0 ? (totalRating / ratingCount).toFixed(1) : "new";

        if (!active) continue;

        console.log(`${i + 1}. ${name} (ID: ${id})`);
        console.log(`   Rating: ${avgRating} stars | Price: ${price} ETH/job | Jobs: ${totalJobs}`);
        console.log(`   Tags: ${tags.join(", ")}`);
        console.log(`   ${description}\n`);
    }
}

main().catch(err => { console.error("Error:", err.message); process.exit(1); });
