/**
 * EVM Chain Configurations
 * Includes chainId, native token, block explorers, and default public RPCs
 */

export const chains = {
  ethereum: {
    chainId: 1,
    name: "Ethereum",
    nativeToken: {
      symbol: "ETH",
      decimals: 18
    },
    explorer: {
      name: "Etherscan",
      url: "https://etherscan.io"
    },
    rpcs: [
      "https://ethereum.publicnode.com",
      "https://cloudflare-eth.com",
      "https://rpc.ankr.com/eth"
    ]
  },
  
  base: {
    chainId: 8453,
    name: "Base",
    nativeToken: {
      symbol: "ETH",
      decimals: 18
    },
    explorer: {
      name: "BaseScan",
      url: "https://basescan.org"
    },
    rpcs: [
      "https://mainnet.base.org",
      "https://base.publicnode.com",
      "https://base.llamarpc.com"
    ]
  },
  
  polygon: {
    chainId: 137,
    name: "Polygon",
    nativeToken: {
      symbol: "POL",
      decimals: 18
    },
    explorer: {
      name: "PolygonScan",
      url: "https://polygonscan.com"
    },
    rpcs: [
      "https://polygon.llamarpc.com",
      "https://polygon.publicnode.com",
      "https://rpc.ankr.com/polygon"
    ]
  },
  
  arbitrum: {
    chainId: 42161,
    name: "Arbitrum One",
    nativeToken: {
      symbol: "ETH",
      decimals: 18
    },
    explorer: {
      name: "Arbiscan",
      url: "https://arbiscan.io"
    },
    rpcs: [
      "https://arbitrum.publicnode.com",
      "https://arbitrum.llamarpc.com",
      "https://rpc.ankr.com/arbitrum"
    ]
  },
  
  optimism: {
    chainId: 10,
    name: "Optimism",
    nativeToken: {
      symbol: "ETH",
      decimals: 18
    },
    explorer: {
      name: "Optimism Etherscan",
      url: "https://optimistic.etherscan.io"
    },
    rpcs: [
      "https://optimism.publicnode.com",
      "https://optimism.llamarpc.com",
      "https://rpc.ankr.com/optimism"
    ]
  },
  
  megaeth: {
    chainId: 4326,
    name: "MegaETH",
    nativeToken: {
      symbol: "ETH",
      decimals: 18
    },
    explorer: {
      name: "Etherscan",
      url: "https://mega.etherscan.io"
    },
    rpcs: [
      "https://mainnet.megaeth.com/rpc",
      "https://rpc-megaeth-mainnet.globalstake.io"
    ],
    // MegaETH supports eth_sendRawTransactionSync (EIP-7966) — returns tx receipt directly in response (<10ms)
    // See: https://docs.megaeth.com/realtime-api
    // EIP-7966: https://ethereum-magicians.org/t/eip-7966-eth-sendrawtransactionsync-method/24640
    syncRpc: "eth_sendRawTransactionSync"
  }
};

/**
 * Get chain config by name
 * @param {string} chainName - Chain name (e.g., "base", "ethereum")
 * @returns {Object} Chain configuration
 */
export function getChain(chainName) {
  const chain = chains[chainName.toLowerCase()];
  if (!chain) {
    throw new Error(`Unsupported chain: ${chainName}. Supported chains: ${Object.keys(chains).join(', ')}`);
  }
  return chain;
}

/**
 * Get all supported chain names
 * @returns {string[]} Array of chain names
 */
export function getSupportedChains() {
  return Object.keys(chains);
}

/**
 * Create explorer URL for transaction
 * @param {string} chainName - Chain name
 * @param {string} txHash - Transaction hash
 * @returns {string} Explorer URL
 */
export function getExplorerTxUrl(chainName, txHash) {
  const chain = getChain(chainName);
  return `${chain.explorer.url}/tx/${txHash}`;
}

/**
 * Create explorer URL for address
 * @param {string} chainName - Chain name
 * @param {string} address - Wallet address
 * @returns {string} Explorer URL
 */
export function getExplorerAddressUrl(chainName, address) {
  const chain = getChain(chainName);
  return `${chain.explorer.url}/address/${address}`;
}