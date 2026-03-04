#!/usr/bin/env node
require("dotenv").config();

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawn, spawnSync } = require("node:child_process");
const readline = require("node:readline/promises");
const { stdin: input, stdout: output } = require("node:process");
const { Keypair } = require("@solana/web3.js");

const { parseArgs } = require("./common");

const SKILL_DIR = path.join(__dirname, "..");
const ENV_PATH = path.join(SKILL_DIR, ".env");
const STRATEGY_DIR = path.join(SKILL_DIR, "state", "strategies");

function usage() {
  console.log(`Usage:
  node scripts/onboard.js
  node scripts/onboard.js --wallet-path ~/.config/solana/id.json --market-id 1 --margin 1000000
  node scripts/onboard.js --strategy-file ./state/strategies/my-strategy.txt --market-id 1 --margin 1000000

Options:
  --wallet-path <path>          Optional preferred wallet path
  --strategy-file <path>        Optional existing strategy prompt file
  --market-id <u64>             Optional (prompted if missing)
  --margin <u64>                Optional (prompted if missing)
  --type <market|limit>         Optional, default: market
  --price <u64>                 Required when --type limit
  --ttl <i64>                   Optional, default: 300
  --deposit <u64>               Optional collateral deposit before order
  --reduce-only                 Optional flag
  --min-confidence <0..1>       Optional, default: 0.75
  --cooldown-ms <ms>            Optional, default: 15000
  --max-orders <n>              Optional, default: 0 (unlimited)
  --channel <name>              Optional, default: agent.signals
  --agent-name <name>           Optional signal source filter
  --dry-run                     Optional, do not place real orders
`);
}

function expandHome(rawPath) {
  const value = String(rawPath || "").trim();
  if (!value) {
    return "";
  }
  if (value === "~") {
    return os.homedir();
  }
  if (value.startsWith("~/")) {
    return path.join(os.homedir(), value.slice(2));
  }
  return value;
}

function fileExists(target) {
  try {
    return fs.existsSync(target);
  } catch (_error) {
    return false;
  }
}

function parseWalletFile(walletPath) {
  const absolutePath = path.resolve(expandHome(walletPath));
  if (!fileExists(absolutePath)) {
    throw new Error("wallet file not found");
  }
  const raw = fs.readFileSync(absolutePath, "utf8");
  const decoded = JSON.parse(raw);
  if (!Array.isArray(decoded)) {
    throw new Error("wallet file must be a JSON array");
  }
  const secret = Uint8Array.from(decoded);
  const keypair = Keypair.fromSecretKey(secret);
  return {
    walletPath: absolutePath,
    walletAddress: keypair.publicKey.toBase58()
  };
}

function parseSolanaConfigWalletPath() {
  const result = spawnSync("solana", ["config", "get"], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });
  if (result.status !== 0) {
    return "";
  }
  const outputText = `${result.stdout || ""}\n${result.stderr || ""}`;
  const matched = outputText.match(/Keypair Path:\s*(.+)/i);
  if (!matched) {
    return "";
  }
  return String(matched[1] || "").trim();
}

function discoverWalletPaths(args) {
  const candidates = [];
  if (args["wallet-path"]) {
    candidates.push(String(args["wallet-path"]));
  }
  if (process.env.KEYPAIR_PATH) {
    candidates.push(process.env.KEYPAIR_PATH);
  }
  if (process.env.ANCHOR_WALLET) {
    candidates.push(process.env.ANCHOR_WALLET);
  }
  candidates.push("~/.config/solana/id.json");
  const solanaConfigPath = parseSolanaConfigWalletPath();
  if (solanaConfigPath) {
    candidates.push(solanaConfigPath);
  }

  const deduped = [];
  const seen = new Set();
  for (const rawPath of candidates) {
    const absolute = path.resolve(expandHome(rawPath));
    if (!absolute || seen.has(absolute)) {
      continue;
    }
    seen.add(absolute);
    deduped.push(absolute);
  }
  return deduped;
}

function evaluateWalletPaths(paths) {
  const available = [];
  const rejected = [];
  for (const walletPath of paths) {
    try {
      const parsed = parseWalletFile(walletPath);
      available.push(parsed);
    } catch (error) {
      rejected.push({
        walletPath,
        reason: error instanceof Error ? error.message : String(error)
      });
    }
  }
  return { available, rejected };
}

