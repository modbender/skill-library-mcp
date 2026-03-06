const { Connection, Keypair, Transaction, SystemProgram, PublicKey } = require('@solana/web3.js');
const fs = require('fs');

// X1 Mainnet RPC
const RPC_URL = process.env.X1_RPC_URL || 'https://rpc.mainnet.x1.xyz';

// Known memo program IDs to try
const MEMO_PROGRAM_IDS = [
  'MemoSq4gqABAXKb96qnHnM4C8A6ZfjZJdP8KDnE6b2T', // Solana Memo v2
  'Memo1UhkJRfHyvLMc3yP1x4sGrHw2ZPRZ7P36zZY7Vn', // Solana Memo v1
];

async function findWorkingMemoProgram(connection) {
  for (const programId of MEMO_PROGRAM_IDS) {
    try {
      const pubkey = new PublicKey(programId);
      const accountInfo = await connection.getAccountInfo(pubkey);
      if (accountInfo && accountInfo.executable) {
        console.log('Found working memo program:', programId);
        return pubkey;
      }
    } catch {
      // Continue to next
    }
  }
  return null;
}

async function anchorCID(cid, walletPath) {
  try {
    // Load wallet
    const walletData = JSON.parse(fs.readFileSync(walletPath, 'utf8'));
    const secretKey = Uint8Array.from(walletData.secretKey);
    const keypair = Keypair.fromSecretKey(secretKey);
    
    console.log('Using wallet:', keypair.publicKey.toBase58());
    
    // Connect to X1 mainnet
    const connection = new Connection(RPC_URL, 'confirmed');
    console.log('Connected to', RPC_URL);
    
    // Check balance
    const balance = await connection.getBalance(keypair.publicKey);
    console.log('Wallet balance:', (balance / 1e9).toFixed(4), 'XN');
    
    if (balance < 0.0001 * 1e9) {
      throw new Error('Insufficient balance. Need at least 0.0001 XN for transaction fee.');
    }
    
    // Try to find a working memo program
    const memoProgram = await findWorkingMemoProgram(connection);
    
    const transaction = new Transaction();
    let method = 'transfer-only';
    
    if (memoProgram) {
      // Use memo program if available
      console.log('Using memo program for CID anchoring');
      const { TransactionInstruction } = require('@solana/web3.js');
      const memoInstruction = new TransactionInstruction({
        programId: memoProgram,
        keys: [],
        data: Buffer.from(`IPFS:${cid}`, 'utf8'),
      });
      transaction.add(memoInstruction);
      method = 'memo-program';
    }
    
    // Add a minimal self-transfer (0 XN) to make transaction valid
    // This is required even with memo program
    const transferInstruction = SystemProgram.transfer({
      fromPubkey: keypair.publicKey,
      toPubkey: keypair.publicKey,
      lamports: 0,
    });
    transaction.add(transferInstruction);
    
    console.log('Transaction created with CID:', cid);
    console.log('Anchoring method:', method);
    
    // Send transaction
    console.log('Submitting transaction to X1 mainnet...');
    const signature = await connection.sendTransaction(transaction, [keypair], {
      skipPreflight: false,
      preflightCommitment: 'confirmed',
    });
    
    // Wait for confirmation
    console.log('Waiting for confirmation...');
    await connection.confirmTransaction({ signature }, 'confirmed');
    
    console.log('✓ Transaction confirmed:', signature);
    
    return {
      signature,
      explorerUrl: `https://explorer.mainnet.x1.xyz/tx/${signature}`,
      cid,
      method,
    };
  } catch (err) {
    console.error('Detailed error:', err.message);
    if (err.logs) {
      console.error('Transaction logs:', err.logs);
    }
    throw err;
  }
}

module.exports = { anchorCID };
