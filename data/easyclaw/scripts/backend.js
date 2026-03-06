#!/usr/bin/env node
require("dotenv").config();

const {
  deriveUserMarginPda,
  parseArgs,
  programIdsFromEnv,
  readSigner
} = require("./common");
const { apiBaseUrl, apiRequest, wsUrl } = require("./backend-common");

function usage() {
  console.log(`Usage:
  node scripts/backend.js doctor
  node scripts/backend.js health
  node scripts/backend.js system-status
  node scripts/backend.js chart-candles [--market <symbol>] [--timeframe <1m|5m|15m|1h|4h|1d>] [--limit <n>]
  node scripts/backend.js positions [--mine] [--user-margin <pda>] [--market-id <id>] [--limit <n>] [--offset <n>]
  node scripts/backend.js orders [--mine] [--user-margin <pda>] [--user-pubkey <pk>] [--status <Open|Executed|...>] [--market-id <id>]
  node scripts/backend.js fills [--mine] [--user-margin <pda>] [--user-pubkey <pk>] [--market-id <id>]
  node scripts/backend.js position-history [--mine] [--user-margin <pda>] [--market-id <id>] [--limit <n>] [--offset <n>]
  node scripts/backend.js orderbook-heatmap --exchange <binance|okx|...> --symbol <pair> [--from <unix>] [--to <unix>] [--limit <n>] [--offset <n>]
  node scripts/backend.js orderbook-heatmap-aggregated --symbol-key <key> [--from <unix>] [--to <unix>] [--limit <n>] [--offset <n>]
  node scripts/backend.js trades [--agent-id <id>] [--from <unix>] [--to <unix>] [--limit <n>] [--offset <n>]
  node scripts/backend.js portfolio [--period <7d|30d|all>]
  node scripts/backend.js agent-portfolio --agent-id <id> [--period <7d|30d|all>]
  node scripts/backend.js leaderboard [--metric <win_rate|pnl_pct>] [--period <all_time|30d|7d>] [--min-trades <n>]
  node scripts/backend.js agents
  node scripts/backend.js agent-create --name <text> --strategy-id <id> [--risk-profile-json <json>]
  node scripts/backend.js agent --agent-id <id>
  node scripts/backend.js agent-owner-binding --agent-id <id>
  node scripts/backend.js agent-owner-rebind --agent-id <id> --challenge-id <id> --signature <sig>
  node scripts/backend.js agent-session-start --agent-id <id> --mode <paper|live>
  node scripts/backend.js agent-session-stop --agent-id <id> --session-id <id>
  node scripts/backend.js agent-risk --agent-id <id>
  node scripts/backend.js agent-risk-patch --agent-id <id> [--max-position-usdc <n>] [--daily-loss-limit-usdc <n>] [--kill-switch-enabled <true|false>]
  node scripts/backend.js kill-switch [--all] [--agent-id <id>] [--agent-ids <csv>]
  node scripts/backend.js strategy-templates
  node scripts/backend.js strategy-create --name <text> [--entry-rules-json <json>] [--exit-rules-json <json>] [--risk-defaults-json <json>]
  node scripts/backend.js strategy --strategy-id <id>
  node scripts/backend.js strategy-patch --strategy-id <id> [--name <text>] [--entry-rules-json <json>] [--exit-rules-json <json>]
  node scripts/backend.js strategy-publish --strategy-id <id>
  node scripts/backend.js auth-challenge --wallet-pubkey <pk> --intent <owner_bind|session|live_stepup>
  node scripts/backend.js auth-verify --challenge-id <id> --signature <sig> --wallet-pubkey <pk>
  node scripts/backend.js auth-refresh [--token <session_token>]

Options:
  --json          Print raw JSON output
  --token <jwt>   Override EASYCLAW_API_TOKEN for auth endpoints
`);
}

function parseMainArgs(argv) {
  const command = argv[0] || "help";
  const args = parseArgs(argv.slice(1));
  return { command, args };
}

function parseBoolFlag(value) {
  if (value === true) return true;
  if (typeof value !== "string") return false;
  const normalized = value.trim().toLowerCase();
  return normalized === "1" || normalized === "true" || normalized === "yes";
}

function maybeNumber(raw) {
  if (raw === undefined || raw === null || String(raw).trim() === "") {
    return undefined;
  }
  const value = Number(raw);
  if (!Number.isFinite(value)) {
    throw new Error(`Invalid numeric value: ${raw}`);
  }
  return value;
}

