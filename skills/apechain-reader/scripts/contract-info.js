#!/usr/bin/env node
// Multi-chain Contract Info — returns contract details as JSON
// Usage: node contract-info.js <address> [--chain apechain]

const { getChain, rpcCall, hexToNumber, parseArgs, formatOutput } = require("./lib/rpc");

async function initArgs() {
  try {
    return await parseArgs(process.argv);
  } catch (err) {
    console.log(formatOutput({ error: err.message }, "json"));
    process.exit(1);
  }
}

const SELECTORS = {
  name: "0x06fdde03",
  symbol: "0x95d89b41",
  totalSupply: "0x18160ddd",
  owner: "0x8da5cb5b",
  decimals: "0x313ce567",
  supportsInterface: "0x01ffc9a7",
};

async function callContract(rpc, selector) {
  try {
    return await rpcCall(rpc, "eth_call", [{ to: address, data: selector }, "latest"]);
  } catch { return null; }
}

function decodeString(hex) {
  if (!hex || hex === "0x" || hex.length < 130) return null;
  try {
    const len = parseInt(hex.slice(66, 130), 16);
    if (len === 0 || len > 100) return null;
    const strHex = hex.slice(130, 130 + len * 2);
    return Buffer.from(strHex, "hex").toString("utf-8").replace(/\0/g, "");
  } catch { return null; }
}

function decodeUint(hex) {
  if (!hex || hex === "0x") return null;
  try { return Number(BigInt(hex)); } catch { return null; }
}

function decodeAddress(hex) {
  if (!hex || hex.length < 66) return null;
  const addr = "0x" + hex.slice(26, 66);
  return addr === "0x" + "0".repeat(40) ? null : addr;
}

async function main() {
  const { address, chainName, outputFormat } = await initArgs();
  const chain = getChain(chainName);
  const rpc = chain.rpc;

  const code = await rpcCall(rpc, "eth_getCode", [address, "latest"]);
  const isContract = code && code !== "0x" && code !== "0x0";

  if (!isContract) {
    console.log(formatOutput({ address, chain: chain.name, chainId: chain.id, isContract: false, type: "EOA (wallet)" }, outputFormat));
    return;
  }

  // ERC-165: check if supports ERC-721 or ERC-1155
  const erc721Interface = "80ac58cd";
  const erc1155Interface = "d9b67a26";
  const [supports721, supports1155, nameHex, symbolHex, totalSupplyHex, ownerHex, decimalsHex] = await Promise.all([
    callContract(rpc, SELECTORS.supportsInterface + erc721Interface.padEnd(64, "0")),
    callContract(rpc, SELECTORS.supportsInterface + erc1155Interface.padEnd(64, "0")),
    callContract(rpc, SELECTORS.name),
    callContract(rpc, SELECTORS.symbol),
    callContract(rpc, SELECTORS.totalSupply),
    callContract(rpc, SELECTORS.owner),
    callContract(rpc, SELECTORS.decimals),
  ]);

  const is721 = supports721?.endsWith("1");
  const is1155 = supports1155?.endsWith("1");
  const decimals = decodeUint(decimalsHex);

  let type = "Contract (other)";
  if (is721) type = "ERC-721 (NFT)";
  else if (is1155) type = "ERC-1155 (Multi-Token)";
  else if (decimals !== null && decimals <= 18) type = "ERC-20 (Token)";

  console.log(formatOutput({
    address,
    chain: chain.name,
    chainId: chain.id,
    isContract: true,
    type,
    name: decodeString(nameHex),
    symbol: decodeString(symbolHex),
    totalSupply: decodeUint(totalSupplyHex),
    decimals,
    owner: decodeAddress(ownerHex),
    explorer: `${chain.explorer}/address/${address}`,
  }, outputFormat));
}

main().catch(err => {
  console.log(formatOutput({ error: err.message }, "json"));
  process.exit(1);
});
