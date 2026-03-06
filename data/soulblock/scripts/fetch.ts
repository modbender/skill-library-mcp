const DEFAULT_CONTRACT_ADDRESS = "0xfa5A304Db36A6933Ce1eC727A7a524a102a3454F";
const DEFAULT_BASE_RPC_URL = "https://mainnet.base.org";
const BASE_CHAIN_ID = 8453;
const MAX_FRAGMENT_SIZE = 2048;
const MAX_FRAGMENTS = 64;

const ABI = [
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function getFragmentCount(uint256 tokenId) view returns (uint256)",
  "function getFragmentContent(uint256 tokenId, uint256 index) view returns (bytes)",
  "function getGenesisBlock(uint256 tokenId) view returns (uint256)",
  "function getMinter(uint256 tokenId) view returns (address)",
] as const;

type EthersModule = typeof import("ethers");

let cachedEthers: EthersModule | null = null;

function printUsageAndExit(): never {
  console.error("Usage: npx ts-node scripts/fetch.ts <token-id>");
  console.error("Example: npx ts-node scripts/fetch.ts 42");
  console.error(
    "Optional env: SOULBLOCKS_CONTRACT_ADDRESS (overrides built-in default)",
  );
  process.exit(1);
}

function parseTokenId(rawTokenId: string | undefined): bigint {
  if (!rawTokenId) {
    printUsageAndExit();
  }

  if (!/^\d+$/.test(rawTokenId)) {
    throw new Error(`Invalid token ID "${rawTokenId}". Expected a positive integer.`);
  }

  const tokenId = BigInt(rawTokenId);
  if (tokenId < 1n) {
    throw new Error("Token ID must be >= 1.");
  }

  return tokenId;
}

function getContractAddress(): string {
  const address =
    process.env.SOULBLOCKS_CONTRACT_ADDRESS ??
    process.env.NEXT_PUBLIC_CONTRACT_ADDRESS ??
    DEFAULT_CONTRACT_ADDRESS;

  if (!/^0x[a-fA-F0-9]{40}$/.test(address)) {
    throw new Error(
      `Invalid contract address: ${address}. ` +
      (address === DEFAULT_CONTRACT_ADDRESS
        ? "The default address has not been set yet. Set SOULBLOCKS_CONTRACT_ADDRESS or wait for mainnet deployment."
        : "Check your SOULBLOCKS_CONTRACT_ADDRESS environment variable."),
    );
  }

  return address;
}

function getRpcUrl(): string {
  return (
    process.env.SOULBLOCK_RPC_URL ??
    process.env.NEXT_PUBLIC_RPC_URL ??
    DEFAULT_BASE_RPC_URL
  );
}

function getErrorMessage(error: unknown): string {
  if (typeof error === "object" && error !== null) {
    const value = error as {
      shortMessage?: unknown;
      reason?: unknown;
      message?: unknown;
    };

    if (typeof value.shortMessage === "string" && value.shortMessage.length > 0) {
      return value.shortMessage;
    }

    if (typeof value.reason === "string" && value.reason.length > 0) {
      return value.reason;
    }

    if (typeof value.message === "string" && value.message.length > 0) {
      return value.message;
    }
  }

  return String(error);
}

function isCallException(error: unknown): boolean {
  if (typeof error !== "object" || error === null) {
    return false;
  }

  return "code" in error && (error as { code?: unknown }).code === "CALL_EXCEPTION";
}

function decodeFragment(rawBytes: unknown, index: number): string {
  let bytes: Uint8Array;

  if (typeof rawBytes === "string" && rawBytes.startsWith("0x")) {
    bytes = Uint8Array.from(Buffer.from(rawBytes.slice(2), "hex"));
  } else if (rawBytes instanceof Uint8Array) {
    bytes = rawBytes;
  } else {
    throw new Error(`Fragment ${index} returned unsupported bytes format.`);
  }

  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    // Fragment data should be UTF-8. Fallback keeps output usable if malformed bytes exist.
    console.error(
      `Warning: fragment ${index} contains invalid UTF-8. Decoding with replacement characters.`,
    );
    return Buffer.from(bytes).toString("utf8");
  }
}

async function getEthers(): Promise<EthersModule> {
  if (cachedEthers) {
    return cachedEthers;
  }

  try {
    cachedEthers = await import("ethers");
    return cachedEthers;
  } catch {
    throw new Error(
      "Missing dependency: ethers. Run `npm install` in skills/soulblock before using fetch.ts.",
    );
  }
}

async function fetchSoulBlock(tokenId: bigint): Promise<string> {
  const contractAddress = getContractAddress();
  const rpcUrl = getRpcUrl();
  const { ethers } = await getEthers();

  const provider = new ethers.JsonRpcProvider(
    rpcUrl,
    { chainId: BASE_CHAIN_ID, name: "base" },
    { staticNetwork: true },
  );

  const deployedCode = await provider.getCode(contractAddress);
  if (deployedCode === "0x") {
    throw new Error(`No contract is deployed at ${contractAddress} on ${rpcUrl}.`);
  }

  const contract = new ethers.Contract(contractAddress, ABI, provider);

  let owner: string;
  let fragmentCountRaw: bigint;
  let genesisBlock: bigint;
  let minter: string;

  try {
    owner = await contract.ownerOf(tokenId);
    fragmentCountRaw = await contract.getFragmentCount(tokenId);
    genesisBlock = await contract.getGenesisBlock(tokenId);
    minter = await contract.getMinter(tokenId);
  } catch (error) {
    if (isCallException(error)) {
      throw new Error(
        `Soul Block #${tokenId.toString()} was not found or the contract call reverted.`,
      );
    }
    throw error;
  }

  const fragmentCount = Number(fragmentCountRaw);
  if (!Number.isSafeInteger(fragmentCount) || fragmentCount < 0) {
    throw new Error(`Invalid fragment count returned by contract: ${fragmentCountRaw}`);
  }
  if (fragmentCount > MAX_FRAGMENTS) {
    throw new Error(
      `Contract returned ${fragmentCount} fragments, above expected max ${MAX_FRAGMENTS}.`,
    );
  }

  const fragments: string[] = [];
  for (let index = 0; index < fragmentCount; index += 1) {
    const rawContent = await contract.getFragmentContent(tokenId, index);
    const decoded = decodeFragment(rawContent, index);
    const byteLength = Buffer.byteLength(decoded, "utf8");
    if (byteLength > MAX_FRAGMENT_SIZE && index > 0) {
      throw new Error(
        `Fragment ${index} is ${byteLength} bytes, above expected max ${MAX_FRAGMENT_SIZE}.`,
      );
    }
    fragments.push(decoded);
  }

  const soulContent = fragments.join("\n\n");
  const paddedTokenId = tokenId.toString().padStart(5, "0");

  return [
    `# Soul Block #${paddedTokenId}`,
    "",
    `**Owner:** ${owner}`,
    `**Minter:** ${minter}`,
    `**Fragments:** ${fragmentCount}`,
    `**Genesis Block:** ${genesisBlock.toString()}`,
    `**View:** https://soulblocks.ai/soul/${tokenId.toString()}`,
    "",
    "---",
    "",
    soulContent,
    "",
    "---",
    "",
    "*Loaded from SoulBlocks contract on Base.*",
    "*This identity is append-only and may have evolved since this snapshot.*",
  ].join("\n");
}

async function main(): Promise<void> {
  const tokenId = parseTokenId(process.argv[2]);
  const markdown = await fetchSoulBlock(tokenId);
  console.log(markdown);
}

main().catch((error: unknown) => {
  console.error(`Error: ${getErrorMessage(error)}`);
  process.exit(1);
});
