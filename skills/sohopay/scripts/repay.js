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
            creditor: "0xa7cf4D816183F5fC48e46Ccdaeea77311c69B568",
            borrowerManager: "0xa891C7F98e3Eb42cB61213F28f3B8Aa13a8Be435",
            usdc: "0xB8c7a6A36978a7f9dc2C80e44533e7f17e271864",
        },
    },
    testnet: {
        name: "base-sepolia",
        rpcUrl: "https://sepolia.base.org",
        chainId: 84532n, // Base Sepolia
        addresses: {
            creditor: "0xa7cf4D816183F5fC48e46Ccdaeea77311c69B568",
            borrowerManager: "0xa891C7F98e3Eb42cB61213F28f3B8Aa13a8Be435",
            usdc: "0xB8c7a6A36978a7f9dc2C80e44533e7f17e271864",
        },
    },
};

// --- ABIs ---
const CREDITOR_ABI = [
    "function repay(uint256 amount, address stablecoin) external",
];

const BORROWER_MANAGER_ABI = [
    "function isBorrowerRegistered(address) view returns (bool)",
    "function isActiveBorrower(address) view returns (bool)",
    "function getAgentSpendLimit(address) view returns (uint256)",
];

const ERC20_ABI = [
    "function balanceOf(address) view returns (uint256)",
    "function allowance(address owner, address spender) view returns (uint256)",
    "function approve(address spender, uint256 amount) returns (bool)",
];

function printUsage() {
    console.error(`\nUSAGE:\n  node repay.js <amount>                    # repay on mainnet (USDC)\n  node repay.js mainnet <amount>            # explicit mainnet\n  node repay.js testnet <amount>            # Base Sepolia testnet\n\nExamples:\n  node repay.js 5                            # repay 5 USDC on mainnet\n  node repay.js testnet 1.5                  # repay 1.5 USDC on testnet\n`);
}

async function main() {
    // 1. Load Signer from Environment
    const privateKey = process.env.PRIVATE_KEY;
    if (!privateKey) {
        console.error("❌ FATAL: PRIVATE_KEY environment variable not set. This script cannot sign transactions.");
        process.exit(1);
    }

    // 2. Parse Command-Line Arguments
    const args = process.argv.slice(2);
    if (args.length < 1) {
        printUsage();
        process.exit(1);
    }

    let networkKey = "mainnet";
    let amountString;

    if (args[0].toLowerCase() === "mainnet" || args[0].toLowerCase() === "testnet") {
        networkKey = args[0].toLowerCase();
        if (args.length < 2) {
            printUsage();
            process.exit(1);
        }
        amountString = args[1];
    } else {
        amountString = args[0];
    }

    const networkConfig = NETWORKS[networkKey];

    // Parse amount into USDC decimals
    let amount;
    try {
        amount = ethers.parseUnits(amountString, USDC_DECIMALS);
    } catch (e) {
        console.error(`❌ Invalid amount '${amountString}'. Must be a numeric value.`);
        process.exit(1);
    }

    if (amount === 0n) {
        console.error("❌ Amount must be greater than 0.");
        process.exit(1);
    }

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
    const borrowerAddress = wallet.address;

    console.log("--- SOHO Pay Repayment ---");
    console.log(`- Network: ${networkConfig.name} (${networkKey})`);
    console.log(`- Borrower (from PRIVATE_KEY): ${borrowerAddress}`);
    console.log(`- Requested repayment: ${amountString} USDC (${amount.toString()} atomic units)`);
    console.log("-------------------------------------------");

    const borrowerManager = new ethers.Contract(
        networkConfig.addresses.borrowerManager,
        BORROWER_MANAGER_ABI,
        provider
    );

    const usdc = new ethers.Contract(networkConfig.addresses.usdc, ERC20_ABI, provider);

    // 4. Pre-flight checks (registration & activity)
    console.log("\n🔍 Performing pre-flight checks...");
    const isRegistered = await borrowerManager.isBorrowerRegistered(borrowerAddress);
    const isActive = await borrowerManager.isActiveBorrower(borrowerAddress);
    const creditLimit = await borrowerManager.getAgentSpendLimit(borrowerAddress);

    console.log(`- Borrower Registered? ${isRegistered ? "✅ yes" : "❌ no"}`);
    console.log(`- Borrower Active? ${isActive ? "✅ yes" : "❌ no"}`);
    console.log(`- Current spend limit: ${ethers.formatUnits(creditLimit, USDC_DECIMALS)} USDC`);

    if (!isRegistered || !isActive) {
        if (!isRegistered) console.error("\n❌ REASON: Borrower is not registered with SOHO Pay.");
        if (!isActive) console.error("\n❌ REASON: Borrower is not active.");
        console.error("Repayment aborted due to failed borrower status checks.");
        process.exit(1);
    }

    // 5. Check USDC balance and allowance
    console.log("\n🔍 Checking USDC balance & allowance...");
    const balance = await usdc.balanceOf(borrowerAddress);
    const allowance = await usdc.allowance(borrowerAddress, networkConfig.addresses.creditor);

    console.log(`- USDC balance: ${ethers.formatUnits(balance, USDC_DECIMALS)} USDC`);
    console.log(`- Allowance to Creditor: ${ethers.formatUnits(allowance, USDC_DECIMALS)} USDC`);

    if (balance < amount) {
        console.error(`\n❌ REASON: Insufficient USDC balance. Need ${ethers.formatUnits(amount, USDC_DECIMALS)} but have ${ethers.formatUnits(balance, USDC_DECIMALS)}.`);
        process.exit(1);
    }

    const signerUsdc = usdc.connect(wallet);

    if (allowance < amount) {
        console.log("\n⚠️  Allowance is too low. Sending approve() for the repayment amount...");
        try {
            const approveTx = await signerUsdc.approve(networkConfig.addresses.creditor, amount);
            console.log(`- approve() tx hash: ${approveTx.hash}`);
            console.log("Waiting for approval confirmation...");
            const approveReceipt = await approveTx.wait();
            console.log(`- Approval confirmed in block: ${approveReceipt.blockNumber}`);
        } catch (error) {
            console.error("\n❌ approve() transaction failed:", error.reason || error.message);
            process.exit(1);
        }
    } else {
        console.log("\n✅ Existing allowance is sufficient; no approve() needed.");
    }

    // 6. Call Creditor.repay(amount, stablecoin)
    console.log("\n🚀 Submitting repay() transaction to the Creditor contract...");
    const creditor = new ethers.Contract(networkConfig.addresses.creditor, CREDITOR_ABI, wallet);

    try {
        const tx = await creditor.repay(amount, networkConfig.addresses.usdc);
        console.log(`- repay() tx hash: ${tx.hash}`);
        console.log("Waiting for confirmation...");
        const receipt = await tx.wait();
        console.log(`\n🎉 Repayment confirmed in block: ${receipt.blockNumber}`);
    } catch (error) {
        console.error("\n❌ Repayment transaction failed:", error.reason || error.message);
        process.exit(1);
    }
}

main().catch((err) => {
    console.error("\n❌ Unexpected error in repay.js:", err);
    process.exit(1);
});
