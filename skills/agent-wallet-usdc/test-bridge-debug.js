// Debug Bridge Kit - check what's happening
import { BridgeKit } from "@circle-fin/bridge-kit";
import { createViemAdapterFromPrivateKey } from "@circle-fin/adapter-viem-v2";
import { ethers } from "ethers";
import dotenv from "dotenv";

dotenv.config();

const seedPhrase = process.env.WALLET_SEED_PHRASE;
const hdNode = ethers.HDNodeWallet.fromPhrase(seedPhrase.trim());
const privateKey = hdNode.privateKey;

console.log("Wallet:", hdNode.address);

const kit = new BridgeKit();

// Check supported chains first
console.log("\n--- Checking Bridge Kit config ---");

const adapter = createViemAdapterFromPrivateKey({
  privateKey: privateKey,
});

console.log("Adapter created");

// Try to get a quote first instead of full bridge
const main = async () => {
  try {
    // Check if there's a quote method
    console.log("Kit methods:", Object.keys(kit));
    console.log("Kit prototype:", Object.getOwnPropertyNames(Object.getPrototypeOf(kit)));
    
    console.log("\n--- Starting bridge with timeout ---");
    
    // Add manual timeout
    const bridgePromise = kit.bridge({
      from: { adapter, chain: "Base_Sepolia" },
      to: { adapter, chain: "Ethereum_Sepolia" },
      amount: "1.00",
    });
    
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error("Bridge timeout after 60s")), 60000)
    );
    
    const result = await Promise.race([bridgePromise, timeoutPromise]);
    console.log("Result:", JSON.stringify(result, null, 2));
  } catch (err) {
    console.error("Error:", err.message);
    console.error("Stack:", err.stack);
  }
};

main();
