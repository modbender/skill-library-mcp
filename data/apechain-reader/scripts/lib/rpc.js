// Shared RPC + chain utilities for ApeChain reader scripts
const crypto = require('crypto');

const CHAINS = {
  apechain: { id: 33139, rpc: "https://apechain.calderachain.xyz/http", name: "ApeChain", symbol: "APE", explorer: "https://apescan.io", coingeckoId: "apecoin" },
  ethereum: { id: 1, rpc: "https://eth.llamarpc.com", name: "Ethereum", symbol: "ETH", explorer: "https://etherscan.io", coingeckoId: "ethereum" },
  base: { id: 8453, rpc: "https://base.llamarpc.com", name: "Base", symbol: "ETH", explorer: "https://basescan.org", coingeckoId: "ethereum" },
  arbitrum: { id: 42161, rpc: "https://arb1.arbitrum.io/rpc", name: "Arbitrum", symbol: "ETH", explorer: "https://arbiscan.io", coingeckoId: "ethereum" },
  polygon: { id: 137, rpc: "https://polygon.llamarpc.com", name: "Polygon", symbol: "MATIC", explorer: "https://polygonscan.com", coingeckoId: "matic-network" },
  optimism: { id: 10, rpc: "https://optimism.llamarpc.com", name: "Optimism", symbol: "ETH", explorer: "https://optimistic.etherscan.io", coingeckoId: "ethereum" },
  avalanche: { id: 43114, rpc: "https://avalanche.drpc.org", name: "Avalanche", symbol: "AVAX", explorer: "https://snowscan.xyz", coingeckoId: "avalanche-2" },
  bsc: { id: 56, rpc: "https://bsc.llamarpc.com", name: "BNB Chain", symbol: "BNB", explorer: "https://bscscan.com", coingeckoId: "binancecoin" },
};

// ENS registry contract on Ethereum mainnet
const ENS_REGISTRY = "0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e";

// ERC-721 Transfer event topic
const TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";
// ERC-1155 TransferSingle
const TRANSFER_SINGLE_TOPIC = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62";

function getChain(name) {
  const chain = CHAINS[name?.toLowerCase()] || CHAINS.apechain;
  return chain;
}

