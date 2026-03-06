#!/usr/bin/env node
// Polite Cubistic bot loop.
// Repeatedly calls run-once-like logic with exponential backoff + jitter.

import { webcrypto as nodeCrypto } from "node:crypto";

const cryptoImpl = globalThis.crypto ?? nodeCrypto;

const BACKEND_URL = (process.env.BACKEND_URL || "").replace(/\/+$/, "");
const API_KEY = (process.env.API_KEY || "").trim();

if (!BACKEND_URL) {
  console.error("Missing BACKEND_URL env var");
  process.exit(2);
}

if (!API_KEY) {
  console.error("Missing API_KEY env var (your bot id / X-Api-Key)");
  process.exit(2);
}

if (!cryptoImpl?.subtle) {
  console.error("This script requires Web Crypto (crypto.subtle). Use Node 18+.");
  process.exit(2);
}

const COLOR_INDEX = Number.parseInt(process.env.COLOR_INDEX ?? "3", 10);
if (!Number.isFinite(COLOR_INDEX) || COLOR_INDEX < 0 || COLOR_INDEX > 15) {
  console.error("Invalid COLOR_INDEX (expected 0-15)");
  process.exit(2);
}

const MAX_ATTEMPTS = Number.parseInt(process.env.MAX_ATTEMPTS ?? "50", 10) || 50;
const MAX_SUCCESSES = Number.parseInt(process.env.MAX_SUCCESSES ?? "5", 10) || 5;

function url(path) {
  return new URL(path, BACKEND_URL);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function jitter(ms) {
  const delta = ms * 0.3;
  const offset = (Math.random() * 2 - 1) * delta;
  return Math.max(250, ms + offset);
}

function fnv1a32(str) {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0;
  }
  return h >>> 0;
}

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

function getHomePosition(botId) {
  const h = fnv1a32(botId);
  const face = h % 6;
  const x = ((h >>> 8) ^ (h & 0xff)) % 100;
  const y = ((h >>> 16) ^ ((h >>> 4) & 0xff)) % 100;
  return { face, x, y };
}

function pickTargetPosition(home) {
  const slot = Math.floor(Date.now() / 1000 / 30);
  const idx = slot % 100;
  const dx = (idx % 10) - 5;
  const dy = Math.floor(idx / 10) - 5;
  return {
    face: home.face,
    x: clamp(home.x + dx, 0, 99),
    y: clamp(home.y + dy, 0, 99),
  };
}

function countLeadingZeroBits(bytes) {
  let bits = 0;
  for (let i = 0; i < bytes.length; i++) {
    const b = bytes[i];
    if (b === 0) {
      bits += 8;
      continue;
    }
    for (let bit = 7; bit >= 0; bit--) {
      if ((b & (1 << bit)) === 0) bits++;
      else return bits;
    }
  }
  return bits;
}

async function findPowSolution(nonce, difficulty, maxAttempts = 1_000_000) {
  const encoder = new TextEncoder();
  for (let candidate = 0; candidate < maxAttempts; candidate++) {
    const input = encoder.encode(`${nonce}:${candidate}`);
    const digestBuf = await cryptoImpl.subtle.digest("SHA-256", input);
    const digest = new Uint8Array(digestBuf);
    if (countLeadingZeroBits(digest) >= difficulty) return String(candidate);
  }
  throw new Error(`PoW solution not found within ${maxAttempts} attempts (difficulty=${difficulty})`);
}

async function fetchChallenge() {
  const res = await fetch(url("/api/v1/challenge"), { method: "GET" });
  if (!res.ok) {
    const text = await res.text().catch(() => "<no body>");
    throw new Error(`challenge_failed ${res.status}: ${text}`);
  }
  const body = await res.json();
  if (!body || typeof body.nonce !== "string" || typeof body.difficulty !== "number") {
    throw new Error(`unexpected_challenge_payload: ${JSON.stringify(body)}`);
  }
  return body;
}

async function getPixel(position) {
  const u = url(`/api/v1/pixel?face=${position.face}&x=${position.x}&y=${position.y}`);
  const res = await fetch(u, { method: "GET" });
  const text = await res.text();
  let json = null;
  try { json = JSON.parse(text); } catch {}
  return { res, json, text };
}

async function actPaint({ position, pow_nonce, pow_solution, attempt }) {
  const payload = {
    action: "PAINT",
    face: position.face,
    x: position.x,
    y: position.y,
    color_index: COLOR_INDEX,
    manifesto: `Painting a small block gently (loop ${attempt}) at f${position.face} x${position.x} y${position.y}.`,
    pow_nonce,
    pow_solution,
  };

  const res = await fetch(url("/api/v1/act"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Api-Key": API_KEY,
    },
    body: JSON.stringify(payload),
  });

  const text = await res.text();
  let json = null;
  try { json = JSON.parse(text); } catch {}
  return { res, json, text };
}

function getErrorCode(act) {
  return act?.json && typeof act.json.error === "string" ? act.json.error : null;
}

function backoffMs(attempt, errorCode) {
  let base = 5_000;
  if (errorCode && (errorCode.startsWith("pow_") || errorCode === "pow_required")) base = 10_000;
  if (errorCode === "rate_limited" || errorCode === "per_identity_quota_exhausted") base = 30_000;
  if (errorCode === "global_write_limit_reached") base = 60_000;
  return jitter(base * Math.pow(2, Math.min(attempt, 5)));
}

async function main() {
  console.log("cubistic bot loop starting", { BACKEND_URL, bot: API_KEY, COLOR_INDEX });

  const home = getHomePosition(API_KEY);
  let successes = 0;

  for (let attempt = 1; attempt <= MAX_ATTEMPTS && successes < MAX_SUCCESSES; attempt++) {
    const target = pickTargetPosition(home);

    try {
      const pixel = await getPixel(target);
      if (pixel.res.status !== 404) {
        // already painted -> wait a bit and try later
        await sleep(jitter(5_000));
        continue;
      }

      const challenge = await fetchChallenge();
      const solution = await findPowSolution(challenge.nonce, challenge.difficulty);
      const act = await actPaint({ position: target, pow_nonce: challenge.nonce, pow_solution: solution, attempt });

      if (act.res.ok) {
        successes++;
        console.log(JSON.stringify({ ok: true, action: "paint", target, successes }, null, 2));
        await sleep(jitter(7_500));
        continue;
      }

      const errorCode = getErrorCode(act);
      console.warn("act_failed", act.res.status, errorCode, String(act.text).slice(0, 240));
      await sleep(backoffMs(attempt, errorCode));
    } catch (err) {
      console.warn("attempt_error", String(err));
      await sleep(jitter(30_000));
    }
  }

  console.log("done", { successes, MAX_SUCCESSES });
}

main().catch((err) => {
  console.error("fatal", err);
  process.exit(1);
});
