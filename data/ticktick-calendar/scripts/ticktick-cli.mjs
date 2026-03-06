#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { createTickTickRuntime, parseTickTickEnvFromRuntime } from "../dist/src/index.js";
import {
  DEFAULT_TOKEN_PATH,
  ReauthRequiredError,
  buildTickTickAuthUrl,
  createOAuthState,
  createWebhookReauthNotifierFromEnv,
  exchangeCodeAndPersistToken,
  getAccessTokenWithAutoReauth,
  parseCallbackUrl,
} from "../skill-entry/token-manager.mjs";

const DEFAULT_ENV_PATH = path.resolve(process.cwd(), ".env");

function printUsage() {
  console.log(`TickTick CLI

Usage:
  ticktick-cli <command> [options]

Commands:
  auth-url [--state <value>]
  auth-exchange (--callbackUrl <url> | --code <code>)
  list-projects [--includeClosed]
  list-tasks [--projectId <id>] [--from <iso>] [--to <iso>] [--includeCompleted] [--limit <n>]
  create-task --projectId <id> --title <text> [--content <text>] [--description <text>] [--startDate <iso>] [--dueDate <iso>] [--isAllDay] [--priority <0|1|3|5>] [--tags a,b,c]
  update-task --taskId <id> [--title <text>] [--content <text>] [--description <text>] [--startDate <iso>] [--dueDate <iso>] [--clearStartDate] [--clearDueDate] [--isAllDay <true|false>] [--priority <0|1|3|5>] [--tags a,b,c]
  complete-task --taskId <id> [--completedAt <iso>]

Global options:
  --env <path>         Path to .env (default: ./ .env)
  --tokenPath <path>   Token JSON path (default: ~/.config/ticktick/token.json)
  --help               Show help
`);
}

function parseArgv(argv) {
  const out = {
    command: argv[2],
    flags: new Map(),
    booleans: new Set(),
  };

  for (let i = 3; i < argv.length; i += 1) {
    const part = argv[i];
    if (!part.startsWith("--")) {
      throw new Error(`Unexpected positional argument: ${part}`);
    }

    const key = part.slice(2);
    const next = argv[i + 1];

    if (next === undefined || next.startsWith("--")) {
      out.booleans.add(key);
      continue;
    }

    out.flags.set(key, next);
    i += 1;
  }

  return out;
}

function hasFlag(parsed, key) {
  return parsed.booleans.has(key) || parsed.flags.has(key);
}

function readFlag(parsed, key) {
  return parsed.flags.get(key);
}

function readRequiredFlag(parsed, key) {
  const value = readFlag(parsed, key);
  if (!value) {
    throw new Error(`Missing required option --${key}`);
  }
  return value;
}

function parseBoolean(value, key) {
  if (value === "true") return true;
  if (value === "false") return false;
  throw new Error(`--${key} must be 'true' or 'false'`);
}

function parseNumber(value, key) {
  const n = Number.parseInt(value, 10);
  if (!Number.isFinite(n)) {
    throw new Error(`--${key} must be an integer`);
  }
  return n;
}

function parseTags(value) {
  return value
    .split(",")
    .map((v) => v.trim())
    .filter((v) => v.length > 0);
}

async function loadDotEnv(filePath) {
  try {
    const raw = await fs.readFile(filePath, "utf8");
    for (const line of raw.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const idx = trimmed.indexOf("=");
      if (idx <= 0) continue;
      const key = trimmed.slice(0, idx).trim();
      let value = trimmed.slice(idx + 1).trim();

      if (
        (value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))
      ) {
        value = value.slice(1, -1);
      }

      if (!(key in process.env)) {
        process.env[key] = value;
      }
    }
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return;
    }
    throw error;
  }
}

