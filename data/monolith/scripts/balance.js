import { createPublicClient, http, formatEther, formatUnits } from 'viem';
import { mainnet, base } from 'viem/chains';
import { CHAINS, STABLECOINS, ERC20_BALANCE_ABI } from '../lib/constants.js';
import { formatETH, formatUSDC, shortenAddress } from '../lib/format.js';

/**
 * Check wallet balances (read-only, no daemon needed).
 * Usage: node scripts/balance.js <address> [chainId]
 */
async function main() {
  const [, , address, chainIdStr] = process.argv;

  if (!address) {
    console.error('Usage: balance <address> [chainId]');
    process.exit(1);
  }

  const chainIds = chainIdStr ? [parseInt(chainIdStr, 10)] : [1, 8453];

  for (const chainId of chainIds) {
    const chainConfig = CHAINS[chainId];
    if (!chainConfig) {
      console.error(`Unknown chain: ${chainId}`);
      continue;
    }

    const chain = chainId === 1 ? mainnet : base;
    const client = createPublicClient({
      chain,
      transport: http(chainConfig.rpcUrl),
    });

    console.log(`\n--- ${chainConfig.name} (${chainId}) ---`);

    // ETH balance
    try {
      const balance = await client.getBalance({ address });
      console.log(`ETH: ${formatEther(balance)}`);
    } catch (err) {
      console.log(`ETH: Error fetching balance`);
    }

    // Stablecoin balances
    const stables = STABLECOINS[chainId] || {};
    for (const [tokenAddr, info] of Object.entries(stables)) {
      try {
        const balance = await client.readContract({
          address: tokenAddr,
          abi: ERC20_BALANCE_ABI,
          functionName: 'balanceOf',
          args: [address],
        });
        console.log(`${info.symbol}: ${formatUnits(balance, info.decimals)}`);
      } catch {
        console.log(`${info.symbol}: Error fetching balance`);
      }
    }
  }
}

main();
