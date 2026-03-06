#!/usr/bin/env node

/**
 * telegram-topics.js — Create forum topics in Telegram DM or supergroup
 *
 * Uses the Telegram Bot API `createForumTopic` to automatically create
 * forum topics. Works with both DM (thread mode enabled) and supergroups
 * (bot must be admin with can_manage_topics).
 *
 * Usage:
 *   node telegram-topics.js --token BOT_TOKEN --chat CHAT_ID --name "Operations"
 *   node telegram-topics.js --config ~/.openclaw/openclaw.json --chat CHAT_ID --names "Brand1,Brand2,Operations"
 *
 * Output: JSON mapping of topic names to thread IDs
 *   { "Operations": 7, "Brand1": 3, "Brand2": 4 }
 *
 * Security note: Prefer --config over --token to avoid exposing the token in
 * process listings (ps aux).
 */

const https = require("https");
const fs = require("fs");
const path = require("path");

// ── Constants ────────────────────────────────────────────────────────

const RATE_LIMIT_DELAY_MS = 300;

// ── Argument Parsing ─────────────────────────────────────────────────

function parseArgs(argv) {
  const args = {
    token: null,
    config: null,
    chat: null,
    names: [],
  };

  for (let i = 2; i < argv.length; i++) {
    switch (argv[i]) {
      case "--token":
        args.token = argv[++i];
        break;
      case "--config":
        args.config = argv[++i];
        break;
      case "--chat":
        args.chat = argv[++i];
        break;
      case "--name":
        args.names.push(argv[++i]);
        break;
      case "--names":
        args.names.push(...argv[++i].split(",").map((n) => n.trim()));
        break;
      case "-h":
      case "--help":
        printUsage();
        process.exit(0);
      default:
        console.error(`[ERROR] Unknown option: ${argv[i]}`);
        process.exit(1);
    }
  }

  return args;
}

function printUsage() {
  console.log(`Usage: telegram-topics.js [OPTIONS]

Options:
  --token TOKEN        Bot token (or use --config to read from openclaw.json)
  --config PATH        Path to openclaw.json (reads botToken automatically)
  --chat CHAT_ID       Chat ID (user ID for DM, or supergroup chat ID)
  --name NAME          Create a single topic with this name
  --names NAME1,NAME2  Create multiple topics (comma-separated)
  -h, --help           Show this help

Output:
  JSON object mapping topic names to thread IDs
  Example: { "Operations": 7, "Brand1": 3 }

Prerequisites:
  DM mode:    Bot's Thread Mode must be enabled (via BotFather MiniApp)
  Group mode: Bot must be admin with can_manage_topics permission`);
}

// ── Token Resolution ─────────────────────────────────────────────────

function resolveToken(args) {
  if (args.token) return args.token;

  if (args.config) {
    try {
      const configPath = args.config.startsWith("~")
        ? path.join(process.env.HOME, args.config.slice(1))
        : args.config;
      const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
      const token =
        config?.channels?.telegram?.botToken ||
        config?.channels?.telegram?.credentials?.botToken;
      if (token) return token;
      console.error(
        "[ERROR] No botToken found in config at channels.telegram.botToken"
      );
      process.exit(1);
    } catch (err) {
      console.error(`[ERROR] Failed to read config: ${err.message}`);
      process.exit(1);
    }
  }

  console.error("[ERROR] Either --token or --config is required");
  process.exit(1);
}

// ── Telegram API ─────────────────────────────────────────────────────

