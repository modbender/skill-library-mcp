#!/usr/bin/env node
// Net Protocol Storage Integration for OK Computers
// Read and write onchain data via Net Protocol on Base
// Built by potdealer + olliebot

const { ethers } = require("ethers");

// Net Protocol contracts on Base
const NET_SIMPLE_STORAGE = "0x00000000db40fcb9f4466330982372e27fd7bbf5";
const NET_CHUNKED_STORAGE = "0x000000A822F09aF21b1951B65223F54ea392E6C6";
const NET_CHUNKED_READER = "0x00000005210a7532787419658f6162f771be62f8";
const NET_STORAGE_ROUTER = "0x000000C0bbc2Ca04B85E77D18053e7c38bB97939";
const NET_SAFE_READER = "0x0000000d03bad401fae4935dc9cbbf8084347214";

const CHAIN_ID = 8453;
const RPC = "https://mainnet.base.org";

// Function selectors
const SEL = {
  get: "0x20c027b8",           // get(bytes32 key, address operator) → (string text, bytes value)
  put: "0x31bced08",           // put(bytes32 key, string text, bytes value)
  getTotalWrites: "0x47a21327", // getTotalWrites(bytes32 key, address operator) → uint256
  getValueAtIndex: "0xf3724377" // getValueAtIndex(bytes32 key, address operator, uint256 idx) → (string, bytes)
};

class NetProtocol {
  constructor() {
    this.provider = new ethers.JsonRpcProvider(RPC);
  }

  // --- Key Encoding ---

  // CRITICAL: Short keys (≤32 chars) are LEFT-padded to bytes32
  // Keys >32 chars use keccak256 hash
  // All keys lowercased first
  static encodeKey(key) {
    key = key.toLowerCase();
    if (key.length <= 32) {
      // Left-pad: convert to hex bytes, pad to 32 bytes on the LEFT
      const hex = Buffer.from(key, "utf8").toString("hex");
      return "0x" + hex.padStart(64, "0");
    } else {
      return ethers.solidityPackedKeccak256(["string"], [key]);
    }
  }

  // --- Reading ---

  async rpcCall(to, data) {
    const result = await this.provider.call({ to, data });
    return result;
  }

  // Read the latest value stored at a key by an operator
  async read(key, operator) {
    const keyBytes = NetProtocol.encodeKey(key);
    const operatorPadded = operator.slice(2).toLowerCase().padStart(64, "0");
    const data = SEL.get + keyBytes.slice(2) + operatorPadded;
    const result = await this.rpcCall(NET_SIMPLE_STORAGE, data);
    return NetProtocol.decodeGetResponse(result);
  }

  // Get total number of writes to a key by an operator
  async getTotalWrites(key, operator) {
    const keyBytes = NetProtocol.encodeKey(key);
    const operatorPadded = operator.slice(2).toLowerCase().padStart(64, "0");
    const data = SEL.getTotalWrites + keyBytes.slice(2) + operatorPadded;
    const result = await this.rpcCall(NET_SIMPLE_STORAGE, data);
    if (!result || result === "0x") return 0;
    return parseInt(result, 16);
  }

  // Read a specific version (index) of data at a key
  async readAtIndex(key, operator, index) {
    const keyBytes = NetProtocol.encodeKey(key);
    const operatorPadded = operator.slice(2).toLowerCase().padStart(64, "0");
    const indexPadded = index.toString(16).padStart(64, "0");
    const data = SEL.getValueAtIndex + keyBytes.slice(2) + operatorPadded + indexPadded;
    const result = await this.rpcCall(NET_SIMPLE_STORAGE, data);
    return NetProtocol.decodeGetResponse(result);
  }

  // --- Writing ---

  // Build a transaction to store data on Net Protocol
  // Returns Bankr-compatible transaction JSON
  buildStore(key, text, value) {
    const keyBytes = NetProtocol.encodeKey(key);
    const iface = new ethers.Interface([
      "function put(bytes32 key, string text, bytes value)"
    ]);
    const data = iface.encodeFunctionData("put", [
      keyBytes,
      text || "",
      ethers.toUtf8Bytes(value)
    ]);
    return {
      to: NET_SIMPLE_STORAGE,
      data: data,
      value: "0",
      chainId: CHAIN_ID
    };
  }

  // --- Decoding ---

  // Decode get() response: (string text, bytes value) → { text, value }
  static decodeGetResponse(hex) {
    if (!hex || hex === "0x" || hex.length < 130) return null;
    try {
      const iface = new ethers.Interface([
        "function get(bytes32,address) returns (string text, bytes value)"
      ]);
      const decoded = iface.decodeFunctionResult("get", hex);
      return {
        text: decoded.text,
        value: ethers.toUtf8String(decoded.value)
      };
    } catch (e) {
      // Fallback: manual decode for edge cases
      return NetProtocol.decodeResponseManual(hex);
    }
  }