async function ask(rl, promptText, fallback = "") {
  const answer = await rl.question(promptText);
  const trimmed = String(answer || "").trim();
  if (!trimmed && fallback) {
    return fallback;
  }
  return trimmed;
}

async function askYesNo(rl, promptText, defaultYes) {
  const suffix = defaultYes ? " [Y/n] " : " [y/N] ";
  const answer = await ask(rl, `${promptText}${suffix}`);
  if (!answer) {
    return defaultYes;
  }
  const normalized = answer.toLowerCase();
  if (["y", "yes", "1", "true"].includes(normalized)) {
    return true;
  }
  if (["n", "no", "0", "false"].includes(normalized)) {
    return false;
  }
  return defaultYes;
}

async function chooseWallet(rl, args) {
  const discovered = discoverWalletPaths(args);
  const { available, rejected } = evaluateWalletPaths(discovered);

  if (available.length > 0) {
    console.log("[onboarding] available wallets:");
    for (let i = 0; i < available.length; i += 1) {
      const entry = available[i];
      console.log(`  ${i + 1}. ${entry.walletAddress} (${entry.walletPath})`);
    }
    if (rejected.length > 0) {
      console.log("[onboarding] skipped invalid wallet paths:");
      for (const item of rejected) {
        console.log(`  - ${item.walletPath}: ${item.reason}`);
      }
    }

    const userInput = await ask(
      rl,
      "Select wallet number or enter a custom wallet path (default: 1): ",
      "1"
    );
    const index = Number(userInput);
    if (Number.isInteger(index) && index >= 1 && index <= available.length) {
      return available[index - 1];
    }
    try {
      return parseWalletFile(userInput);
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      throw new Error(`invalid wallet selection: ${detail}`);
    }
  }

  console.log("[onboarding] no readable wallets were discovered automatically.");
  while (true) {
    const walletPath = await ask(rl, "Enter wallet keypair path: ");
    if (!walletPath) {
      continue;
    }
    try {
      return parseWalletFile(walletPath);
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      console.log(`[warn] ${detail}`);
    }
  }
}

function upsertEnvValue(source, key, value) {
  const pattern = new RegExp(`^${key}=.*$`, "m");
  const line = `${key}=${value}`;
  if (pattern.test(source)) {
    return source.replace(pattern, line);
  }
  if (!source.endsWith("\n") && source.length > 0) {
    return `${source}\n${line}\n`;
  }
  return `${source}${line}\n`;
}

function persistWalletSelection(walletPath) {
  let source = "";
  if (fileExists(ENV_PATH)) {
    source = fs.readFileSync(ENV_PATH, "utf8");
  }
  source = upsertEnvValue(source, "KEYPAIR_PATH", walletPath);
  source = upsertEnvValue(source, "ANCHOR_WALLET", walletPath);
  fs.writeFileSync(ENV_PATH, source);
}

async function waitForRegistration(rl, walletAddress) {
  console.log("[action] register this wallet address on the platform:");
  console.log(`  ${walletAddress}`);
  console.log("[action] when registration is done, type 'done'. Type 'quit' to stop.");

  while (true) {
    const answer = (await ask(rl, "registration status > ")).toLowerCase();
    if (!answer) {
      continue;
    }
    if (["done", "d", "complete", "completed"].includes(answer)) {
      return;
    }
    if (["quit", "q", "stop", "cancel"].includes(answer)) {
      throw new Error("onboarding canceled by user before registration confirmation");
    }
    console.log("[info] waiting for explicit confirmation. Type 'done' when ready.");
  }
}

