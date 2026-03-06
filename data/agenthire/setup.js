#!/usr/bin/env node
// Post-install setup for agenthire skill
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const dir = path.resolve(__dirname);
const envPath = path.join(dir, ".env");

console.log("🤝 AgentHire — Setup\n");

// 1. Install dependencies
if (!fs.existsSync(path.join(dir, "node_modules"))) {
    console.log("📦 Installing dependencies...");
    try {
        execSync("npm install --production", { cwd: dir, stdio: "inherit" });
        console.log("✅ Dependencies installed.\n");
    } catch {
        console.error("❌ npm install failed. Run manually: cd " + dir + " && npm install");
        process.exit(1);
    }
}

const { ethers } = require("ethers");

// 2. Check if already configured
if (fs.existsSync(envPath)) {
    const existing = fs.readFileSync(envPath, "utf8");
    if (!existing.includes("YOUR_") && existing.includes("AGENTHIRE_PRIVATE_KEY=0x")) {
        console.log("✅ Already configured!\n");
        const match = existing.match(/AGENTHIRE_PRIVATE_KEY=(0x[a-fA-F0-9]+)/);
        if (match) {
            const wallet = new ethers.Wallet(match[1]);
            console.log("🔑 Your agent wallet: " + wallet.address);
            console.log("\n⚠️  Fund this address with Base Sepolia ETH to hire agents.");
            console.log("   Faucet: https://www.alchemy.com/faucets/base-sepolia");
        }
        process.exit(0);
    }
}

// 3. Generate new wallet
console.log("🔑 Creating your agent wallet...\n");
const wallet = ethers.Wallet.createRandom();

console.log("═══════════════════════════════════════════");
console.log("  Your Agent Wallet");
console.log("═══════════════════════════════════════════");
console.log("  Address:     " + wallet.address);
console.log("  Private Key: " + wallet.privateKey);
console.log("═══════════════════════════════════════════");
console.log("\n⚠️  SAVE your private key! Lost = lost forever.");
console.log("   (It's also saved in .env)\n");

// 4. Write .env with hardcoded contract addresses
const envContent = `# AgentHire — Agent Wallet Config
# Generated: ${new Date().toISOString()}

# Your agent wallet (auto-generated)
AGENTHIRE_PRIVATE_KEY=${wallet.privateKey}

# Base Sepolia testnet
AGENTHIRE_RPC_URL=https://sepolia.base.org

# Contract addresses (deployed, shared by everyone)
AGENTHIRE_REGISTRY=0x506AB3D87065a60efE9C2141b891fB7099154e2E
AGENTHIRE_ESCROW=0xd905035f21C0edda5971803c2aeb3eBe62312b6b
`;

fs.writeFileSync(envPath, envContent);
console.log("📝 Saved to: " + envPath);

// 5. Next steps
console.log("\n📋 Next steps:");
console.log("   1. Fund your wallet with Base Sepolia ETH (free):");
console.log("      → https://www.alchemy.com/faucets/base-sepolia");
console.log("      → Paste: " + wallet.address);
console.log("");
console.log("   2. Search the marketplace:");
console.log("      node scripts/search.js \"token-swap\"");
console.log("");
console.log("   3. Hire an agent:");
console.log("      node scripts/hire.js 1 \"Swap 100 USDC to ETH\"");
console.log("");
console.log("✨ Done! Your agent is ready to hire other agents.");
