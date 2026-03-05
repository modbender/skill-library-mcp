#!/usr/bin/env node

/**
 * Agent Postcard — Send an AI-generated postcard from your Clawbot.
 *
 * Usage:
 *   node send-postcard.mjs --location "Tokyo, Japan" --style vintage
 *   node send-postcard.mjs --location "Paris" --style ghibli --message "Bonjour!"
 *   node send-postcard.mjs --selfie "A robot cat with goggles" --location "Iceland" --style watercolor
 *
 * Environment:
 *   TURAI_API_KEY  — Required. Your Turai API key.
 */

import { readFile, writeFile, access } from "node:fs/promises";
import { resolve, join } from "node:path";
import { parseArgs } from "node:util";

// ---------------------------------------------------------------------------
// CLI args
// ---------------------------------------------------------------------------

const { values: args } = parseArgs({
  options: {
    location:  { type: "string", short: "l" },
    style:     { type: "string", short: "s", default: "vintage" },
    message:   { type: "string", short: "m", default: "" },
    selfie:    { type: "string" },
    persona:   { type: "string", short: "p" },   // path to persona file
    output:    { type: "string", short: "o" },    // output path for image
    post:      { type: "boolean", default: false },  // post to Moltbook (future)
    help:      { type: "boolean", short: "h", default: false },
  },
  strict: true,
});

if (args.help) {
  console.log(`
Agent Postcard — Send AI-generated postcards from your Clawbot

Options:
  -l, --location <place>   Location for the postcard backdrop (required)
  -s, --style <style>      Art style (default: vintage)
      --selfie <prompt>    Custom selfie prompt (skips persona auto-read)
  -p, --persona <path>     Path to persona file (default: auto-detect SOUL.md / IDENTITY.md)
  -m, --message <text>     Message on the postcard
  -o, --output <path>      Save image to this path (default: postcard-<timestamp>.png)
      --post               Post to Moltbook after generating (placeholder)
  -h, --help               Show this help

Styles: vintage, watercolor, modern, cinematic, minimalist, artistic,
        ghibli, oil_painting, sketch, pop_art, impressionist, retro_cartoon

Environment:
  TURAI_API_KEY            Your Turai API key (required)
`);
  process.exit(0);
}

const VALID_STYLES = [
  "vintage", "watercolor", "modern", "cinematic", "minimalist", "artistic",
  "ghibli", "oil_painting", "sketch", "pop_art", "impressionist", "retro_cartoon",
];

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

const apiKey = process.env.TURAI_API_KEY;
if (!apiKey) {
  console.error("Error: TURAI_API_KEY environment variable is not set.");
  console.error("Get a key at https://turai.org and export TURAI_API_KEY=your-key");
  process.exit(1);
}

if (!args.location) {
  console.error("Error: --location is required. Example: --location \"Tokyo, Japan\"");
  process.exit(1);
}

if (!VALID_STYLES.includes(args.style)) {
  console.error(`Error: Invalid style "${args.style}". Valid styles: ${VALID_STYLES.join(", ")}`);
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Persona → selfie prompt
// ---------------------------------------------------------------------------

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || resolve(process.cwd());

async function fileExists(p) {
  try { await access(p); return true; } catch { return false; }
}

async function readPersona() {
  if (args.selfie) return args.selfie;

  // Try explicit path first, then standard locations
  const candidates = args.persona
    ? [resolve(args.persona)]
    : [
        join(WORKSPACE, "SOUL.md"),
        join(WORKSPACE, "IDENTITY.md"),
        join(WORKSPACE, "..", "SOUL.md"),
      ];

  for (const p of candidates) {
    if (await fileExists(p)) {
      const content = await readFile(p, "utf-8");
      return extractSelfiePrompt(content);
    }
  }

  console.warn("Warning: No persona file found. Using generic selfie prompt.");
  return "A friendly AI assistant robot with a warm smile";
}

function extractSelfiePrompt(personaText) {
  // Take the first ~500 chars of meaningful content, strip markdown headers
  const lines = personaText
    .split("\n")
    .filter((l) => !l.startsWith("#") && l.trim().length > 0)
    .slice(0, 10);

  const description = lines.join(" ").slice(0, 500).trim();

  if (description.length < 20) {
    return "A friendly AI assistant with a distinctive personality";
  }

  // Wrap it as a selfie prompt — the API will interpret this
  return `Based on this persona, generate a selfie of this character: ${description}`;
}

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------

async function sendPostcard({ selfiePrompt, location, style, message }) {
  const url = "https://turai.org/api/agent/postcard";

  const body = {
    selfiePrompt,
    location,
    style,
    ...(message && { message }),
  };

  console.log(`📮 Sending postcard request...`);
  console.log(`   Location: ${location}`);
  console.log(`   Style:    ${style}`);
  console.log(`   Message:  ${message || "(none)"}`);

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "Content-Type": "application/json",
      Accept: "application/json, image/png, image/*",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => "(no body)");
    throw new Error(`API error ${res.status}: ${errText}`);
  }

  const contentType = res.headers.get("content-type") || "";

  // If response is JSON, extract image URL or base64
  if (contentType.includes("application/json")) {
    const data = await res.json();
    console.log("📬 API response (JSON):", JSON.stringify(data, null, 2));
    return data;
  }

  // If response is binary image, return as buffer
  const buffer = Buffer.from(await res.arrayBuffer());
  return { imageBuffer: buffer, contentType };
}

// ---------------------------------------------------------------------------
// Save output
// ---------------------------------------------------------------------------

async function saveImage(result) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const defaultName = `postcard-${timestamp}.png`;
  const outPath = args.output ? resolve(args.output) : resolve(WORKSPACE, defaultName);

  if (result.imageBuffer) {
    await writeFile(outPath, result.imageBuffer);
    console.log(`🖼️  Saved postcard to: ${outPath}`);
    return outPath;
  }

  // JSON response — try to download image URL
  const imageUrl = result.imageUrl || result.image_url || result.url;
  if (imageUrl) {
    console.log(`⬇️  Downloading image from: ${imageUrl}`);
    const imgRes = await fetch(imageUrl);
    if (!imgRes.ok) throw new Error(`Failed to download image: ${imgRes.status}`);
    const buf = Buffer.from(await imgRes.arrayBuffer());
    await writeFile(outPath, buf);
    console.log(`🖼️  Saved postcard to: ${outPath}`);
    return outPath;
  }

  // If base64
  const b64 = result.image || result.imageBase64;
  if (b64) {
    const buf = Buffer.from(b64, "base64");
    await writeFile(outPath, buf);
    console.log(`🖼️  Saved postcard to: ${outPath}`);
    return outPath;
  }

  console.log("ℹ️  No image in response. Full response logged above.");
  return null;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const selfiePrompt = await readPersona();
  console.log(`🤳 Selfie prompt: ${selfiePrompt.slice(0, 120)}...`);

  const result = await sendPostcard({
    selfiePrompt,
    location: args.location,
    style: args.style,
    message: args.message,
  });

  const savedPath = await saveImage(result);

  if (args.post && savedPath) {
    console.log("📢 --post flag set. Moltbook integration is a placeholder for now.");
    // Future: POST to Moltbook or send via messaging channel
  }

  console.log("✅ Done!");
}

main().catch((err) => {
  console.error("❌ Error:", err.message);
  process.exit(1);
});
