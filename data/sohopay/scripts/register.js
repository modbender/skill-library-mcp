const { ethers } = require('ethers');
require('dotenv').config();

// --- CONFIGURATION ---
const USDC_DECIMALS = 6; // for logging credit limits nicely

// Support both Base mainnet (default) and Base Sepolia testnet
const NETWORKS = {
    mainnet: {
        name: "base-mainnet",
        rpcUrl: "https://mainnet.base.org",
        chainId: 8453n, // Base mainnet
        addresses: {
            borrowerManager: "0xa891C7F98e3Eb42cB61213F28f3B8Aa13a8Be435",
        },
    },
    testnet: {
        name: "base-sepolia",
        rpcUrl: "https://sepolia.base.org",
        chainId: 84532n, // Base Sepolia
        addresses: {
            borrowerManager: "0xa891C7F98e3Eb42cB61213F28f3B8Aa13a8Be435",
        },
    },
};

const BORROWER_MANAGER_ABI = [
    "function isBorrowerRegistered(address) view returns (bool)",
    "function isActiveBorrower(address) view returns (bool)",
    "function getAgentSpendLimit(address) view returns (uint256)",
    "function registerAgent(address agent) external",
];

function printUsage() {
    console.error(`\nUSAGE:\n  node register.js                       # register this bot (PRIVATE_KEY) on mainnet\n  node register.js mainnet               # same as above\n  node register.js testnet               # register this bot on Base Sepolia (testnet)\n  node register.js mainnet check         # ONLY check status for this bot on mainnet\n  node register.js testnet check         # ONLY check status for this bot on testnet\n\nThis script always operates on the address derived from PRIVATE_KEY.\n`);
}

async function main() {
    // 1. Load Signer from Environment
    const privateKey = process.env.PRIVATE_KEY;
    if (!privateKey) {
        console.error("❌ FATAL: PRIVATE_KEY environment variable not set. This skill cannot sign transactions.");
        process.exit(1);
    }

    // 2. Parse Command-Line Arguments
    // Examples:
    //   node register.js                   # default: mainnet, register
    //   node register.js mainnet           # mainnet, register
    //   node register.js testnet           # testnet, register
    //   node register.js mainnet check     # mainnet, check-only
    //   node register.js testnet check     # testnet, check-only

    let networkKey = "mainnet";
    let mode = "register"; // or "check"

    const args = process.argv.slice(2).map((a) => a.toLowerCase());

    for (const arg of args) {
        if (arg === "mainnet" || arg === "testnet") {
            networkKey = arg;
        } else if (arg === "check" || arg === "status" || arg === "--check") {
            mode = "check";
        } else {
            console.error(`❌ Unknown argument: ${arg}`);
            printUsage();
            process.exit(1);
        }
    }

    const networkConfig = NETWORKS[networkKey];

    // 3. Setup Provider & Wallet
    const provider = new ethers.JsonRpcProvider(networkConfig.rpcUrl);

    const network = await provider.getNetwork();
    const actualChainId = Number(network.chainId);
    const expectedChainId = Number(networkConfig.chainId);

    if (actualChainId !== expectedChainId) {
        console.error(`❌ FATAL: Unexpected chainId ${actualChainId}. Expected ${expectedChainId} (${networkConfig.name}). Aborting.`);
        process.exit(1);
    }

    const wallet = new ethers.Wallet(privateKey, provider);
    const botAddress = wallet.address;

    console.log("--- SOHO Pay Bot Registration / Status ---");
    console.log(`- Network: ${networkConfig.name} (${networkKey})`);
    console.log(`- Bot address (from PRIVATE_KEY): ${botAddress}`);
    console.log("-------------------------------------------");

    const borrowerManager = new ethers.Contract(
        networkConfig.addresses.borrowerManager,
        BORROWER_MANAGER_ABI,
        wallet
    );

    // 4. Check current registration state (works for both register + check-only)
    console.log("\n🔍 Checking current bot state...");
    const isRegistered = await borrowerManager.isBorrowerRegistered(botAddress);
    const isActive = await borrowerManager.isActiveBorrower(botAddress);
    const creditLimit = await borrowerManager.getAgentSpendLimit(botAddress).catch(() => 0n);

    console.log(`- isRegistered: ${isRegistered ? "✅ yes" : "❌ no"}`);
    console.log(`- isActive: ${isActive ? "✅ yes" : "❌ no"}`);
    if (creditLimit) {
        console.log(`- Current spend limit: ${ethers.formatUnits(creditLimit, USDC_DECIMALS)} USDC`);
    }

    // If user only wants to check status, we're done.
    if (mode === "check") {
        console.log("\nℹ️  Check-only mode: no registration transaction sent.");
        return;
    }

    // If already active, nothing more to do.
    if (isActive) {
        console.log("\n✅ Bot is already active with SOHO Pay on this network. No registration transaction needed.");
        return;
    }

    // 5. Send registration transaction
    console.log("\n🚀 Sending registerAgent transaction for this bot...");
    try {
        const tx = await borrowerManager.registerAgent(botAddress);
        console.log(`- Tx hash: ${tx.hash}`);
        console.log("Waiting for confirmation...");
        const receipt = await tx.wait();
        console.log(`\n🎉 Bot registered in block: ${receipt.blockNumber}`);
    } catch (error) {
        console.error("\n❌ Registration transaction failed:", error.reason || error.message);
        process.exit(1);
    }
}

main().catch((err) => {
    console.error("\n❌ Unexpected error in register.js:", err);
    process.exit(1);
});
