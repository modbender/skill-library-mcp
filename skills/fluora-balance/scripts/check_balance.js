#!/usr/bin/env node

const { ethers } = require("ethers");
const fs = require("fs");
const path = require("path");

// Base Mainnet RPC
const BASE_RPC = "https://mainnet.base.org";

// USDC contract address on Base Mainnet
const USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";

// Minimal ERC20 ABI
const ERC20_ABI = [
  "function balanceOf(address account) view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function symbol() view returns (string)"
];

async function getUsdcBalance(walletAddress) {
  try {
    // Create provider
    const provider = new ethers.JsonRpcProvider(BASE_RPC);

    // Create contract instance
    const usdcContract = new ethers.Contract(
      USDC_ADDRESS,
      ERC20_ABI,
      provider
    );

    // Fetch balance + decimals
    const [balance, decimals, symbol] = await Promise.all([
      usdcContract.balanceOf(walletAddress),
      usdcContract.decimals(),
      usdcContract.symbol()
    ]);

    // Format balance
    const formattedBalance = ethers.formatUnits(balance, decimals);

    return {
      wallet: walletAddress,
      balance: formattedBalance,
      symbol: symbol,
      raw: balance.toString()
    };
  } catch (error) {
    console.error("Error fetching USDC balance:", error.message);
    throw error;
  }
}

async function main() {
  try {
    // Read wallet address from ~/.fluora/wallets.json
    const walletsPath = path.join(process.env.HOME, ".fluora", "wallets.json");
    
    if (!fs.existsSync(walletsPath)) {
      console.error("Error: ~/.fluora/wallets.json not found");
      console.error("Make sure Fluora is set up correctly");
      process.exit(1);
    }

    const walletsData = JSON.parse(fs.readFileSync(walletsPath, "utf8"));
    
    // Get mainnet wallet address
    const mainnetWallet = walletsData.USDC_BASE_MAINNET?.address;
    
    if (!mainnetWallet) {
      console.error("Error: No USDC_BASE_MAINNET wallet address found in wallets.json");
      process.exit(1);
    }

    console.log("Checking USDC balance on Base Mainnet...\n");

    // Get balance
    const result = await getUsdcBalance(mainnetWallet);

    console.log(`Wallet: ${result.wallet}`);
    console.log(`Balance: ${result.balance} ${result.symbol}`);
    
    // Return as JSON for programmatic use
    if (process.argv.includes("--json")) {
      console.log("\nJSON Output:");
      console.log(JSON.stringify(result, null, 2));
    }

  } catch (error) {
    console.error("Failed to check balance:", error.message);
    process.exit(1);
  }
}

main();
