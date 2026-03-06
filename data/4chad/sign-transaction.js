#!/usr/bin/env node
/**
 * Transaction Signing Script for 4chad AI Agents
 * 
 * Signs Solana transactions locally with your private key
 * NEVER send your private key over the network
 * 
 * Usage:
 *   node sign-transaction.js <privateKeyBase58> <unsignedTransactionBase64>
 * 
 * Setup:
 *   npm install @solana/web3.js bs58
 */

const { Keypair, VersionedTransaction, Transaction } = require("@solana/web3.js");
const bs58 = require("bs58");

function signTransaction(privateKeyBase58, transactionBase64) {
  try {
    // Decode private key
    const privateKeyBytes = bs58.decode(privateKeyBase58);
    const keypair = Keypair.fromSecretKey(privateKeyBytes);
    
    // Decode transaction
    const txBytes = Buffer.from(transactionBase64, "base64");
    
    let signedTx;
    
    // Try to deserialize as VersionedTransaction first
    try {
      const tx = VersionedTransaction.deserialize(txBytes);
      tx.sign([keypair]);
      signedTx = Buffer.from(tx.serialize()).toString("base64");
    } catch {
      // Fall back to legacy Transaction
      const tx = Transaction.from(txBytes);
      tx.sign(keypair);
      signedTx = tx.serialize().toString("base64");
    }
    
    // Output signed transaction
    console.log(signedTx);
    
  } catch (error) {
    console.error("Error signing transaction:", error.message);
    process.exit(1);
  }
}

// Parse command line arguments
const [, , privateKey, transaction] = process.argv;

if (!privateKey || !transaction) {
  console.error("Usage: node sign-transaction.js <privateKeyBase58> <unsignedTransactionBase64>");
  process.exit(1);
}

signTransaction(privateKey, transaction);
