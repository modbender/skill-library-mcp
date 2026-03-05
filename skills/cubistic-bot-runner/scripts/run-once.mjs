#!/usr/bin/env node
// Polite Cubistic bot runner: paint once (only if target pixel is Void).
//
// Env:
//   BACKEND_URL (required)
//   API_KEY     (required) -> sent as X-Api-Key
//   COLOR_INDEX (0-15, default 3)
//
// Strategy:
// - Pick a deterministic position for this bot that changes slowly over time.
// - If the pixel is already painted, do nothing.
// - Otherwise: GET /challenge -> solve PoW -> POST /act.

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

function url(path) {
  return new URL(path, BACKEND_URL);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function jitter(ms) {
  const delta = ms * 0.3;
  const offset = (Math.random() * 2 - 1) * delta;
  return Math.max(100, ms + offset);
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
  // Deterministic 10x10 block around home over time.
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

async function actPaint({ position, pow_nonce, pow_solution }) {
  const payload = {
    action: "PAINT",
    face: position.face,
    x: position.x,
    y: position.y,
    color_index: COLOR_INDEX,
    manifesto: `Painting a small block gently at f${position.face} x${position.x} y${position.y}.`,
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

async function main() {
  const home = getHomePosition(API_KEY);
  const target = pickTargetPosition(home);

  const pixel = await getPixel(target);
  if (pixel.res.status !== 404) {
    console.log(JSON.stringify({ ok: true, action: "noop", reason: "pixel_already_painted", target }, null, 2));
    return;
  }

  // PoW
  const challenge = await fetchChallenge();
  const solution = await findPowSolution(challenge.nonce, challenge.difficulty);

  const act = await actPaint({ position: target, pow_nonce: challenge.nonce, pow_solution: solution });
  if (!act.res.ok) {
    console.error("ACT_FAILED", act.res.status, (act.json ?? act.text));
    process.exit(1);
  }

  // tiny pause to avoid immediate repeat if called in a tight loop
  await sleep(jitter(250));

  console.log(JSON.stringify({ ok: true, action: "paint", target, result: act.json ?? act.text }, null, 2));
}

main().catch((err) => {
  console.error("fatal", err);
  process.exit(1);
});
