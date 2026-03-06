// wip-grok/core.mjs
// All xAI API functions. Sensor (search) + Actuator (generate).
// Zero dependencies. Pure logic.

import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

// ── Models ──

export const MODELS = {
  search: 'grok-4-1-fast-reasoning',
  image: 'grok-imagine-image',
  video: 'grok-imagine-video',
};

const API_BASE = 'https://api.x.ai/v1';

// ── Auth ──

/**
 * Resolve xAI API key: env var first, then 1Password.
 * Caches the result in process.env for subsequent calls.
 */
export function resolveApiKey() {
  if (process.env.XAI_API_KEY) return process.env.XAI_API_KEY;

  try {
    const key = execSync('op read "op://Agent Secrets/X API/api key"', {
      stdio: ['pipe', 'pipe', 'pipe'],
      timeout: 10000,
    }).toString().trim();
    if (key) {
      process.env.XAI_API_KEY = key;
      return key;
    }
  } catch {
    // 1Password not available
  }

  throw new Error(
    'XAI_API_KEY not found. Set it via:\n' +
    '  1. 1Password: op item edit "X API" --vault "Agent Secrets" "api key=your-key"\n' +
    '  2. Environment: export XAI_API_KEY="your-key"\n' +
    '  Get your key from https://console.x.ai/'
  );
}

function headers() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${resolveApiKey()}`,
  };
}

// ── Sensor: Search ──

/**
 * Search the web using xAI's Grok API.
 * @param {Object} options
 * @param {string} options.query - Search query (required)
 * @param {string} [options.model] - Grok model (default: grok-4-1-fast-reasoning)
 * @param {string[]} [options.allowed_domains] - Restrict to these domains (max 5)
 * @param {string[]} [options.excluded_domains] - Exclude these domains (max 5)
 * @param {boolean} [options.enable_image_understanding] - Analyze images in results
 * @returns {Promise<Object>} { content, citations, usage, raw_response }
 */
export async function search_web(options) {
  const {
    query,
    model = MODELS.search,
    allowed_domains = null,
    excluded_domains = null,
    enable_image_understanding = false,
  } = options;

  if (allowed_domains && allowed_domains.length > 5) throw new Error('Maximum 5 allowed_domains');
  if (excluded_domains && excluded_domains.length > 5) throw new Error('Maximum 5 excluded_domains');
  if (allowed_domains && excluded_domains) throw new Error('Cannot use both allowed_domains and excluded_domains');

  const tool = { type: 'web_search' };
  if (allowed_domains) tool.allowed_domains = allowed_domains;
  if (excluded_domains) tool.excluded_domains = excluded_domains;
  if (enable_image_understanding) tool.enable_image_understanding = true;

  const response = await fetch(`${API_BASE}/responses`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({
      model,
      input: [{ role: 'user', content: query }],
      tools: [tool],
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(`API Error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  const output = data.output || [];
  const lastMessage = output[output.length - 1] || {};

  return {
    content: lastMessage.content || '',
    citations: data.citations || [],
    usage: data.usage || {},
    raw_response: data,
  };
}

/**
 * Search X (Twitter) using xAI's Grok API.
 * @param {Object} options
 * @param {string} options.query - Search query (required)
 * @param {string} [options.model] - Grok model
 * @param {string[]} [options.allowed_x_handles] - Only search these handles (max 10, no @)
 * @param {string[]} [options.excluded_x_handles] - Exclude these handles (max 10, no @)
 * @param {string} [options.from_date] - Start date (YYYY-MM-DD)
 * @param {string} [options.to_date] - End date (YYYY-MM-DD)
 * @param {boolean} [options.enable_image_understanding] - Analyze images
 * @param {boolean} [options.enable_video_understanding] - Analyze videos
 * @returns {Promise<Object>} { content, citations, usage, raw_response }
 */
