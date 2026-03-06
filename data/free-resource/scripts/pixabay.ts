#!/usr/bin/env bun
/**
 * Pixabay API CLI – search and download royalty-free images & videos.
 *
 * Usage:
 *   bun ./scripts/pixabay.ts search-images --query "yellow flowers" --image-type photo
 *   bun ./scripts/pixabay.ts search-videos --query "ocean waves"
 *   bun ./scripts/pixabay.ts download --url "https://..." --output "/path/to/file.jpg"
 */

import * as path from "path";
import * as fs from "fs";

const BASE_IMAGE_URL = "https://pixabay.com/api/";
const BASE_VIDEO_URL = "https://pixabay.com/api/videos/";
const CONFIG_FILE = path.join(import.meta.dir, "..", "config.json");

// ── helpers ──────────────────────────────────────────────────────────────

function loadConfig(): Record<string, any> {
  if (fs.existsSync(CONFIG_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(CONFIG_FILE, "utf-8"));
    } catch (e) {
      return {};
    }
  }
  return {};
}

function getApiKey(args: Record<string, string | undefined>): string {
  // Priority: CLI arg > env var > config file
  const key = args["--key"] ?? process.env.PIXABAY_API_KEY ?? loadConfig()?.pixabay?.api_key;
  if (!key) {
    console.error(
      "Error: API key required. Use --key, set PIXABAY_API_KEY env var, or add to config.json."
    );
    process.exit(1);
  }
  return key;
}

function parseArgs(argv: string[]): {
  command: string;
  flags: Record<string, string>;
} {
  const command = argv[0] ?? "";
  const flags: Record<string, string> = {};
  for (let i = 1; i < argv.length; i++) {
    const arg = argv[i];
    if (arg.startsWith("--") && i + 1 < argv.length && !argv[i + 1].startsWith("--")) {
      flags[arg] = argv[++i];
    } else if (arg.startsWith("--")) {
      // boolean flag
      flags[arg] = "true";
    }
  }
  return { command, flags };
}

async function apiRequest(
  baseUrl: string,
  params: Record<string, string | number>
): Promise<any> {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
  }
  const url = `${baseUrl}?${qs.toString()}`;
  const resp = await fetch(url, {
    headers: { "User-Agent": "PixabayCLI/0.1" },
  });

  // rate-limit info
  const limit = resp.headers.get("X-RateLimit-Limit");
  const remaining = resp.headers.get("X-RateLimit-Remaining");
  const reset = resp.headers.get("X-RateLimit-Reset");
  if (limit) {
    console.error(`Rate limit: ${remaining}/${limit} remaining, resets in ${reset}s`);
  }

  if (!resp.ok) {
    const body = await resp.text();
    console.error(`HTTP ${resp.status}: ${body}`);
    process.exit(1);
  }
  return resp.json();
}

async function downloadFile(url: string, output: string): Promise<void> {
  const resp = await fetch(url);
  if (!resp.ok) {
    console.error(`Download failed – HTTP ${resp.status}`);
    process.exit(1);
  }
  const buf = await resp.arrayBuffer();
  await Bun.write(output, new Uint8Array(buf));
  console.error(`Downloaded: ${output}`);
}

// ── commands ─────────────────────────────────────────────────────────────

