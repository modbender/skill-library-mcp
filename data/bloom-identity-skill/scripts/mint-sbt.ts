#!/usr/bin/env ts-node
import 'dotenv/config';
import { mintIdentitySbt } from '../src/blockchain/identity-sbt';
import { walletStorage } from '../src/blockchain/wallet-storage';

async function main() {
  const userId = process.argv[2];
  if (!userId) {
    console.error('Usage: ts-node scripts/mint-sbt.ts <userId>');
    process.exit(1);
  }

  const contractAddress = process.env.SBT_CONTRACT_ADDRESS as `0x${string}` | undefined;
  if (!contractAddress) {
    console.error('Missing SBT_CONTRACT_ADDRESS');
    process.exit(1);
  }

  const wallet = await walletStorage.getUserWallet(userId);
  if (!wallet?.privateKey) {
    console.error('No local private key available for this user');
    process.exit(1);
  }

  const tokenUri = `data:application/json;base64,${Buffer.from(JSON.stringify({
    name: 'Bloom Identity (Demo)',
    description: 'Demo SBT mint for Bloom Identity',
    attributes: [{ trait_type: 'userId', value: userId }],
  })).toString('base64')}`;

  const txHash = await mintIdentitySbt({
    contractAddress,
    to: wallet.walletAddress as `0x${string}`,
    tokenUri,
    network: wallet.network as 'base-mainnet' | 'base-sepolia',
    privateKey: wallet.privateKey as `0x${string}`,
  });

  console.log('Minted:', txHash);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
