#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { spawn, spawnSync } = require("child_process");

const skillRoot = path.resolve(__dirname, "..");
const dataDir = path.join(skillRoot, ".data");
const paths = {
  dataDir,
  state: path.join(dataDir, "state.json"),
  pid: path.join(dataDir, "daemon.pid"),
  journal: path.join(dataDir, "journal.log"),
  daemonOut: path.join(dataDir, "daemon.out.log"),
  daemonErr: path.join(dataDir, "daemon.err.log"),
  daemonScript: path.join(__dirname, "voice_journal_daemon.js"),
};

function ensureDir() {
  fs.mkdirSync(paths.dataDir, { recursive: true });
}

function copyIfSet(target, key) {
  if (process.env[key]) target[key] = process.env[key];
}

function parseLanguageHintsFromArgs(args) {
  if (!Array.isArray(args) || args.length === 0) return null;

  let candidate = null;
  const flag = args.find((a) => a.startsWith("--language-hints="));
  if (flag) {
    candidate = flag.slice("--language-hints=".length);
  } else if (args[0] && args[0].trim().startsWith("[")) {
    candidate = args.join(" ");
  }
  if (!candidate) return null;

  try {
    const parsed = JSON.parse(candidate);
    if (!Array.isArray(parsed)) return null;
    const cleaned = parsed
      .map((v) => String(v).trim().toLowerCase())
      .filter(Boolean);
    if (cleaned.length === 0) return null;
    return [...new Set(cleaned)];
  } catch (_) {
    return null;
  }
}

function isPidRunning(pid) {
  if (!Number.isInteger(pid) || pid <= 1) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch (_) {
    return false;
  }
}

function readState() {
  if (!fs.existsSync(paths.state)) return null;
  try {
    return JSON.parse(fs.readFileSync(paths.state, "utf8"));
  } catch (_) {
    return null;
  }
}

function readPid() {
  if (!fs.existsSync(paths.pid)) return null;
  const raw = fs.readFileSync(paths.pid, "utf8").trim();
  const pid = Number(raw);
  return Number.isInteger(pid) ? pid : null;
}

function status() {
  const state = readState();
  const pid = readPid() || (state && Number(state.pid)) || null;
  const running = !!pid && isPidRunning(pid);
  const out = {
    running,
    pid,
    stateFile: paths.state,
    journalFile: paths.journal,
    daemonOut: paths.daemonOut,
    daemonErr: paths.daemonErr,
    state,
  };
  console.log(JSON.stringify(out, null, 2));
  return running;
}

function start() {
  ensureDir();
  if (!process.env.SONIOX_API_KEY) {
    console.error("SONIOX_API_KEY is required.");
    process.exit(2);
  }
  const depCheck = spawnSync(
    process.execPath,
    ["-e", "require.resolve('@soniox/node')"],
    { cwd: skillRoot, stdio: "ignore" }
  );
  if (depCheck.status !== 0) {
    console.error("Missing dependency '@soniox/node'. Run `npm install` in this skill directory.");
    process.exit(2);
  }

  const pid = readPid();
  if (pid && isPidRunning(pid)) {
    console.log(`Voice journal already running (pid ${pid}).`);
    status();
    return;
  }

  const startArgs = process.argv.slice(3);
  const languageHints = parseLanguageHintsFromArgs(startArgs);
  const daemonEnv = {};
  copyIfSet(daemonEnv, "PATH");
  copyIfSet(daemonEnv, "HOME");
  copyIfSet(daemonEnv, "LANG");
  copyIfSet(daemonEnv, "LC_ALL");
  copyIfSet(daemonEnv, "XDG_RUNTIME_DIR");
  copyIfSet(daemonEnv, "PULSE_SERVER");
  copyIfSet(daemonEnv, "ALSA_CONFIG_PATH");
  copyIfSet(daemonEnv, "DBUS_SESSION_BUS_ADDRESS");
  daemonEnv.SONIOX_API_KEY = process.env.SONIOX_API_KEY;
  if (languageHints && languageHints.length > 0) {
    daemonEnv.VOICE_JOURNAL_LANGUAGE_HINTS = JSON.stringify(languageHints);
  }

  const outFd = fs.openSync(paths.daemonOut, "a");
  const errFd = fs.openSync(paths.daemonErr, "a");
  const child = spawn(process.execPath, [paths.daemonScript], {
    detached: true,
    stdio: ["ignore", outFd, errFd],
    env: daemonEnv,
  });
  child.unref();

  console.log(`Voice journal start requested (pid ${child.pid}).`);
  if (languageHints && languageHints.length > 0) {
    console.log(`Language hints: ${JSON.stringify(languageHints)}`);
  }
  console.log("Use `node scripts/voice_journal_ctl.js status` to confirm readiness.");
}

async function end() {
  const pid = readPid();
  if (!pid || !isPidRunning(pid)) {
    console.log("Voice journal is not running.");
    return;
  }
  process.kill(pid, "SIGTERM");

  const deadline = Date.now() + 8000;
  while (Date.now() < deadline) {
    if (!isPidRunning(pid)) {
      console.log(`Voice journal stopped (pid ${pid}).`);
      return;
    }
    await new Promise((r) => setTimeout(r, 150));
  }
  console.log(`Stop signal sent to pid ${pid}; process still running.`);
}

function last(minutesArg) {
  const minutes = Number.parseInt(minutesArg || "10", 10);
  const safeMinutes = Number.isFinite(minutes) && minutes > 0 ? minutes : 10;
  const cutoff = Date.now() - safeMinutes * 60 * 1000;

  if (!fs.existsSync(paths.journal)) {
    console.log("");
    return;
  }

  const lines = fs
    .readFileSync(paths.journal, "utf8")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const selected = [];
  for (const line of lines) {
    const tab = line.indexOf("\t");
    if (tab < 0) continue;
    const minute = line.slice(0, tab).trim();
    const text = line.slice(tab + 1).trim();
    const ms = Date.parse(minute);
    if (!Number.isNaN(ms) && ms >= cutoff && text) {
      selected.push({ minute, text });
    }
  }

  if (selected.length === 0) {
    console.log("");
    return;
  }

  const out = selected.map((s) => `[${s.minute}] ${s.text}`).join("\n");
  const args = process.argv.slice(2);
  const full = args.includes("--full");
  const maxCharsArg = args.find((a) => a.startsWith("--max-chars="));
  const argMax = maxCharsArg ? Number.parseInt(maxCharsArg.split("=")[1], 10) : NaN;
  const maxChars = Number.isFinite(argMax) && argMax > 0 ? argMax : 1800;

  if (full || out.length <= maxChars) {
    console.log(out);
    return;
  }

  console.log(out.slice(-maxChars));
}

async function main() {
  const cmd = (process.argv[2] || "").trim().toLowerCase();
  switch (cmd) {
    case "start":
      start();
      return;
    case "end":
    case "stop":
      await end();
      return;
    case "status":
      status();
      return;
    case "last":
      last(process.argv[3]);
      return;
    default:
      console.log(
        [
          "Usage:",
          "  node scripts/voice_journal_ctl.js start",
          "  node scripts/voice_journal_ctl.js start '[\"en\",\"de\"]'",
          "  node scripts/voice_journal_ctl.js start --language-hints='[\"en\",\"de\"]'",
          "  node scripts/voice_journal_ctl.js end",
          "  node scripts/voice_journal_ctl.js status",
          "  node scripts/voice_journal_ctl.js last [minutes] [--full] [--max-chars=1800]",
        ].join("\n")
      );
  }
}

main().catch((err) => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
