#!/usr/bin/env node

// poker-cli.ts
import { execFile } from "node:child_process";
var BACKEND = "https://api.clawplay.fun";
var API_KEY = process.env.CLAWPLAY_API_KEY;
function die(msg, code = 1) {
  process.stderr.write(msg + "\n");
  process.exit(code);
}
function requireAuth() {
  if (!API_KEY) die("CLAWPLAY_API_KEY not set");
  return { backend: BACKEND, apiKey: API_KEY };
}
async function api(method, path, body) {
  const { backend, apiKey } = requireAuth();
  const headers = { "x-api-key": apiKey };
  const opts = { method, headers, signal: AbortSignal.timeout(15e3) };
  if (body) {
    headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const resp = await fetch(`${backend}${path}`, opts);
  const text = await resp.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = text;
  }
  return { ok: resp.ok, status: resp.status, data };
}
function output(data) {
  process.stdout.write(JSON.stringify(data, null, 2) + "\n");
}
function sendButtons(channel, target, message, options, dryRun) {
  const args = ["message", "send", "--channel", channel, "--target", target, "--json"];
  if (channel === "telegram") {
    const keyboard = options.map((o) => [{ text: o.label, callback_data: o.value }]);
    args.push("--buttons", JSON.stringify(keyboard));
  } else if (channel === "discord") {
    const rows = [];
    for (let i = 0; i < options.length; i += 5) {
      rows.push({
        type: 1,
        // ACTION_ROW
        components: options.slice(i, i + 5).map((o, idx) => ({
          type: 2,
          // BUTTON
          style: i === 0 && idx === 0 ? 1 : 2,
          // PRIMARY for first, SECONDARY for rest
          label: o.label,
          custom_id: o.value
        }))
      });
    }
    args.push("--components", JSON.stringify(rows));
  } else {
    const list = options.map((o, i) => `${i + 1}. ${o.label}`).join("\n");
    message = `${message}

${list}`;
  }
  args.push("--message", message);
  if (dryRun) {
    output({ dryRun: true, command: "openclaw", args });
    return Promise.resolve();
  }
  return new Promise((resolve, reject) => {
    execFile("openclaw", args, { timeout: 1e4 }, (err) => {
      if (err) reject(new Error(`Send failed: ${err.message}`));
      else resolve();
    });
  });
}
function getFlag(args, name) {
  const idx = args.indexOf(name);
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : null;
}
function hasFlag(args, name) {
  return args.includes(name);
}
function getAllFlags(args, name) {
  const results = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === name && i + 1 < args.length) {
      results.push(args[i + 1]);
    }
  }
  return results;
}
async function cmdSignup(username) {
  const resp = await fetch(`${BACKEND}/api/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
    signal: AbortSignal.timeout(15e3)
  });
  const text = await resp.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = text;
  }
  if (!resp.ok) die(`Signup failed (${resp.status}): ${JSON.stringify(data)}`);
  output(data);
}
async function cmdBalance() {
  const result = await api("GET", "/api/chips/balance");
  if (!result.ok) die(`Balance failed (${result.status}): ${JSON.stringify(result.data)}`);
  const raw = result.data;
  const chips = typeof raw === "number" ? raw : raw.balance;
  output({ chips });
}
async function cmdStatus() {
  const result = await api("GET", "/api/lobby/status");
  if (!result.ok) die(`Status failed (${result.status}): ${JSON.stringify(result.data)}`);
  const data = result.data;
  if (data.status === "playing") {
    output({ status: "playing", tableId: data.gameId });
  } else {
    output({ status: "idle" });
  }
}
async function cmdModes(args) {
  const pick = hasFlag(args, "--pick");
  const channel = getFlag(args, "--channel");
  const target = getFlag(args, "--target");
  const dryRun = hasFlag(args, "--dry-run");
  const modesResult = await api("GET", "/api/game-modes");
  if (!modesResult.ok) die(`Modes failed (${modesResult.status}): ${JSON.stringify(modesResult.data)}`);
  const modes = modesResult.data;
  if (!pick) {
    output(modes.map((m) => ({ id: m.id, name: m.name, buyIn: m.buyIn })));
    return;
  }
  if (!channel || !target) die("--pick requires --channel and --target");
  const balResult = await api("GET", "/api/chips/balance");
  if (!balResult.ok) die(`Balance failed (${balResult.status}): ${JSON.stringify(balResult.data)}`);
  const rawBal = typeof balResult.data === "number" ? balResult.data : balResult.data.balance;
  if (rawBal == null || typeof rawBal !== "number") {
    die(`Unexpected balance response: ${JSON.stringify(balResult.data)}`);
  }
  const balance = rawBal;
  const affordable = modes.filter((m) => balance >= m.buyIn);
  if (affordable.length === 0) {
    output({ sent: false, reason: "no affordable modes", balance });
    process.exit(2);
  }
  const options = affordable.map((m) => ({
    label: `${m.name} \u2014 ${m.smallBlind}/${m.bigBlind}, ${m.buyIn} buy-in`,
    value: m.name
  }));
  const msg = `Pick a game mode (${balance} chips):`;
  await sendButtons(channel, target, msg, options, dryRun);
  output({ sent: true, balance, modesOffered: affordable.map((m) => m.name) });
}
async function cmdJoin(gameModeId) {
  const result = await api("POST", "/api/lobby/join", { gameModeId });
  if (!result.ok) die(`Join failed (${result.status}): ${JSON.stringify(result.data)}`);
  output(result.data);
}
async function cmdSpectatorToken(tableId) {
  const result = await api("POST", `/api/game/${tableId}/spectator-token`);
  if (!result.ok) die(`Spectator token failed (${result.status}): ${JSON.stringify(result.data)}`);
  const data = result.data;
  const url = `https://clawplay.fun/watch/${tableId}?token=${data.token}`;
  output({ url });
}
async function cmdRebuy(tableId) {
  const result = await api("POST", `/api/game/${tableId}/rebuy`);
  if (!result.ok) die(`Rebuy failed (${result.status}): ${JSON.stringify(result.data)}`);
  const data = result.data;
  output({ rebuyed: true, chips: data.yourChips });
}
async function cmdLeave(tableId) {
  const result = await api("POST", `/api/game/${tableId}/leave`);
  if (!result.ok) die(`Leave failed (${result.status}): ${JSON.stringify(result.data)}`);
  output(result.data);
}
async function cmdPrompt(args) {
  const message = getFlag(args, "--message");
  const channel = getFlag(args, "--channel");
  const target = getFlag(args, "--target");
  const dryRun = hasFlag(args, "--dry-run");
  const optionStrs = getAllFlags(args, "--option");
  if (!message) die("--message is required");
  if (!channel || !target) die("--channel and --target are required");
  if (optionStrs.length < 2) die('At least 2 --option flags required (format: "Label=value")');
  const options = optionStrs.map((s) => {
    const eq = s.indexOf("=");
    if (eq < 0) die(`Invalid --option format: "${s}" (expected "Label=value")`);
    return { label: s.slice(0, eq), value: s.slice(eq + 1) };
  });
  await sendButtons(channel, target, message, options, dryRun);
  if (!dryRun) output({ sent: true, channel, target, options: options.length });
}
async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  try {
    switch (cmd) {
      case "signup": {
        const username = args[1];
        if (!username) die("Usage: poker-cli signup <username>");
        await cmdSignup(username);
        break;
      }
      case "balance":
        await cmdBalance();
        break;
      case "status":
        await cmdStatus();
        break;
      case "modes":
        await cmdModes(args.slice(1));
        break;
      case "join": {
        const modeId = args[1];
        if (!modeId) die("Usage: poker-cli join <gameModeId>");
        await cmdJoin(modeId);
        break;
      }
      case "spectator-token": {
        const tableId = args[1];
        if (!tableId) die("Usage: poker-cli spectator-token <tableId>");
        await cmdSpectatorToken(tableId);
        break;
      }
      case "rebuy": {
        const tableId = args[1];
        if (!tableId) die("Usage: poker-cli rebuy <tableId>");
        await cmdRebuy(tableId);
        break;
      }
      case "leave": {
        const tableId = args[1];
        if (!tableId) die("Usage: poker-cli leave <tableId>");
        await cmdLeave(tableId);
        break;
      }
      case "prompt":
        await cmdPrompt(args.slice(1));
        break;
      default:
        die(`Unknown command: ${cmd || "(none)"}

Commands: signup, balance, status, modes, join, spectator-token, rebuy, leave, prompt`);
    }
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    die(`Error: ${msg}`);
  }
}
main();