function callTelegramAPI(token, method, params) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(params);
    const options = {
      hostname: "api.telegram.org",
      port: 443,
      path: `/bot${token}/${method}`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(payload),
      },
    };

    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed);
        } catch {
          reject(new Error(`Invalid JSON response: ${data}`));
        }
      });
    });

    req.setTimeout(15000, () => {
      req.destroy();
      reject(new Error("Telegram API request timed out"));
    });

    req.on("error", reject);
    req.write(payload);
    req.end();
  });
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function createForumTopic(token, chatId, name, retries = 2) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const result = await callTelegramAPI(token, "createForumTopic", {
        chat_id: chatId,
        name: name,
      });

      if (result.ok) {
        return result.result;
      }

      // Handle specific errors with guidance
      const desc = result.description || "";

      if (desc.includes("PEER_ID_INVALID") || desc.includes("chat not found")) {
        console.error(`[ERROR] Chat ID ${chatId} is invalid or bot cannot access it.`);
        console.error(
          "  - For DM: Make sure you've sent at least one message to the bot"
        );
        console.error(
          "  - For groups: Make sure the bot is a member of the group"
        );
        process.exit(1);
      }

      if (
        desc.includes("not enough rights") ||
        desc.includes("CHAT_ADMIN_REQUIRED")
      ) {
        console.error(
          `[ERROR] Bot lacks permission to create topics in chat ${chatId}.`
        );
        console.error(
          "  - For groups: Make the bot an admin with 'Manage Topics' permission"
        );
        console.error(
          "  - For DM: Enable Thread Mode via BotFather MiniApp:"
        );
        console.error("    1. Open Telegram, find @BotFather");
        console.error(
          "    2. Tap 'Open' (bottom-left) to open the BotFather MiniApp"
        );
        console.error("    3. Select your bot");
        console.error("    4. Go to Bot Settings → Thread Mode → Enable");
        process.exit(1);
      }

      if (desc.includes("FORUM_NOT_ENABLED") || desc.includes("topics must be enabled")) {
        console.error(`[ERROR] Forum/topics mode is not enabled for chat ${chatId}.`);
        console.error("  - For DM: Enable Thread Mode via BotFather MiniApp:");
        console.error("    1. Open Telegram, find @BotFather");
        console.error("    2. Tap 'Open' (bottom-left) to open the BotFather MiniApp");
        console.error("    3. Select your bot → Bot Settings → Thread Mode → Enable");
        console.error("  - For groups: Enable Topics in group settings");
        process.exit(1);
      }

      // Handle rate limiting
      if (result.error_code === 429) {
        const retryAfter = result.parameters?.retry_after || 5;
        console.error(
          `[WARN] Rate limited. Waiting ${retryAfter}s before retrying...`
        );
        await sleep(retryAfter * 1000);
        continue;
      }

      // Other retryable error
      if (attempt < retries) {
        const delay = (attempt + 1) * 1000;
        console.error(
          `[WARN] Attempt ${attempt + 1} failed: ${desc}. Retrying in ${delay}ms...`
        );
        await sleep(delay);
        continue;
      }

      console.error(`[ERROR] Failed to create topic "${name}": ${desc}`);
      process.exit(1);
    } catch (err) {
      if (attempt < retries) {
        const delay = (attempt + 1) * 1000;
        console.error(
          `[WARN] Network error: ${err.message}. Retrying in ${delay}ms...`
        );
        await sleep(delay);
        continue;
      }
      console.error(`[ERROR] Network error creating topic "${name}": ${err.message}`);
      process.exit(1);
    }
  }
}

// ── Main ─────────────────────────────────────────────────────────────

async function main() {
  const args = parseArgs(process.argv);

  if (args.names.length === 0) {
    console.error("[ERROR] At least one --name or --names is required");
    process.exit(1);
  }

  if (!args.chat) {
    console.error("[ERROR] --chat is required");
    process.exit(1);
  }

  const token = resolveToken(args);
  const chatId = args.chat;
  const result = {};

  for (let i = 0; i < args.names.length; i++) {
    const name = args.names[i];

    // Rate-limit delay between API calls (skip before first call)
    if (i > 0) {
      await sleep(RATE_LIMIT_DELAY_MS);
    }

    const topic = await createForumTopic(token, chatId, name);
    if (topic) {
      result[name] = topic.message_thread_id;
      console.error(`[OK] Created topic "${name}" → thread ID ${topic.message_thread_id}`);
    } else {
      console.error(`[SKIP] Topic "${name}" — could not create`);
    }
  }

  // Output the result as JSON to stdout
  console.log(JSON.stringify(result, null, 2));
}

main();
