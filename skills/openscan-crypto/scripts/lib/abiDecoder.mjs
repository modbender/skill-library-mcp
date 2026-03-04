/**
 * Minimal ABI decoder — no external dependencies
 * Handles: address, uint*, int*, bool, bytes32, bytes, string, fixed-size arrays
 * Does NOT handle: dynamic arrays, tuples (would need viem for those)
 */

/**
 * Decode a single ABI-encoded value from a 32-byte hex chunk
 */
export function decodeValue(hex, type) {
  if (!hex) return "";
  const cleaned = hex.startsWith("0x") ? hex.slice(2) : hex;

  if (type === "address") {
    return `0x${cleaned.slice(-40)}`;
  }
  if (type === "bool") {
    return BigInt(`0x${cleaned}`) === 1n ? "true" : "false";
  }
  if (type.startsWith("uint")) {
    return BigInt(`0x${cleaned}`).toString();
  }
  if (type.startsWith("int")) {
    const value = BigInt(`0x${cleaned}`);
    const max = BigInt("0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");
    if (value > max) {
      const maxUint = BigInt("0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");
      return (-(maxUint - value + 1n)).toString();
    }
    return value.toString();
  }
  if (type === "bytes32") {
    return `0x${cleaned}`;
  }
  // For other types, return raw hex
  return `0x${cleaned}`;
}

/**
 * Parse a function/event signature to extract param types
 * e.g. "transfer(address,uint256)" → ["address", "uint256"]
 */
export function parseSignatureParams(signature) {
  const match = signature.match(/^(\w+)\((.*)\)$/);
  if (!match) return { name: signature, params: [] };

  const name = match[1];
  const paramsStr = match[2] || "";
  if (!paramsStr) return { name, params: [] };

  // Handle nested parens (tuples)
  const params = [];
  let depth = 0;
  let current = "";
  for (const char of paramsStr) {
    if (char === "(") { depth++; current += char; }
    else if (char === ")") { depth--; current += char; }
    else if (char === "," && depth === 0) {
      if (current) params.push(current.trim());
      current = "";
    } else {
      current += char;
    }
  }
  if (current) params.push(current.trim());

  return { name, params };
}

/**
 * Decode calldata parameters given a list of types
 * Handles static types (32-byte slots) and basic dynamic types (bytes, string)
 * 
 * @param {string} data - Hex string of calldata (WITHOUT the 4-byte selector)
 * @param {string[]} types - Array of ABI types
 * @returns {Array<{type: string, value: string}>}
 */
export function decodeParams(data, types) {
  if (!data || data === "0x") return [];
  const cleaned = data.startsWith("0x") ? data.slice(2) : data;
  const results = [];
  const SLOT = 64; // 32 bytes = 64 hex chars

  for (let i = 0; i < types.length; i++) {
    const type = types[i];
    const offset = i * SLOT;

    if (offset >= cleaned.length) break;

    const chunk = cleaned.slice(offset, offset + SLOT);

    // Dynamic types: bytes, string, arrays — read offset pointer, then decode
    if (type === "bytes" || type === "string" || type.endsWith("[]")) {
      const dataOffset = Number(BigInt(`0x${chunk}`)) * 2; // byte offset → hex offset
      if (dataOffset < cleaned.length) {
        const lengthHex = cleaned.slice(dataOffset, dataOffset + SLOT);
        const length = Number(BigInt(`0x${lengthHex}`));

        if (type === "string") {
          const strHex = cleaned.slice(dataOffset + SLOT, dataOffset + SLOT + length * 2);
          let str = "";
          for (let j = 0; j < strHex.length; j += 2) {
            const code = parseInt(strHex.slice(j, j + 2), 16);
            if (code === 0) break;
            str += String.fromCharCode(code);
          }
          results.push({ type, value: str });
        } else if (type.endsWith("[]")) {
          // Dynamic array
          const elementType = type.slice(0, -2);
          const items = [];
          for (let j = 0; j < length; j++) {
            const itemHex = cleaned.slice(dataOffset + SLOT + j * SLOT, dataOffset + SLOT + (j + 1) * SLOT);
            items.push(decodeValue(`0x${itemHex}`, elementType));
          }
          results.push({ type, value: `[${items.join(", ")}]` });
        } else {
          // bytes
          results.push({ type, value: `0x${cleaned.slice(dataOffset + SLOT, dataOffset + SLOT + length * 2)}` });
        }
      } else {
        results.push({ type, value: `0x${chunk}` });
      }
    } else {
      // Static type — decode from the 32-byte slot
      results.push({ type, value: decodeValue(`0x${chunk}`, type) });
    }
  }

  return results;
}

/**
 * Compute the 4-byte function selector from a signature
 * Uses Web Crypto API (available in Node.js 18+)
 */
export async function computeSelector(signature) {
  const encoder = new TextEncoder();
  const data = encoder.encode(signature);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  // Actually we need keccak256, not SHA-256. Since we don't have keccak,
  // we'll rely on the 4byte directory lookup instead.
  // This function is a placeholder — in practice we match by selector from external sources.
  return null;
}
