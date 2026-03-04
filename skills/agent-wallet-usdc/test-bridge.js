// Minimal Bridge Kit test - exactly like Circle's docs
import { BridgeKit } from "@circle-fin/bridge-kit";
import { createViemAdapterFromPrivateKey } from "@circle-fin/adapter-viem-v2";
import { inspect } from "util";
import { ethers } from "ethers";
import * as bip39 from "bip39";
import dotenv from "dotenv";

dotenv.config();

// Derive private key from seed phrase
const seedPhrase = process.env.WALLET_SEED_PHRASE;
if (!seedPhrase) {
  console.error("WALLET_SEED_PHRASE not set");
  process.exit(1);
}

const hdNode = ethers.HDNodeWallet.fromPhrase(seedPhrase.trim());
const privateKey = hdNode.privateKey;

console.log("Wallet address:", hdNode.address);
console.log("Private key prefix:", privateKey.slice(0, 10) + "...");

const kit = new BridgeKit();

const bridgeUSDC = async () => {
  try {
    // Single adapter for both chains (like Circle's example)
    const adapter = createViemAdapterFromPrivateKey({
      privateKey: privateKey,
    });

    console.log("---------------Starting Bridging---------------");
    console.log("From: Base_Sepolia");
    console.log("To: Ethereum_Sepolia");
    console.log("Amount: 1.00 USDC");

    const result = await kit.bridge({
      from: { adapter, chain: "Base_Sepolia" },
      to: { adapter, chain: "Ethereum_Sepolia" },
      amount: "1.00",
    });

    console.log("RESULT", inspect(result, false, null, true));
  } catch (err) {
    console.log("ERROR", inspect(err, false, null, true));
  }
};

bridgeUSDC();