function maybeBoolean(raw, name) {
  if (raw === undefined || raw === null || String(raw).trim() === "") {
    return undefined;
  }
  if (raw === true) {
    return true;
  }
  if (typeof raw !== "string") {
    throw new Error(`Invalid boolean value for ${name}: ${raw}`);
  }
  const normalized = raw.trim().toLowerCase();
  if (normalized === "1" || normalized === "true" || normalized === "yes") {
    return true;
  }
  if (normalized === "0" || normalized === "false" || normalized === "no") {
    return false;
  }
  throw new Error(`Invalid boolean value for ${name}: ${raw}`);
}

function parseJSONString(raw, name) {
  if (raw === undefined || raw === null || String(raw).trim() === "") {
    return undefined;
  }
  const value = String(raw).trim();
  try {
    return JSON.parse(value);
  } catch (_error) {
    throw new Error(`Invalid JSON for ${name}`);
  }
}

function parseJSONObject(raw, name, fallback) {
  const value = parseJSONString(raw, name);
  if (value === undefined) {
    return fallback;
  }
  if (value === null || Array.isArray(value) || typeof value !== "object") {
    throw new Error(`${name} must be a JSON object`);
  }
  return value;
}

function requiredString(raw, flagName) {
  const value = String(raw || "").trim();
  if (!value) {
    throw new Error(`${flagName} is required`);
  }
  return value;
}

