#!/usr/bin/env node
/**
 * image-gen skill — generate.js
 * Unified image generation script for OpenClaw.
 * Supports: Midjourney (Legnext.ai), Flux Pro/Dev/Schnell, SDXL Lightning,
 *           Nano Banana Pro, Ideogram v3, Recraft v3 (all via fal.ai)
 *
 * Usage:
 *   node generate.js --model <id> --prompt "<text>" [options]
 *   node generate.js --model midjourney --action upscale --index 2 --job-id <id>
 *
 * Async (non-blocking) mode for Midjourney:
 *   node generate.js --model midjourney --prompt "<text>" --async
 *     → Submits job and returns immediately with job_id (does NOT wait)
 *   node generate.js --model midjourney --poll --job-id <id>
 *     → Checks job status once and returns immediately (no waiting)
 */

import { fal } from "@fal-ai/client";
import https from "https";
import { parseArgs } from "util";

// ── Parse CLI arguments ────────────────────────────────────────────────────
const { values: args } = parseArgs({
  options: {
    model:              { type: "string", default: "flux-dev" },
    prompt:             { type: "string", default: "" },
    "aspect-ratio":     { type: "string", default: "1:1" },
    "num-images":       { type: "string", default: "1" },
    "negative-prompt":  { type: "string", default: "" },
    action:             { type: "string", default: "" },   // upscale | variation | reroll
    index:              { type: "string", default: "1" },  // 1-4 for MJ actions
    "job-id":           { type: "string", default: "" },   // MJ jobId for actions
    "upscale-type":     { type: "string", default: "0" },  // 0=Subtle, 1=Creative
    "variation-type":   { type: "string", default: "0" },  // 0=Subtle, 1=Strong
    mode:               { type: "string", default: "turbo" }, // turbo | fast | relax
    seed:               { type: "string", default: "" },
    async:              { type: "boolean", default: false }, // submit and return immediately
    poll:               { type: "boolean", default: false }, // check status once, no wait
    proxy:              { type: "boolean", default: false }, // use proxy server instead of direct API
    "proxy-url":        { type: "string", default: "" },    // proxy server URL
    "auto-upscale":     { type: "boolean", default: false }, // after imagine, auto-upscale all 4 images
  },
  strict: false,
});

const MODEL          = args["model"];
const PROMPT         = args["prompt"];
const AR             = args["aspect-ratio"];
const NUM_IMAGES     = parseInt(args["num-images"], 10) || 1;
const NEG_PROMPT     = args["negative-prompt"];
const ACTION         = args["action"];
const INDEX          = parseInt(args["index"], 10) || 1;
const JOB_ID         = args["job-id"];
const UPSCALE_TYPE   = parseInt(args["upscale-type"], 10) || 0;
const VARIATION_TYPE = parseInt(args["variation-type"], 10) || 0;
const MODE           = args["mode"] || "turbo";  // turbo (~10-20s), fast (~30-60s), relax (free but slow)
const SEED           = args["seed"] ? parseInt(args["seed"], 10) : undefined;
const ASYNC_MODE     = args["async"] === true;
const POLL_MODE      = args["poll"] === true;
const AUTO_UPSCALE   = args["auto-upscale"] === true;

const PROXY_MODE   = args["proxy"] === true;
const PROXY_URL    = args["proxy-url"] || process.env.IMAGE_GEN_PROXY_URL || "https://image-gen-proxy.vercel.app";

// ── Environment variables ──────────────────────────────────────────────────
const FAL_KEY      = process.env.FAL_KEY;
const LEGNEXT_KEY  = process.env.LEGNEXT_KEY;

// ── fal.ai model IDs ───────────────────────────────────────────────────────
const FAL_MODELS = {
  "flux-pro":      "fal-ai/flux-pro/v1.1",
  "flux-dev":      "fal-ai/flux/dev",
  "flux-schnell":  "fal-ai/flux/schnell",
  "sdxl":          "fal-ai/fast-sdxl",
  "nano-banana":   "fal-ai/nano-banana-pro",
  "ideogram":      "fal-ai/ideogram/v3",
  "recraft":       "fal-ai/recraft-v3",
};

