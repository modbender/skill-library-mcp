#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { spawn, spawnSync } = require("child_process");
const { RealtimeSttSession, SONIOX_API_WS_URL } = require("@soniox/node");

const SAMPLE_RATE = 16000;
const BYTES_PER_SECOND = SAMPLE_RATE * 2;
const RECONNECT_MS = 15 * 60 * 1000;
const ROLLING_WINDOW_MS = 60 * 60 * 1000;
const MAX_PENDING_AUDIO_BYTES = 30 * BYTES_PER_SECOND;
const FLUSH_INTERVAL_MS = 3000;

const skillRoot = path.resolve(__dirname, "..");
const dataDir = path.join(skillRoot, ".data");
const sonioxApiKey = (process.env.SONIOX_API_KEY || "").trim();
// Prevent accidental secret propagation to child processes.
delete process.env.SONIOX_API_KEY;
const paths = {
  dataDir,
  state: path.join(dataDir, "state.json"),
  pid: path.join(dataDir, "daemon.pid"),
  journal: path.join(dataDir, "journal.log"),
  daemonOut: path.join(dataDir, "daemon.out.log"),
  daemonErr: path.join(dataDir, "daemon.err.log"),
};
const baseChildEnv = {};
if (process.env.PATH) baseChildEnv.PATH = process.env.PATH;
if (process.env.HOME) baseChildEnv.HOME = process.env.HOME;
if (process.env.LANG) baseChildEnv.LANG = process.env.LANG;
if (process.env.LC_ALL) baseChildEnv.LC_ALL = process.env.LC_ALL;
if (process.env.XDG_RUNTIME_DIR) baseChildEnv.XDG_RUNTIME_DIR = process.env.XDG_RUNTIME_DIR;
if (process.env.PULSE_SERVER) baseChildEnv.PULSE_SERVER = process.env.PULSE_SERVER;
if (process.env.ALSA_CONFIG_PATH) baseChildEnv.ALSA_CONFIG_PATH = process.env.ALSA_CONFIG_PATH;
if (process.env.DBUS_SESSION_BUS_ADDRESS) {
  baseChildEnv.DBUS_SESSION_BUS_ADDRESS = process.env.DBUS_SESSION_BUS_ADDRESS;
}

let audioProc = null;
let session = null;
let sessionBaseEpochMs = 0;
let rotating = false;
let shuttingDown = false;
let pendingAudioChunks = [];
let pendingAudioBytes = 0;
let reconnectTimer = null;
let flushTimer = null;
let stateTimer = null;
const minuteBuckets = new Map();
const recentTokenKeys = new Set();
const recentTokenQueue = [];
const MAX_RECENT_TOKENS = 12000;
let configuredLanguageHints = null;
let disableLanguageHints = false;
let recoverTimer = null;
let lastStreamErrorLogAt = 0;

function ensureDir() {
  fs.mkdirSync(paths.dataDir, { recursive: true });
  try {
    fs.chmodSync(paths.dataDir, 0o700);
  } catch (_) {
    // Best effort hardening.
  }
}

function hardenFile(pathname) {
  try {
    if (fs.existsSync(pathname)) {
      fs.chmodSync(pathname, 0o600);
    }
  } catch (_) {
    // Best effort hardening.
  }
}

function atomicWrite(pathname, content) {
  const tmp = `${pathname}.tmp`;
  fs.writeFileSync(tmp, content, { mode: 0o600 });
  fs.renameSync(tmp, pathname);
  hardenFile(pathname);
}

function nowIso() {
  return new Date().toISOString();
}

function safeNumber(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function parseLanguageHints() {
  const raw = process.env.VOICE_JOURNAL_LANGUAGE_HINTS;
  if (!raw || !raw.trim()) return null;
  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return null;
    const cleaned = parsed
      .map((v) => String(v).trim().toLowerCase())
      .filter(Boolean);
    return cleaned.length > 0 ? cleaned : null;
  } catch (_) {
    return null;
  }
}

