// Test estimate without JSON serialization issue
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

const adapter = createViemAdapterFromPrivateKey({
  privateKey: privateKey,
});

const main = async () => {
  try {
    console.log("\n--- estimate ---");
    const estimate = await kit.estimate({
      from: { adapter, chain: "Base_Sepolia" },
      to: { adapter, chain: "Ethereum_Sepolia" },
      amount: "1.00",
    });
    
    // Log each field individually to avoid BigInt issues
    console.log("Estimate received:");
    console.log("  amount:", estimate.amount?.toString());
    console.log("  fee:", estimate.fee?.toString());
    console.log("  provider:", estimate.provider);
    console.log("  steps:", estimate.steps?.length);
    console.log("Keys:", Object.keys(estimate));
    
    // Log the entire estimate using util.inspect
    const { inspect } = await import("util");
    console.log("\nFull estimate:", inspect(estimate, { depth: 5 }));
    
  } catch (err) {
    console.error("Error:", err.message);
    console.error("Stack:", err.stack);
  }
};

main();
