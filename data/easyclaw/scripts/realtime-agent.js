#!/usr/bin/env node
require("dotenv").config();

const fs = require("node:fs");
const path = require("node:path");
const { spawn } = require("node:child_process");
const WebSocket = require("ws");

const {
  deriveUserMarginPda,
  parseArgs,
  programIdsFromEnv,
  readSigner
} = require("./common");
const { apiRequest, wsUrl } = require("./backend-common");

function usage() {
  console.log(`Usage:
  node scripts/realtime-agent.js --market-id 1 --margin 1000000
  node scripts/realtime-agent.js --market-id 1 --margin 1000000 --min-confidence 0.75 --agent-name "Alpha Momentum"
  node scripts/realtime-agent.js --market-id 1 --margin 1000000 --strategy-file ./state/strategies/strategy.txt

Options:
  --market-id <u64>                   Required
  --margin <u64>                      Required order margin
  --type <market|limit>               Default: market
  --price <u64>                       Optional fixed price for limit orders
  --ttl <i64>                         Default: 300
  --deposit <u64>                     Optional collateral deposit before order
  --reduce-only                       Optional flag
  --min-confidence <0..1>             Default: 0.7
  --agent-name <name>                 Optional signal agent filter
  --cooldown-ms <ms>                  Default: 15000
  --max-orders <n>                    Default: 0 (unlimited)
  --channel <name>                    Default: agent.signals
  --strategy <text>                   Optional strategy prompt text
  --strategy-file <path>              Optional strategy prompt file
  --reconnect-base-delay-ms <ms>      Default: 1000
  --reconnect-max-delay-ms <ms>       Default: 30000
  --max-reconnect-attempts <n>        Default: 0 (unlimited)
  --dry-run                           Do not place real orders
`);
}

function toBool(value) {
  if (value === true) return true;
  if (typeof value !== "string") return false;
  const normalized = value.trim().toLowerCase();
  return normalized === "1" || normalized === "true" || normalized === "yes";
}

function toNumber(value, fallback) {
  if (value === undefined || value === null || String(value).trim() === "") {
    return fallback;
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(`Invalid numeric value: ${value}`);
  }
  return parsed;
}

function toInt(value, fallback) {
  if (value === undefined || value === null || String(value).trim() === "") {
    return fallback;
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(`Invalid integer value: ${value}`);
  }
  return Math.floor(parsed);
}

function normalizeSignalSide(side) {
  const normalized = String(side || "").trim().toLowerCase();
  if (normalized === "long" || normalized === "buy" || normalized === "bid") {
    return "buy";
  }
  if (normalized === "short" || normalized === "sell" || normalized === "ask") {
    return "sell";
  }
  return "";
}

function signalItemsFromEnvelope(envelope) {
  if (!envelope || envelope.type !== "event") {
    return [];
  }

  const data = envelope.data;
  if (!data) {
    return [];
  }
  if (Array.isArray(data)) {
    return data;
  }
  if (typeof data === "object") {
    if (Array.isArray(data.items)) {
      return data.items;
    }
    if (data.agent_name || data.side) {
      return [data];
    }
  }
  return [];
}

function normalizeInlineText(value) {
  return String(value || "")
    .replace(/\s+/g, " ")
    .trim();
}

function compactStrategySummary(strategyPrompt) {
  const normalized = normalizeInlineText(strategyPrompt);
  if (!normalized) {
    return "(none)";
  }
  if (normalized.length <= 120) {
    return normalized;
  }
  return `${normalized.slice(0, 117)}...`;
}

function readStrategyPrompt(args) {
  const filePath = String(args["strategy-file"] || "").trim();
  if (filePath) {
    const absolutePath = path.resolve(filePath);
    if (!fs.existsSync(absolutePath)) {
      throw new Error(`strategy file not found: ${absolutePath}`);
    }
    const fileText = fs.readFileSync(absolutePath, "utf8").trim();
    return {
      strategyPrompt: fileText,
      strategySource: absolutePath
    };
  }

  const inline = String(args.strategy || "").trim();
  return {
    strategyPrompt: inline,
    strategySource: inline ? "inline" : ""
  };
}