  static decodeResponseManual(hex) {
    if (!hex || hex === "0x") return null;
    hex = hex.slice(2);
    try {
      const bytesOffset = parseInt(hex.slice(64, 128), 16) * 2;
      const bytesLen = parseInt(hex.slice(bytesOffset, bytesOffset + 64), 16);
      const bytesHex = hex.slice(bytesOffset + 64, bytesOffset + 64 + bytesLen * 2);
      let content = "";
      for (let i = 0; i < bytesHex.length; i += 2) {
        const code = parseInt(bytesHex.slice(i, i + 2), 16);
        if (code > 0) content += String.fromCharCode(code);
      }
      return { text: "", value: content };
    } catch (e) {
      return null;
    }
  }
}

// --- CLI ---
if (require.main === module) {
  const args = process.argv.slice(2);
  const cmd = args[0];

  const usage = `
Net Protocol Storage — Read/Write onchain data on Base

Usage:
  node net-protocol.js read <key> <operator>       Read stored data
  node net-protocol.js count <key> <operator>       Get total writes
  node net-protocol.js build-store <key> <text>     Build store transaction (prints JSON)
  node net-protocol.js encode-key <key>             Show bytes32 encoding of a key
  node net-protocol.js info                         Show contract addresses

Contracts:
  Simple Storage:  ${NET_SIMPLE_STORAGE}
  Chunked Storage: ${NET_CHUNKED_STORAGE}
  Chunked Reader:  ${NET_CHUNKED_READER}
  Storage Router:  ${NET_STORAGE_ROUTER}

Key Encoding:
  Keys ≤32 chars → LEFT-padded hex to bytes32
  Keys >32 chars → keccak256 hash
  All keys lowercased first

Examples:
  node net-protocol.js read "my-page" 0x2460F6C6CA04DD6a73E9B5535aC67Ac48726c09b
  node net-protocol.js encode-key "okc-test"
  node net-protocol.js build-store "my-page" "<h1>Hello</h1>"
`;

  if (!cmd || cmd === "help" || cmd === "--help") {
    console.log(usage);
    process.exit(0);
  }

  if (cmd === "info") {
    console.log("Net Protocol Storage Contracts (Base, Chain ID 8453)");
    console.log("─".repeat(55));
    console.log(`Simple Storage:  ${NET_SIMPLE_STORAGE}`);
    console.log(`Chunked Storage: ${NET_CHUNKED_STORAGE}`);
    console.log(`Chunked Reader:  ${NET_CHUNKED_READER}`);
    console.log(`Storage Router:  ${NET_STORAGE_ROUTER}`);
    console.log(`Safe Reader:     ${NET_SAFE_READER}`);
    process.exit(0);
  }

  if (cmd === "encode-key") {
    const key = args[1];
    if (!key) { console.error("Usage: encode-key <key>"); process.exit(1); }
    console.log(`Key: "${key}"`);
    console.log(`Bytes32: ${NetProtocol.encodeKey(key)}`);
    process.exit(0);
  }

  if (cmd === "build-store") {
    const key = args[1];
    const text = args[2];
    if (!key || !text) { console.error("Usage: build-store <key> <text>"); process.exit(1); }
    const np = new NetProtocol();
    const tx = np.buildStore(key, key, text);
    console.log(JSON.stringify(tx, null, 2));
    console.log(`\nSubmit via: curl -X POST https://api.bankr.bot/agent/submit -H "X-API-Key: $BANKR_API_KEY" -H "Content-Type: application/json" -d '${JSON.stringify({ transaction: tx })}'`);
    process.exit(0);
  }

  (async () => {
    const np = new NetProtocol();

    if (cmd === "read") {
      const key = args[1];
      const operator = args[2];
      if (!key || !operator) { console.error("Usage: read <key> <operator>"); process.exit(1); }
      console.log(`Reading key "${key}" from operator ${operator}...`);
      console.log(`Key bytes32: ${NetProtocol.encodeKey(key)}`);
      const result = await np.read(key, operator);
      if (!result) {
        console.log("No data found.");
      } else {
        console.log(`Text: ${result.text}`);
        console.log(`Value (${result.value.length} chars):`);
        console.log(result.value.slice(0, 500) + (result.value.length > 500 ? "..." : ""));
      }
    }

    if (cmd === "count") {
      const key = args[1];
      const operator = args[2];
      if (!key || !operator) { console.error("Usage: count <key> <operator>"); process.exit(1); }
      const count = await np.getTotalWrites(key, operator);
      console.log(`Total writes to "${key}" by ${operator}: ${count}`);
    }
  })();
}

module.exports = {
  NetProtocol,
  NET_SIMPLE_STORAGE,
  NET_CHUNKED_STORAGE,
  NET_CHUNKED_READER,
  NET_STORAGE_ROUTER,
  NET_SAFE_READER
};
