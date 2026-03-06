/**
 * Function input decoder — decodes transaction calldata
 * Uses 4byte.directory for signature lookup + manual ABI decoding
 */

import { parseSignatureParams, decodeParams } from "./abiDecoder.mjs";

// Well-known function selectors (most common, avoids API call)
const KNOWN_FUNCTIONS = {
  "0xa9059cbb": "transfer(address,uint256)",
  "0x095ea7b3": "approve(address,uint256)",
  "0x23b872dd": "transferFrom(address,address,uint256)",
  "0x70a08231": "balanceOf(address)",
  "0x18160ddd": "totalSupply()",
  "0xdd62ed3e": "allowance(address,address)",
  "0x313ce567": "decimals()",
  "0x06fdde03": "name()",
  "0x95d89b41": "symbol()",
  // Uniswap V2 Router
  "0x7ff36ab5": "swapExactETHForTokens(uint256,address[],address,uint256)",
  "0x18cbafe5": "swapExactTokensForETH(uint256,uint256,address[],address,uint256)",
  "0x38ed1739": "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
  "0xfb3bdb41": "swapETHForExactTokens(uint256,address[],address,uint256)",
  "0xe8e33700": "addLiquidity(address,address,uint256,uint256,uint256,uint256,address,uint256)",
  "0xf305d719": "addLiquidityETH(address,uint256,uint256,uint256,address,uint256)",
  "0xbaa2abde": "removeLiquidity(address,address,uint256,uint256,uint256,address,uint256)",
  "0x02751cec": "removeLiquidityETH(address,uint256,uint256,uint256,address,uint256)",
  // Uniswap V3
  "0x414bf389": "exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))",
  "0xc04b8d59": "exactInput((bytes,address,uint256,uint256,uint256))",
  "0xdb3e2198": "exactOutputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))",
  // Multicall
  "0xac9650d8": "multicall(bytes[])",
  "0x5ae401dc": "multicall(uint256,bytes[])",
  // Common
  "0x3593564c": "execute(bytes,bytes[],uint256)",
  "0xd0e30db0": "deposit()",
  "0x2e1a7d4d": "withdraw(uint256)",
  "0xa22cb465": "setApprovalForAll(address,bool)",
  "0x42842e0e": "safeTransferFrom(address,address,uint256)",
  "0xb88d4fde": "safeTransferFrom(address,address,uint256,bytes)",
  "0x40c10f19": "mint(address,uint256)",
  "0x9dc29fac": "burn(address,uint256)",
  "0x150b7a02": "onERC721Received(address,address,uint256,bytes)",
  "0xf23a6e61": "onERC1155Received(address,address,uint256,uint256,bytes)",
};

/**
 * Look up function signature from 4byte.directory API
 */
async function lookup4byte(selector) {
  try {
    const res = await fetch(
      `https://www.4byte.directory/api/v1/signatures/?hex_signature=${selector}&ordering=-created_at`,
      { signal: AbortSignal.timeout(5000) }
    );
    if (!res.ok) return null;
    const data = await res.json();
    if (data.results && data.results.length > 0) {
      return data.results[0].text_signature;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Decode transaction input data
 * @param {string} input - Transaction input hex (e.g. "0xa9059cbb000...")
 * @returns {Object} Decoded function with name, signature, params
 */
export async function decodeFunctionInput(input) {
  if (!input || input === "0x" || input.length < 10) {
    return null; // No input data (plain ETH transfer)
  }

  const selector = input.slice(0, 10).toLowerCase();
  const calldata = input.slice(10); // Everything after the 4-byte selector

  // Look up signature
  let signature = KNOWN_FUNCTIONS[selector];
  let source = "local";

  if (!signature) {
    signature = await lookup4byte(selector);
    source = signature ? "4byte.directory" : "unknown";
  }

  if (!signature) {
    return {
      selector,
      functionName: null,
      signature: null,
      source: "unknown",
      params: [],
      rawCalldata: `0x${calldata}`,
    };
  }

  // Parse signature and decode params
  const { name, params: paramTypes } = parseSignatureParams(signature);
  const decoded = decodeParams(calldata, paramTypes);

  // Attach param names from signature if possible
  // Re-parse the signature to get named params if available
  const paramNames = getParamNamesFromSignature(signature);

  const params = decoded.map((d, i) => ({
    name: paramNames[i] || `param${i}`,
    type: d.type,
    value: d.value,
  }));

  return {
    selector,
    functionName: name,
    signature,
    source,
    params,
  };
}

/**
 * Extract parameter names from well-known function signatures
 */
function getParamNamesFromSignature(signature) {
  const knownParams = {
    "transfer(address,uint256)": ["to", "amount"],
    "approve(address,uint256)": ["spender", "amount"],
    "transferFrom(address,address,uint256)": ["from", "to", "amount"],
    "balanceOf(address)": ["owner"],
    "allowance(address,address)": ["owner", "spender"],
    "swapExactETHForTokens(uint256,address[],address,uint256)": ["amountOutMin", "path", "to", "deadline"],
    "swapExactTokensForETH(uint256,uint256,address[],address,uint256)": ["amountIn", "amountOutMin", "path", "to", "deadline"],
    "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)": ["amountIn", "amountOutMin", "path", "to", "deadline"],
    "swapETHForExactTokens(uint256,address[],address,uint256)": ["amountOut", "path", "to", "deadline"],
    "addLiquidityETH(address,uint256,uint256,uint256,address,uint256)": ["token", "amountTokenDesired", "amountTokenMin", "amountETHMin", "to", "deadline"],
    "removeLiquidityETH(address,uint256,uint256,uint256,address,uint256)": ["token", "liquidity", "amountTokenMin", "amountETHMin", "to", "deadline"],
    "deposit()": [],
    "withdraw(uint256)": ["amount"],
    "mint(address,uint256)": ["to", "amount"],
    "burn(address,uint256)": ["from", "amount"],
    "setApprovalForAll(address,bool)": ["operator", "approved"],
    "safeTransferFrom(address,address,uint256)": ["from", "to", "tokenId"],
  };
  return knownParams[signature] || [];
}
