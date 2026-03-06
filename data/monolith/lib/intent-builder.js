import {
  encodeFunctionData,
  encodeAbiParameters,
  encodePacked,
  createPublicClient,
  http,
} from 'viem';
import { mainnet, base } from 'viem/chains';
import {
  STABLECOINS,
  ERC20_TRANSFER_ABI,
  CHAINS,
  UNISWAP,
  V3_FEES,
  QUOTER_V2_ABI,
} from './constants.js';

/**
 * Build intents ({target, calldata, value}) for common actions.
 * The skill is UNTRUSTED — it MUST NOT set nonce, gas, chainId, fees, or signatures.
 * Only target, calldata, value, and optionally chainHint.
 */

/**
 * Build a native ETH transfer intent.
 */
export function buildETHTransfer(to, amountWei, chainId) {
  const intent = {
    target: to,
    calldata: '0x',
    value: amountWei.toString(),
  };
  if (chainId) intent.chainHint = chainId.toString();
  return intent;
}

/**
 * Build an ERC-20 transfer intent.
 * @param {string} tokenAddress - The ERC-20 contract address.
 * @param {string} to - Recipient address.
 * @param {bigint} amount - Amount in token's smallest unit.
 */
export function buildERC20Transfer(tokenAddress, to, amount) {
  const calldata = encodeFunctionData({
    abi: ERC20_TRANSFER_ABI,
    functionName: 'transfer',
    args: [to, amount],
  });

  return {
    target: tokenAddress,
    calldata,
    value: '0',
  };
}

/**
 * Build a USDC transfer intent for a specific chain.
 * @param {number} chainId - Chain ID (1 or 8453).
 * @param {string} to - Recipient address.
 * @param {number} amountUSDC - Amount in human-readable USDC (e.g., 100 for 100 USDC).
 */
export function buildUSDCTransfer(chainId, to, amountUSDC) {
  const stables = STABLECOINS[chainId];
  if (!stables) throw new Error(`No stablecoins configured for chain ${chainId}`);

  const [usdcAddress, info] = Object.entries(stables)[0];
  const amount = BigInt(Math.round(amountUSDC * 10 ** info.decimals));

  return {
    ...buildERC20Transfer(usdcAddress, to, amount),
    chainHint: chainId.toString(),
  };
}

/**
 * Get the USDC contract address for a chain.
 * Lookup is by (chainId, address) tuple — never by symbol string.
 * @param {number} chainId - Chain ID (1 or 8453).
 * @returns {string|null} USDC contract address or null if not configured.
 */
export function getUSDCAddress(chainId) {
  const stables = STABLECOINS[chainId];
  if (!stables) return null;

  // USDC addresses are the first (and currently only) entry per chain
  // Identified by (chainId, contractAddress), not by symbol
  const usdcAddresses = {
    1: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    8453: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  };

  return usdcAddresses[chainId] || null;
}

/**
 * Query Uniswap V3 QuoterV2 for expected output amount.
 * Read-only RPC call — no daemon needed.
 * @param {number} chainId
 * @param {string} tokenIn - Input token address.
 * @param {string} tokenOut - Output token address.
 * @param {bigint} amountIn - Input amount in smallest unit.
 * @param {number} fee - Pool fee tier (e.g., 500, 3000).
 * @returns {Promise<bigint>} Expected output amount.
 */
export async function quoteExactInputSingle(chainId, tokenIn, tokenOut, amountIn, fee) {
  const chain = chainId === 1 ? mainnet : base;
  const client = createPublicClient({
    chain,
    transport: http(CHAINS[chainId].rpcUrl),
  });

  const quoterAddress = UNISWAP.QUOTER_V2[chainId];
  if (!quoterAddress) throw new Error(`No QuoterV2 for chain ${chainId}`);

  const [amountOut] = await client.readContract({
    address: quoterAddress,
    abi: QUOTER_V2_ABI,
    functionName: 'quoteExactInputSingle',
    args: [
      {
        tokenIn,
        tokenOut,
        amountIn,
        fee,
        sqrtPriceLimitX96: 0n,
      },
    ],
  });

  return amountOut;
}

