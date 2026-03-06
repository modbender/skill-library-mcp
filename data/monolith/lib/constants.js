// Chain configurations
export const CHAINS = {
  1: {
    name: 'Ethereum Mainnet',
    rpcUrl: 'https://ethereum-rpc.publicnode.com',
    bundlerUrl: 'https://public.pimlico.io/v2/1/rpc',
    explorer: 'https://etherscan.io',
  },
  8453: {
    name: 'Base',
    rpcUrl: 'https://mainnet.base.org',
    bundlerUrl: 'https://public.pimlico.io/v2/8453/rpc',
    explorer: 'https://basescan.org',
  },
};

// Known stablecoin addresses by (chainId, address)
export const STABLECOINS = {
  1: {
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': { symbol: 'USDC', decimals: 6 },
  },
  8453: {
    '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913': { symbol: 'USDC', decimals: 6 },
  },
};

// ERC-4337 v0.7 EntryPoint
export const ENTRY_POINT = '0x0000000071727De22E5E9d8BAf0edAc6f37da032';

// Uniswap V3 addresses
export const UNISWAP = {
  UNIVERSAL_ROUTER: '0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD',
  QUOTER_V2: {
    1: '0x61fFE014bA17989E743c5F6cB21bF9697530B21e',
    8453: '0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a',
  },
  WETH: {
    1: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    8453: '0x4200000000000000000000000000000000000006',
  },
  // Universal Router command bytes
  COMMAND_V3_SWAP_EXACT_IN: 0x00,
  COMMAND_WRAP_ETH: 0x0b,
  // Universal Router special addresses
  ADDRESS_THIS: '0x0000000000000000000000000000000000000002',
  MSG_SENDER: '0x0000000000000000000000000000000000000001',
};

// Uniswap V3 pool fee tiers
export const V3_FEES = {
  LOWEST: 100,   // 0.01%
  LOW: 500,      // 0.05% — typical for stablecoin pairs
  MEDIUM: 3000,  // 0.3% — typical for ETH/USDC
  HIGH: 10000,   // 1%
};

// QuoterV2 ABI (only the function we need)
export const QUOTER_V2_ABI = [
  {
    type: 'function',
    name: 'quoteExactInputSingle',
    inputs: [
      {
        name: 'params',
        type: 'tuple',
        components: [
          { name: 'tokenIn', type: 'address' },
          { name: 'tokenOut', type: 'address' },
          { name: 'amountIn', type: 'uint256' },
          { name: 'fee', type: 'uint24' },
          { name: 'sqrtPriceLimitX96', type: 'uint160' },
        ],
      },
    ],
    outputs: [
      { name: 'amountOut', type: 'uint256' },
      { name: 'sqrtPriceX96After', type: 'uint160' },
      { name: 'initializedTicksCrossed', type: 'uint32' },
      { name: 'gasEstimate', type: 'uint256' },
    ],
    stateMutability: 'nonpayable',
  },
];

// Daemon socket path
export const SOCKET_PATH =
  process.env.MONOLITH_SOCKET || `${process.env.HOME}/.monolith/daemon.sock`;

// Common ABIs for encoding
export const ERC20_TRANSFER_ABI = [
  {
    type: 'function',
    name: 'transfer',
    inputs: [
      { name: 'to', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [{ type: 'bool' }],
  },
];

export const ERC20_BALANCE_ABI = [
  {
    type: 'function',
    name: 'balanceOf',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ type: 'uint256' }],
  },
];

/**
 * Validate that chainId is one of the supported chains (1 or 8453).
 * @param {number} chainId
 * @throws {Error} if chainId is not supported
 */
export function validateChainId(chainId) {
  if (chainId !== 1 && chainId !== 8453) {
    throw new Error(
      `Unsupported chainId: ${chainId}. Only Ethereum Mainnet (1) and Base (8453) are supported.`
    );
  }
}
