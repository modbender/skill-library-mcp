import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { config as loadDotenv } from "dotenv";
import { chromium, type Request } from "playwright";

loadDotenv();

type ContextCookieInput = {
  name: string;
  value: string;
  url?: string;
  domain?: string;
  path?: string;
  expires?: number;
  httpOnly?: boolean;
  secure?: boolean;
  sameSite?: "Strict" | "Lax" | "None";
  partitionKey?: string;
};

type AnalyzeOptions = {
  targetUrl: string;
  outputPath: string;
  headless: boolean;
  durationMs: number;
  cookieHeader: string | undefined;
  cookiesJsonPath: string | undefined;
};

type CapturedRequest = {
  method: string;
  url: string;
  path: string;
  headers: Record<string, string>;
  postData?: string;
};

const HELP_TEXT = `
Usage:
  bun run scripts/analyze-api.ts [--target <url>] [--output <path>] [--duration-ms <number>] [--headless true|false] [--cookie-header "<cookie-string>"] [--cookies-json <path>]

Examples:
  bun run scripts/analyze-api.ts --target https://www.binance.com/en/square --duration-ms 30000
  bun run scripts/analyze-api.ts --cookies-json ./cookies.json --output ./api-report.json
`;

const readArgValue = (argv: string[], flag: string): string | undefined => {
  const index = argv.indexOf(flag);
  if (index < 0) {
    return undefined;
  }
  const value = argv[index + 1];
  return value && !value.startsWith("--") ? value : undefined;
};

const parseBooleanFlag = (value: string | undefined, defaultValue: boolean): boolean => {
  if (value === undefined) {
    return defaultValue;
  }
  return value.toLowerCase() !== "false";
};

const parseNumberFlag = (value: string | undefined, defaultValue: number): number => {
  if (value === undefined) {
    return defaultValue;
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new Error(`Invalid numeric flag value: ${value}`);
  }
  return parsed;
};

const parseCookieHeader = (cookieHeader: string): ContextCookieInput[] =>
  cookieHeader
    .split(";")
    .map((segment) => segment.trim())
    .filter((segment) => segment.length > 0)
    .map((segment) => {
      const separatorIndex = segment.indexOf("=");
      if (separatorIndex <= 0) {
        throw new Error(`Invalid cookie segment "${segment}"`);
      }
      const name = segment.slice(0, separatorIndex).trim();
      const value = segment.slice(separatorIndex + 1).trim();
      return {
        name,
        value,
        domain: ".binance.com",
        path: "/",
        httpOnly: false,
        secure: true,
        sameSite: "Lax" as const
      };
    });

const loadCookies = (options: AnalyzeOptions): ContextCookieInput[] => {
  if (options.cookiesJsonPath) {
    const filePath = path.resolve(process.cwd(), options.cookiesJsonPath);
    const raw = readFileSync(filePath, "utf8");
    const parsed = JSON.parse(raw) as unknown;

    if (!Array.isArray(parsed)) {
      throw new Error("cookies-json must be a JSON array");
    }

    return parsed.map((item) => {
      const cookie = item as Partial<ContextCookieInput>;
      if (!cookie.name || !cookie.value) {
        throw new Error("Each cookie entry must include name and value");
      }

      return {
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain ?? ".binance.com",
        path: cookie.path ?? "/",
        httpOnly: cookie.httpOnly ?? false,
        secure: cookie.secure ?? true,
        sameSite: cookie.sameSite ?? "Lax"
      };
    });
  }

  if (options.cookieHeader) {
    return parseCookieHeader(options.cookieHeader);
  }

  return [];
};

const toCapturedRequest = (request: Request): CapturedRequest | undefined => {
  const url = request.url();
  if (!url.includes("/bapi/")) {
    return undefined;
  }

  const parsedUrl = new URL(url);
  const headers = request.headers();
  const postData = request.postData();
  return {
    method: request.method(),
    url,
    path: parsedUrl.pathname,
    headers,
    ...(postData ? { postData: postData.slice(0, 1200) } : {})
  };
};

const guessEndpoint = (paths: string[], keywords: string[]): string | undefined =>
  paths.find((candidate) => keywords.every((keyword) => candidate.toLowerCase().includes(keyword.toLowerCase())));

const buildSuggestions = (paths: string[]): Record<string, string | undefined> => ({
  BINANCE_VALIDATE_SESSION_PATH: guessEndpoint(paths, ["user"]),
  BINANCE_PUBLISH_POST_PATH: guessEndpoint(paths, ["post", "publish"]),
  BINANCE_GET_POST_STATUS_PATH: guessEndpoint(paths, ["post", "detail"]),
  BINANCE_IMAGE_UPLOAD_PATH: guessEndpoint(paths, ["upload", "image"])
});

const parseOptions = (argv: string[]): AnalyzeOptions => {
  if (argv.includes("--help") || argv.includes("-h")) {
    process.stdout.write(`${HELP_TEXT}\n`);
    process.exit(0);
  }

  return {
    targetUrl: readArgValue(argv, "--target") ?? "https://www.binance.com/en/square",
    outputPath: readArgValue(argv, "--output") ?? "docs/api-analysis.json",
    durationMs: parseNumberFlag(readArgValue(argv, "--duration-ms"), 20_000),
    headless: parseBooleanFlag(readArgValue(argv, "--headless"), false),
    cookieHeader: readArgValue(argv, "--cookie-header") ?? process.env.BINANCE_COOKIE_HEADER,
    cookiesJsonPath: readArgValue(argv, "--cookies-json")
  };
};

const run = async (): Promise<void> => {
  const options = parseOptions(process.argv.slice(2));
  const cookies = loadCookies(options);

  const browser = await chromium.launch({ headless: options.headless });
  const context = await browser.newContext();

  if (cookies.length > 0) {
    await context.addCookies(cookies);
  }

  const page = await context.newPage();
  const captured = new Map<string, CapturedRequest>();

  page.on("request", (request) => {
    const normalized = toCapturedRequest(request);
    if (!normalized) {
      return;
    }
    const key = `${normalized.method} ${normalized.path}`;
    if (!captured.has(key)) {
      captured.set(key, normalized);
    }
  });

  await page.goto(options.targetUrl, { waitUntil: "domcontentloaded", timeout: 60_000 });
  await page.waitForTimeout(options.durationMs);

  const requests = Array.from(captured.values()).sort((a, b) => a.path.localeCompare(b.path));
  const uniquePaths = Array.from(new Set(requests.map((request) => request.path))).sort();
  const report = {
    generatedAt: new Date().toISOString(),
    targetUrl: options.targetUrl,
    sampleSize: requests.length,
    uniquePaths,
    suggestedEnv: buildSuggestions(uniquePaths),
    capturedRequests: requests
  };

  const outputPath = path.resolve(process.cwd(), options.outputPath);
  writeFileSync(outputPath, JSON.stringify(report, null, 2), "utf8");

  await context.close();
  await browser.close();

  process.stdout.write(`Captured ${requests.length} Binance API requests.\n`);
  process.stdout.write(`Report saved to ${outputPath}\n`);
};

run().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : "Unknown error";
  process.stderr.write(`analyze-api failed: ${message}\n`);
  process.exitCode = 1;
});