function shouldLogStreamErrorNow() {
  const now = Date.now();
  if (now - lastStreamErrorLogAt < 3000) {
    return false;
  }
  lastStreamErrorLogAt = now;
  return true;
}

function scheduleRecover(delayMs = 800) {
  if (shuttingDown || recoverTimer) return;
  recoverTimer = setTimeout(async () => {
    recoverTimer = null;
    await rotateSession();
  }, delayMs);
}

function minuteKeyFromEpochMs(ms) {
  const d = new Date(ms);
  d.setUTCSeconds(0, 0);
  return d.toISOString().slice(0, 16) + "Z";
}

function log(...args) {
  const line = `[${nowIso()}] ${args.join(" ")}\n`;
  fs.appendFileSync(paths.daemonOut, line, { mode: 0o600 });
  hardenFile(paths.daemonOut);
}

function logError(...args) {
  const line = `[${nowIso()}] ${args.join(" ")}\n`;
  fs.appendFileSync(paths.daemonErr, line, { mode: 0o600 });
  hardenFile(paths.daemonErr);
}

function isCommandAvailable(cmd) {
  const result = spawnSync("which", [cmd], {
    env: baseChildEnv,
    stdio: "ignore",
  });
  return result.status === 0;
}

function resolveAudioCommand() {
  const platform = process.platform;
  const candidates = [];

  if (platform === "linux") {
    candidates.push({
      probe: "arecord",
      cmd: "arecord",
      args: ["-q", "-f", "S16_LE", "-r", String(SAMPLE_RATE), "-c", "1", "-t", "raw"],
      source: "linux-arecord",
    });
    candidates.push({
      probe: "rec",
      cmd: "rec",
      args: ["-q", "-d", "-t", "raw", "-b", "16", "-e", "signed-integer", "-r", String(SAMPLE_RATE), "-c", "1", "-"],
      source: "linux-rec",
    });
    candidates.push({
      probe: "ffmpeg",
      cmd: "ffmpeg",
      args: ["-loglevel", "error", "-f", "pulse", "-i", "default", "-ac", "1", "-ar", String(SAMPLE_RATE), "-f", "s16le", "-"],
      source: "linux-ffmpeg-pulse",
    });
  } else if (platform === "darwin") {
    candidates.push({
      probe: "rec",
      cmd: "rec",
      args: ["-q", "-d", "-t", "raw", "-b", "16", "-e", "signed-integer", "-r", String(SAMPLE_RATE), "-c", "1", "-"],
      source: "macos-rec",
    });
    candidates.push({
      probe: "ffmpeg",
      cmd: "ffmpeg",
      args: ["-loglevel", "error", "-f", "avfoundation", "-i", ":0", "-ac", "1", "-ar", String(SAMPLE_RATE), "-f", "s16le", "-"],
      source: "macos-ffmpeg-avfoundation",
    });
  }

  for (const c of candidates) {
    if (isCommandAvailable(c.probe)) {
      return c;
    }
  }

  throw new Error(
    "No supported microphone capture command found (need arecord, rec, or ffmpeg)."
  );
}

function appendTokenText(minuteKey, tokenText) {
  const prior = minuteBuckets.get(minuteKey) || "";
  const next = `${prior}${tokenText}`;
  minuteBuckets.set(minuteKey, next);
}

function pruneOldMinutes() {
  const cutoff = Date.now() - ROLLING_WINDOW_MS;
  for (const [k] of minuteBuckets.entries()) {
    const ms = Date.parse(k);
    if (!Number.isNaN(ms) && ms < cutoff) {
      minuteBuckets.delete(k);
    }
  }
}

function flushJournal() {
  pruneOldMinutes();
  const lines = Array.from(minuteBuckets.entries())
    .sort(([a], [b]) => Date.parse(a) - Date.parse(b))
    .map(([minute, text]) => `${minute}\t${text}`)
    .filter((line) => line.trim().length > 0);
  atomicWrite(paths.journal, lines.join("\n") + (lines.length ? "\n" : ""));
}

