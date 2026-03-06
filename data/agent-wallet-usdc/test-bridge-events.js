// Test bridge with event listeners
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

// Listen to events
kit.on("step", (step) => {
  console.log(`[STEP EVENT] ${step.name}: ${step.state}`);
  if (step.txHash) console.log(`  TX: ${step.txHash}`);
  if (step.error) console.log(`  Error: ${step.error}`);
});

kit.on("error", (err) => {
  console.log(`[ERROR EVENT] ${err.message}`);
});

const adapter = createViemAdapterFromPrivateKey({
  privateKey: privateKey,
});

const main = async () => {
  try {
    console.log("\n--- Starting bridge with events ---");
    
    const bridgePromise = kit.bridge({
      from: { adapter, chain: "Base_Sepolia" },
      to: { adapter, chain: "Ethereum_Sepolia" },
      amount: "1.00",
    });
    
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error("Bridge timeout after 90s")), 90000)
    );
    
    const result = await Promise.race([bridgePromise, timeoutPromise]);
    
    const { inspect } = await import("util");
    console.log("\nResult:", inspect(result, { depth: 5 }));
    
  } catch (err) {
    console.error("\nError:", err.message);
  }
};

main();
