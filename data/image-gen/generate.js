#!/usr/bin/env node
/**
 * image-gen skill — generate.js
 * Unified image generation script for OpenClaw.
 *
 * Supported models:
 *   Midjourney (via Legnext.ai), Flux Pro/Dev/Schnell, SDXL Lightning,
 *   Nano Banana Pro, Ideogram v3, Recraft v3 (all via fal.ai)
 *
 * External endpoints contacted:
 *   - api.legnext.ai  (Midjourney proxy — requires LEGNEXT_KEY)
 *   - gateway.fal.ai  (fal.ai models — requires FAL_KEY)
 *
 * This script does NOT:
 *   - Write to the filesystem (no token persistence, no caching)
 *   - Contact any endpoints other than those listed above
 *   - Execute dynamic code (no eval, no Function constructor)
 *   - Collect or exfiltrate user data
 *
 * Usage:
 *   node generate.js --model <id> --prompt "<text>" [options]
 *   node generate.js --model midjourney --action upscale --index 2 --job-id <id>
 */

"use strict";

import { fal } from "@fal-ai/client";
import https from "https";
import { parseArgs } from "util";

// ── Constants ─────────────────────────────────────────────────────────────
const ALLOWED_MODELS = [
  "midjourney", "flux-pro", "flux-dev", "flux-schnell",
  "sdxl", "nano-banana", "ideogram", "recraft",
];

const ALLOWED_ASPECT_RATIOS = [
  "1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "21:9",
];

const ALLOWED_ACTIONS = ["", "upscale", "variation", "reroll", "describe"];

const ALLOWED_MODES = ["turbo", "fast", "relax"];

const MAX_PROMPT_LENGTH = 4000;

// ── Parse CLI arguments ────────────────────────────────────────────────────
const { values: args } = parseArgs({
  options: {
    model:              { type: "string", default: "flux-dev" },
    prompt:             { type: "string", default: "" },
    "aspect-ratio":     { type: "string", default: "1:1" },
    "num-images":       { type: "string", default: "1" },
    "negative-prompt":  { type: "string", default: "" },
    action:             { type: "string", default: "" },
    index:              { type: "string", default: "1" },
    "job-id":           { type: "string", default: "" },
    "upscale-type":     { type: "string", default: "0" },
    "variation-type":   { type: "string", default: "0" },
    mode:               { type: "string", default: "turbo" },
    seed:               { type: "string", default: "" },
  },
  strict: false,
});

// ── Input validation ──────────────────────────────────────────────────────
function validateInputs() {
  if (!ALLOWED_MODELS.includes(args["model"])) {
    error(`Invalid model: "${args["model"]}". Allowed: ${ALLOWED_MODELS.join(", ")}`);
  }
  if (!ALLOWED_ASPECT_RATIOS.includes(args["aspect-ratio"])) {
    error(`Invalid aspect ratio: "${args["aspect-ratio"]}". Allowed: ${ALLOWED_ASPECT_RATIOS.join(", ")}`);
  }
  if (!ALLOWED_ACTIONS.includes(args["action"])) {
    error(`Invalid action: "${args["action"]}". Allowed: upscale, variation, reroll, describe`);
  }
  if (!ALLOWED_MODES.includes(args["mode"])) {
    error(`Invalid mode: "${args["mode"]}". Allowed: ${ALLOWED_MODES.join(", ")}`);
  }
  const numImages = parseInt(args["num-images"], 10);
  if (isNaN(numImages) || numImages < 1 || numImages > 4) {
    error(`Invalid num-images: "${args["num-images"]}". Must be 1-4.`);
  }
  if (args["prompt"] && args["prompt"].length > MAX_PROMPT_LENGTH) {
    error(`Prompt too long (${args["prompt"].length} chars). Maximum: ${MAX_PROMPT_LENGTH}.`);
  }
  const index = parseInt(args["index"], 10);
  if (isNaN(index) || index < 1 || index > 4) {
    error(`Invalid index: "${args["index"]}". Must be 1-4.`);
  }
  const upscaleType = parseInt(args["upscale-type"], 10);
  if (isNaN(upscaleType) || (upscaleType !== 0 && upscaleType !== 1)) {
    error(`Invalid upscale-type: "${args["upscale-type"]}". Must be 0 (Subtle) or 1 (Creative).`);
  }
  const variationType = parseInt(args["variation-type"], 10);
  if (isNaN(variationType) || (variationType !== 0 && variationType !== 1)) {
    error(`Invalid variation-type: "${args["variation-type"]}". Must be 0 (Subtle) or 1 (Strong).`);
  }
}

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
const MODE           = args["mode"] || "turbo";
const SEED           = args["seed"] ? parseInt(args["seed"], 10) : undefined;