function writeState(extra = {}) {
  const state = {
    running: !shuttingDown,
    pid: process.pid,
    startedAt: startedAtIso,
    updatedAt: nowIso(),
    journalFile: paths.journal,
    reconnectEveryMinutes: 15,
    keepsMinutes: 60,
    ...extra,
  };
  atomicWrite(paths.state, JSON.stringify(state, null, 2));
}

function enqueueAudio(buf) {
  pendingAudioChunks.push(buf);
  pendingAudioBytes += buf.length;
  while (pendingAudioBytes > MAX_PENDING_AUDIO_BYTES && pendingAudioChunks.length > 0) {
    const drop = pendingAudioChunks.shift();
    pendingAudioBytes -= drop.length;
  }
}

function streamAudioChunk(buf) {
  if (!session) {
    enqueueAudio(buf);
    return;
  }
  try {
    session.sendAudio(new Uint8Array(buf));
  } catch (err) {
    enqueueAudio(buf);
    const msg = err && err.message ? err.message : String(err);
    if (shouldLogStreamErrorNow()) {
      logError("sendAudio failed:", msg);
    }
    if (msg.includes('session is in "error" state')) {
      scheduleRecover(500);
    }
  }
}

function flushPendingAudio() {
  if (!session || pendingAudioChunks.length === 0) {
    return;
  }
  const chunks = pendingAudioChunks;
  pendingAudioChunks = [];
  pendingAudioBytes = 0;
  for (const c of chunks) {
    try {
      session.sendAudio(new Uint8Array(c));
    } catch (err) {
      enqueueAudio(c);
      logError("pending flush failed:", err && err.message ? err.message : String(err));
      break;
    }
  }
}

function processResult(result) {
  if (!result || !Array.isArray(result.tokens)) {
    return;
  }
  for (const token of result.tokens) {
    if (!token || !token.text) {
      continue;
    }
    if (token.is_final === false) {
      continue;
    }
    const startMs =
      safeNumber(token.start_ms) ??
      safeNumber(token.startMs) ??
      safeNumber(token.end_ms) ??
      safeNumber(token.endMs) ??
      0;
    const endMs =
      safeNumber(token.end_ms) ??
      safeNumber(token.endMs) ??
      startMs;
    const dedupeKey = `${startMs}:${endMs}:${token.text}`;
    if (recentTokenKeys.has(dedupeKey)) {
      continue;
    }
    recentTokenKeys.add(dedupeKey);
    recentTokenQueue.push(dedupeKey);
    if (recentTokenQueue.length > MAX_RECENT_TOKENS) {
      const stale = recentTokenQueue.shift();
      recentTokenKeys.delete(stale);
    }
    const minuteKey = minuteKeyFromEpochMs(sessionBaseEpochMs + startMs);
    appendTokenText(minuteKey, String(token.text));
  }
}

async function closeSessionGracefully() {
  if (!session) return;
  const s = session;
  session = null;
  const methods = ["finish", "close", "disconnect", "end"];
  for (const m of methods) {
    if (typeof s[m] === "function") {
      try {
        await s[m]();
      } catch (err) {
        logError(`${m} failed:`, err && err.message ? err.message : String(err));
      }
      return;
    }
  }
}

async function createSession() {
  if (!sonioxApiKey) {
    throw new Error("SONIOX_API_KEY is required");
  }

  const wsUrl = SONIOX_API_WS_URL;
  if (configuredLanguageHints === null) {
    configuredLanguageHints = parseLanguageHints();
  }
  const languageHints = disableLanguageHints ? null : configuredLanguageHints;
  const sessionConfig = {
    model: "stt-rt-v4",
    audio_format: "pcm_s16le",
    sample_rate: SAMPLE_RATE,
    num_channels: 1,
  };
  if (languageHints) {
    sessionConfig.language_hints = languageHints;
  }
  const s = new RealtimeSttSession(sonioxApiKey, wsUrl, sessionConfig);

  s.on("connected", () => {
    log("Soniox session started");
    if (languageHints) {
      log("language_hints:", JSON.stringify(languageHints));
    }
  });
  s.on("result", (result) => {
    processResult(result);
  });
  s.on("error", (err) => {
    const msg = err && err.message ? err.message : String(err);
    logError("Soniox session error:", msg);
    if (msg.toLowerCase().includes("invalid language hint")) {
      disableLanguageHints = true;
      logError("Disabling language_hints and reconnecting.");
    }
    scheduleRecover(500);
  });
  s.on("finished", () => {
    log("Soniox session finished");
  });
  s.on("disconnected", (reason) => {
    log("Soniox session disconnected", reason ? `reason=${reason}` : "");
  });

  await s.connect();
  session = s;
  sessionBaseEpochMs = Date.now();
  writeState({ sessionStartedAt: nowIso() });
  flushPendingAudio();
}

