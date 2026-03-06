#!/usr/bin/env npx tsx
/**
 * Zeru ERC-8004 Identity Registry — OpenClaw Skill CLI
 *
 * Commands:
 *   register      --name <name> --description <desc> --endpoint <url> [--image <url>]
 *   read          <agentId>
 *   fee
 *   set-metadata  <agentId> --key <key> --value <value>
 *   unset-wallet  <agentId>
 *
 * Env:
 *   PRIVATE_KEY  — Required for write operations (register, set-metadata, unset-wallet)
 *   RPC_URL      — Optional, override default RPC
 */

import { readFileSync } from "fs";
import { Wallet, JsonRpcProvider, formatEther } from "ethers";
import {
  resolveConfig,
  createAgentURI,
  updateAgentURI,
  registerAgent,
  getAgent,
  getRegistrationFee,
  isRegistrationEnabled,
  getAgentWallet,
  setMetadata,
  unsetAgentWallet,
  ZeruError,
} from "../lib/index.js";

// ── Helpers ──

function die(msg: string): never {
  console.error(`\u274C ${msg}`);
  process.exit(1);
}

function parseArgs(argv: string[]): { command: string; positional: string[]; flags: Record<string, string> } {
  const command = argv[0] ?? "";
  const positional: string[] = [];
  const flags: Record<string, string> = {};

  let i = 1;
  while (i < argv.length) {
    const arg = argv[i];
    if (arg.startsWith("--") && i + 1 < argv.length) {
      flags[arg.slice(2)] = argv[i + 1];
      i += 2;
    } else {
      positional.push(arg);
      i++;
    }
  }
  return { command, positional, flags };
}

/** Default chain: Base Mainnet. Override with CHAIN_ID env or --chain flag. */
function getChainId(): number {
  const envChain = process.env.CHAIN_ID;
  if (envChain) return Number(envChain);
  // Check for --chain flag in args
  const idx = process.argv.indexOf("--chain");
  if (idx !== -1 && process.argv[idx + 1]) return Number(process.argv[idx + 1]);
  return 8453; // Base Mainnet default
}

function getChainLabel(chainId: number): string {
  if (chainId === 8453) return "Base Mainnet (8453)";
  if (chainId === 84532) return "Base Sepolia (84532)";
  return `Chain ${chainId}`;
}

function getSigner() {
  const pk = process.env.PRIVATE_KEY;
  if (!pk) die("PRIVATE_KEY env var not set. Add it to your OpenClaw config under skills.entries.zeru-erc8004-identity.env");
  const config = resolveConfig({
    chainId: getChainId(),
    rpcUrl: process.env.RPC_URL,
  });
  const provider = new JsonRpcProvider(config.rpcUrl);
  const signer = new Wallet(pk, provider);
  return { config, signer };
}

function getReadConfig() {
  return resolveConfig({
    chainId: getChainId(),
    rpcUrl: process.env.RPC_URL,
  });
}

// ── Commands ──

async function cmdRegister(flags: Record<string, string>) {
  const jsonFile = flags.json;

  let input: Record<string, unknown>;

  if (jsonFile) {
    // ── JSON file mode: read full agent input from file ──
    let raw: string;
    try {
      raw = readFileSync(jsonFile, "utf-8");
    } catch (e) {
      die(`Cannot read JSON file: ${jsonFile} — ${e instanceof Error ? e.message : e}`);
    }
    try {
      input = JSON.parse(raw!);
    } catch {
      die(`Invalid JSON in file: ${jsonFile}`);
    }
  } else {
    // ── Simple flag mode: --name, --description, --endpoint ──
    const name = flags.name;
    const description = flags.description ?? flags.desc;
    const endpoint = flags.endpoint;
    const image = flags.image;

    if (!name) die("Missing --name (or use --json <file>). Usage:\n  register --name 'My Agent' --description 'What it does' --endpoint 'https://...'\n  register --json agent.json");
    if (!description) die("Missing --description");
    if (!endpoint) die("Missing --endpoint");

    input = {
      name,
      description,
      services: [{ name: "api", endpoint }],
    };
    if (image) input.image = image;
  }

  const { config, signer } = getSigner();
  const address = await signer.getAddress();

  // Set owner from signer if not provided
  if (!input!.owner) input!.owner = address;

  console.log("\u26D3\uFE0F  Zeru ERC-8004 Agent Registration");
  console.log("\u2501".repeat(40));
  console.log(`  Network:  ${getChainLabel(config.chainId)}`);
  console.log(`  Wallet:   ${address}`);
  if (jsonFile) console.log(`  JSON:     ${jsonFile}`);
  console.log(`  Name:     ${(input! as any).name}`);

  // 1. Fee
  const fee = await getRegistrationFee(config);
  console.log(`  Fee:      ${formatEther(fee)} ETH`);

  const enabled = await isRegistrationEnabled(config);
  if (!enabled) die("Registration is currently disabled on this contract");

  // 2. Check balance
  const balance = await signer.provider!.getBalance(address);
  if (balance < fee + BigInt(50000) * BigInt(1e9)) {
    die(`Insufficient balance. Need ~${formatEther(fee)} ETH + gas. Have ${formatEther(balance)} ETH`);
  }

  console.log("");
  console.log("Step 1/4: Creating agent URI...");
  const { id, agentURI, json } = await createAgentURI(config, signer, input! as any);
  console.log(`  URI: ${agentURI}`);

  console.log("Step 2/4: Minting NFT on-chain...");
  const { agentId, txHash } = await registerAgent(config, { signer, agentURI });
  console.log(`  Agent ID: ${agentId}`);
  console.log(`  Tx: ${txHash}`);

  console.log("Step 3/4: Updating document with real agentId...");
  await updateAgentURI(config, signer, id, {
    ...json,
    registrations: [{
      agentId: Number(agentId),
      agentRegistry: `eip155:${config.chainId}:${config.identityRegistryAddress}`,
    }],
  });

  console.log("Step 4/4: Verifying on-chain...");
  const agent = await getAgent(config, agentId);

  console.log("");
  console.log("\u2705 Registration complete!");
  console.log("\u2501".repeat(40));
  console.log(`  Agent ID:    ${agentId}`);
  console.log(`  Name:        ${name}`);
  console.log(`  Owner:       ${agent.owner}`);
  console.log(`  Agent URI:   ${agent.agentURI}`);
  console.log(`  Wallet:      ${agent.agentWallet ?? "(not set)"}`);
  console.log(`  Tx Hash:     ${txHash}`);
}