async function captureStrategyPrompt(rl, args) {
  if (args["strategy-file"]) {
    const absolutePath = path.resolve(expandHome(args["strategy-file"]));
    if (!fileExists(absolutePath)) {
      throw new Error(`strategy file not found: ${absolutePath}`);
    }
    const promptText = fs.readFileSync(absolutePath, "utf8").trim();
    if (!promptText) {
      throw new Error(`strategy file is empty: ${absolutePath}`);
    }
    return {
      promptText,
      originalPath: absolutePath
    };
  }

  console.log("[strategy] enter the strategy prompt.");
  console.log("[strategy] submit an empty line to finish.");

  const lines = [];
  while (true) {
    const prefix = lines.length === 0 ? "strategy > " : "          ";
    const line = await rl.question(prefix);
    const trimmed = String(line || "");
    if (trimmed.trim() === "") {
      if (lines.length === 0) {
        continue;
      }
      break;
    }
    lines.push(trimmed);
  }

  return {
    promptText: lines.join("\n"),
    originalPath: ""
  };
}

function timestampSlug() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function saveStrategyPrompt(strategyPrompt, walletAddress, walletPath) {
  fs.mkdirSync(STRATEGY_DIR, { recursive: true });
  const slug = timestampSlug();
  const txtPath = path.join(STRATEGY_DIR, `${slug}-strategy.txt`);
  const metaPath = path.join(STRATEGY_DIR, `${slug}-strategy.json`);

  fs.writeFileSync(txtPath, `${strategyPrompt.trim()}\n`);
  fs.writeFileSync(
    metaPath,
    `${JSON.stringify(
      {
        created_at: new Date().toISOString(),
        wallet_address: walletAddress,
        wallet_path: walletPath,
        strategy_file: txtPath
      },
      null,
      2
    )}\n`
  );

  return {
    txtPath,
    metaPath
  };
}

function isUnsignedIntegerText(value) {
  return /^\d+$/.test(String(value || "").trim());
}

async function askUnsignedInteger(rl, label, initialValue, fallback = "") {
  let candidate = String(initialValue || "").trim() || fallback;
  while (true) {
    if (candidate && isUnsignedIntegerText(candidate)) {
      return candidate;
    }
    candidate = await ask(rl, `${label}: `, fallback);
  }
}

function parseMaybeFloat(raw, fallback) {
  const value = String(raw || "").trim();
  if (!value) {
    return fallback;
  }
  const number = Number(value);
  if (!Number.isFinite(number)) {
    throw new Error(`invalid numeric value: ${raw}`);
  }
  return number;
}

function parseMaybeInt(raw, fallback) {
  const value = String(raw || "").trim();
  if (!value) {
    return fallback;
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(`invalid integer value: ${raw}`);
  }
  return Math.floor(parsed);
}

function parseBool(raw) {
  if (raw === true) {
    return true;
  }
  if (raw === undefined || raw === null || raw === false) {
    return false;
  }
  const normalized = String(raw).trim().toLowerCase();
  return ["1", "true", "yes", "y"].includes(normalized);
}

async function collectTradeConfig(rl, args) {
  const marketId = await askUnsignedInteger(rl, "market id", args["market-id"]);
  const margin = await askUnsignedInteger(rl, "margin (raw USDC units)", args.margin);

  let orderType = String(args.type || "market").trim().toLowerCase();
  if (orderType !== "market" && orderType !== "limit") {
    orderType = "";
  }
  while (!orderType) {
    const selected = (await ask(rl, "order type (market/limit) [market]: ", "market"))
      .toLowerCase()
      .trim();
    if (selected === "market" || selected === "limit") {
      orderType = selected;
    }
  }

  let price = String(args.price || "").trim();
  if (orderType === "limit") {
    price = await askUnsignedInteger(rl, "limit price (raw price units)", price);
  }

  const ttl = String(parseMaybeInt(args.ttl, 300));
  const deposit = String(args.deposit || "").trim();
  if (deposit && !isUnsignedIntegerText(deposit)) {
    throw new Error("--deposit must be an unsigned integer");
  }

  const minConfidence = parseMaybeFloat(args["min-confidence"], 0.75);
  const cooldownMs = parseMaybeInt(args["cooldown-ms"], 15000);
  const maxOrders = parseMaybeInt(args["max-orders"], 0);
  const channel = String(args.channel || "agent.signals").trim() || "agent.signals";
  const agentName = String(args["agent-name"] || "").trim();
  let dryRun = parseBool(args["dry-run"]);
  if (args["dry-run"] === undefined) {
    const executeRealOrders = await askYesNo(
      rl,
      "Execute real orders immediately?",
      false
    );
    dryRun = !executeRealOrders;
  }

  return {
    marketId,
    margin,
    orderType,
    price,
    ttl,
    deposit,
    reduceOnly: parseBool(args["reduce-only"]),
    minConfidence,
    cooldownMs,
    maxOrders,
    channel,
    agentName,
    dryRun
  };
}