// ── Environment variables ──────────────────────────────────────────────────
const FAL_KEY      = process.env.FAL_KEY;
const LEGNEXT_KEY  = process.env.LEGNEXT_KEY;

// ── fal.ai model IDs ───────────────────────────────────────────────────────
const FAL_MODELS = {
  "flux-pro":      "fal-ai/flux-pro/v1.1",
  "flux-dev":      "fal-ai/flux/dev",
  "flux-schnell":  "fal-ai/flux/schnell",
  "sdxl":          "fal-ai/lightning-models/sdxl-lightning-4step",
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

// ── Legnext.ai HTTP helper ─────────────────────────────────────────────────
// Connects ONLY to api.legnext.ai for Midjourney image generation.
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
        catch (e) { reject(new Error(`Invalid JSON response from api.legnext.ai: ${data.slice(0, 200)}`)); }
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

// ── Midjourney via Legnext.ai ──────────────────────────────────────────────
async function generateMidjourney() {
  if (!LEGNEXT_KEY) error("LEGNEXT_KEY is not set. Please configure it in your OpenClaw skill env.");

  // ── Upscale action ─────────────────────────────────────────────────────
  if (ACTION === "upscale" && JOB_ID) {
    const imageNo = INDEX - 1;
    process.stderr.write(`[MJ] Upscaling image ${INDEX} (imageNo=${imageNo}, type=${UPSCALE_TYPE}) from job ${JOB_ID}\n`);
    const res = await legnextRequest("POST", "/upscale", {
      jobId: JOB_ID,
      imageNo,
      type: UPSCALE_TYPE,
    });
    if (!res.job_id) error("Legnext upscale submission failed", res);
    process.stderr.write(`[MJ] Upscale job submitted: ${res.job_id}\n`);
    const result = await legnextPoll(res.job_id);
    output({
      success: true,
      model: "midjourney",
      action: "upscale",
      jobId: res.job_id,
      imageUrl: result.output?.image_url || null,
    });
    return;
  }

  // ── Variation action ───────────────────────────────────────────────────
  if (ACTION === "variation" && JOB_ID) {
    const imageNo = INDEX - 1;
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
    const result = await legnextPoll(res.job_id);
    output({
      success: true,
      model: "midjourney",
      action: "variation",
      jobId: res.job_id,
      imageUrl: result.output?.image_url || null,
      imageUrls: result.output?.image_urls || [],
    });
    return;
  }

  // ── Reroll action ──────────────────────────────────────────────────────
  if (ACTION === "reroll" && JOB_ID) {
    process.stderr.write(`[MJ] Rerolling job ${JOB_ID}\n`);
    const res = await legnextRequest("POST", "/reroll", { jobId: JOB_ID });
    if (!res.job_id) error("Legnext reroll submission failed", res);
    process.stderr.write(`[MJ] Reroll job submitted: ${res.job_id}\n`);
    const result = await legnextPoll(res.job_id);
    output({
      success: true,
      model: "midjourney",
      action: "reroll",
      jobId: res.job_id,
      imageUrl: result.output?.image_url || null,
      imageUrls: result.output?.image_urls || [],
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

  let mjPrompt = PROMPT;
  if (AR && AR !== "1:1") {
    mjPrompt += ` --ar ${AR}`;
  }
  if (MODE === "turbo") {
    mjPrompt += " --turbo";
  } else if (MODE === "fast") {
    mjPrompt += " --fast";
  } else if (MODE === "relax") {
    mjPrompt += " --relax";
  }

  process.stderr.write(`[MJ] Submitting imagine via Legnext.ai (mode=${MODE}): "${mjPrompt.slice(0, 100)}..."\n`);
  const res = await legnextRequest("POST", "/diffusion", {
    text: mjPrompt,
  });

  if (!res.job_id) error("Legnext imagine submission failed", res);
  const jobId = res.job_id;
  process.stderr.write(`[MJ] Job submitted: ${jobId}\n`);

  const result = await legnextPoll(jobId);

  output({
    success: true,
    model: "midjourney",
    provider: "legnext.ai",
    jobId,
    prompt: mjPrompt,
    imageUrl: result.output?.image_url || null,
    imageUrls: result.output?.image_urls || [],
    seed: result.output?.seed || null,
    note: "4 images generated. Use --action upscale --index <1-4> --job-id to upscale, or --action variation to create variants.",
  });
}

// ── fal.ai models ──────────────────────────────────────────────────────────
// Connects ONLY to fal.ai (gateway.fal.ai) for image generation.
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
  validateInputs();

  if (MODEL === "midjourney") {
    await generateMidjourney();
  } else if (FAL_MODELS[MODEL]) {
    await generateFal(MODEL);
  } else {
    error(`Unknown model: "${MODEL}". Valid options: ${ALLOWED_MODELS.join(", ")}`);
  }
}

main().catch((err) => {
  error(err.message, err.stack);
});