async function cmdRead(positional: string[]) {
  const agentId = positional[0];
  if (!agentId) die("Missing agentId. Usage: read <agentId>");

  const config = getReadConfig();

  console.log(`\u26D3\uFE0F  Agent #${agentId}`);
  console.log("\u2501".repeat(40));

  const agent = await getAgent(config, BigInt(agentId));
  console.log(`  Owner:       ${agent.owner}`);
  console.log(`  Agent URI:   ${agent.agentURI}`);
  console.log(`  Wallet:      ${agent.agentWallet ?? "(not set)"}`);

  if (agent.parsedJson) {
    const j = agent.parsedJson as Record<string, unknown>;
    if (j.name) console.log(`  Name:        ${j.name}`);
    if (j.description) console.log(`  Description: ${String(j.description).slice(0, 100)}`);
    if (j.active !== undefined) console.log(`  Active:      ${j.active}`);
    if (Array.isArray(j.services)) {
      for (const s of j.services) {
        const svc = s as Record<string, unknown>;
        console.log(`  Service:     ${svc.name} → ${svc.endpoint}`);
      }
    }
  }
}

async function cmdFee() {
  const config = getReadConfig();

  console.log("\u26D3\uFE0F  Zeru Registry Info");
  console.log("\u2501".repeat(40));

  const fee = await getRegistrationFee(config);
  const enabled = await isRegistrationEnabled(config);

  console.log(`  Network:      ${getChainLabel(config.chainId)}`);
  console.log(`  Registry:     ${config.identityRegistryAddress}`);
  console.log(`  Fee:          ${formatEther(fee)} ETH`);
  console.log(`  Registration: ${enabled ? "OPEN" : "CLOSED"}`);
}

async function cmdSetMetadata(positional: string[], flags: Record<string, string>) {
  const agentId = positional[0];
  const key = flags.key;
  const value = flags.value;

  if (!agentId) die("Missing agentId. Usage: set-metadata <agentId> --key <key> --value <value>");
  if (!key) die("Missing --key");
  if (!value) die("Missing --value");

  const { config, signer } = getSigner();

  console.log(`\u26D3\uFE0F  Setting metadata on Agent #${agentId}`);
  console.log("\u2501".repeat(40));
  console.log(`  Key:   ${key}`);
  console.log(`  Value: ${value}`);

  const txHash = await setMetadata(config, signer, BigInt(agentId), key, value);
  console.log("");
  console.log(`\u2705 Metadata set! Tx: ${txHash}`);
}

async function cmdUnsetWallet(positional: string[]) {
  const agentId = positional[0];
  if (!agentId) die("Missing agentId. Usage: unset-wallet <agentId>");

  const { config, signer } = getSigner();

  console.log(`\u26D3\uFE0F  Unsetting wallet for Agent #${agentId}`);
  console.log("\u2501".repeat(40));

  const txHash = await unsetAgentWallet(config, signer, BigInt(agentId));
  console.log("");
  console.log(`\u2705 Wallet unset! Tx: ${txHash}`);
}

// ── Main ──

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log("Zeru ERC-8004 Identity Registry");
    console.log("\u2501".repeat(40));
    console.log("Commands:");
    console.log("  register     --json <file>  (full agent JSON — recommended)");
    console.log("  register     --name <n> --description <d> --endpoint <url> [--image <url>]");
    console.log("  read         <agentId>");
    console.log("  fee          Show registration fee and status");
    console.log("  set-metadata <agentId> --key <key> --value <value>");
    console.log("  unset-wallet <agentId>");
    console.log("");
    console.log("Global flags:");
    console.log("  --chain <id> Chain ID (default: 8453 = Base Mainnet, 84532 = Base Sepolia)");
    console.log("");
    console.log("Env:");
    console.log("  PRIVATE_KEY  Required for write operations");
    console.log("  CHAIN_ID     Optional, override chain (default: 8453)");
    console.log("  RPC_URL      Optional, override RPC");
    return;
  }

  const { command, positional, flags } = parseArgs(args);

  try {
    switch (command) {
      case "register":
        await cmdRegister(flags);
        break;
      case "read":
        await cmdRead(positional);
        break;
      case "fee":
        await cmdFee();
        break;
      case "set-metadata":
        await cmdSetMetadata(positional, flags);
        break;
      case "unset-wallet":
        await cmdUnsetWallet(positional);
        break;
      default:
        die(`Unknown command: ${command}. Use: register, read, fee, set-metadata, unset-wallet`);
    }
  } catch (e) {
    if (e instanceof ZeruError) {
      console.error(`\n\u274C ZeruError [${e.code}]: ${e.message}`);
      if (e.details) console.error("  Details:", JSON.stringify(e.details, null, 2));
    } else if (e instanceof Error) {
      console.error(`\n\u274C Error: ${e.message}`);
    }
    process.exit(1);
  }
}

main();