async function searchImages(flags: Record<string, string>) {
  const key = getApiKey(flags);
  const params: Record<string, string | number> = { key };

  if (flags["--query"]) params.q = flags["--query"];
  if (flags["--id"]) params.id = flags["--id"];
  if (flags["--lang"]) params.lang = flags["--lang"];
  if (flags["--image-type"] && flags["--image-type"] !== "all")
    params.image_type = flags["--image-type"];
  if (flags["--orientation"] && flags["--orientation"] !== "all")
    params.orientation = flags["--orientation"];
  if (flags["--category"]) params.category = flags["--category"];
  if (flags["--min-width"]) params.min_width = Number(flags["--min-width"]);
  if (flags["--min-height"]) params.min_height = Number(flags["--min-height"]);
  if (flags["--colors"]) params.colors = flags["--colors"];
  if (flags["--editors-choice"]) params.editors_choice = "true";
  if (flags["--safesearch"]) params.safesearch = "true";
  if (flags["--order"] && flags["--order"] !== "popular")
    params.order = flags["--order"];
  if (flags["--page"]) params.page = Number(flags["--page"]);
  if (flags["--per-page"]) {
    const perPage = Number(flags["--per-page"]);
    params.per_page = perPage < 5 ? 5 : perPage;
  }

  const data = await apiRequest(BASE_IMAGE_URL, params);
  console.error(
    `Found ${data.totalHits ?? 0} accessible images (total: ${data.total ?? 0})`
  );

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Results saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function searchVideos(flags: Record<string, string>) {
  const key = getApiKey(flags);
  const params: Record<string, string | number> = { key };

  if (flags["--query"]) params.q = flags["--query"];
  if (flags["--id"]) params.id = flags["--id"];
  if (flags["--lang"]) params.lang = flags["--lang"];
  if (flags["--video-type"] && flags["--video-type"] !== "all")
    params.video_type = flags["--video-type"];
  if (flags["--category"]) params.category = flags["--category"];
  if (flags["--min-width"]) params.min_width = Number(flags["--min-width"]);
  if (flags["--min-height"]) params.min_height = Number(flags["--min-height"]);
  if (flags["--editors-choice"]) params.editors_choice = "true";
  if (flags["--safesearch"]) params.safesearch = "true";
  if (flags["--order"] && flags["--order"] !== "popular")
    params.order = flags["--order"];
  if (flags["--page"]) params.page = Number(flags["--page"]);
  if (flags["--per-page"]) {
    const perPage = Number(flags["--per-page"]);
    params.per_page = perPage < 5 ? 5 : perPage;
  }

  const data = await apiRequest(BASE_VIDEO_URL, params);
  console.error(
    `Found ${data.totalHits ?? 0} accessible videos (total: ${data.total ?? 0})`
  );

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Results saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function download(flags: Record<string, string>) {
  if (!flags["--url"]) {
    console.error("Error: --url is required");
    process.exit(1);
  }
  if (!flags["--output"]) {
    console.error("Error: --output is required");
    process.exit(1);
  }
  await downloadFile(flags["--url"], flags["--output"]);
}

// ── help ─────────────────────────────────────────────────────────────────

function printHelp() {
  console.log(`Pixabay API CLI – search and download royalty-free images & videos

Commands:
  search-images   Search for images
  search-videos   Search for videos
  download        Download a file by URL

Common flags:
  --key           Pixabay API key (or set PIXABAY_API_KEY env var)
  --query / -q    Search term (max 100 chars)
  --id            Retrieve by Pixabay ID
  --lang          Language code (default: en)
  --category      Filter by category
  --min-width     Minimum width in px
  --min-height    Minimum height in px
  --editors-choice  Only Editor's Choice results
  --safesearch    Only results suitable for all ages
  --order         popular | latest (default: popular)
  --page          Page number (default: 1)
  --per-page      Results per page, 5-200 (default: 20)
  --output / -o   Save JSON to file

Image-specific:
  --image-type    all | photo | illustration | vector
  --orientation   all | horizontal | vertical
  --colors        Comma-separated color filter

Video-specific:
  --video-type    all | film | animation

Download:
  --url           URL to download
  --output        Local file path to save`);
}

// ── main ─────────────────────────────────────────────────────────────────

const rawArgs = process.argv.slice(2);
if (rawArgs.length === 0 || rawArgs[0] === "--help" || rawArgs[0] === "-h") {
  printHelp();
  process.exit(0);
}

const { command, flags } = parseArgs(rawArgs);

switch (command) {
  case "search-images":
    await searchImages(flags);
    break;
  case "search-videos":
    await searchVideos(flags);
    break;
  case "download":
    await download(flags);
    break;
  default:
    console.error(`Unknown command: ${command}`);
    printHelp();
    process.exit(1);
}