async function rotateSession() {
  if (rotating || shuttingDown) return;
  rotating = true;
  try {
    log("Rotating Soniox session");
    await closeSessionGracefully();
    await createSession();
  } catch (err) {
    logError("rotateSession failed:", err && err.message ? err.message : String(err));
  } finally {
    rotating = false;
  }
}

function startAudioCapture() {
  const ac = resolveAudioCommand();
  log("Audio source:", ac.source, ac.cmd, ...ac.args);
  audioProc = spawn(ac.cmd, ac.args, {
    stdio: ["ignore", "pipe", "pipe"],
    env: baseChildEnv,
  });

  audioProc.stdout.on("data", (chunk) => {
    streamAudioChunk(chunk);
  });

  audioProc.stderr.on("data", (data) => {
    const msg = String(data).trim();
    if (msg) {
      logError("audio stderr:", msg);
    }
  });

  audioProc.on("exit", (code, signal) => {
    if (!shuttingDown) {
      logError(`audio process exited unexpectedly code=${code} signal=${signal}`);
    }
  });
}

async function shutdown(exitCode = 0) {
  if (shuttingDown) return;
  shuttingDown = true;
  if (reconnectTimer) clearInterval(reconnectTimer);
  if (flushTimer) clearInterval(flushTimer);
  if (stateTimer) clearInterval(stateTimer);
  if (recoverTimer) clearTimeout(recoverTimer);

  try {
    if (audioProc && !audioProc.killed) {
      audioProc.kill("SIGTERM");
    }
  } catch (err) {
    logError("audioProc.kill failed:", String(err));
  }

  await closeSessionGracefully();
  flushJournal();
  writeState({ running: false, stoppedAt: nowIso() });
  try {
    if (fs.existsSync(paths.pid)) {
      fs.unlinkSync(paths.pid);
    }
  } catch (err) {
    logError("unlink pid failed:", String(err));
  }
  process.exit(exitCode);
}

const startedAtIso = nowIso();

async function main() {
  ensureDir();
  atomicWrite(paths.pid, String(process.pid));
  writeState();
  log("Voice journal daemon starting", `pid=${process.pid}`);

  startAudioCapture();
  await createSession();
  flushJournal();

  reconnectTimer = setInterval(() => {
    rotateSession().catch((err) => {
      logError("reconnect timer error:", String(err));
    });
  }, RECONNECT_MS);

  flushTimer = setInterval(() => {
    try {
      flushJournal();
    } catch (err) {
      logError("flushJournal error:", String(err));
    }
  }, FLUSH_INTERVAL_MS);

  stateTimer = setInterval(() => {
    writeState();
  }, 5000);

  process.on("SIGTERM", () => {
    shutdown(0).catch(() => process.exit(1));
  });
  process.on("SIGINT", () => {
    shutdown(0).catch(() => process.exit(1));
  });
}

main().catch((err) => {
  try {
    ensureDir();
    logError("fatal:", err && err.stack ? err.stack : String(err));
    writeState({ running: false, fatalError: String(err) });
    if (fs.existsSync(paths.pid)) fs.unlinkSync(paths.pid);
  } catch (_) {
    // Ignore secondary failures while failing fast.
  }
  process.exit(1);
});