function parseCSV(raw) {
  if (raw === undefined || raw === null || String(raw).trim() === "") {
    return [];
  }
  return String(raw)
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function mineIdentity() {
  const { signer } = readSigner();
  const { orderEngine } = programIdsFromEnv();
  const userMargin = deriveUserMarginPda(signer.publicKey, orderEngine);
  return {
    userPubkey: signer.publicKey.toBase58(),
    userMargin: userMargin.toBase58()
  };
}

function jsonOrPrint(payload, outputAsJSON) {
  if (outputAsJSON) {
    console.log(JSON.stringify(payload, null, 2));
    return;
  }

  if (payload === null || payload === undefined) {
    console.log("(empty)");
    return;
  }

  if (typeof payload === "string") {
    console.log(payload);
    return;
  }

  console.log(JSON.stringify(payload, null, 2));
}

async function runCommand(command, args) {
  const outputAsJSON = parseBoolFlag(args.json);
  const token = args.token;

  switch (command) {
    case "doctor": {
      const payload = {
        apiBaseUrl: apiBaseUrl(),
        wsUrl: wsUrl(),
        hasAuthToken:
          Boolean(process.env.EASYCLAW_API_TOKEN) ||
          Boolean(process.env.API_AUTH_TOKEN) ||
          Boolean(args.token),
        timestamp: Math.floor(Date.now() / 1000)
      };
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "health": {
      const payload = await apiRequest("/healthz");
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "system-status": {
      const payload = await apiRequest("/v1/system/status");
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "chart-candles": {
      const payload = await apiRequest("/v1/chart/candles", {
        query: {
          market: args.market,
          timeframe: args.timeframe,
          limit: args.limit
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "positions": {
      const mine = parseBoolFlag(args.mine);
      const identity = mine ? mineIdentity() : null;
      const payload = await apiRequest("/api/v1/positions", {
        query: {
          user_margin: args["user-margin"] || (identity ? identity.userMargin : undefined),
          market_id: args["market-id"],
          limit: args.limit,
          offset: args.offset
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "orders": {
      const mine = parseBoolFlag(args.mine);
      const identity = mine ? mineIdentity() : null;
      const payload = await apiRequest("/api/v1/orders", {
        query: {
          user_margin: args["user-margin"] || (identity ? identity.userMargin : undefined),
          user_pubkey: args["user-pubkey"] || (identity ? identity.userPubkey : undefined),
          market_id: args["market-id"],
          status: args.status,
          limit: args.limit,
          offset: args.offset
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "fills": {
      const mine = parseBoolFlag(args.mine);
      const identity = mine ? mineIdentity() : null;
      const payload = await apiRequest("/api/v1/fills", {
        query: {
          user_margin: args["user-margin"] || (identity ? identity.userMargin : undefined),
          user_pubkey: args["user-pubkey"] || (identity ? identity.userPubkey : undefined),
          market_id: args["market-id"],
          limit: args.limit,
          offset: args.offset
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "position-history": {
      const mine = parseBoolFlag(args.mine);
      const identity = mine ? mineIdentity() : null;
      const payload = await apiRequest("/api/v1/position-history", {
        query: {
          user_margin: args["user-margin"] || (identity ? identity.userMargin : undefined),
          market_id: args["market-id"],
          limit: args.limit,
          offset: args.offset
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "orderbook-heatmap": {
      const exchange = requiredString(args.exchange, "--exchange");
      const symbol = requiredString(args.symbol, "--symbol");
      const payload = await apiRequest("/api/v1/orderbook-heatmap", {
        query: {
          exchange,
          symbol,
          from: maybeNumber(args.from),
          to: maybeNumber(args.to),
          limit: args.limit,
          offset: args.offset
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "orderbook-heatmap-aggregated": {
      const symbolKey = requiredString(args["symbol-key"], "--symbol-key");
      const payload = await apiRequest("/api/v1/orderbook-heatmap-aggregated", {
        query: {
          symbol_key: symbolKey,
          from: maybeNumber(args.from),
          to: maybeNumber(args.to),
          limit: args.limit,
          offset: args.offset
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "trades": {
      const payload = await apiRequest("/v1/trades", {
        query: {
          agent_id: args["agent-id"],
          from: maybeNumber(args.from),
          to: maybeNumber(args.to),
          limit: args.limit,
          offset: args.offset
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "portfolio": {
      const payload = await apiRequest("/v1/portfolio", {
        query: {
          period: args.period || "7d"
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agent-portfolio": {
      const agentId = String(args["agent-id"] || "").trim();
      if (!agentId) {
        throw new Error("--agent-id is required");
      }
      const payload = await apiRequest(`/v1/portfolio/agents/${encodeURIComponent(agentId)}`, {
        query: {
          period: args.period || "7d"
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "leaderboard": {
      const payload = await apiRequest("/v1/leaderboard", {
        query: {
          metric: args.metric || "pnl_pct",
          period: args.period || "7d",
          min_trades: args["min-trades"] || 20
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agents": {
      const payload = await apiRequest("/v1/agents");
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agent": {
      const agentID = requiredString(args["agent-id"], "--agent-id");
      const payload = await apiRequest(`/v1/agents/${encodeURIComponent(agentID)}`);
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agent-owner-binding": {
      const agentID = requiredString(args["agent-id"], "--agent-id");
      const payload = await apiRequest(
        `/v1/agents/${encodeURIComponent(agentID)}/owner-binding`
      );
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agent-owner-rebind": {
      const agentID = requiredString(args["agent-id"], "--agent-id");
      const challengeID = requiredString(args["challenge-id"], "--challenge-id");
      const signature = requiredString(args.signature, "--signature");
      const payload = await apiRequest(
        `/v1/agents/${encodeURIComponent(agentID)}/owner-binding/rebind`,
        {
          method: "POST",
          body: {
            challenge_id: challengeID,
            signature
          },
          token
        }
      );
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agent-session-start": {
      const agentID = requiredString(args["agent-id"], "--agent-id");
      const mode = requiredString(args.mode, "--mode");
      const payload = await apiRequest(
        `/v1/agents/${encodeURIComponent(agentID)}/sessions`,
        {
          method: "POST",
          body: { mode },
          requireAuth: true,
          token
        }
      );
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agent-session-stop": {
      const agentID = requiredString(args["agent-id"], "--agent-id");
      const sessionID = requiredString(args["session-id"], "--session-id");
      const payload = await apiRequest(
        `/v1/agents/${encodeURIComponent(agentID)}/sessions/${encodeURIComponent(
          sessionID
        )}`,
        {
          method: "DELETE",
          requireAuth: true,
          token
        }
      );
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agent-risk": {
      const agentID = requiredString(args["agent-id"], "--agent-id");
      const payload = await apiRequest(`/v1/agents/${encodeURIComponent(agentID)}/risk`);
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agent-risk-patch": {
      const agentID = requiredString(args["agent-id"], "--agent-id");
      const maxPositionUSDC = maybeNumber(args["max-position-usdc"]);
      const dailyLossLimitUSDC = maybeNumber(args["daily-loss-limit-usdc"]);
      const killSwitchEnabled = maybeBoolean(
        args["kill-switch-enabled"],
        "--kill-switch-enabled"
      );

      const body = {};
      if (maxPositionUSDC !== undefined) {
        body.max_position_usdc = maxPositionUSDC;
      }
      if (dailyLossLimitUSDC !== undefined) {
        body.daily_loss_limit_usdc = dailyLossLimitUSDC;
      }
      if (killSwitchEnabled !== undefined) {
        body.kill_switch_enabled = killSwitchEnabled;
      }
      if (Object.keys(body).length === 0) {
        throw new Error(
          "At least one of --max-position-usdc, --daily-loss-limit-usdc, --kill-switch-enabled is required"
        );
      }

      const payload = await apiRequest(
        `/v1/agents/${encodeURIComponent(agentID)}/risk`,
        {
          method: "PATCH",
          body,
          requireAuth: true,
          token
        }
      );
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "kill-switch": {
      const all = parseBoolFlag(args.all);
      const agentIDs = [
        ...parseCSV(args["agent-ids"]),
        ...parseCSV(args["agent-id"])
      ];
      const body = {
        agent_ids: all ? ["all"] : agentIDs
      };
      if (!all && body.agent_ids.length === 0) {
        throw new Error("Pass --all or --agent-ids <csv> (or --agent-id <id>)");
      }

      const payload = await apiRequest("/v1/safety/kill-switch", {
        method: "POST",
        body,
        requireAuth: true,
        token
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "strategy-templates": {
      const payload = await apiRequest("/v1/strategy/templates");
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "strategy-create": {
      const name = requiredString(args.name, "--name");
      const entryRules = parseJSONObject(args["entry-rules-json"], "--entry-rules-json", {});
      const exitRules = parseJSONObject(args["exit-rules-json"], "--exit-rules-json", {});
      const riskDefaults = parseJSONObject(
        args["risk-defaults-json"],
        "--risk-defaults-json",
        {}
      );
      const payload = await apiRequest("/v1/strategies", {
        method: "POST",
        body: {
          name,
          entry_rules: entryRules,
          exit_rules: exitRules,
          risk_defaults: riskDefaults
        },
        requireAuth: true,
        token
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "strategy": {
      const strategyID = requiredString(args["strategy-id"], "--strategy-id");
      const payload = await apiRequest(`/v1/strategies/${encodeURIComponent(strategyID)}`);
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "strategy-patch": {
      const strategyID = requiredString(args["strategy-id"], "--strategy-id");
      const name = args.name !== undefined ? String(args.name).trim() : undefined;
      const entryRules = parseJSONObject(
        args["entry-rules-json"],
        "--entry-rules-json",
        undefined
      );
      const exitRules = parseJSONObject(
        args["exit-rules-json"],
        "--exit-rules-json",
        undefined
      );
      const body = {};
      if (name !== undefined && name !== "") {
        body.name = name;
      }
      if (entryRules !== undefined) {
        body.entry_rules = entryRules;
      }
      if (exitRules !== undefined) {
        body.exit_rules = exitRules;
      }
      if (Object.keys(body).length === 0) {
        throw new Error(
          "At least one of --name, --entry-rules-json, --exit-rules-json is required"
        );
      }

      const payload = await apiRequest(
        `/v1/strategies/${encodeURIComponent(strategyID)}`,
        {
          method: "PATCH",
          body,
          requireAuth: true,
          token
        }
      );
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "strategy-publish": {
      const strategyID = requiredString(args["strategy-id"], "--strategy-id");
      const payload = await apiRequest(
        `/v1/strategies/${encodeURIComponent(strategyID)}/publish`,
        {
          method: "POST",
          requireAuth: true,
          token
        }
      );
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "agent-create": {
      const name = requiredString(args.name, "--name");
      const strategyID = requiredString(args["strategy-id"], "--strategy-id");
      const riskProfile = parseJSONObject(
        args["risk-profile-json"],
        "--risk-profile-json",
        undefined
      );
      const body = {
        name,
        strategy_id: strategyID
      };
      if (riskProfile !== undefined) {
        body.risk_profile = riskProfile;
      }
      const payload = await apiRequest("/v1/agents", {
        method: "POST",
        body,
        requireAuth: true,
        token
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "auth-challenge": {
      const walletPubkey = String(args["wallet-pubkey"] || "").trim();
      const intent = String(args.intent || "session").trim();
      if (!walletPubkey) {
        throw new Error("--wallet-pubkey is required");
      }
      const payload = await apiRequest("/v1/auth/challenge", {
        method: "POST",
        body: {
          wallet_pubkey: walletPubkey,
          intent
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "auth-verify": {
      const challengeID = String(args["challenge-id"] || "").trim();
      const signature = String(args.signature || "").trim();
      const walletPubkey = String(args["wallet-pubkey"] || "").trim();
      if (!challengeID || !signature || !walletPubkey) {
        throw new Error("--challenge-id, --signature, --wallet-pubkey are required");
      }
      const payload = await apiRequest("/v1/auth/verify-signature", {
        method: "POST",
        body: {
          challenge_id: challengeID,
          signature,
          wallet_pubkey: walletPubkey
        }
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "auth-refresh": {
      const payload = await apiRequest("/v1/auth/session/refresh", {
        method: "POST",
        requireAuth: true,
        token
      });
      jsonOrPrint(payload, outputAsJSON);
      return;
    }

    case "help":
    case "-h":
    case "--help":
      usage();
      return;

    default:
      throw new Error(`Unknown backend command: ${command}`);
  }
}

async function main() {
  const { command, args } = parseMainArgs(process.argv.slice(2));
  await runCommand(command, args);
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[error] ${message}`);
  process.exit(1);
});