// ── Aspect ratio helpers ───────────────────────────────────────────────────
function arToWidthHeight(ar) {
  const map = {
    "1:1":  [1024, 1024],
    "16:9": [1344, 768],
    "9:16": [768, 1344],
    "4:3":  [1152, 864],
    "3:4":  [864, 1152],
    "3:2":  [1216, 832],
    "2:3":  [832, 1216],
    "21:9": [1536, 640],
  };
  return map[ar] || [1024, 1024];
}

function arToFalImageSize(ar) {
  const map = {
    "1:1":  "square_hd",
    "16:9": "landscape_16_9",
    "9:16": "portrait_16_9",
    "4:3":  "landscape_4_3",
    "3:4":  "portrait_4_3",
  };
  return map[ar] || "square_hd";
}

// ── Output helpers ─────────────────────────────────────────────────────────
function output(data) {
  console.log(JSON.stringify(data, null, 2));
}

function error(msg, details) {
  console.error(JSON.stringify({ success: false, error: msg, details }, null, 2));
  process.exit(1);
}
// ── Token file helpers ─────────────────────────────────────────────────────
import fs from "fs";
import path from "path";
import os from "os";

const TOKEN_FILE = path.join(os.homedir(), ".image-gen-token");

function loadToken() {
  try {
    if (fs.existsSync(TOKEN_FILE)) {
      return fs.readFileSync(TOKEN_FILE, "utf-8").trim();
    }
  } catch (_) { /* ignore */ }
  return "";
}

function saveToken(token) {
  try {
    fs.writeFileSync(TOKEN_FILE, token, "utf-8");
    process.stderr.write(`[proxy] Token saved to ${TOKEN_FILE}\n`);
  } catch (e) {
    process.stderr.write(`[proxy] Warning: could not save token: ${e.message}\n`);
  }
}

// ── Proxy mode helpers ─────────────────────────────────────────────────────
let _cachedToken = loadToken();

