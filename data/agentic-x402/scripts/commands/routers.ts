#!/usr/bin/env npx tsx
// List routers where the agent's wallet is a beneficiary

import { getClient, getWalletAddress } from '../core/client.js';
import { parseArgs, formatCrypto, formatUsd, truncateAddress, formatError } from '../core/utils.js';
import { getConfig, getUsdcAddress } from '../core/config.js';
import { formatUnits } from 'viem';

const ERC20_BALANCE_ABI = [{
  name: 'balanceOf',
  type: 'function',
  stateMutability: 'view',
  inputs: [{ name: 'account', type: 'address' }],
  outputs: [{ name: '', type: 'uint256' }],
}] as const;

interface BeneficiaryLink {
  id: string;
  router_address: string;
  metadata: {
    name: string;
    description?: string;
    chainId?: number;
    chainName?: string;
  };
  amount: string;
  chain_id: number;
  token_address: string;
  beneficiary_percentage: number;
  created_at: string;
}

async function main() {
  const { flags } = parseArgs(process.argv.slice(2));

  if (flags.help || flags.h) {
    console.log(`
x402 routers - List routers where your wallet is a beneficiary

Usage: x402 routers [options]

Options:
  --with-balance   Fetch on-chain USDC balance for each router
  --json           Output as JSON
  -h, --help       Show this help

Shows:
  - Router address and link name
  - Your beneficiary share percentage
  - On-chain USDC balance (with --with-balance)
  - Estimated withdrawal amount based on your share
`);
    process.exit(0);
  }

  const config = getConfig();
  const jsonOutput = flags.json === true;
  const withBalance = flags['with-balance'] === true;

  try {
    const address = getWalletAddress();
    const apiUrl = `${config.x402LinksApiUrl}/api/links/beneficiary/${address}`;

    const response = await fetch(apiUrl);
    const data = await response.json();

    if (!response.ok || !data.success) {
      if (jsonOutput) {
        console.log(JSON.stringify({ success: false, error: data.error || 'Failed to fetch routers' }));
      } else {
        console.error('Error:', data.error || 'Failed to fetch routers');
      }
      process.exit(1);
    }

    const links: BeneficiaryLink[] = data.links;

    if (links.length === 0) {
      if (jsonOutput) {
        console.log(JSON.stringify({ success: true, routers: [] }));
      } else {
        console.log('No routers found where your wallet is a beneficiary.');
      }
      return;
    }

    // Optionally fetch on-chain balances
    let balances: Map<string, { raw: bigint; formatted: string }> | null = null;

    if (withBalance) {
      const client = getClient();
      const usdcAddress = getUsdcAddress(config.chainId);
      balances = new Map();

      const balancePromises = links.map(async (link) => {
        const routerAddr = link.router_address as `0x${string}`;
        try {
          const balance = await client.publicClient.readContract({
            address: usdcAddress,
            abi: ERC20_BALANCE_ABI,
            functionName: 'balanceOf',
            args: [routerAddr],
          });
          return { router: routerAddr, raw: balance, formatted: formatUnits(balance, 6) };
        } catch {
          return { router: routerAddr, raw: 0n, formatted: '0' };
        }
      });

      const results = await Promise.all(balancePromises);
      for (const r of results) {
        balances.set(r.router.toLowerCase(), { raw: r.raw, formatted: r.formatted });
      }
    }

    if (jsonOutput) {
      const routers = links.map((link) => {
        const bal = balances?.get(link.router_address.toLowerCase());
        const share = link.beneficiary_percentage / 100;
        return {
          routerAddress: link.router_address,
          name: link.metadata?.name || 'Unnamed',
          chainId: link.chain_id,
          sharePercent: link.beneficiary_percentage,
          ...(bal ? {
            balance: bal.formatted,
            balanceRaw: bal.raw.toString(),
            estimatedWithdrawal: (parseFloat(bal.formatted) * share).toFixed(6),
          } : {}),
          createdAt: link.created_at,
        };
      });
      console.log(JSON.stringify({ success: true, address, routers }));
      return;
    }

    // Human-readable output
    console.log('Your Payment Routers');
    console.log('====================');
    console.log('');
    console.log(`Wallet: ${address}`);
    console.log(`Found: ${links.length} router(s)`);
    console.log('');

    for (const link of links) {
      const name = link.metadata?.name || 'Unnamed';
      const share = link.beneficiary_percentage;

      console.log(`  ${name}`);
      console.log(`    Router:  ${link.router_address}`);
      console.log(`    Share:   ${share}%`);

      if (balances) {
        const bal = balances.get(link.router_address.toLowerCase());
        if (bal) {
          const balNum = parseFloat(bal.formatted);
          const est = balNum * (share / 100);
          console.log(`    Balance: ${formatCrypto(bal.formatted, 'USDC', 2)}`);
          console.log(`    Est. withdrawal: ${formatCrypto(est.toFixed(2), 'USDC', 2)}`);
        }
      }
      console.log('');
    }

    if (!withBalance) {
      console.log('Tip: Use --with-balance to see on-chain USDC balances');
    }
    console.log('Use "x402 distribute <router-address>" to withdraw funds');

  } catch (error) {
    if (jsonOutput) {
      console.log(JSON.stringify({ success: false, error: formatError(error) }));
    } else {
      console.error('Error:', formatError(error));
    }
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