function buildDecisionReason(signal, strategyPrompt) {
  const details = [];

  const explicitReason = normalizeInlineText(
    signal.reason || signal.rationale || signal.thesis || signal.note || signal.comment || ""
  );
  if (explicitReason) {
    details.push(explicitReason);
  }

  const signalPrice = String(signal.price || "").trim();
  if (signalPrice) {
    details.push(`signal_price=${signalPrice}`);
  }

  const strategySnippet = compactStrategySummary(strategyPrompt);
  if (strategySnippet !== "(none)") {
    details.push(`strategy="${strategySnippet}"`);
  }

  if (details.length === 0) {
    return "signal side/confidence matched filters";
  }
  return details.join("; ");
}

async function executeOrder(orderArgs) {
  const scriptPath = path.join(__dirname, "order-execute.js");
  const args = [scriptPath, ...orderArgs];

  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, args, {
      cwd: path.join(__dirname, ".."),
      stdio: ["ignore", "pipe", "pipe"]
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += String(chunk);
    });
    child.stderr.on("data", (chunk) => {
      stderr += String(chunk);
    });

    child.on("error", (error) => {
      reject(error);
    });

    child.on("close", (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
        return;
      }
      reject(new Error(`order-execute exited with code=${code} stderr=${stderr.trim()}`));
    });
  });
}

