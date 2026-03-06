import { ethers } from 'ethers';

// ─── Types ──────────────────────────────────────────────────────────

export type ChainType = 'ETH' | 'BSC' | 'POLYGON' | 'ARBITRUM' | 'OPTIMISM';

interface ChainConfig {
  name: string;
  rpcUrl: string;
  nativeSymbol: string;
  nativeName: string;
  explorerUrl: string;
}

export interface WalletAsset {
  symbol: string;
  name: string;
  quantity: number;
  type: 'CRYPTO';
  currency: 'USD';
  chain: string;
}

// ─── Chain Configs ──────────────────────────────────────────────────

export const CHAIN_CONFIGS: Record<ChainType, ChainConfig> = {
  ETH: {
    name: 'Ethereum',
    rpcUrl: 'https://eth.llamarpc.com',
    nativeSymbol: 'ETH',
    nativeName: 'Ethereum',
    explorerUrl: 'https://etherscan.io',
  },
  BSC: {
    name: 'BNB Smart Chain',
    rpcUrl: 'https://bsc-dataseed.binance.org',
    nativeSymbol: 'BNB',
    nativeName: 'BNB',
    explorerUrl: 'https://bscscan.com',
  },
  POLYGON: {
    name: 'Polygon',
    rpcUrl: 'https://polygon-rpc.com',
    nativeSymbol: 'MATIC',
    nativeName: 'Polygon',
    explorerUrl: 'https://polygonscan.com',
  },
  ARBITRUM: {
    name: 'Arbitrum',
    rpcUrl: 'https://arb1.arbitrum.io/rpc',
    nativeSymbol: 'ETH',
    nativeName: 'Ethereum',
    explorerUrl: 'https://arbiscan.io',
  },
  OPTIMISM: {
    name: 'Optimism',
    rpcUrl: 'https://mainnet.optimism.io',
    nativeSymbol: 'ETH',
    nativeName: 'Ethereum',
    explorerUrl: 'https://optimistic.etherscan.io',
  },
};

const COMMON_TOKENS: Record<ChainType, Array<{ address: string; symbol: string; name: string; decimals: number }>> = {
  ETH: [
    { address: '0xdAC17F958D2ee523a2206206994597C13D831ec7', symbol: 'USDT', name: 'Tether USD', decimals: 6 },
    { address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', symbol: 'USDC', name: 'USD Coin', decimals: 6 },
    { address: '0x6B175474E89094C44Da98b954EedeAC495271d0F', symbol: 'DAI', name: 'Dai Stablecoin', decimals: 18 },
    { address: '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', symbol: 'WBTC', name: 'Wrapped BTC', decimals: 8 },
    { address: '0x514910771AF9Ca656af840dff83E8264EcF986CA', symbol: 'LINK', name: 'ChainLink Token', decimals: 18 },
  ],
  BSC: [
    { address: '0x55d398326f99059fF775485246999027B3197955', symbol: 'USDT', name: 'Tether USD', decimals: 18 },
    { address: '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d', symbol: 'USDC', name: 'USD Coin', decimals: 18 },
    { address: '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56', symbol: 'BUSD', name: 'Binance USD', decimals: 18 },
    { address: '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c', symbol: 'BTCB', name: 'Binance BTC', decimals: 18 },
  ],
  POLYGON: [
    { address: '0xc2132D05D31c914a87C6611C10748AEb04B58e8F', symbol: 'USDT', name: 'Tether USD', decimals: 6 },
    { address: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174', symbol: 'USDC', name: 'USD Coin', decimals: 6 },
    { address: '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063', symbol: 'DAI', name: 'Dai Stablecoin', decimals: 18 },
  ],
  ARBITRUM: [
    { address: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', symbol: 'USDT', name: 'Tether USD', decimals: 6 },
    { address: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', symbol: 'USDC', name: 'USD Coin', decimals: 6 },
  ],
  OPTIMISM: [
    { address: '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58', symbol: 'USDT', name: 'Tether USD', decimals: 6 },
    { address: '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85', symbol: 'USDC', name: 'USD Coin', decimals: 6 },
  ],
};

const ERC20_ABI = [
  'function balanceOf(address owner) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
];

// ─── Fetch Functions ────────────────────────────────────────────────

export async function fetchWalletBalances(address: string, chainType: ChainType): Promise<WalletAsset[]> {
  const config = CHAIN_CONFIGS[chainType];
  if (!config) throw new Error(`Unsupported chain type: ${chainType}`);
  if (!ethers.isAddress(address)) throw new Error('Invalid wallet address');

  const provider = new ethers.JsonRpcProvider(config.rpcUrl);
  const assets: WalletAsset[] = [];

  try {
    // Native token balance
    const nativeBalance = await provider.getBalance(address);
    const nativeAmount = parseFloat(ethers.formatEther(nativeBalance));

    if (nativeAmount > 0.0001) {
      assets.push({
        symbol: config.nativeSymbol,
        name: config.nativeName,
        quantity: nativeAmount,
        type: 'CRYPTO',
        currency: 'USD',
        chain: chainType,
      });
    }

    // ERC20 balances
    const tokens = COMMON_TOKENS[chainType] || [];
    const tokenPromises = tokens.map(async (token) => {
      try {
        const contract = new ethers.Contract(token.address, ERC20_ABI, provider);
        const balance = await contract.balanceOf(address);
        const amount = parseFloat(ethers.formatUnits(balance, token.decimals));

        if (amount > 0.01) {
          return {
            symbol: token.symbol,
            name: token.name,
            quantity: amount,
            type: 'CRYPTO' as const,
            currency: 'USD' as const,
            chain: chainType,
          };
        }
      } catch { /* skip failed token */ }
      return null;
    });

    const results = await Promise.all(tokenPromises);
    for (const r of results) {
      if (r) assets.push(r);
    }
  } catch (error) {
    throw new Error(`Failed to fetch wallet balances on ${chainType}: ${error}`);
  }

  return assets;
}

export async function fetchAllChainBalances(address: string): Promise<WalletAsset[]> {
  const chains = Object.keys(CHAIN_CONFIGS) as ChainType[];
  const results = await Promise.allSettled(
    chains.map(chain => fetchWalletBalances(address, chain)),
  );

  const allAssets: WalletAsset[] = [];
  for (const result of results) {
    if (result.status === 'fulfilled') {
      allAssets.push(...result.value);
    }
  }
  return allAssets;
}

export function isValidEvmAddress(address: string): boolean {
  return ethers.isAddress(address);
}

// ─── CLI Entry Point ────────────────────────────────────────────────

const command = process.argv[2];

if (command) {
  try {
    let result: unknown;

    switch (command) {
      case 'sync': {
        const address = process.argv[3];
        const chain = process.argv[4] as ChainType | undefined;
        if (!address) throw new Error('Usage: sync <address> [chain]');

        if (chain) {
          result = await fetchWalletBalances(address, chain);
        } else {
          result = await fetchAllChainBalances(address);
        }
        break;
      }
      case 'validate': {
        const address = process.argv[3];
        if (!address) throw new Error('Usage: validate <address>');
        result = { valid: isValidEvmAddress(address) };
        break;
      }
      default:
        result = { error: `Unknown command: ${command}` };
    }

    console.log(JSON.stringify(result));
  } catch (err: any) {
    console.log(JSON.stringify({ error: err.message }));
    process.exit(1);
  }
}
