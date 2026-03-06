#!/usr/bin/env bun
/**
 * Jamendo API CLI – search and download royalty-free music.
 *
 * Usage:
 *   bun ./scripts/jamendo.ts search --query "rock" --limit 10
 *   bun ./scripts/jamendo.ts track --id 12345
 *   bun ./scripts/jamendo.ts album --id 12345
 *   bun ./scripts/jamendo.ts artist --id 12345
 *   bun ./scripts/jamendo.ts download --id 12345 --output ./music.mp3
 */

import * as path from "path";
import * as fs from "fs";

const BASE_URL = "https://api.jamendo.com/v3.0";
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

function getClientId(args: Record<string, string | undefined>): string {
  // Priority: CLI arg > env var > config file
  const clientId = args["--client-id"] ?? args["--key"] ?? process.env.JAMENDO_CLIENT_ID ?? loadConfig()?.jamendo?.client_id;
  if (!clientId) {
    console.error(
      "Error: Client ID required. Use --client-id, set JAMENDO_CLIENT_ID env var, or add to config.json."
    );
    process.exit(1);
  }
  return clientId;
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
      flags[arg] = "true";
    }
  }
  return { command, flags };
}

async function apiRequest(
  endpoint: string,
  params: Record<string, string | number | undefined>,
  clientId: string
): Promise<any> {
  const qs = new URLSearchParams();
  qs.set("client_id", clientId);
  qs.set("format", "json");

  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") {
      qs.set(k, String(v));
    }
  }

  const url = `${BASE_URL}${endpoint}/?${qs.toString()}`;
  const resp = await fetch(url, {
    headers: { "User-Agent": "JamendoCLI/0.1" },
  });

  if (!resp.ok) {
    const body = await resp.text();
    console.error(`HTTP ${resp.status}: ${body}`);
    process.exit(1);
  }

  const data = await resp.json();

  // Jamendo returns status in headers.status
  if (data.headers?.status !== "success") {
    console.error(`API Error: ${data.headers?.error_message || "Unknown error"}`);
    process.exit(1);
  }

  return data;
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

