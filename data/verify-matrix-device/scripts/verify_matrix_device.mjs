#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createInterface } from "node:readline/promises";

const DEFAULT_OPENCLAW_JSON = process.env.OPENCLAW_JSON || path.join(os.homedir(), ".openclaw", "openclaw.json");
const BOOLEAN_FLAGS = new Set(["help", "direct", "access-token", "password", "password-only"]);
const SHORT_FLAG_ALIASES = {
  "-p": "password",
  "-t": "access-token",
};

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const rawFlag = argv[i];
    const flag = SHORT_FLAG_ALIASES[rawFlag] ? `--${SHORT_FLAG_ALIASES[rawFlag]}` : rawFlag;
    if (!flag.startsWith("--")) {
      throw new Error(`Unexpected arg: ${flag}`);
    }
    const flagName = flag.slice(2);
    if (BOOLEAN_FLAGS.has(flagName)) {
      if (flagName === "password-only") {
        args.password = true;
      } else if (flagName === "direct") {
        args["access-token"] = true;
      } else {
        args[flagName] = true;
      }
      continue;
    }
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for ${flag}`);
    }
    args[flagName] = value;
    i += 1;
  }
  return args;
}

function usage() {
  console.log(`Usage:
npm run verify-account
npm run verify-direct
npm run verify-password
node scripts/verify_matrix_device.mjs [--homeserver https://matrix.example.org] [--username alice] [--user-id @alice:example.org] [--device-id ABCDEF1234] [--openclaw-json /path/to/openclaw.json] [--access-token|--direct|-t|--password|-p]

Prompts:
  default mode:
    username (OpenClaw account id, Matrix user id, or unique localpart)
  access-token mode (--access-token, --direct, or -t):
    matrix user ID
    access token (hidden input)
  password mode (--password or -p):
    matrix user ID
    password (hidden input)
    target device ID
  homeserver
  recovery key (hidden input)

Defaults:
  OPENCLAW_JSON=${DEFAULT_OPENCLAW_JSON}
`);
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function extractLocalpart(userId) {
  if (typeof userId !== "string") return "";
  if (userId.startsWith("@")) {
    return userId.split(":")[0].slice(1);
  }
  return userId;
}

function buildResolvedAccount(accountId, account, openclawJsonPath) {
  if (!account?.accessToken || !account?.userId) {
    throw new Error(`Missing channels.matrix.accounts.${accountId}.accessToken/userId in ${openclawJsonPath}`);
  }
  return { accountId, userId: account.userId, targetAccessToken: account.accessToken };
}

function ensureTty(label) {
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    throw new Error(`${label} requires an interactive terminal.`);
  }
}

async function promptText(label, defaultValue) {
  ensureTty(label);
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    const suffix = defaultValue ? ` [${defaultValue}]` : "";
    const answer = (await rl.question(`${label}${suffix}: `)).trim();
    return answer || defaultValue || "";
  } finally {
    rl.close();
  }
}

async function promptRequiredText(label, defaultValue) {
  while (true) {
    const value = await promptText(label, defaultValue);
    if (value) return value;
    console.error(`${label} cannot be empty.`);
  }
}

async function promptSecret(label) {
  ensureTty(label);
  return new Promise((resolve, reject) => {
    const stdin = process.stdin;
    const stdout = process.stdout;
    const previousRawMode = Boolean(stdin.isRaw);
    let value = "";

    const cleanup = () => {
      stdin.removeListener("data", onData);
      stdin.setRawMode(previousRawMode);
      stdout.write("\n");
    };

    const onData = (chunk) => {
      const text = chunk.toString("utf8");
      if (text.startsWith("\u001b")) {
        return;
      }

      for (const ch of text) {
        if (ch === "\r" || ch === "\n") {
          cleanup();
          resolve(value);
          return;
        }
        if (ch === "\u0003") {
          cleanup();
          reject(new Error("Prompt aborted by user."));
          return;
        }
        if (ch === "\u0008" || ch === "\u007f") {
          value = value.slice(0, -1);
          continue;
        }
        if (ch >= " " && ch !== "\u007f") {
          value += ch;
        }
      }
    };

    stdout.write(`${label}: `);
    stdin.resume();
    stdin.setRawMode(true);
    stdin.on("data", onData);
  });
}

async function promptRequiredSecret(label) {
  while (true) {
    const value = await promptSecret(label);
    if (value) return value;
    console.error(`${label} cannot be empty.`);
  }
}

function resolveOpenClawAccount(oc, username, openclawJsonPath) {
  const accounts = oc?.channels?.matrix?.accounts;
  if (!accounts || typeof accounts !== "object") {
    throw new Error(`Missing channels.matrix.accounts in ${openclawJsonPath}`);
  }

  const direct = accounts[username];
  if (direct) {
    return buildResolvedAccount(username, direct, openclawJsonPath);
  }

  const exactMatches = Object.entries(accounts).filter(([, account]) => account?.userId === username);
  if (exactMatches.length === 1) {
    const [accountId, account] = exactMatches[0];
    return buildResolvedAccount(accountId, account, openclawJsonPath);
  }

  if (exactMatches.length > 1) {
    const accountIds = exactMatches.map(([accountId]) => accountId).join(", ");
    throw new Error(`Username "${username}" matches multiple Matrix user ids in ${openclawJsonPath}: ${accountIds}. Use the OpenClaw account id.`);
  }

  const localpart = extractLocalpart(username);
  const localpartMatches = Object.entries(accounts).filter(([, account]) => extractLocalpart(account?.userId) === localpart);
  if (localpartMatches.length === 1) {
    const [accountId, account] = localpartMatches[0];
    return buildResolvedAccount(accountId, account, openclawJsonPath);
  }

  if (localpartMatches.length > 1) {
    const accountIds = localpartMatches.map(([accountId]) => accountId).join(", ");
    throw new Error(`Username "${username}" is ambiguous in ${openclawJsonPath}; matches: ${accountIds}. Use the OpenClaw account id or full Matrix user id.`);
  }

  throw new Error(`No OpenClaw Matrix account matched "${username}" in ${openclawJsonPath}`);
}

async function runVerify({ homeserver, userId, targetAccessToken, password, targetDeviceId, recoveryKey }) {
  const mod = await import("./verify_matrix_device_sdk.mjs");
  if (password) {
    return mod.verifyDeviceByPassword({ homeserver, userId, password, targetDeviceId, recoveryKey });
  }
  return mod.verifyActiveDevice({ homeserver, userId, targetAccessToken, recoveryKey });
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    usage();
    return;
  }

  const homeserver = await promptRequiredText("Homeserver URL", args.homeserver);
  let account;

  if (args["access-token"]) {
    const userId = await promptRequiredText("Matrix user ID", args["user-id"] || args.username);
    const targetAccessToken = await promptRequiredSecret("Access token (hidden)");
    account = { accountId: null, userId, targetAccessToken };
    console.log(`[+] Access-token mode target: ${account.userId}`);
  } else if (args.password) {
    const userId = await promptRequiredText("Matrix user ID", args["user-id"] || args.username);
    const password = await promptRequiredSecret("Password (hidden)");
    const targetDeviceId = await promptRequiredText("Target device ID", args["device-id"]);
    account = { accountId: null, userId, password, targetDeviceId };
    console.log(`[+] Password mode target: ${account.userId} / ${account.targetDeviceId}`);
  } else {
    const openclawJsonPath = args["openclaw-json"] || DEFAULT_OPENCLAW_JSON;
    if (!fs.existsSync(openclawJsonPath)) {
      throw new Error(`OpenClaw config not found at ${openclawJsonPath}. Use --access-token or --password to test without openclaw.json.`);
    }
    const oc = readJson(openclawJsonPath);
    const username = await promptRequiredText("Username", args.username);
    account = resolveOpenClawAccount(oc, username, openclawJsonPath);
    console.log(`[+] OpenClaw account: ${account.accountId} (${account.userId})`);
  }

  const recoveryKey = await promptRequiredSecret("Recovery key (hidden)");

  await runVerify({
    homeserver,
    userId: account.userId,
    targetAccessToken: account.targetAccessToken,
    password: account.password,
    targetDeviceId: account.targetDeviceId,
    recoveryKey,
  });
}

main().catch((e) => {
  console.error(e?.stack || String(e));
  process.exit(1);
});
