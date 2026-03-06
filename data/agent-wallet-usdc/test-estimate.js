// Test estimate and getSupportedChains
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
    console.log("\n--- getSupportedChains ---");
    const chains = await kit.getSupportedChains();
    console.log("Supported chains:", chains);
    
    console.log("\n--- estimate ---");
    const estimate = await kit.estimate({
      from: { adapter, chain: "Base_Sepolia" },
      to: { adapter, chain: "Ethereum_Sepolia" },
      amount: "1.00",
    });
    console.log("Estimate:", JSON.stringify(estimate, null, 2));
    
  } catch (err) {
    console.error("Error:", err.message);
  }
};

main();