async function searchTracks(flags: Record<string, string>) {
  const clientId = getClientId(flags);
  const params: Record<string, string | number | undefined> = {};

  // Pagination
  if (flags["--limit"]) params.limit = Number(flags["--limit"]);
  if (flags["--offset"]) params.offset = Number(flags["--offset"]);
  if (flags["--fullcount"]) params.fullcount = "true";

  // Search parameters
  if (flags["--query"]) params.search = flags["--query"];
  if (flags["--name"]) params.name = flags["--name"];
  if (flags["--namesearch"]) params.namesearch = flags["--namesearch"];
  if (flags["--tags"]) params.tags = flags["--tags"];
  if (flags["--fuzzytags"]) params.fuzzytags = flags["--fuzzytags"];

  // Filters
  if (flags["--artist-id"]) params.artist_id = flags["--artist-id"];
  if (flags["--artist-name"]) params.artist_name = flags["--artist-name"];
  if (flags["--album-id"]) params.album_id = flags["--album-id"];
  if (flags["--album-name"]) params.album_name = flags["--album-name"];
  if (flags["--type"]) params.type = flags["--type"];
  if (flags["--featured"]) params.featured = "true";

  // Music attributes
  if (flags["--vocalinstrumental"]) params.vocalinstrumental = flags["--vocalinstrumental"];
  if (flags["--acousticelectric"]) params.acousticelectric = flags["--acousticelectric"];
  if (flags["--speed"]) params.speed = flags["--speed"];
  if (flags["--lang"]) params.lang = flags["--lang"];
  if (flags["--gender"]) params.gender = flags["--gender"];

  // Date/duration range
  if (flags["--datebetween"]) params.datebetween = flags["--datebetween"];
  if (flags["--durationbetween"]) params.durationbetween = flags["--durationbetween"];

  // Audio format
  if (flags["--audioformat"]) params.audioformat = flags["--audioformat"];
  if (flags["--imagesize"]) params.imagesize = flags["--imagesize"];

  // Sorting
  if (flags["--order"]) params.order = flags["--order"];
  if (flags["--boost"]) params.boost = flags["--boost"];
  if (flags["--groupby"]) params.groupby = flags["--groupby"];

  // Include extra info
  if (flags["--include"]) params.include = flags["--include"];

  // License filters
  if (flags["--ccnc"]) params.ccnc = "true";
  if (flags["--ccsa"]) params.ccsa = "true";
  if (flags["--ccnd"]) params.ccnd = "true";

  const data = await apiRequest("/tracks", params, clientId);

  const header = data.results_count
    ? `Found ${data.results_fullcount ?? data.results_count} tracks (showing ${data.results_count})`
    : `Found ${data.results?.length ?? 0} tracks`;
  console.error(header);

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Results saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function getTrack(flags: Record<string, string>) {
  const clientId = getClientId(flags);
  const id = flags["--id"];

  if (!id) {
    console.error("Error: --id is required");
    process.exit(1);
  }

  const params: Record<string, string | number | undefined> = {
    id,
    include: flags["--include"] || "musicinfo,stats,licenses",
  };
  if (flags["--audioformat"]) params.audioformat = flags["--audioformat"];

  const data = await apiRequest("/tracks", params, clientId);

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Track info saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function searchAlbums(flags: Record<string, string>) {
  const clientId = getClientId(flags);
  const params: Record<string, string | number | undefined> = {};

  if (flags["--limit"]) params.limit = Number(flags["--limit"]);
  if (flags["--offset"]) params.offset = Number(flags["--offset"]);
  if (flags["--fullcount"]) params.fullcount = "true";

  if (flags["--id"]) params.id = flags["--id"];
  if (flags["--name"]) params.name = flags["--name"];
  if (flags["--namesearch"]) params.namesearch = flags["--namesearch"];
  if (flags["--artist-id"]) params.artist_id = flags["--artist-id"];
  if (flags["--artist-name"]) params.artist_name = flags["--artist-name"];
  if (flags["--datebetween"]) params.datebetween = flags["--datebetween"];
  if (flags["--type"]) params.type = flags["--type"];
  if (flags["--imagesize"]) params.imagesize = flags["--imagesize"];
  if (flags["--order"]) params.order = flags["--order"];

  const data = await apiRequest("/albums", params, clientId);

  console.error(`Found ${data.results?.length ?? 0} albums`);

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Results saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function searchArtists(flags: Record<string, string>) {
  const clientId = getClientId(flags);
  const params: Record<string, string | number | undefined> = {};

  if (flags["--limit"]) params.limit = Number(flags["--limit"]);
  if (flags["--offset"]) params.offset = Number(flags["--offset"]);
  if (flags["--fullcount"]) params.fullcount = "true";

  if (flags["--id"]) params.id = flags["--id"];
  if (flags["--name"]) params.name = flags["--name"];
  if (flags["--namesearch"]) params.namesearch = flags["--namesearch"];
  if (flags["--datebetween"]) params.datebetween = flags["--datebetween"];
  if (flags["--hasimage"]) params.hasimage = "true";
  if (flags["--order"]) params.order = flags["--order"];

  const data = await apiRequest("/artists", params, clientId);

  console.error(`Found ${data.results?.length ?? 0} artists`);

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Results saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function getArtistTracks(flags: Record<string, string>) {
  const clientId = getClientId(flags);
  const id = flags["--id"];

  if (!id) {
    console.error("Error: --id is required");
    process.exit(1);
  }

  const params: Record<string, string | number | undefined> = { artist_id: id };
  if (flags["--limit"]) params.limit = Number(flags["--limit"]);
  if (flags["--order"]) params.order = flags["--order"];
  if (flags["--audioformat"]) params.audioformat = flags["--audioformat"];

  const data = await apiRequest("/tracks", params, clientId);

  console.error(`Found ${data.results?.length ?? 0} tracks`);

  const json = JSON.stringify(data, null, 2);
  if (flags["--output"]) {
    await Bun.write(flags["--output"], json);
    console.error(`Results saved to: ${flags["--output"]}`);
  } else {
    console.log(json);
  }
}

async function downloadTrack(flags: Record<string, string>) {
  const clientId = getClientId(flags);
  const id = flags["--id"];

  if (!id) {
    console.error("Error: --id is required");
    process.exit(1);
  }
  if (!flags["--output"]) {
    console.error("Error: --output is required for download");
    process.exit(1);
  }

  // Get track info with download URL
  const params: Record<string, string | undefined> = {
    id,
    audioformat: flags["--format"] || "mp32",
    audiodlformat: flags["--format"] || "mp32",
  };

  const data = await apiRequest("/tracks", params, clientId);

  if (!data.results?.[0]) {
    console.error("Error: Track not found");
    process.exit(1);
  }

  const track = data.results[0];

  if (!track.audiodownload_allowed) {
    console.error("Error: Download not allowed for this track");
    console.error(`Stream URL: ${track.audio}`);
    process.exit(1);
  }

  console.error(`Downloading: ${track.name} by ${track.artist_name}`);
  await downloadFile(track.audiodownload, flags["--output"]);
}

async function streamUrl(flags: Record<string, string>) {
  const clientId = getClientId(flags);
  const id = flags["--id"];

  if (!id) {
    console.error("Error: --id is required");
    process.exit(1);
  }

  const params: Record<string, string | undefined> = {
    id,
    audioformat: flags["--format"] || "mp32",
  };

  const data = await apiRequest("/tracks", params, clientId);

  if (!data.results?.[0]) {
    console.error("Error: Track not found");
    process.exit(1);
  }

  const track = data.results[0];
  console.log(track.audio);
}

// ── help ─────────────────────────────────────────────────────────────────

function printHelp() {
  console.log(`Jamendo API CLI – search and download royalty-free music

Commands:
  search            Search for music tracks
  track             Get track details by ID
  album             Search/get album details
  artist            Search/get artist details
  artist-tracks     Get all tracks by an artist
  download          Download a track by ID
  stream            Get streaming URL for a track

Common flags:
  --client-id       Jamendo Client ID (or set JAMENDO_CLIENT_ID env var)
  --output / -o     Save JSON output to file

Search flags:
  --query           Free text search (track, album, artist, tags)
  --name            Exact name match
  --namesearch      Fuzzy name search
  --tags            Tag search (AND logic, use + to separate)
  --fuzzytags       Fuzzy tag search (OR logic)
  --artist-id       Filter by artist ID
  --artist-name     Filter by artist name
  --album-id        Filter by album ID
  --limit           Results per page (max 200, default 10)
  --offset          Pagination offset
  --order           Sort order (see below)
  --include         Extra info: musicinfo, stats, licenses, lyrics

Music attribute filters:
  --vocalinstrumental  vocal | instrumental
  --acousticelectric   acoustic | electric
  --speed              verylow | low | medium | high | veryhigh
  --gender             male | female
  --lang               Lyrics language (2-letter code)
  --featured           Featured tracks only

Date/Duration filters:
  --datebetween      Date range: yyyy-mm-dd_yyyy-mm-dd
  --durationbetween  Duration range in seconds: from_to

Audio formats:
  --audioformat      mp31 (96kbps) | mp32 (192kbps VBR) | ogg | flac

Sort options (add _asc or _desc):
  relevance (default), popularity_week, popularity_month, popularity_total,
  downloads_week, downloads_month, downloads_total, listens_*, name, releasedate

Examples:
  # Search for rock music
  bun ./scripts/jamendo.ts search --query "rock" --limit 10

  # Search instrumental background music
  bun ./scripts/jamendo.ts search --query "background" --vocalinstrumental instrumental

  # Search by tags
  bun ./scripts/jamendo.ts search --tags "electronic+chill" --order popularity_total_desc

  # Get track details
  bun ./scripts/jamendo.ts track --id 12345 --include musicinfo,stats

  # Download a track
  bun ./scripts/jamendo.ts download --id 12345 --output ./music.mp3

  # Get artist's tracks
  bun ./scripts/jamendo.ts artist-tracks --id 421168 --limit 20

  # Search albums
  bun ./scripts/jamendo.ts album --artist-name "Artist Name"

  # Get FLAC format
  bun ./scripts/jamendo.ts search --query "jazz" --audioformat flac`);
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
    await searchTracks(flags);
    break;
  case "track":
    await getTrack(flags);
    break;
  case "album":
    await searchAlbums(flags);
    break;
  case "artist":
    await searchArtists(flags);
    break;
  case "artist-tracks":
    await getArtistTracks(flags);
    break;
  case "download":
    await downloadTrack(flags);
    break;
  case "stream":
    await streamUrl(flags);
    break;
  default:
    console.error(`Unknown command: ${command}`);
    printHelp();
    process.exit(1);
}