function buildOrderArgs(config, side) {
  const out = [
    "--market-id",
    config.marketId,
    "--side",
    side,
    "--type",
    config.orderType,
    "--margin",
    config.margin,
    "--ttl",
    config.ttl
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

  return out;
}

function bigintFromText(raw) {
  const value = String(raw || "").trim();
  if (!/^-?\d+$/.test(value)) {
    return 0n;
  }
  return BigInt(value);
}

function summarizePositionItem(position) {
  const longQty = bigintFromText(position.long_qty);
  const shortQty = bigintFromText(position.short_qty);
  const longNotional = bigintFromText(position.long_entry_notional);
  const shortNotional = bigintFromText(position.short_entry_notional);
  const marketID = String(position.market_id || "").trim() || "?";

  return `market=${marketID} long_qty=${longQty.toString()} short_qty=${shortQty.toString()} long_notional=${longNotional.toString()} short_notional=${shortNotional.toString()}`;
}

async function printPositionSnapshot(userMargin) {
  try {
    const [positions, history] = await Promise.all([
      apiRequest("/api/v1/positions", {
        query: {
          user_margin: userMargin,
          limit: 20,
          offset: 0
        }
      }),
      apiRequest("/api/v1/position-history", {
        query: {
          user_margin: userMargin,
          limit: 5,
          offset: 0
        }
      })
    ]);

    const positionItems = Array.isArray(positions?.items) ? positions.items : [];
    const historyItems = Array.isArray(history?.items) ? history.items : [];
    const activePositions = positionItems.filter((item) => {
      return bigintFromText(item.long_qty) > 0n || bigintFromText(item.short_qty) > 0n;
    });

    console.log(
      `[state] positions_total=${positionItems.length} positions_active=${activePositions.length} recent_history=${historyItems.length} user_margin=${userMargin}`
    );
    for (const position of activePositions.slice(0, 3)) {
      console.log(`[state] ${summarizePositionItem(position)}`);
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.log(`[warn] snapshot fetch failed: ${message}`);
  }
}

function createRuntimeState() {
  return {
    seenSignals: new Set(),
    lastExecutionAt: 0,
    activeOrder: Promise.resolve(),
    placedOrders: 0,
    reconnectAttempts: 0,
    reconnectTimer: null,
    socket: null,
    stopRequested: false,
    stopReason: "",
    maxOrders: 0,
    maybeFinalize: null
  };
}

function requestStop(state, reason) {
  if (state.stopRequested) {
    return;
  }
  state.stopRequested = true;
  state.stopReason = reason;

  if (state.reconnectTimer) {
    clearTimeout(state.reconnectTimer);
    state.reconnectTimer = null;
  }

  if (state.socket) {
    try {
      const safeReason = String(reason || "stop").slice(0, 120);
      if (
        state.socket.readyState === WebSocket.OPEN ||
        state.socket.readyState === WebSocket.CONNECTING
      ) {
        state.socket.close(1000, safeReason);
      }
    } catch (_ignored) {
    }
  }

  if (typeof state.maybeFinalize === "function") {
    state.maybeFinalize();
  }
}

function scheduleReconnect(state, config, connect) {
  if (state.stopRequested) {
    return;
  }

  const nextAttempt = state.reconnectAttempts + 1;
  if (config.maxReconnectAttempts > 0 && nextAttempt > config.maxReconnectAttempts) {
    console.error("[error] maximum websocket reconnect attempts reached");
    process.exitCode = 1;
    requestStop(state, "max reconnect attempts reached");
    return;
  }

  state.reconnectAttempts = nextAttempt;
  const backoff = Math.min(
    config.reconnectMaxDelayMs,
    config.reconnectBaseDelayMs * (2 ** (nextAttempt - 1))
  );

  console.log(
    `[warn] websocket reconnect scheduled in ${backoff}ms (attempt=${nextAttempt})`
  );

  state.reconnectTimer = setTimeout(() => {
    state.reconnectTimer = null;
    connect();
  }, backoff);
}

function enqueueSignalExecution(signal, side, confidence, ts, config, state, userMargin) {
  const signalAgent = String(signal.agent_name || "").trim() || "unknown-agent";
  const dedupeKey = `${signalAgent}:${side}:${ts}`;
  if (state.seenSignals.has(dedupeKey)) {
    return;
  }
  state.seenSignals.add(dedupeKey);

  state.activeOrder = state.activeOrder
    .then(async () => {
      if (state.stopRequested) {
        return;
      }

      const nowMs = Date.now();
      if (config.cooldownMs > 0 && nowMs - state.lastExecutionAt < config.cooldownMs) {
        return;
      }
      if (config.maxOrders > 0 && state.placedOrders >= config.maxOrders) {
        requestStop(state, "max orders reached");
        return;
      }

      const orderArgs = buildOrderArgs(config, side);
      const reason = buildDecisionReason(signal, config.strategyPrompt);
      console.log(
        `[decision] agent=${signalAgent} side=${side} confidence=${confidence.toFixed(4)} ts=${ts} reason=${JSON.stringify(reason)}`
      );

      if (config.dryRun) {
        console.log(`[dry-run] node scripts/order-execute.js ${orderArgs.join(" ")}`);
      } else {
        const result = await executeOrder(orderArgs);
        if (result.stdout.trim()) {
          process.stdout.write(result.stdout);
        }
        if (result.stderr.trim()) {
          process.stderr.write(result.stderr);
        }
      }

      state.lastExecutionAt = Date.now();
      state.placedOrders += 1;
      console.log(
        `[report] placed_orders=${state.placedOrders} side=${side} confidence=${confidence.toFixed(4)} rationale=${JSON.stringify(reason)}`
      );
      await printPositionSnapshot(userMargin);

      if (config.maxOrders > 0 && state.placedOrders >= config.maxOrders) {
        console.log(`[info] max orders reached (${config.maxOrders}), stopping`);
        requestStop(state, "max orders reached");
      }
    })
    .catch((error) => {
      const message = error instanceof Error ? error.message : String(error);
      console.error(`[error] order execution failed: ${message}`);
    });
}

function connectWebsocket(config, state, userMargin) {
  if (state.stopRequested) {
    return;
  }

  const endpoint = wsUrl();
  const socket = new WebSocket(endpoint);
  state.socket = socket;
  let openedAt = 0;

  socket.on("open", () => {
    openedAt = Date.now();
    state.reconnectAttempts = 0;
    console.log(`[info] websocket connected: ${endpoint}`);
    socket.send(
      JSON.stringify({
        type: "subscribe",
        channel: config.channel
      })
    );
  });

  socket.on("message", (raw) => {
    let envelope;
    try {
      envelope = JSON.parse(String(raw));
    } catch (_err) {
      return;
    }

    const signals = signalItemsFromEnvelope(envelope);
    for (const signal of signals) {
      const signalAgent = String(signal.agent_name || "").trim();
      const side = normalizeSignalSide(signal.side);
      const confidence = toNumber(signal.confidence, 0);
      const ts = Math.floor(toNumber(signal.ts, Math.floor(Date.now() / 1000)));

      if (!side) {
        continue;
      }
      if (config.agentNameFilter && signalAgent !== config.agentNameFilter) {
        continue;
      }
      if (confidence < config.minConfidence) {
        continue;
      }

      enqueueSignalExecution(signal, side, confidence, ts, config, state, userMargin);
    }
  });

  socket.on("error", (error) => {
    console.error(`[error] websocket: ${error.message}`);
  });

  socket.on("close", (code, reason) => {
    const reasonText = reason ? String(reason) : "";
    const openMs = openedAt > 0 ? Date.now() - openedAt : 0;
    console.log(`[warn] websocket closed code=${code} reason=${reasonText} open_ms=${openMs}`);

    if (state.socket === socket) {
      state.socket = null;
    }

    if (state.stopRequested) {
      if (typeof state.maybeFinalize === "function") {
        state.maybeFinalize();
      }
      return;
    }

    scheduleReconnect(state, config, () => {
      connectWebsocket(config, state, userMargin);
    });
  });
}

async function runRealtimeTrading(config, userMargin) {
  const state = createRuntimeState();
  state.maxOrders = config.maxOrders;

  return new Promise((resolve) => {
    let finished = false;

    const finish = () => {
      if (finished) {
        return;
      }
      finished = true;
      process.off("SIGINT", handleSignal);
      process.off("SIGTERM", handleSignal);
      resolve();
    };

    state.maybeFinalize = () => {
      if (!state.stopRequested) {
        return;
      }
      if (state.socket) {
        return;
      }
      if (state.reconnectTimer) {
        return;
      }
      state.activeOrder
        .catch(() => {
        })
        .finally(() => {
          finish();
        });
    };

    const handleSignal = () => {
      console.log("[info] shutdown signal received");
      requestStop(state, "signal");
    };

    process.on("SIGINT", handleSignal);
    process.on("SIGTERM", handleSignal);

    connectWebsocket(config, state, userMargin);
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || args.h) {
    usage();
    return;
  }

  const marketId = String(args["market-id"] || "").trim();
  const margin = String(args.margin || "").trim();
  if (!marketId) {
    throw new Error("--market-id is required");
  }
  if (!margin) {
    throw new Error("--margin is required");
  }

  const orderType = String(args.type || "market").trim().toLowerCase();
  if (orderType !== "market" && orderType !== "limit") {
    throw new Error("--type must be market or limit");
  }

  const price = String(args.price || "").trim();
  if (orderType === "limit" && !price) {
    throw new Error("--price is required for limit orders");
  }

  const ttl = String(args.ttl || "300").trim();
  const deposit = String(args.deposit || "").trim();
  const reduceOnly = toBool(args["reduce-only"]);
  const minConfidence = toNumber(args["min-confidence"], 0.7);
  const cooldownMs = Math.max(0, toInt(args["cooldown-ms"], 15000));
  const maxOrders = Math.max(0, toInt(args["max-orders"], 0));
  const channel = String(args.channel || "agent.signals").trim();
  const agentNameFilter = String(args["agent-name"] || "").trim();
  const dryRun = toBool(args["dry-run"]);

  const reconnectBaseDelayMs = Math.max(250, toInt(args["reconnect-base-delay-ms"], 1000));
  const reconnectMaxDelayMs = Math.max(
    reconnectBaseDelayMs,
    toInt(args["reconnect-max-delay-ms"], 30000)
  );
  const maxReconnectAttempts = Math.max(0, toInt(args["max-reconnect-attempts"], 0));

  const { strategyPrompt, strategySource } = readStrategyPrompt(args);

  const { signer } = readSigner();
  const { orderEngine } = programIdsFromEnv();
  const userMargin = deriveUserMarginPda(signer.publicKey, orderEngine).toBase58();

  const config = {
    marketId,
    margin,
    orderType,
    price,
    ttl,
    deposit,
    reduceOnly,
    minConfidence,
    cooldownMs,
    maxOrders,
    channel,
    agentNameFilter,
    dryRun,
    strategyPrompt,
    reconnectBaseDelayMs,
    reconnectMaxDelayMs,
    maxReconnectAttempts
  };

  console.log(`[info] ws=${wsUrl()}`);
  console.log(`[info] channel=${channel}`);
  console.log(`[info] wallet=${signer.publicKey.toBase58()} user_margin=${userMargin}`);
  console.log(`[info] min_confidence=${minConfidence} cooldown_ms=${cooldownMs} dry_run=${dryRun}`);
  if (strategySource) {
    console.log(`[info] strategy_source=${strategySource}`);
  }
  if (strategyPrompt) {
    console.log(`[info] strategy_summary="${compactStrategySummary(strategyPrompt)}"`);
  }

  await printPositionSnapshot(userMargin);
  await runRealtimeTrading(config, userMargin);
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[error] ${message}`);
  process.exit(1);
});
