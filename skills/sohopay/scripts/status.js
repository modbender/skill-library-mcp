const { ethers } = require('ethers');
require('dotenv').config();

// --- CONFIGURATION ---
const USDC_DECIMALS = 6;

// Support both Base mainnet (default) and Base Sepolia testnet
const NETWORKS = {
    mainnet: {
        name: "base-mainnet",
        rpcUrl: "https://mainnet.base.org",
        chainId: 8453n, // Base mainnet
        addresses: {
            borrowerManager: "0xa891C7F98e3Eb42cB61213F28f3B8Aa13a8Be435",
            usdc: "0xB8c7a6A36978a7f9dc2C80e44533e7f17e271864",
        },
    },
    testnet: {
        name: "base-sepolia",
        rpcUrl: "https://sepolia.base.org",
        chainId: 84532n, // Base Sepolia
        addresses: {
            borrowerManager: "0xa891C7F98e3Eb42cB61213F28f3B8Aa13a8Be435",
            usdc: "0xB8c7a6A36978a7f9dc2C80e44533e7f17e271864",
        },
    },
};

// Use the *public mapping getter* s_borrowerProfiles(address) instead of getBorrowerProfile.
// ABI from your BorrowerManager:
// function s_borrowerProfiles(address) view returns (
//   uint256 creditLimit,
//   uint256 outstandingDebt,
//   uint256 totalSpent,
//   uint256 totalRepaid,
//   uint256 spendingCount,
//   uint256 repaymentCount,
//   uint256 lastActivityTime,
//   uint256 creditScore,
//   bool    isActive,
//   uint256 agentSpendLimit
// )
const BORROWER_MANAGER_ABI = [
    "function isBorrowerRegistered(address) view returns (bool)",
    "function isActiveBorrower(address) view returns (bool)",
    "function s_borrowerProfiles(address) view returns (uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,bool,uint256)",
];

const ERC20_ABI = [
    "function balanceOf(address) view returns (uint256)",
];

function printUsage() {
    console.error(`\nUSAGE:\n  node status.js                      # check bot status on mainnet\n  node status.js mainnet              # explicit mainnet\n  node status.js testnet              # Base Sepolia testnet\n`);
}

async function main() {
    const privateKey = process.env.PRIVATE_KEY;
    if (!privateKey) {
        console.error("❌ FATAL: PRIVATE_KEY environment variable not set. This script needs it to know which bot to inspect.");
        process.exit(1);
    }

    const args = process.argv.slice(2);
    let networkKey = "mainnet";

    if (args[0]) {
        const maybeNet = args[0].toLowerCase();
        if (maybeNet === "mainnet" || maybeNet === "testnet") {
            networkKey = maybeNet;
        } else {
            printUsage();
            process.exit(1);
        }
    }

    const networkConfig = NETWORKS[networkKey];

    const provider = new ethers.JsonRpcProvider(networkConfig.rpcUrl);
    const network = await provider.getNetwork();
    const actualChainId = Number(network.chainId);
    const expectedChainId = Number(networkConfig.chainId);

    if (actualChainId !== expectedChainId) {
        console.error(`❌ FATAL: Unexpected chainId ${actualChainId}. Expected ${expectedChainId} (${networkConfig.name}). Aborting.`);
        process.exit(1);
    }

    const wallet = new ethers.Wallet(privateKey, provider);
    const borrowerAddress = wallet.address;

    console.log("--- SOHO Pay Bot Status ---");
    console.log(`- Network: ${networkConfig.name} (${networkKey})`);
    console.log(`- Bot / Borrower address: ${borrowerAddress}`);
    console.log("-------------------------------------------");

    const borrowerManager = new ethers.Contract(
        networkConfig.addresses.borrowerManager,
        BORROWER_MANAGER_ABI,
        provider
    );

    console.log("\n🔍 Fetching registration & profile (via s_borrowerProfiles)...");
    const isRegistered = await borrowerManager.isBorrowerRegistered(borrowerAddress);
    const isActive = await borrowerManager.isActiveBorrower(borrowerAddress);

    let tuple;
    try {
        tuple = await borrowerManager.s_borrowerProfiles(borrowerAddress);
    } catch (err) {
        console.error("\n❌ Failed to read s_borrowerProfiles. ABI should match the on-chain mapping getter, but decode still failed.");
        console.error(err.reason || err.message || err);
        process.exit(1);
    }

    // tuple layout: [creditLimit, outstandingDebt, totalSpent, totalRepaid, spendingCount,
    //                repaymentCount, lastActivityTime, creditScore, isActive, agentSpendLimit]
    const creditLimit = tuple[0];
    const outstandingDebt = tuple[1];
    const totalSpent = tuple[2];
    const totalRepaid = tuple[3];
    const spendingCount = tuple[4];
    const repaymentCount = tuple[5];
    const lastActivityTime = tuple[6];
    const creditScore = tuple[7];
    const profileIsActive = tuple[8];
    const agentSpendLimit = tuple[9];

    // Fetch USDC wallet balance for this bot
    const usdc = new ethers.Contract(networkConfig.addresses.usdc, ERC20_ABI, provider);
    const usdcBalanceRaw = await usdc.balanceOf(borrowerAddress);
    const usdcBalance = ethers.formatUnits(usdcBalanceRaw, USDC_DECIMALS);

    console.log(`- Registered (mapping): ${isRegistered ? "✅ yes" : "❌ no"}`);
    console.log(`- Active (BorrowerManager): ${isActive ? "✅ yes" : "❌ no"}`);
    console.log(`- USDC wallet balance: ${usdcBalance} USDC`);

    console.log("\n📊 Borrower Profile (from s_borrowerProfiles):");
    console.log(`- Credit limit:       ${ethers.formatUnits(creditLimit, USDC_DECIMALS)} USDC`);
    console.log(`- Outstanding debt:   ${ethers.formatUnits(outstandingDebt, USDC_DECIMALS)} USDC`);
    console.log(`- Total spent:        ${ethers.formatUnits(totalSpent, USDC_DECIMALS)} USDC`);
    console.log(`- Total repaid:       ${ethers.formatUnits(totalRepaid, USDC_DECIMALS)} USDC`);
    console.log(`- Spending count:     ${spendingCount.toString()}`);
    console.log(`- Repayment count:    ${repaymentCount.toString()}`);
    console.log(`- Last activity time: ${Number(lastActivityTime) === 0n ? "never" : new Date(Number(lastActivityTime) * 1000).toISOString()}`);
    console.log(`- Credit score:       ${creditScore.toString()}`);
    console.log(`- isActive (profile): ${profileIsActive ? "✅ yes" : "❌ yes"}`);
    console.log(`- Agent spend limit:  ${ethers.formatUnits(agentSpendLimit, USDC_DECIMALS)} USDC`);

    // Friendly single-line summary for tools that grep the output
    console.log("\nSUMMARY:");
    console.log(`USDC balance for ${borrowerAddress} on ${networkConfig.name}: ${usdcBalance} USDC`);
    console.log(`Outstanding debt for ${borrowerAddress} on ${networkConfig.name}: ${ethers.formatUnits(outstandingDebt, USDC_DECIMALS)} USDC`);
}

main().catch((err) => {
    console.error("\n❌ Unexpected error in status.js:", err);
    process.exit(1);
});
