const { ethers } = require('ethers');
const crypto = require('crypto');
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
    "function spendWithAuthorization(address,address,address,uint256,uint256,bytes32,uint256,uint256,bytes)"
];
const BORROWER_MANAGER_ABI = [
    "function isBorrowerRegistered(address) view returns (bool)",
    "function isActiveBorrower(address) view returns (bool)",
    "function getAgentSpendLimit(address) view returns (uint256)",
    "function registerAgent(address agent) external",
];

async function main() {
    // 1. Load Signer from Environment
    const privateKey = process.env.PRIVATE_KEY;
    if (!privateKey) {
        console.error("❌ FATAL: PRIVATE_KEY environment variable not set. This skill cannot sign transactions.");
        process.exit(1);
    }

    // 2. Parse Command-Line Arguments
    // Usage:
    //   node pay.js <amount> <merchant_address>        # default: mainnet
    //   node pay.js mainnet <amount> <merchant_address>
    //   node pay.js testnet <amount> <merchant_address>
    if (process.argv.length < 4) {
        console.error("❌ USAGE: node pay.js [mainnet|testnet] <amount> <merchant_address>");
        process.exit(1);
    }

    let networkKey = "mainnet";
    let amountString;
    let merchantInput;

    const maybeNetwork = process.argv[2].toLowerCase();
    if (maybeNetwork === "mainnet" || maybeNetwork === "testnet") {
        networkKey = maybeNetwork;
        if (process.argv.length < 5) {
            console.error("❌ USAGE: node pay.js [mainnet|testnet] <amount> <merchant_address>");
            process.exit(1);
        }
        amountString = process.argv[3];
        merchantInput = process.argv[4];
    } else {
        // Default to mainnet if no explicit network is provided
        amountString = process.argv[2];
        merchantInput = process.argv[3];
    }

    const networkConfig = NETWORKS[networkKey];

    if (!ethers.isAddress(merchantInput)) {
        console.error("❌ ERROR: merchant_address must be a valid EVM address (0x...). No name-to-address or random generation is allowed.");
        process.exit(1);
    }

    const amount = ethers.parseUnits(amountString, USDC_DECIMALS);

    // 3. Setup Provider & Wallet
    const provider = new ethers.JsonRpcProvider(networkConfig.rpcUrl);

    // Safety guard: ensure we are on the expected Base network
    const network = await provider.getNetwork();
    // Normalise to numbers for comparison (ethers may return number or bigint depending on version)
    const actualChainId = Number(network.chainId);
    const expectedChainId = Number(networkConfig.chainId);

    if (actualChainId !== expectedChainId) {
        console.error(`❌ FATAL: Unexpected chainId ${actualChainId}. Expected ${expectedChainId} (${networkConfig.name}). Aborting.`);
        process.exit(1);
    }

    const wallet = new ethers.Wallet(privateKey, provider);
    const payerAddress = wallet.address;

    // Safety guard: warn if native balance looks too large for a test key
    const nativeBalance = await provider.getBalance(payerAddress);
    const nativeBalanceEth = Number(ethers.formatEther(nativeBalance));
    if (nativeBalanceEth > 0.5) {
        console.warn(`⚠️  WARNING: Signer native balance is ${nativeBalanceEth} ETH-equivalent, which is high for a testnet key. Ensure this is NOT a mainnet or real-funds wallet.`);
    }

    console.log(`--- Initializing SOHO Pay Transaction ---`);
    console.log(`- Network: ${networkConfig.name} (${networkKey})`);
    console.log(`- Signer (PRIVATE_KEY): ${payerAddress}`);

    // 4. Merchant Address (explicit only)
    const merchantAddress = merchantInput;
    console.log(`- Merchant (Address): ${merchantAddress}`);
    console.log(`- Amount: ${amountString} USDC (${amount.toString()} atomic units)`);
    console.log(`-------------------------------------------`);

    // 5. Pre-Flight Checks
    console.log("\n🔍 Performing Pre-Flight Checks...");
    const borrowerManager = new ethers.Contract(networkConfig.addresses.borrowerManager, BORROWER_MANAGER_ABI, provider);

    let isRegistered = await borrowerManager.isBorrowerRegistered(payerAddress);
    let isActive = await borrowerManager.isActiveBorrower(payerAddress);
    let creditLimit = await borrowerManager.getAgentSpendLimit(payerAddress);

    console.log(`- Borrower Registered? ${isRegistered ? '✅ Yes' : '❌ No'}`);
    console.log(`- Borrower Active? ${isActive ? '✅ Yes' : '❌ No'}`);
    console.log(`- Borrower Credit Limit: ${ethers.formatUnits(creditLimit, USDC_DECIMALS)} USDC`);

    // If the agent is not registered/active yet, attempt one-time auto-registration
    if (!isRegistered || !isActive) {
        console.log("\n🚀 Agent not registered/active on this BorrowerManager. Attempting auto-registration via registerAgent(agent)...");
        try {
            const borrowerManagerWithSigner = borrowerManager.connect(wallet);
            const tx = await borrowerManagerWithSigner.registerAgent(payerAddress);
            console.log(`- registerAgent tx hash: ${tx.hash}`);
            console.log("Waiting for confirmation...");
            const receipt = await tx.wait();
            console.log(`\n🎉 Agent registration confirmed in block: ${receipt.blockNumber}`);
        } catch (error) {
            console.error("\n❌ Auto-registration failed:", error.reason || error.message);
            console.error("Transaction aborted because the agent could not be registered.");
            process.exit(1);
        }

        // Re-run pre-flight checks after registration
        console.log("\n🔁 Re-checking borrower state after registration...");
        isRegistered = await borrowerManager.isBorrowerRegistered(payerAddress);
        isActive = await borrowerManager.isActiveBorrower(payerAddress);
        creditLimit = await borrowerManager.getAgentSpendLimit(payerAddress);

        console.log(`- Borrower Registered? ${isRegistered ? '✅ Yes' : '❌ No'}`);
        console.log(`- Borrower Active? ${isActive ? '✅ Yes' : '❌ No'}`);
        console.log(`- Borrower Credit Limit: ${ethers.formatUnits(creditLimit, USDC_DECIMALS)} USDC`);
    }

    if (!isRegistered || !isActive || creditLimit < amount) {
        if (!isRegistered) console.error("\n❌ REASON: Borrower is not registered.");
        if (!isActive) console.error("\n❌ REASON: Borrower is not active.");
        if (creditLimit < amount) console.error(`\n❌ REASON: Credit limit (${ethers.formatUnits(creditLimit, USDC_DECIMALS)}) is less than amount (${amountString}).`);
        console.error("Transaction aborted due to failed pre-flight checks.");
        process.exit(1);
    }
    console.log("✅ All checks passed.");

    // 6. EIP-712 Signing
    const domain = { name: 'CreditContract', version: '1', chainId: Number(networkConfig.chainId), verifyingContract: networkConfig.addresses.creditor };
    const types = {
        SpendWithAuthorization: [
            { name: 'payer', type: 'address' }, { name: 'merchant', type: 'address' },
            { name: 'asset', type: 'address' }, { name: 'amount', type: 'uint256' },
            { name: 'paymentPlanId', type: 'uint256' }, { name: 'nonce', type: 'bytes32' },
            { name: 'validAfter', type: 'uint256' }, { name: 'expiry', type: 'uint256' }
        ]
    };
    const nonce = '0x' + crypto.randomBytes(32).toString('hex');
    const now = Math.floor(Date.now() / 1000);
    const message = {
        payer: payerAddress, merchant: merchantAddress, asset: networkConfig.addresses.usdc,
        amount: amount, paymentPlanId: 0, nonce: nonce,
        validAfter: now - 60, expiry: now + 600
    };
    
    console.log("\n✍️  Signing EIP-712 message...");
    const signature = await wallet.signTypedData(domain, types, message);

    // 7. Execute Transaction
    const creditorContract = new ethers.Contract(networkConfig.addresses.creditor, CREDITOR_ABI, wallet);
    try {
        console.log("\n🚀 Submitting transaction to the blockchain...");
        const tx = await creditorContract.spendWithAuthorization(
            message.payer, message.merchant, message.asset, message.amount,
            message.paymentPlanId, message.nonce, message.validAfter, message.expiry,
            signature
        );
        console.log(`\n✅ Transaction sent! Hash: ${tx.hash}`);
        console.log(`Waiting for confirmation...`);
        const receipt = await tx.wait();
        console.log(`\n🎉 Transaction confirmed in block: ${receipt.blockNumber}`);
    } catch (error) {
        console.error("\n❌ On-Chain Transaction Failed:", error.reason || error.message);
        process.exit(1);
    }
}

main();
