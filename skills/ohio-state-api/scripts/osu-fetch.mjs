#!/usr/bin/env node

const SERVICE_BASE_URLS = {
  athletics: "https://content.osu.edu/v3/athletics",
  bus: "https://content.osu.edu/v2/bus",
  buildings: "https://content.osu.edu/v2/api",
  calendar: "https://content.osu.edu/v2/calendar",
  classes: "https://content.osu.edu/v2/classes",
  dining: "https://content.osu.edu/v2/api/v1/dining",
  directory: "https://content.osu.edu",
  events: "https://content.osu.edu/v2",
  foodtrucks: "https://content.osu.edu/v2/foodtruck",
  library: "https://content.osu.edu/v2/library",
  merchants: "https://content.osu.edu/v2",
  parking: "https://content.osu.edu/v2/parking/garages",
  recsports: "https://content.osu.edu/v3",
  studentorgs: "https://content.osu.edu/v2/student-org",
};

function printHelp(exitCode = 0) {
  const services = Object.keys(SERVICE_BASE_URLS).sort().join(", ");
  // eslint-disable-next-line no-console
  console.log(`
osu-fetch.mjs - Fetch JSON from OSU Content APIs

Usage:
  node ohio-state-api/scripts/osu-fetch.mjs <url> [--param k=v ...] [--extract a.b.c] [--timeout-ms 15000]
  node ohio-state-api/scripts/osu-fetch.mjs --service <name> --path <path> [--param k=v ...] [--extract a.b.c] [--timeout-ms 15000]

Options:
  --service <name>     One of: ${services}
  --path <path>        Path appended to the service base URL (leading '/' optional)
  --param k=v          Add a query parameter (repeatable)
  --extract a.b.c      Print only the JSON subtree at the given dot path
  --timeout-ms <n>     Request timeout in milliseconds (default: 15000)
  -h, --help           Show this help
`.trim());
  process.exit(exitCode);
}

function parseArgs(argv) {
  const args = {
    url: null,
    service: null,
    path: null,
    params: [],
    extract: null,
    timeoutMs: 15000,
  };

  const positionals = [];
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "-h" || token === "--help") {
      printHelp(0);
    } else if (token === "--service") {
      args.service = argv[++i] ?? null;
    } else if (token === "--path") {
      args.path = argv[++i] ?? null;
    } else if (token === "--param") {
      const value = argv[++i] ?? "";
      args.params.push(value);
    } else if (token === "--extract") {
      args.extract = argv[++i] ?? null;
    } else if (token === "--timeout-ms") {
      const value = Number(argv[++i]);
      if (!Number.isFinite(value) || value <= 0) {
        throw new Error(`--timeout-ms must be a positive number (got ${String(value)})`);
      }
      args.timeoutMs = value;
    } else if (token.startsWith("-")) {
      throw new Error(`Unknown option: ${token}`);
    } else {
      positionals.push(token);
    }
  }

  if (positionals.length > 0) {
    args.url = positionals[0];
  }

  return args;
}

function buildUrl({ url, service, path, params }) {
  let finalUrl = url;

  if (!finalUrl) {
    if (!service || !path) {
      throw new Error("Provide either <url> or both --service and --path.");
    }
    const base = SERVICE_BASE_URLS[service];
    if (!base) {
      throw new Error(`Unknown service '${service}'. Use --help to see valid services.`);
    }
    // Treat --path as relative to the service base URL.
    // If the user provides "/locations", strip the leading slash so it doesn't
    // clobber the base path (URL resolution would otherwise jump to origin).
    const baseWithSlash = base.endsWith("/") ? base : `${base}/`;
    const normalizedPath = path.startsWith("/") ? path.slice(1) : path;
    finalUrl = new URL(normalizedPath, baseWithSlash).toString();
  } else if (!finalUrl.startsWith("http://") && !finalUrl.startsWith("https://")) {
    throw new Error(`URL must start with http(s):// (got ${finalUrl})`);
  }

  const u = new URL(finalUrl);
  for (const p of params) {
    const idx = p.indexOf("=");
    if (idx <= 0) {
      throw new Error(`--param must be k=v (got ${p})`);
    }
    u.searchParams.set(p.slice(0, idx), p.slice(idx + 1));
  }
  return u;
}

function extractDotPath(value, dotPath) {
  if (!dotPath) return value;
  const parts = dotPath.split(".").filter(Boolean);
  let current = value;
  for (const part of parts) {
    if (current == null) return null;
    if (Array.isArray(current)) {
      const idx = Number(part);
      current = Number.isInteger(idx) ? current[idx] : null;
    } else if (typeof current === "object") {
      current = current[part];
    } else {
      return null;
    }
  }
  return current;
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0) {
    printHelp(1);
  }

  const args = parseArgs(argv);
  const url = buildUrl(args);

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), args.timeoutMs);

  try {
    let res;
    try {
      res = await fetch(url, {
        method: "GET",
        headers: { accept: "application/json" },
        signal: controller.signal,
      });
    } catch (err) {
      const causeMsg =
        err && typeof err === "object" && "cause" in err && err.cause && typeof err.cause === "object" && "message" in err.cause
          ? ` (${String(err.cause.message)})`
          : "";
      // eslint-disable-next-line no-console
      console.error(`Network error fetching ${url.toString()}: ${err?.message || String(err)}${causeMsg}`);
      process.exit(1);
      return;
    }

    const contentType = res.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json") || contentType.includes("+json");

    if (!res.ok) {
      const body = await res.text().catch(() => "");
      const snippet = body.length > 2000 ? `${body.slice(0, 2000)}\n…(truncated)…` : body;
      // eslint-disable-next-line no-console
      console.error(`HTTP ${res.status} ${res.statusText} for ${url.toString()}`);
      if (snippet) {
        // eslint-disable-next-line no-console
        console.error(snippet);
      }
      process.exit(2);
    }

    const data = isJson ? await res.json() : await res.text();
    const extracted = extractDotPath(data, args.extract);

    // eslint-disable-next-line no-console
    console.log(
      typeof extracted === "string"
        ? extracted
        : JSON.stringify(extracted, null, 2)
    );
  } finally {
    clearTimeout(timeout);
  }
}

main().catch((err) => {
  const msg = err?.name === "AbortError" ? "Request timed out." : (err?.message || String(err));
  // eslint-disable-next-line no-console
  console.error(`Error: ${msg}`);
  process.exit(1);
});