function buildAutotradeArgs(config, strategyFilePath) {
  const out = [
    path.join(__dirname, "realtime-agent.js"),
    "--market-id",
    config.marketId,
    "--margin",
    config.margin,
    "--type",
    config.orderType,
    "--ttl",
    config.ttl,
    "--min-confidence",
    String(config.minConfidence),
    "--cooldown-ms",
    String(config.cooldownMs),
    "--max-orders",
    String(config.maxOrders),
    "--channel",
    config.channel,
    "--strategy-file",
    strategyFilePath
  ];

  if (config.orderType === "limit") {
    out.push("--price", config.price);
  }
  if (config.deposit) {
    out.push("--deposit", config.deposit);
  }
  if (config.reduceOnly) {
    out.push("--reduce-only");
  }
  if (config.agentName) {
    out.push("--agent-name", config.agentName);
  }
  if (config.dryRun) {
    out.push("--dry-run");
  }

  return out;
}

async function runAutotrade(args, walletPath) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, args, {
      cwd: SKILL_DIR,
      stdio: "inherit",
      env: {
        ...process.env,
        KEYPAIR_PATH: walletPath,
        ANCHOR_WALLET: walletPath
      }
    });

    child.on("error", (error) => {
      reject(error);
    });
    child.on("close", (code) => {
      if (code === 0) {
        resolve();
        return;
      }
      reject(new Error(`autotrade exited with code=${code}`));
    });
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || args.h) {
    usage();
    return;
  }

  const rl = readline.createInterface({ input, output });
  try {
    const wallet = await chooseWallet(rl, args);
    persistWalletSelection(wallet.walletPath);
    process.env.KEYPAIR_PATH = wallet.walletPath;
    process.env.ANCHOR_WALLET = wallet.walletPath;

    console.log(`[onboarding] selected wallet: ${wallet.walletAddress}`);
    console.log(`[onboarding] wallet path: ${wallet.walletPath}`);
    await waitForRegistration(rl, wallet.walletAddress);

    const strategy = await captureStrategyPrompt(rl, args);
    const saved =
      strategy.originalPath.length > 0
        ? {
            txtPath: strategy.originalPath,
            metaPath: ""
          }
        : saveStrategyPrompt(strategy.promptText, wallet.walletAddress, wallet.walletPath);
    if (!strategy.originalPath) {
      console.log(`[onboarding] strategy saved: ${saved.txtPath}`);
      console.log(`[onboarding] metadata saved: ${saved.metaPath}`);
    } else {
      console.log(`[onboarding] strategy loaded: ${saved.txtPath}`);
    }

    const tradeConfig = await collectTradeConfig(rl, args);
    console.log("[summary] trading configuration:");
    console.log(`  wallet: ${wallet.walletAddress}`);
    console.log(`  market_id: ${tradeConfig.marketId}`);
    console.log(`  margin: ${tradeConfig.margin}`);
    console.log(`  type: ${tradeConfig.orderType}`);
    if (tradeConfig.orderType === "limit") {
      console.log(`  price: ${tradeConfig.price}`);
    }
    console.log(`  min_confidence: ${tradeConfig.minConfidence}`);
    console.log(`  cooldown_ms: ${tradeConfig.cooldownMs}`);
    console.log(`  dry_run: ${tradeConfig.dryRun}`);
    console.log(`  strategy_file: ${saved.txtPath}`);

    const confirmed = await askYesNo(rl, "Start trading with this strategy now?", false);
    if (!confirmed) {
      console.log("[onboarding] canceled before trading start.");
      return;
    }

    const autotradeArgs = buildAutotradeArgs(tradeConfig, saved.txtPath);
    console.log("[onboarding] starting realtime trading agent...");
    await runAutotrade(autotradeArgs, wallet.walletPath);
  } finally {
    rl.close();
  }
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[error] ${message}`);
  process.exit(1);
});