export async function search_x(options) {
  const {
    query,
    model = MODELS.search,
    allowed_x_handles = null,
    excluded_x_handles = null,
    from_date = null,
    to_date = null,
    enable_image_understanding = false,
    enable_video_understanding = false,
  } = options;

  if (allowed_x_handles && allowed_x_handles.length > 10) throw new Error('Maximum 10 allowed_x_handles');
  if (excluded_x_handles && excluded_x_handles.length > 10) throw new Error('Maximum 10 excluded_x_handles');
  if (allowed_x_handles && excluded_x_handles) throw new Error('Cannot use both allowed_x_handles and excluded_x_handles');

  const tool = { type: 'x_search' };
  if (allowed_x_handles) tool.allowed_x_handles = allowed_x_handles;
  if (excluded_x_handles) tool.excluded_x_handles = excluded_x_handles;
  if (from_date) tool.from_date = from_date;
  if (to_date) tool.to_date = to_date;
  if (enable_image_understanding) tool.enable_image_understanding = true;
  if (enable_video_understanding) tool.enable_video_understanding = true;

  const response = await fetch(`${API_BASE}/responses`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({
      model,
      input: [{ role: 'user', content: query }],
      tools: [tool],
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(`API Error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  const output = data.output || [];
  const lastMessage = output[output.length - 1] || {};

  return {
    content: lastMessage.content || '',
    citations: data.citations || [],
    usage: data.usage || {},
    raw_response: data,
  };
}

// ── Actuator: Image Generation ──

/**
 * Generate images from text using Grok Imagine.
 * @param {Object} options
 * @param {string} options.prompt - Text description (required, max 8000 chars)
 * @param {string} [options.model] - Model (default: grok-imagine-image)
 * @param {number} [options.n] - Number of images (1-10, default: 1)
 * @param {string} [options.response_format] - "url" or "b64_json" (default: "url")
 * @param {string} [options.aspect_ratio] - e.g. "1:1", "16:9", "9:16", "4:3"
 * @returns {Promise<Object>} { images: [{ url, b64_json?, revised_prompt }] }
 */
export async function generate_image(options) {
  const {
    prompt,
    model = MODELS.image,
    n = 1,
    response_format = 'url',
    aspect_ratio = null,
  } = options;

  if (!prompt) throw new Error('prompt is required');
  if (n < 1 || n > 10) throw new Error('n must be 1-10');

  const body = { model, prompt, n, response_format };
  if (aspect_ratio) body.aspect_ratio = aspect_ratio;

  const response = await fetch(`${API_BASE}/images/generations`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(`API Error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  return {
    images: (data.data || []).map(img => ({
      url: img.url || null,
      b64_json: img.b64_json || null,
      revised_prompt: img.revised_prompt || null,
    })),
  };
}

/**
 * Edit images using natural language with Grok Imagine.
 * @param {Object} options
 * @param {string} options.prompt - Edit instruction (required)
 * @param {string|string[]} options.image - Image URL(s) or base64 data URI(s). Up to 3.
 * @param {string} [options.model] - Model (default: grok-imagine-image)
 * @param {number} [options.n] - Number of outputs (1-10, default: 1)
 * @param {string} [options.response_format] - "url" or "b64_json"
 * @returns {Promise<Object>} { images: [{ url, b64_json?, revised_prompt }] }
 */
export async function edit_image(options) {
  const {
    prompt,
    image,
    model = MODELS.image,
    n = 1,
    response_format = 'url',
  } = options;

  if (!prompt) throw new Error('prompt is required');
  if (!image) throw new Error('image is required (URL or base64 data URI)');

  const images = Array.isArray(image) ? image : [image];
  if (images.length > 3) throw new Error('Maximum 3 source images');

  // Build input with image(s) + text prompt
  const content = [];
  for (const img of images) {
    // If it looks like a file path, read and base64 encode
    let imageUrl = img;
    if (!img.startsWith('http') && !img.startsWith('data:')) {
      const data = readFileSync(img);
      const ext = img.split('.').pop().toLowerCase();
      const mime = ext === 'png' ? 'image/png' : ext === 'webp' ? 'image/webp' : 'image/jpeg';
      imageUrl = `data:${mime};base64,${data.toString('base64')}`;
    }
    content.push({ type: 'image_url', image_url: { url: imageUrl } });
  }
  content.push({ type: 'text', text: prompt });

  const response = await fetch(`${API_BASE}/images/edits`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({
      model,
      image: images[0],
      prompt,
      n,
      response_format,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(`API Error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  return {
    images: (data.data || []).map(img => ({
      url: img.url || null,
      b64_json: img.b64_json || null,
      revised_prompt: img.revised_prompt || null,
    })),
  };
}

// ── Actuator: Video Generation ──

/**
 * Start async video generation with Grok Imagine.
 * @param {Object} options
 * @param {string} options.prompt - Text description (required)
 * @param {string} [options.model] - Model (default: grok-imagine-video)
 * @param {number} [options.duration] - Duration in seconds (1-15, default: 5)
 * @param {string} [options.resolution] - "480p" or "720p" (default: "720p")
 * @param {string} [options.aspect_ratio] - e.g. "16:9", "9:16", "1:1"
 * @param {string} [options.image] - Seed image URL for image-to-video
 * @returns {Promise<Object>} { request_id }
 */
export async function generate_video(options) {
  const {
    prompt,
    model = MODELS.video,
    duration = 5,
    resolution = '720p',
    aspect_ratio = null,
    image = null,
  } = options;

  if (!prompt) throw new Error('prompt is required');
  if (duration < 1 || duration > 15) throw new Error('duration must be 1-15 seconds');

  const body = { model, prompt, duration, resolution };
  if (aspect_ratio) body.aspect_ratio = aspect_ratio;
  if (image) body.image_url = image;

  const response = await fetch(`${API_BASE}/video/generations`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(`API Error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  return { request_id: data.request_id || data.id };
}

/**
 * Poll for video generation status.
 * @param {Object} options
 * @param {string} options.request_id - The request ID from generate_video
 * @returns {Promise<Object>} { status, url?, duration?, error? }
 */
export async function poll_video(options) {
  const { request_id } = options;
  if (!request_id) throw new Error('request_id is required');

  const response = await fetch(`${API_BASE}/video/generations/${request_id}`, {
    method: 'GET',
    headers: headers(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(`API Error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  return {
    status: data.state || data.status || 'unknown',
    url: data.video_url || data.url || null,
    duration: data.duration || null,
    error: data.error || null,
  };
}

/**
 * Wait for video generation to complete (convenience wrapper).
 * @param {Object} options
 * @param {string} options.request_id - The request ID
 * @param {number} [options.interval_ms] - Poll interval (default: 5000)
 * @param {number} [options.timeout_ms] - Max wait time (default: 300000 = 5 min)
 * @returns {Promise<Object>} { status, url?, duration?, error? }
 */
export async function wait_for_video(options) {
  const {
    request_id,
    interval_ms = 5000,
    timeout_ms = 300000,
  } = options;

  const start = Date.now();
  while (Date.now() - start < timeout_ms) {
    const result = await poll_video({ request_id });
    if (result.status === 'completed' || result.status === 'succeeded') return result;
    if (result.status === 'failed') throw new Error(`Video generation failed: ${result.error || 'unknown error'}`);
    await new Promise(r => setTimeout(r, interval_ms));
  }

  throw new Error(`Video generation timed out after ${timeout_ms}ms`);
}