async function main() {
  const parsed = parseArgv(process.argv);

  if (!parsed.command || parsed.command === "--help" || hasFlag(parsed, "help")) {
    printUsage();
    return;
  }

  const envPath = path.resolve(readFlag(parsed, "env") ?? DEFAULT_ENV_PATH);
  const tokenPath = path.resolve(readFlag(parsed, "tokenPath") ?? process.env.TICKTICK_TOKEN_PATH ?? DEFAULT_TOKEN_PATH);

  await loadDotEnv(envPath);

  const env = parseTickTickEnvFromRuntime();
  const onReauthRequired = createWebhookReauthNotifierFromEnv();

  if (parsed.command === "auth-url") {
    const state = readFlag(parsed, "state") ?? createOAuthState();
    const authUrl = buildTickTickAuthUrl(env, state);
    console.log(JSON.stringify({ state, authUrl, redirectUri: env.redirectUri }, null, 2));
    return;
  }

  if (parsed.command === "auth-exchange") {
    const callbackUrl = readFlag(parsed, "callbackUrl");
    const codeFromFlag = readFlag(parsed, "code");

    let code = codeFromFlag;
    let state;

    if (callbackUrl) {
      const parsedCallback = parseCallbackUrl(callbackUrl);
      if (parsedCallback.error) {
        throw new Error(
          `OAuth callback returned error='${parsedCallback.error}'${
            parsedCallback.errorDescription ? ` description='${parsedCallback.errorDescription}'` : ""
          }`
        );
      }
      code = parsedCallback.code;
      state = parsedCallback.state;
    }

    if (!code) {
      throw new Error("auth-exchange requires --callbackUrl <url> or --code <code>");
    }

    const token = await exchangeCodeAndPersistToken({ code, tokenPath, env });
    console.log(
      JSON.stringify(
        {
          ok: true,
          tokenPath,
          state,
          tokenType: token.tokenType,
          scope: token.scope,
          expiresIn: token.expiresIn,
          hasRefreshToken: typeof token.refreshToken === "string" && token.refreshToken.length > 0,
        },
        null,
        2
      )
    );
    return;
  }

  const runtime = createTickTickRuntime({
    env,
    getAccessToken: async () =>
      getAccessTokenWithAutoReauth({
        tokenPath,
        env,
        onReauthRequired,
      }),
  });

  let result;

  switch (parsed.command) {
    case "list-projects": {
      result = await runtime.useCases.listProjects.execute({
        includeClosed: hasFlag(parsed, "includeClosed") ? true : undefined,
      });
      break;
    }

    case "list-tasks": {
      const limitRaw = readFlag(parsed, "limit");
      result = await runtime.useCases.listTasks.execute({
        projectId: readFlag(parsed, "projectId"),
        from: readFlag(parsed, "from"),
        to: readFlag(parsed, "to"),
        includeCompleted: hasFlag(parsed, "includeCompleted") ? true : undefined,
        limit: limitRaw ? parseNumber(limitRaw, "limit") : undefined,
      });
      break;
    }

    case "create-task": {
      const priorityRaw = readFlag(parsed, "priority");
      const tagsRaw = readFlag(parsed, "tags");
      result = await runtime.useCases.createTask.execute({
        projectId: readRequiredFlag(parsed, "projectId"),
        title: readRequiredFlag(parsed, "title"),
        content: readFlag(parsed, "content"),
        description: readFlag(parsed, "description"),
        startDate: readFlag(parsed, "startDate"),
        dueDate: readFlag(parsed, "dueDate"),
        isAllDay: hasFlag(parsed, "isAllDay") ? true : undefined,
        priority: priorityRaw ? parseNumber(priorityRaw, "priority") : undefined,
        tags: tagsRaw ? parseTags(tagsRaw) : undefined,
      });
      break;
    }

    case "update-task": {
      const priorityRaw = readFlag(parsed, "priority");
      const tagsRaw = readFlag(parsed, "tags");
      const isAllDayRaw = readFlag(parsed, "isAllDay");

      let startDate = readFlag(parsed, "startDate");
      let dueDate = readFlag(parsed, "dueDate");

      if (hasFlag(parsed, "clearStartDate")) {
        startDate = null;
      }
      if (hasFlag(parsed, "clearDueDate")) {
        dueDate = null;
      }

      result = await runtime.useCases.updateTask.execute({
        taskId: readRequiredFlag(parsed, "taskId"),
        title: readFlag(parsed, "title"),
        content: readFlag(parsed, "content"),
        description: readFlag(parsed, "description"),
        startDate,
        dueDate,
        isAllDay: isAllDayRaw ? parseBoolean(isAllDayRaw, "isAllDay") : undefined,
        priority: priorityRaw ? parseNumber(priorityRaw, "priority") : undefined,
        tags: tagsRaw ? parseTags(tagsRaw) : undefined,
      });
      break;
    }

    case "complete-task": {
      result = await runtime.useCases.completeTask.execute({
        taskId: readRequiredFlag(parsed, "taskId"),
        completedAt: readFlag(parsed, "completedAt"),
      });
      break;
    }

    default:
      throw new Error(`Unknown command: ${parsed.command}`);
  }

  console.log(JSON.stringify(result, null, 2));
}

main().catch((error) => {
  if (error instanceof ReauthRequiredError) {
    console.error("[ticktick-cli]", error.message);
    console.error("[ticktick-cli] Reauthorize URL:", error.authUrl);
    console.error("[ticktick-cli] After approval, run:");
    console.error("[ticktick-cli] npm run ticktick:cli -- auth-exchange --callbackUrl '<callback-url>'");
    process.exit(2);
  }

  console.error("[ticktick-cli]", error instanceof Error ? error.message : error);
  process.exit(1);
});