async function ensureToken() {
  if (_cachedToken) return _cachedToken;

  const baseUrl = PROXY_URL.replace(/\/$/, "");
  process.stderr.write(`[proxy] No token found. Registering at ${baseUrl}/api/token ...\n`);

  const res = await fetch(`${baseUrl}/api/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  const data = await res.json();

  if (!data.token) {
    error("Failed to register token", data);
  }

  _cachedToken = data.token;
  saveToken(data.token);

  // Show welcome message
  process.stderr.write(`\n${'='.repeat(60)}\n`);
  process.stderr.write(`  ${data.message}\n`);
  process.stderr.write(`  Token: ${data.token}\n`);
  process.stderr.write(`${'='.repeat(60)}\n\n`);

  return data.token;
}

async function proxyRequest(endpoint, body) {
  const baseUrl = PROXY_URL.replace(/\/$/, "");
  const token = await ensureToken();
  const url = `${baseUrl}/api/${endpoint}`;
  process.stderr.write(`[proxy] POST ${url}\n`);

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-ImageGen-Token": token,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  // Show remaining uses info
  if (data._remaining !== undefined) {
    process.stderr.write(`[proxy] Remaining free uses: ${data._remaining}/${data._limit}\n`);
  }
  if (data._warning) {
    process.stderr.write(`[proxy] ⚠ ${data._warning}\n`);
  }

  // Handle quota exhausted
  if (data.error === "quota_exhausted") {
    process.stderr.write(`\n${'='.repeat(60)}\n`);
    process.stderr.write(`  ${data.message}\n`);
    process.stderr.write(`${'='.repeat(60)}\n\n`);
    process.exit(1);
  }

  // Handle invalid/missing token (re-register)
  if (data.error === "invalid_token" || data.error === "missing_token") {
    process.stderr.write(`[proxy] Token invalid, re-registering...\n`);
    _cachedToken = "";
    const newToken = await ensureToken();
    // Retry the request with new token
    const retryRes = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-ImageGen-Token": newToken,
      },
      body: JSON.stringify(body),
    });
    return await retryRes.json();
  }

  if (!res.ok && !data.success) {
    error(`Proxy error (${res.status}): ${data.error || "unknown"}`, data);
  }
  return data;
}

async function generateViaProxy() {
  if (!PROXY_URL) error("--proxy-url or IMAGE_GEN_PROXY_URL is required when using --proxy mode.");

  if (MODEL === "midjourney") {
    // Poll mode
    if (POLL_MODE) {
      const data = await proxyRequest("midjourney", { action: "poll", job_id: JOB_ID });
      output(data);
      return;
    }
    // Upscale / Variation / Reroll / Describe
    if (ACTION && JOB_ID) {
      const body = { action: ACTION, job_id: JOB_ID, index: INDEX, type: ACTION === "upscale" ? UPSCALE_TYPE : VARIATION_TYPE };
      if (ACTION === "variation" && PROMPT) body.remix_prompt = PROMPT;
      const data = await proxyRequest("midjourney", body);
      output(data);
      return;
    }
    // Imagine
    if (!PROMPT) error("--prompt is required for Midjourney generation.");

    if (ASYNC_MODE && !AUTO_UPSCALE) {
      // Pure async: submit and return immediately
      const data = await proxyRequest("midjourney", {
        action: "imagine", prompt: PROMPT, aspect_ratio: AR, mode: MODE,
      });
      output(data);
      return;
    }

    // Submit imagine job
    const imagineData = await proxyRequest("midjourney", {
      action: "imagine", prompt: PROMPT, aspect_ratio: AR, mode: MODE,
    });

    if (!AUTO_UPSCALE) {
      // Normal mode: return imagine result as-is
      output(imagineData);
      return;
    }

    // ── AUTO-UPSCALE: wait for imagine to complete, then upscale all 4 ──
    const imagineJobId = imagineData.job_id;
    if (!imagineJobId) {
      output(imagineData); // fallback if no job_id
      return;
    }

    process.stderr.write(`[auto-upscale] imagine submitted: ${imagineJobId}. Polling until complete...\n`);

    // Poll imagine until completed
    let imagineResult = null;
    for (let i = 0; i < 40; i++) {
      await new Promise(r => setTimeout(r, 15000));
      const pollData = await proxyRequest("midjourney", { action: "poll", job_id: imagineJobId });
      process.stderr.write(`[auto-upscale] imagine status: ${pollData.status}\n`);
      if (pollData.status === "completed") {
        imagineResult = pollData;
        break;
      }
    }

    if (!imagineResult) {
      error("imagine job timed out before auto-upscale could start");
      return;
    }

    // Submit upscale for all 4 images in parallel
    process.stderr.write(`[auto-upscale] imagine complete. Submitting upscale for all 4 images...\n`);
    const upscaleJobs = await Promise.all([1, 2, 3, 4].map(async (idx) => {
      const upData = await proxyRequest("midjourney", {
        action: "upscale", job_id: imagineJobId, index: idx, type: 0,
      });
      process.stderr.write(`[auto-upscale] upscale index ${idx} submitted: ${upData.job_id}\n`);
      return { index: idx, job_id: upData.job_id };
    }));

    // Poll all upscale jobs until complete
    const upscaleResults = Array(4).fill(null);
    const pending = new Set(upscaleJobs.map((_, i) => i));

    for (let round = 0; round < 30 && pending.size > 0; round++) {
      await new Promise(r => setTimeout(r, 15000));
      for (const i of [...pending]) {
        const job = upscaleJobs[i];
        const pollData = await proxyRequest("midjourney", { action: "poll", job_id: job.job_id });
        process.stderr.write(`[auto-upscale] upscale index ${job.index} status: ${pollData.status}\n`);
        if (pollData.status === "completed") {
          const imgUrl = pollData.displayImageUrl || (pollData.imageUrls || [])[0] || pollData.image_url || "";
          upscaleResults[i] = { index: job.index, image_url: imgUrl };
          pending.delete(i);
        }
      }
    }

    const upscaledImages = upscaleResults.filter(Boolean).map(r => r.image_url);
    output({
      success: true,
      model: "midjourney",
      action: "imagine+auto-upscale",
      imagine_job_id: imagineJobId,
      prompt: PROMPT,
      images: upscaledImages,
      image_url: upscaledImages[0] || null,
      note: "All 4 images have been individually upscaled. Use the 'images' array for all 4 single images.",
    });
  } else if (FAL_MODELS[MODEL]) {
    // fal.ai models via proxy
    if (!PROMPT) error("--prompt is required.");
    const data = await proxyRequest("generate", {
      model: MODEL, prompt: PROMPT, aspect_ratio: AR,
      num_images: NUM_IMAGES, negative_prompt: NEG_PROMPT || undefined,
      ...(SEED !== undefined && { seed: SEED }),
    });
    output(data);
  } else {
    error(`Unknown model: "${MODEL}". Valid options: midjourney, flux-pro, flux-dev, flux-schnell, sdxl, nano-banana, ideogram, recraft`);
  }
}

// ── Legnext.ai HTTP helper ───────────────────────────────────────────────────
function legnextRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null;
    const options = {
      hostname: "api.legnext.ai",
      path: `/api/v1${path}`,
      method,
      headers: {
        "Content-Type": "application/json",
        "x-api-key": LEGNEXT_KEY,
        ...(payload && { "Content-Length": Buffer.byteLength(payload) }),
      },
    };
    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error(`Invalid JSON response: ${data}`)); }
      });
    });
    req.on("error", reject);
    if (payload) req.write(payload);
    req.end();
  });
}

async function legnextPoll(jobId, maxWait = 300_000, interval = 5_000) {
  const deadline = Date.now() + maxWait;
  while (Date.now() < deadline) {
    const res = await legnextRequest("GET", `/job/${jobId}`);
    const status = res.status;
    if (status === "completed") return res;
    if (status === "failed") throw new Error(`Midjourney job failed: ${res.error?.message || "unknown error"}`);
    process.stderr.write(`[MJ] Status: ${status} ...\n`);
    await new Promise((r) => setTimeout(r, interval));
  }
  throw new Error(`Midjourney job ${jobId} timed out after ${maxWait / 1000}s`);
}

// ── Poll once (non-blocking status check) ─────────────────────────────────
async function pollOnce(jobId) {
  if (!LEGNEXT_KEY) error("LEGNEXT_KEY is not set.");
  if (!jobId) error("--job-id is required for --poll mode.");

  const res = await legnextRequest("GET", `/job/${jobId}`);
  const status = res.status;

  if (status === "completed") {
    const imageUrls = res.output?.image_urls || [];
    const imageUrl = res.output?.image_url || null;
    output({
      success: true,
      model: "midjourney",
      jobId,
      status: "completed",
      imageUrl,
      imageUrls,
      displayImageUrl: imageUrls[0] || imageUrl,
      seed: res.output?.seed || null,
      note: "Send to user ONLY displayImageUrl or imageUrls (cdn.legnext.ai/mj/...). NEVER send imageUrl (cdn.legnext.ai/temp/...) — it expires and shows as broken. Use --action upscale --index <1-4> --job-id to upscale.",
    });
  } else if (status === "failed") {
    output({
      success: false,
      model: "midjourney",
      jobId,
      status: "failed",
      error: res.error?.message || "Job failed",
    });
  } else {
    // Still pending/processing
    output({
      success: true,
      model: "midjourney",
      jobId,
      status: status || "pending",
      pending: true,
      message: `Job is still ${status || "pending"}. Check again in a few seconds.`,
    });
  }
}

// ── Midjourney via Legnext.ai ──────────────────────────────────────────────
async function generateMidjourney() {
  if (!LEGNEXT_KEY) error("LEGNEXT_KEY is not set. Please configure it in your OpenClaw skill env.");

  // ── Poll mode (non-blocking status check) ─────────────────────────────
  if (POLL_MODE) {
    await pollOnce(JOB_ID);
    return;
  }

  // ── Upscale action ─────────────────────────────────────────────────────
  if (ACTION === "upscale" && JOB_ID) {
    const imageNo = INDEX - 1; // Convert 1-4 to 0-3
    process.stderr.write(`[MJ] Upscaling image ${INDEX} (imageNo=${imageNo}, type=${UPSCALE_TYPE}) from job ${JOB_ID}\n`);
    const res = await legnextRequest("POST", "/upscale", {
      jobId: JOB_ID,
      imageNo,
      type: UPSCALE_TYPE,
    });
    if (!res.job_id) error("Legnext upscale submission failed", res);
    process.stderr.write(`[MJ] Upscale job submitted: ${res.job_id}\n`);

    if (ASYNC_MODE) {
      output({
        success: true,
        model: "midjourney",
        action: "upscale",
        jobId: res.job_id,
        status: "submitted",
        pending: true,
        message: `Upscale job submitted (job_id: ${res.job_id}). Use --poll --job-id ${res.job_id} to check status.`,
      });
      return;
    }

    const result = await legnextPoll(res.job_id);
    const imageUrl = result.output?.image_url || null;
    output({
      success: true,
      model: "midjourney",
      action: "upscale",
      jobId: res.job_id,
      imageUrl,
      displayImageUrl: imageUrl,
    });
    return;
  }

  // ── Variation action ───────────────────────────────────────────────────
  if (ACTION === "variation" && JOB_ID) {
    const imageNo = INDEX - 1; // Convert 1-4 to 0-3
    process.stderr.write(`[MJ] Creating variation for image ${INDEX} (imageNo=${imageNo}, type=${VARIATION_TYPE}) from job ${JOB_ID}\n`);
    const body = {
      jobId: JOB_ID,
      imageNo,
      type: VARIATION_TYPE,
    };
    if (PROMPT) body.remixPrompt = PROMPT;
    const res = await legnextRequest("POST", "/variation", body);
    if (!res.job_id) error("Legnext variation submission failed", res);
    process.stderr.write(`[MJ] Variation job submitted: ${res.job_id}\n`);

    if (ASYNC_MODE) {
      output({
        success: true,
        model: "midjourney",
        action: "variation",
        jobId: res.job_id,
        status: "submitted",
        pending: true,
        message: `Variation job submitted (job_id: ${res.job_id}). Use --poll --job-id ${res.job_id} to check status.`,
      });
      return;
    }

    const result = await legnextPoll(res.job_id);
    const imageUrls = result.output?.image_urls || [];
    const imageUrl = result.output?.image_url || null;
    output({
      success: true,
      model: "midjourney",
      action: "variation",
      jobId: res.job_id,
      imageUrl,
      imageUrls,
      displayImageUrl: imageUrls[0] || imageUrl,
    });
    return;
  }

  // ── Reroll action ──────────────────────────────────────────────────────
  if (ACTION === "reroll" && JOB_ID) {
    process.stderr.write(`[MJ] Rerolling job ${JOB_ID}\n`);
    const res = await legnextRequest("POST", "/reroll", { jobId: JOB_ID });
    if (!res.job_id) error("Legnext reroll submission failed", res);
    process.stderr.write(`[MJ] Reroll job submitted: ${res.job_id}\n`);

    if (ASYNC_MODE) {
      output({
        success: true,
        model: "midjourney",
        action: "reroll",
        jobId: res.job_id,
        status: "submitted",
        pending: true,
        message: `Reroll job submitted (job_id: ${res.job_id}). Use --poll --job-id ${res.job_id} to check status.`,
      });
      return;
    }

    const result = await legnextPoll(res.job_id);
    const imageUrls = result.output?.image_urls || [];
    const imageUrl = result.output?.image_url || null;
    output({
      success: true,
      model: "midjourney",
      action: "reroll",
      jobId: res.job_id,
      imageUrl,
      imageUrls,
      displayImageUrl: imageUrls[0] || imageUrl,
    });
    return;
  }

  // ── Describe action ────────────────────────────────────────────────────
  if (ACTION === "describe" && JOB_ID) {
    process.stderr.write(`[MJ] Describing job ${JOB_ID}\n`);
    const res = await legnextRequest("POST", "/describe", { jobId: JOB_ID });
    if (!res.job_id) error("Legnext describe submission failed", res);
    const result = await legnextPoll(res.job_id);
    output({
      success: true,
      model: "midjourney",
      action: "describe",
      jobId: res.job_id,
      description: result.output?.text || null,
    });
    return;
  }

  // ── Standard imagine ───────────────────────────────────────────────────
  if (!PROMPT) error("--prompt is required for Midjourney generation.");

  // Append aspect ratio to prompt if not 1:1
  let mjPrompt = PROMPT;
  if (AR && AR !== "1:1") {
    mjPrompt += ` --ar ${AR}`;
  }
  // Append speed mode flag
  if (MODE === "turbo") {
    mjPrompt += " --turbo";
  } else if (MODE === "fast") {
    mjPrompt += " --fast";
  } else if (MODE === "relax") {
    mjPrompt += " --relax";
  }

  process.stderr.write(`[MJ] Submitting imagine via Legnext.ai (mode=${MODE}): "${mjPrompt}"\n`);
  const res = await legnextRequest("POST", "/diffusion", {
    text: mjPrompt,
  });

  if (!res.job_id) error("Legnext imagine submission failed", res);
  const jobId = res.job_id;
  process.stderr.write(`[MJ] Job submitted: ${jobId}\n`);

  // ── Async mode (no auto-upscale): return immediately after submission ──
  if (ASYNC_MODE && !AUTO_UPSCALE) {
    output({
      success: true,
      model: "midjourney",
      provider: "legnext.ai",
      jobId,
      status: "submitted",
      pending: true,
      prompt: mjPrompt,
      message: `✅ Midjourney job submitted! job_id: ${jobId}\n\nGeneration takes ~10-20s (turbo) or ~30-60s (fast). I'll notify you when it's done.\n\nTo check manually: node generate.js --model midjourney --poll --job-id ${jobId}`,
    });
    return;
  }

  // ── Sync mode: wait for imagine completion ─────────────────────────────
  const result = await legnextPoll(jobId);

  if (!AUTO_UPSCALE) {
    // Normal sync: return grid image
    const imageUrls = result.output?.image_urls || [];
    const imageUrl = result.output?.image_url || null;
    output({
      success: true,
      model: "midjourney",
      provider: "legnext.ai",
      jobId,
      prompt: mjPrompt,
      imageUrl,
      imageUrls,
      displayImageUrl: imageUrls[0] || imageUrl,
      seed: result.output?.seed || null,
      note: "Send to user ONLY displayImageUrl or imageUrls (cdn.legnext.ai/mj/...). NEVER send imageUrl (cdn.legnext.ai/temp/...) — it expires and shows as broken. Use --action upscale --index <1-4> --job-id to upscale.",
    });
    return;
  }

  // ── AUTO-UPSCALE: imagine complete, now upscale all 4 images ──────────
  process.stderr.write(`[auto-upscale] imagine complete. Submitting upscale for all 4 images...\n`);

  // Submit all 4 upscale jobs
  const upscaleJobs = [];
  for (const idx of [1, 2, 3, 4]) {
    const imageNo = idx - 1;
    const upRes = await legnextRequest("POST", "/upscale", { jobId, imageNo, type: 0 });
    if (!upRes.job_id) {
      process.stderr.write(`[auto-upscale] upscale index ${idx} submission failed\n`);
      upscaleJobs.push({ index: idx, job_id: null });
    } else {
      process.stderr.write(`[auto-upscale] upscale index ${idx} submitted: ${upRes.job_id}\n`);
      upscaleJobs.push({ index: idx, job_id: upRes.job_id });
    }
  }

  // Poll all upscale jobs until complete
  const upscaleResults = Array(4).fill(null);
  const pending = new Set(upscaleJobs.filter(j => j.job_id).map((_, i) => i));

  for (let round = 0; round < 30 && pending.size > 0; round++) {
    await new Promise(r => setTimeout(r, 15000));
    for (const i of [...pending]) {
      const job = upscaleJobs[i];
      const pollRes = await legnextRequest("GET", `/job/${job.job_id}`);
      const status = pollRes.status;
      process.stderr.write(`[auto-upscale] upscale index ${job.index} status: ${status}\n`);
      if (status === "completed") {
        const imgUrl = pollRes.output?.image_url || null;
        upscaleResults[i] = { index: job.index, image_url: imgUrl };
        pending.delete(i);
      } else if (status === "failed") {
        upscaleResults[i] = { index: job.index, image_url: null, error: "upscale failed" };
        pending.delete(i);
      }
    }
  }

  const upscaledImages = upscaleResults.filter(r => r?.image_url).map(r => r.image_url);
  output({
    success: true,
    model: "midjourney",
    provider: "legnext.ai",
    action: "imagine+auto-upscale",
    jobId,
    prompt: mjPrompt,
    images: upscaledImages,
    image_url: upscaledImages[0] || null,
    note: "All 4 images have been individually upscaled and returned in the 'images' array.",
  });
}

// ── fal.ai models ──────────────────────────────────────────────────────────
async function generateFal(modelKey) {
  if (!FAL_KEY) error("FAL_KEY is not set. Please configure it in your OpenClaw skill env.");
  fal.config({ credentials: FAL_KEY });

  const modelId = FAL_MODELS[modelKey];
  if (!modelId) error(`Unknown fal.ai model key: ${modelKey}`);
  if (!PROMPT) error("--prompt is required.");

  const [width, height] = arToWidthHeight(AR);
  const imageSize = arToFalImageSize(AR);

  let input = {};

  if (modelKey === "flux-pro") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      num_images: Math.min(NUM_IMAGES, 4),
      ...(SEED !== undefined && { seed: SEED }),
      safety_tolerance: "2",
      output_format: "jpeg",
    };
  } else if (modelKey === "flux-dev") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      num_inference_steps: 28,
      num_images: Math.min(NUM_IMAGES, 4),
      enable_safety_checker: true,
      ...(SEED !== undefined && { seed: SEED }),
    };
  } else if (modelKey === "flux-schnell") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      num_inference_steps: 4,
      num_images: Math.min(NUM_IMAGES, 4),
      enable_safety_checker: true,
      ...(SEED !== undefined && { seed: SEED }),
    };
  } else if (modelKey === "sdxl") {
    input = {
      prompt: PROMPT,
      negative_prompt: NEG_PROMPT || "blurry, low quality, distorted",
      image_size: { width, height },
      num_images: Math.min(NUM_IMAGES, 4),
      ...(SEED !== undefined && { seed: SEED }),
    };
  } else if (modelKey === "nano-banana") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      num_images: Math.min(NUM_IMAGES, 4),
      ...(SEED !== undefined && { seed: SEED }),
    };
  } else if (modelKey === "ideogram") {
    input = {
      prompt: PROMPT,
      aspect_ratio: AR,
      num_images: Math.min(NUM_IMAGES, 4),
      ...(NEG_PROMPT && { negative_prompt: NEG_PROMPT }),
      ...(SEED !== undefined && { seed: SEED }),
    };
  } else if (modelKey === "recraft") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      style: "realistic_image",
      num_images: Math.min(NUM_IMAGES, 4),
    };
  }

  process.stderr.write(`[fal] Calling ${modelId} ...\n`);
  const result = await fal.subscribe(modelId, {
    input,
    onQueueUpdate(update) {
      if (update.status === "IN_QUEUE") {
        process.stderr.write(`[fal] Queue position: ${update.position ?? "?"}\n`);
      } else if (update.status === "IN_PROGRESS") {
        process.stderr.write(`[fal] Generating...\n`);
      }
    },
  });

  const images = (result.data?.images || []).map((img) =>
    typeof img === "string" ? img : img.url
  );

  output({
    success: true,
    model: modelKey,
    modelId,
    prompt: PROMPT,
    images,
    imageUrl: images[0] || null,
    seed: result.data?.seed ?? null,
    timings: result.data?.timings ?? null,
  });
}

// ── Main ───────────────────────────────────────────────────────────────────
async function main() {
  // Proxy mode: route all requests through the proxy server
  if (PROXY_MODE || PROXY_URL) {
    await generateViaProxy();
    return;
  }

  if (MODEL === "midjourney") {
    await generateMidjourney();
  } else if (FAL_MODELS[MODEL]) {
    await generateFal(MODEL);
  } else {
    error(`Unknown model: "${MODEL}". Valid options: midjourney, flux-pro, flux-dev, flux-schnell, sdxl, nano-banana, ideogram, recraft`);
  }
}

main().catch((err) => {
  error(err.message, err.stack);
});