async function rpcCall(rpcUrl, method, params, maxRetries = 3, timeoutMs = 10000) {
  const delays = [500, 1000, 2000]; // Exponential backoff: 500ms, 1s, 2s
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
      
      const res = await fetch(rpcUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const json = await res.json();
      if (json.error) throw new Error(json.error.message);
      return json.result;
      
    } catch (error) {
      // Clear timeout on any error
      clearTimeout && clearTimeout();
      
      const isLastAttempt = attempt === maxRetries;
      const isAbortError = error.name === 'AbortError';
      const shouldRetry = !isLastAttempt && (isAbortError || error.message.includes('fetch'));
      
      if (shouldRetry) {
        const delay = delays[attempt] || 2000;
        console.error(`RPC call failed (attempt ${attempt + 1}/${maxRetries + 1}): ${error.message}. Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      
      // Final attempt failed or error not retryable
      if (isAbortError) {
        throw new Error(`RPC request timed out after ${timeoutMs}ms`);
      }
      throw error;
    }
  }
}

function padAddress(addr) {
  return "0x" + addr.toLowerCase().replace("0x", "").padStart(64, "0");
}

function unpadAddress(hex) {
  if (!hex || hex.length < 66) return null;
  return "0x" + hex.slice(26).toLowerCase();
}

function hexToNumber(hex) {
  if (!hex) return 0;
  return Number(BigInt(hex));
}

function validateAddress(addr) {
  if (!addr) {
    throw new Error("Address is required");
  }
  if (!/^0x[a-fA-F0-9]{40}$/i.test(addr)) {
    throw new Error("Invalid address format. Address must be 0x followed by 40 hexadecimal characters");
  }
  return addr.toLowerCase();
}

// ENS namehash implementation
function namehash(name) {
  if (!name) return '0x' + '0'.repeat(64);
  
  const labels = name.split('.');
  let hash = '0x' + '0'.repeat(64);
  
  for (let i = labels.length - 1; i >= 0; i--) {
    const labelHash = crypto.createHash('keccak256').update(labels[i]).digest('hex');
    const combined = hash.slice(2) + labelHash;
    hash = '0x' + crypto.createHash('keccak256').update(Buffer.from(combined, 'hex')).digest('hex');
  }
  
  return hash;
}

// Resolve ENS name to address using Ethereum mainnet
async function resolveENS(name) {
  if (!name.endsWith('.eth')) {
    throw new Error(`Invalid ENS name: ${name}. ENS names must end with .eth`);
  }
  
  const ethereum = CHAINS.ethereum;
  const nameHash = namehash(name);
  
  try {
    // Call resolver(namehash) on ENS registry
    const resolverData = '0x0178b8bf' + nameHash.slice(2); // resolver(bytes32)
    const resolverResult = await rpcCall(ethereum.rpc, 'eth_call', [{
      to: ENS_REGISTRY,
      data: resolverData
    }, 'latest']);
    
    if (!resolverResult || resolverResult === '0x' + '0'.repeat(64)) {
      throw new Error(`No resolver found for ENS name: ${name}`);
    }
    
    const resolverAddress = '0x' + resolverResult.slice(26); // Extract last 20 bytes
    
    // Call addr(namehash) on the resolver
    const addrData = '0x3b3b57de' + nameHash.slice(2); // addr(bytes32)
    const addrResult = await rpcCall(ethereum.rpc, 'eth_call', [{
      to: resolverAddress,
      data: addrData
    }, 'latest']);
    
    if (!addrResult || addrResult === '0x' + '0'.repeat(64)) {
      throw new Error(`No address found for ENS name: ${name}`);
    }
    
    return '0x' + addrResult.slice(26); // Extract last 20 bytes
  } catch (error) {
    throw new Error(`Could not resolve ENS name: ${name}. ${error.message}`);
  }
}

// Collection name cache for in-memory caching during script run
const collectionNameCache = new Map();

// Price cache for CoinGecko API results
let priceCache = null;
let priceCacheTime = 0;
const PRICE_CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Resolve collection name using Alchemy API or RPC fallback
async function resolveCollectionName(contractAddress, chainName = 'apechain') {
  const cacheKey = `${chainName}:${contractAddress.toLowerCase()}`;
  if (collectionNameCache.has(cacheKey)) {
    return collectionNameCache.get(cacheKey);
  }
  
  let name = null;
  
  // Try Alchemy API first
  const alchemyKey = process.env.ALCHEMY_API_KEY;
  if (alchemyKey && chainName === 'apechain') {
    try {
      const alchemyUrl = `https://apechain-mainnet.g.alchemy.com/nft/v3/${alchemyKey}/getContractMetadata?contractAddress=${contractAddress}`;
      const response = await fetch(alchemyUrl);
      if (response.ok) {
        const data = await response.json();
        if (data.name) {
          name = data.name;
        }
      }
    } catch (error) {
      // Ignore Alchemy errors, fall back to RPC
    }
  }
  
  // Try RPC fallback if Alchemy failed
  if (!name) {
    try {
      const chain = getChain(chainName);
      const nameData = '0x06fdde03'; // name() function selector
      const result = await rpcCall(chain.rpc, 'eth_call', [{
        to: contractAddress,
        data: nameData
      }, 'latest']);
      
      if (result && result !== '0x') {
        // Decode string from ABI-encoded result
        const hex = result.slice(2);
        if (hex.length >= 128) {
          const lengthHex = hex.slice(64, 128);
          const length = parseInt(lengthHex, 16);
          if (length > 0 && length < 1000) {
            const nameHex = hex.slice(128, 128 + length * 2);
            name = Buffer.from(nameHex, 'hex').toString('utf8');
          }
        }
      }
    } catch (error) {
      // Ignore RPC errors
    }
  }
  
  // Fallback to short address format
  if (!name) {
    name = contractAddress.slice(0, 6) + '...' + contractAddress.slice(-4);
  }
  
  collectionNameCache.set(cacheKey, name);
  return name;
}

// Fetch token prices from CoinGecko with caching
async function fetchTokenPrices() {
  const now = Date.now();
  
  // Return cached prices if still fresh
  if (priceCache && (now - priceCacheTime) < PRICE_CACHE_DURATION) {
    return priceCache;
  }
  
  try {
    const coingeckoUrl = 'https://api.coingecko.com/api/v3/simple/price?ids=apecoin,ethereum,matic-network,avalanche-2,binancecoin&vs_currencies=usd';
    const response = await fetch(coingeckoUrl, {
      headers: { 'User-Agent': 'WalletLens/1.0' }
    });
    
    if (response.ok) {
      const data = await response.json();
      priceCache = data;
      priceCacheTime = now;
      return data;
    }
  } catch (error) {
    // Gracefully degrade - return null if CoinGecko fails
  }
  
  return null;
}

// Get USD price for a chain's native token
async function getTokenPrice(chainName) {
  const chain = getChain(chainName);
  const prices = await fetchTokenPrices();
  
  if (!prices || !chain.coingeckoId) {
    return null;
  }
  
  const tokenData = prices[chain.coingeckoId];
  return tokenData ? tokenData.usd : null;
}

function validateChain(chainName) {
  if (!chainName) {
    return "apechain"; // default
  }
  const normalizedName = chainName.toLowerCase();
  if (!CHAINS[normalizedName]) {
    const supportedChains = Object.keys(CHAINS).join(", ");
    throw new Error(`Unsupported chain "${chainName}". Supported chains: ${supportedChains}`);
  }
  return normalizedName;
}

async function parseArgs(argv) {
  const args = argv.slice(2);
  let rawAddress = args.find(a => a && (a.startsWith("0x") || a.endsWith(".eth")));
  const chainIdx = args.indexOf("--chain");
  const rawChainName = chainIdx >= 0 ? args[chainIdx + 1] : "apechain";
  const limitIdx = args.indexOf("--limit");
  const limit = limitIdx >= 0 ? parseInt(args[limitIdx + 1]) || 20 : 20;
  
  // Parse output format flags
  const hasJsonFlag = args.includes("--json");
  const hasPrettyFlag = args.includes("--pretty");
  const outputFormat = hasPrettyFlag ? "pretty" : "json"; // Default to JSON, pretty only if explicitly requested
  
  // Handle ENS resolution (temporarily disabled due to keccak256 dependency)
  if (rawAddress && rawAddress.endsWith(".eth")) {
    throw new Error("ENS resolution temporarily unavailable. Please use wallet address instead.");
    // try {
    //   rawAddress = await resolveENS(rawAddress);
    // } catch (error) {
    //   throw error; // Let the error bubble up with clear message
    // }
  }
  
  // Validate inputs
  const address = validateAddress(rawAddress);
  const chainName = validateChain(rawChainName);
  
  return { address, chainName, limit, outputFormat, args };
}

function formatOutput(data, format) {
  if (format === "pretty") {
    return formatPretty(data);
  }
  return JSON.stringify(data, null, 2);
}

function formatPretty(data) {
  if (data.error) {
    return `❌ Error: ${data.error}`;
  }
  
  // Handle different script types
  if (data.isContract !== undefined) {
    // wallet-lookup or contract-info
    return formatWalletOrContract(data);
  } else if (data.transactions) {
    // tx-history
    return formatTransactionHistory(data);
  } else if (data.holdings) {
    // nft-holdings
    return formatNFTHoldings(data);
  } else if (data.botScore !== undefined) {
    // bot-detect
    return formatBotDetection(data);
  }
  
  // Fallback to JSON for unknown formats
  return JSON.stringify(data, null, 2);
}

function formatWalletOrContract(data) {
  const lines = [];
  
  // Add summary at the top for pretty mode
  if (data.summary) {
    lines.push(data.summary);
    lines.push('');
  }
  
  lines.push(`🔍 ${data.isContract ? 'Contract' : 'Wallet'}: ${data.address}`);
  lines.push(`⛓️  Chain: ${data.chain} (${data.chainId})`);
  
  if (data.balance) {
    const symbol = Object.keys(data.balance)[0];
    const amount = data.balance[symbol];
    if (data.balanceUSD) {
      lines.push(`💰 Balance: ${amount} ${symbol} (~$${data.balanceUSD.toFixed(2)})`);
    } else {
      lines.push(`💰 Balance: ${amount} ${symbol}`);
    }
  }
  
  if (data.transactionCount !== undefined) {
    lines.push(`📊 Transactions: ${data.transactionCount.toLocaleString()}`);
  }
  
  if (data.type && data.type !== 'EOA (wallet)') {
    lines.push(`📋 Type: ${data.type}`);
    if (data.name) lines.push(`🏷️  Name: ${data.name}`);
    if (data.symbol) lines.push(`🔤 Symbol: ${data.symbol}`);
    if (data.totalSupply) lines.push(`📈 Total Supply: ${data.totalSupply.toLocaleString()}`);
  }
  
  if (data.nftActivity) {
    lines.push(`🎨 NFT Activity: ${data.nftActivity.received} received, ${data.nftActivity.sent} sent`);
    lines.push(`📦 Collections: ${data.nftCollectionsHeld}`);
    
    // Show collection names if available
    if (data.topHoldings && data.topHoldings.length > 0) {
      lines.push(`🏆 Top Collections:`);
      for (const holding of data.topHoldings.slice(0, 3)) {
        const name = holding.name || (holding.contract.slice(0, 6) + '...' + holding.contract.slice(-4));
        lines.push(`   ${name}: ${holding.count} NFT${holding.count !== 1 ? 's' : ''}`);
      }
    }
  }
  
  if (data.explorer) {
    lines.push(`🔗 Explorer: ${data.explorer}`);
  }
  
  return lines.join('\n');
}

function formatTransactionHistory(data) {
  const lines = [];
  lines.push(`📜 Transaction History: ${data.address}`);
  lines.push(`⛓️  Chain: ${data.chain}`);
  lines.push(`📊 Found: ${data.count} recent transactions`);
  lines.push('');
  
  for (const tx of data.transactions.slice(0, 10)) {
    const direction = tx.direction === 'IN' ? '📥' : '📤';
    const type = tx.type === 'NFT' ? '🎨' : '🪙';
    const amount = tx.type === 'NFT' ? `Token #${tx.tokenId}` : `${tx.value} tokens`;
    const time = tx.timestamp ? new Date(tx.timestamp).toLocaleDateString() : `Block ${tx.block}`;
    lines.push(`${direction} ${type} ${amount} - ${time}`);
    lines.push(`   Contract: ${tx.contract}`);
    lines.push(`   TX: ${tx.txHash?.slice(0, 20)}...`);
    lines.push('');
  }
  
  return lines.join('\n');
}

function formatNFTHoldings(data) {
  const lines = [];
  lines.push(`🎨 NFT Holdings: ${data.address}`);
  lines.push(`⛓️  Chain: ${data.chain}`);
  lines.push(`📊 Total NFTs: ${data.totalNFTs} across ${data.collections} collections`);
  lines.push('');
  
  for (const holding of data.holdings.slice(0, 10)) {
    const collectionName = holding.name || (holding.contract.slice(0, 6) + '...' + holding.contract.slice(-4));
    lines.push(`📦 Collection: ${collectionName}`);
    lines.push(`   Contract: ${holding.contract}`);
    lines.push(`   Held: ${holding.held} NFTs (${holding.totalIn} in, ${holding.totalOut} out)`);
    if (holding.tokenIds.length > 0) {
      const ids = holding.tokenIds.slice(0, 5).join(', ');
      const more = holding.tokenIds.length > 5 ? ` and ${holding.tokenIds.length - 5} more` : '';
      lines.push(`   Token IDs: ${ids}${more}`);
    }
    lines.push('');
  }
  
  return lines.join('\n');
}

function formatBotDetection(data) {
  const lines = [];
  const scoreEmoji = data.botScore >= 75 ? '🤖' : data.botScore >= 40 ? '⚠️' : '👤';
  lines.push(`${scoreEmoji} Bot Analysis: ${data.address}`);
  lines.push(`⛓️  Chain: ${data.chain}`);
  lines.push(`🎯 Score: ${data.botScore}/100 - ${data.verdict.toUpperCase()}`);
  lines.push('');
  
  if (data.breakdown) {
    lines.push('📊 Score Breakdown:');
    for (const [key, info] of Object.entries(data.breakdown)) {
      if (typeof info === 'object' && info.score !== undefined) {
        lines.push(`   ${key}: ${info.score}/${info.max} - ${info.detail}`);
      }
    }
    lines.push('');
  }
  
  if (data.stats) {
    lines.push('📈 Activity Stats:');
    lines.push(`   Buys: ${data.stats.totalBuys}, Sells: ${data.stats.totalSells}`);
    lines.push(`   Collections: ${data.stats.collections}, Fast Flips: ${data.stats.fastFlips}`);
  }
  
  return lines.join('\n');
}

module.exports = { CHAINS, TRANSFER_TOPIC, TRANSFER_SINGLE_TOPIC, getChain, rpcCall, padAddress, unpadAddress, hexToNumber, parseArgs, validateAddress, validateChain, formatOutput, resolveENS, resolveCollectionName, namehash, fetchTokenPrices, getTokenPrice };