/**
 * Build a V3 swap path (packed encoding: tokenIn + fee + tokenOut).
 */
function buildV3Path(tokenIn, fee, tokenOut) {
  return encodePacked(
    ['address', 'uint24', 'address'],
    [tokenIn, fee, tokenOut]
  );
}

/**
 * Encode Universal Router execute(commands, inputs[], deadline) calldata.
 * Shared by both API and fallback paths.
 */
function encodeUniversalRouterExecute(amountInWei, amountOutMin, weth, fee, tokenOutAddress) {
  const commands = '0x0b00';

  const wrapInput = encodeAbiParameters(
    [{ type: 'address' }, { type: 'uint256' }],
    [UNISWAP.ADDRESS_THIS, amountInWei]
  );

  const path = buildV3Path(weth, fee, tokenOutAddress);
  const swapInput = encodeAbiParameters(
    [
      { type: 'address' },
      { type: 'uint256' },
      { type: 'uint256' },
      { type: 'bytes' },
      { type: 'bool' },
    ],
    [UNISWAP.MSG_SENDER, amountInWei, amountOutMin, path, false]
  );

  const deadline = BigInt(Math.floor(Date.now() / 1000) + 1800);
  const calldata = encodeFunctionData({
    abi: [
      {
        type: 'function',
        name: 'execute',
        inputs: [
          { name: 'commands', type: 'bytes' },
          { name: 'inputs', type: 'bytes[]' },
          { name: 'deadline', type: 'uint256' },
        ],
        outputs: [],
        stateMutability: 'payable',
      },
    ],
    functionName: 'execute',
    args: [commands, [wrapInput, swapInput], deadline],
  });

  return calldata;
}

// Fee tier iteration order for fallback (most common first)
const FALLBACK_FEE_TIERS = [3000, 500, 10000];

/**
 * Resolve output token symbol to address.
 * @param {string} tokenOut - Token symbol ('USDC') or hex address.
 * @param {number} chainId
 * @returns {string} Token address.
 */
export function resolveTokenOutAddress(tokenOut, chainId) {
  if (tokenOut.startsWith('0x')) return tokenOut;
  if (tokenOut.toUpperCase() === 'USDC') {
    const addr = getUSDCAddress(chainId);
    if (!addr) throw new Error(`No USDC address for chain ${chainId}`);
    return addr;
  }
  throw new Error(`Unsupported output token: ${tokenOut}`);
}

/**
 * Try the Uniswap Routing API for a swap quote.
 * Returns { target, calldata, value, amountOut } on success, or null on failure.
 *
 * @param {number} chainId
 * @param {string} tokenInAddress - WETH address
 * @param {string} tokenOutAddress
 * @param {bigint} amountInWei
 * @param {number} maxSlippageBps
 * @returns {Promise<{target: string, calldata: string, value: string, amountOut: bigint}|null>}
 */
