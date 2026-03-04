/**
 * NFT Minting Skill
 * Handles minting NFTs on Base network
 */
import { ethers } from 'ethers';
import * as fs from 'fs';
import * as dotenv from 'dotenv';
dotenv.config();

function getPrivateKey(): string {
  if (process.env.PRIVATE_KEY_FILE) {
    return fs.readFileSync(process.env.PRIVATE_KEY_FILE, 'utf8').trim();
  }
  return process.env.BASE_PRIVATE_KEY!;
}

// Minimal ERC721 ABI for minting
const NFT_ABI = [
  'function safeMint(address to, string memory uri) public returns (uint256)',
  'function tokenCounter() public view returns (uint256)',
  'event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)',
  'event ArtMinted(address indexed to, uint256 indexed tokenId, string uri)'
];

interface MintResult {
  tokenId: string;
  txHash: string;
  blockNumber: number;
  gasUsed: string;
}


async function retryWithBackoff<T>(
  fn: () => Promise<T>, 
  retries = 3, 
  delay = 1000, 
  factor = 2
): Promise<T> {
  try {
    return await fn();
  } catch (error: any) {
    if (retries <= 0) throw error;
    
    // Check for specific retryable errors (optional hardcoding common RPC errors)
    const isNetworkError = error.code === 'NETWORK_ERROR' || 
                           error.code === 'TIMEOUT' || 
                           error.message.includes('rate limit') ||
                           error.message.includes('503');
                           
    if (!isNetworkError && !error.message.includes('nonce')) {
       // If it's a logic error (e.g., revert), maybe don't retry? 
       // But gas spikes can look like reverts sometimes.
       // We'll retry anyway for robustness in this simple agent.
    }

    console.log(`[Mint] Error: ${error.message}. Retrying in ${delay}ms... (${retries} left)`);
    await new Promise(resolve => setTimeout(resolve, delay));
    return retryWithBackoff(fn, retries - 1, delay * factor, factor);
  }
}

export async function mintNFT(metadataUri: string): Promise<MintResult> {
  const provider = new ethers.JsonRpcProvider(process.env.BASE_RPC_URL);
  const wallet = new ethers.Wallet(getPrivateKey(), provider);

  const contract = new ethers.Contract(
    process.env.NFT_CONTRACT_ADDRESS!,
    NFT_ABI,
    wallet
  );

  console.log(`[Mint] Minting NFT with metadata: ipfs://${metadataUri}`);
  console.log(`[Mint] Wallet: ${wallet.address}`);

  // Estimate gas first (with retry)
  const gasEstimate = await retryWithBackoff(async () => {
    return await contract.safeMint.estimateGas(
      wallet.address,
      `ipfs://${metadataUri}`
    );
  });

  console.log(`[Mint] Estimated gas: ${gasEstimate.toString()}`);

  // Send transaction with 20% buffer (with retry)
  const tx = await retryWithBackoff(async () => {
    return await contract.safeMint(
      wallet.address,
      `ipfs://${metadataUri}`,
      { gasLimit: (gasEstimate * 120n) / 100n }
    );
  });

  console.log(`[Mint] Transaction sent: ${tx.hash}`);

  const receipt = await tx.wait();

  // Parse Transfer event to get tokenId
  const transferEvent = receipt.logs.find(
    (log: any) => log.topics[0] === ethers.id('Transfer(address,address,uint256)')
  );

  const tokenId = transferEvent
    ? ethers.toBigInt(transferEvent.topics[3]).toString()
    : 'unknown';

  console.log(`[Mint] Success! Token #${tokenId} minted in block ${receipt.blockNumber}`);

  return {
    tokenId,
    txHash: tx.hash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString()
  };
}

export async function getWalletBalance(): Promise<string> {
  const provider = new ethers.JsonRpcProvider(process.env.BASE_RPC_URL);
  const wallet = new ethers.Wallet(getPrivateKey(), provider);
  const balance = await provider.getBalance(wallet.address);
  return ethers.formatEther(balance);
}

export async function getWalletAddress(): Promise<string> {
  const wallet = new ethers.Wallet(getPrivateKey());
  return wallet.address;
}

export async function getTokenCount(): Promise<number> {
  const provider = new ethers.JsonRpcProvider(process.env.BASE_RPC_URL);
  const contract = new ethers.Contract(
    process.env.NFT_CONTRACT_ADDRESS!,
    NFT_ABI,
    provider
  );

  const count = await contract.tokenCounter();
  return Number(count);
}
