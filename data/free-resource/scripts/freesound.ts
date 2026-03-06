#!/usr/bin/env bun
/**
 * Freesound API CLI – search and download free sound effects.
 *
 * Usage:
 *   bun ./scripts/freesound.ts search --query "piano note"
 *   bun ./scripts/freesound.ts get --id 12345
 *   bun ./scripts/freesound.ts similar --id 12345
 *   bun ./scripts/freesound.ts download --id 12345 --output ./sound.mp3
 */

import * as path from "path";
import * as fs from "fs";

const BASE_URL = "https://freesound.org/apiv2";
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

function getApiToken(args: Record<string, string | undefined>): string {
  // Priority: CLI arg > env var > config file
  const token = args["--token"] ?? args["--key"] ?? process.env.FREESOUND_API_TOKEN ?? loadConfig()?.freesound?.api_token;
  if (!token) {
    console.error(
      "Error: API token required. Use --token, set FREESOUND_API_TOKEN env var, or add to config.json."
    );
    process.exit(1);
  }
  return token;
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
  endpoint: string,
  params: Record<string, string | number | undefined>,
  token: string
): Promise<any> {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
  }
  const url = `${BASE_URL}${endpoint}?${qs.toString()}`;
  const resp = await fetch(url, {
    headers: {
      "Authorization": `Token ${token}`,
      "User-Agent": "FreesoundCLI/0.1"
    },
  });

  if (!resp.ok) {
    const body = await resp.text();
    console.error(`HTTP ${resp.status}: ${body}`);
    process.exit(1);
  }
  return resp.json();
}

async function downloadFile(url: string, output: string, token?: string): Promise<void> {
  const headers: Record<string, string> = {
    "User-Agent": "FreesoundCLI/0.1"
  };
  if (token) {
    headers["Authorization"] = `Token ${token}`;
  }

  const resp = await fetch(url, { headers });
  if (!resp.ok) {
    console.error(`Download failed – HTTP ${resp.status}`);
    process.exit(1);
  }
  const buf = await resp.arrayBuffer();
  await Bun.write(output, new Uint8Array(buf));
  console.error(`Downloaded: ${output}`);
}

// ── commands ─────────────────────────────────────────────────────────────