export async function tryRoutingAPI(chainId, tokenInAddress, tokenOutAddress, amountInWei, maxSlippageBps) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);

  try {
    const body = {
      tokenInChainId: chainId,
      tokenOutChainId: chainId,
      tokenIn: tokenInAddress,
      tokenOut: tokenOutAddress,
      amount: amountInWei.toString(),
      type: 'EXACT_INPUT',
      slippageTolerance: (maxSlippageBps / 100).toFixed(2),
      configs: [{ routingType: 'CLASSIC', protocols: ['V3'] }],
    };

    const res = await fetch('https://api.uniswap.org/v2/quote', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!res.ok) return null;

    const data = await res.json();

    // Validate response shape
    if (!data.quote || !data.methodParameters) return null;
    const { methodParameters, quote } = data;
    const target = methodParameters.to;
    const calldata = methodParameters.calldata;
    const value = methodParameters.value;

    // Safety: target must be the expected Universal Router
    if (target.toLowerCase() !== UNISWAP.UNIVERSAL_ROUTER.toLowerCase()) return null;

    // Safety: chainId in response must match request
    if (data.chainId !== undefined && data.chainId !== chainId) return null;

    // Safety: calldata must be present and non-empty hex
    if (!calldata || calldata === '0x' || calldata.length < 10) return null;

    // Safety: value must be numeric string
    if (value === undefined || value === null) return null;

    // Safety: value must not exceed requested amountIn (prevents overspend)
    if (BigInt(value) > amountInWei) return null;

    const amountOut = BigInt(quote.amount ?? 0);
    if (amountOut === 0n) return null;

    return { target, calldata, value: String(value), amountOut };
  } catch {
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * Fallback: probe on-chain QuoterV2 across fee tiers and pick the best quote.
 * Tier iteration order: [3000, 500, 10000].
 *
 * @param {number} chainId
 * @param {string} weth
 * @param {string} tokenOutAddress
 * @param {bigint} amountInWei
 * @param {number} maxSlippageBps
 * @returns {Promise<{fee: number, amountOut: bigint, amountOutMin: bigint}>}
 */
export async function fallbackQuote(chainId, weth, tokenOutAddress, amountInWei, maxSlippageBps, _quoter = quoteExactInputSingle) {
  const results = [];
  const errors = [];

  for (const fee of FALLBACK_FEE_TIERS) {
    try {
      const amountOut = await _quoter(chainId, weth, tokenOutAddress, amountInWei, fee);
      if (amountOut > 0n) {
        results.push({ fee, amountOut });
      }
    } catch (err) {
      errors.push({ fee, error: err.message });
    }
  }

  if (results.length === 0) {
    const tierSummary = FALLBACK_FEE_TIERS.map(f => {
      const e = errors.find(x => x.fee === f);
      return `${f}bps: ${e ? e.error : 'zero output'}`;
    }).join('; ');
    throw new Error(`All fee tier quotes failed. Tried [${FALLBACK_FEE_TIERS.join(', ')}]. Details: ${tierSummary}`);
  }

  // Pick best amountOut
  results.sort((a, b) => (b.amountOut > a.amountOut ? 1 : b.amountOut < a.amountOut ? -1 : 0));
  const best = results[0];
  const amountOutMin = best.amountOut * BigInt(10000 - maxSlippageBps) / 10000n;

  return { fee: best.fee, amountOut: best.amountOut, amountOutMin };
}

/**
 * Build a full Uniswap swap intent (ETH -> token).
 * Uses Uniswap Routing API when available; falls back to on-chain V3 fee-tier probing.
 *
 * @param {number} chainId - Chain ID (1 or 8453).
 * @param {bigint} amountInWei - ETH amount in wei.
 * @param {string} tokenOut - Output token symbol ('USDC') or address.
 * @param {number} [maxSlippageBps=50] - Max slippage in basis points (default 0.5%).
 * @returns {Promise<{target: string, calldata: string, value: string, chainHint: string, quotedAmountOut: bigint, source: string}>}
 */
export async function buildSwapIntent(chainId, amountInWei, tokenOut = 'USDC', maxSlippageBps = 50, _quoter = quoteExactInputSingle) {
  const weth = UNISWAP.WETH[chainId];
  if (!weth) throw new Error(`No WETH address for chain ${chainId}`);

  const tokenOutAddress = resolveTokenOutAddress(tokenOut, chainId);

  // Primary: try Routing API
  const apiResult = await tryRoutingAPI(chainId, weth, tokenOutAddress, amountInWei, maxSlippageBps);
  if (apiResult) {
    return {
      target: apiResult.target,
      calldata: apiResult.calldata,
      value: apiResult.value,
      chainHint: chainId.toString(),
      quotedAmountOut: apiResult.amountOut,
      source: 'routing-api',
    };
  }

  // Fallback: on-chain QuoterV2 with fee tier probing
  const { fee, amountOut, amountOutMin } = await fallbackQuote(
    chainId, weth, tokenOutAddress, amountInWei, maxSlippageBps, _quoter
  );

  const calldata = encodeUniversalRouterExecute(amountInWei, amountOutMin, weth, fee, tokenOutAddress);

  return {
    target: UNISWAP.UNIVERSAL_ROUTER,
    calldata,
    value: amountInWei.toString(),
    chainHint: chainId.toString(),
    quotedAmountOut: amountOut,
    source: 'on-chain-quoter',
  };
}
