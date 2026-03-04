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
    output({
      success: true,
      model: "midjourney",
      jobId,
      status: "completed",
      imageUrl: res.output?.image_url || null,
      imageUrls: res.output?.image_urls || [],
      seed: res.output?.seed || null,
      note: "4 images generated. Use --action upscale --index <1-4> --job-id to upscale, or --action variation to create variants.",
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

  // ── Async mode: return immediately after submission ────────────────────
  if (ASYNC_MODE) {
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

  // ── Sync mode: wait for completion (default, may block Bot) ───────────
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