async function searchSounds(flags: Record<string, string>) {
  const token = getApiToken(flags);
  const params: Record<string, string | number | undefined> = {};

  if (flags["--query"]) params.query = flags["--query"];
  if (flags["--filter"]) params.filter = flags["--filter"];
  if (flags["--sort"]) params.sort = flags["--sort"];
  if (flags["--fields"]) params.fields = flags["--fields"];
  if (flags["--page"]) params.page = Number(flags["--page"]);
  if (flags["--page-size"]) params.page_size = Number(flags["--page-size"]);
  if (flags["--group-by-pack"]) params.group_by_pack = "1";

  const data = await apiRequest("/search/", params, token);
  console.error(
    `Found ${data.count ?? 0} sounds (showing ${data.results?.length ?? 0})`
  );

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Results saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function getSound(flags: Record<string, string>) {
  const token = getApiToken(flags);
  const id = flags["--id"];

  if (!id) {
    console.error("Error: --id is required");
    process.exit(1);
  }

  const params: Record<string, string | undefined> = {};
  if (flags["--fields"]) params.fields = flags["--fields"];

  const data = await apiRequest(`/sounds/${id}/`, params, token);

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Sound info saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function getSimilar(flags: Record<string, string>) {
  const token = getApiToken(flags);
  const id = flags["--id"];

  if (!id) {
    console.error("Error: --id is required");
    process.exit(1);
  }

  const params: Record<string, string | number | undefined> = {};
  if (flags["--fields"]) params.fields = flags["--fields"];
  if (flags["--page"]) params.page = Number(flags["--page"]);
  if (flags["--page-size"]) params.page_size = Number(flags["--page-size"]);

  const data = await apiRequest(`/sounds/${id}/similar/`, params, token);
  console.error(
    `Found ${data.count ?? 0} similar sounds`
  );

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Results saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function getComments(flags: Record<string, string>) {
  const token = getApiToken(flags);
  const id = flags["--id"];

  if (!id) {
    console.error("Error: --id is required");
    process.exit(1);
  }

  const data = await apiRequest(`/sounds/${id}/comments/`, {}, token);

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Comments saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function downloadPreview(flags: Record<string, string>) {
  const token = getApiToken(flags);
  const id = flags["--id"];

  if (!id) {
    console.error("Error: --id is required");
    process.exit(1);
  }
  if (!flags["--output"]) {
    console.error("Error: --output is required for download");
    process.exit(1);
  }

  // First get sound info to retrieve preview URL
  const sound = await apiRequest(`/sounds/${id}/`, { fields: "previews,name" }, token);

  // Prefer HQ MP3, fallback to LQ MP3
  const previewUrl = sound.previews?.["preview-hq-mp3"] || sound.previews?.["preview-lq-mp3"];

  if (!previewUrl) {
    console.error("Error: No preview URL available for this sound");
    process.exit(1);
  }

  console.error(`Downloading: ${sound.name}`);
  await downloadFile(previewUrl, flags["--output"]);
}

async function downloadSound(flags: Record<string, string>) {
  const token = getApiToken(flags);
  const id = flags["--id"];

  if (!id) {
    console.error("Error: --id is required");
    process.exit(1);
  }
  if (!flags["--output"]) {
    console.error("Error: --output is required for download");
    process.exit(1);
  }

  // Get download URL
  const data = await apiRequest(`/sounds/${id}/download/`, {}, token);

  if (!data.download_link) {
    console.error("Error: No download link returned. Note: OAuth2 may be required for original file downloads.");
    process.exit(1);
  }

  await downloadFile(data.download_link, flags["--output"], token);
}

// ── help ─────────────────────────────────────────────────────────────────

function printHelp() {
  console.log(`Freesound API CLI – search and download free sound effects

Commands:
  search          Search for sounds
  get             Get sound details by ID
  similar         Get similar sounds by ID
  comments        Get comments for a sound
  download        Download sound preview (high-quality MP3)

Common flags:
  --token         Freesound API token (or set FREESOUND_API_TOKEN env var)
  --output / -o   Save JSON output to file

Search flags:
  --query         Search term (supports +/- modifiers, phrases in quotes)
  --filter        Filter results (e.g., "duration:[0.1 TO 1.0]" "type:wav")
  --sort          Sort by: score (default), duration_desc, created_desc,
                  downloads_desc, rating_desc, etc.
  --fields        Comma-separated fields to return
                  (default: id,name,tags,username,license)
  --page          Page number (default: 1)
  --page-size     Results per page, max 150 (default: 15)
  --group-by-pack Group results by pack (1/0)

Get/Similar/Comments flags:
  --id            Sound ID (required)
  --fields        Comma-separated fields to return

Download flags:
  --id            Sound ID (required)
  --output        Local file path to save (required)

Filter examples:
  --filter "duration:[0.1 TO 1.0]"
  --filter "type:wav"
  --filter "tag:piano"
  --filter "bpm:120"
  --filter "license:Creative Commons 0"

Examples:
  # Search for piano sounds
  bun ./scripts/freesound.ts search --query "piano note" --page-size 10

  # Search with filter
  bun ./scripts/freesound.ts search --query "drum" --filter "duration:[0 TO 2]" --sort downloads_desc

  # Get sound details
  bun ./scripts/freesound.ts get --id 12345 --fields id,name,previews,duration

  # Get similar sounds
  bun ./scripts/freesound.ts similar --id 12345

  # Download preview
  bun ./scripts/freesound.ts download --id 12345 --output ./sound.mp3`);
}

// ── main ─────────────────────────────────────────────────────────────────

const rawArgs = process.argv.slice(2);
if (rawArgs.length === 0 || rawArgs[0] === "--help" || rawArgs[0] === "-h") {
  printHelp();
  process.exit(0);
}

const { command, flags } = parseArgs(rawArgs);

switch (command) {
  case "search":
    await searchSounds(flags);
    break;
  case "get":
    await getSound(flags);
    break;
  case "similar":
    await getSimilar(flags);
    break;
  case "comments":
    await getComments(flags);
    break;
  case "download":
    await downloadPreview(flags);
    break;
  case "download-original":
    await downloadSound(flags);
    break;
  default:
    console.error(`Unknown command: ${command}`);
    printHelp();
    process.exit(1);
}
