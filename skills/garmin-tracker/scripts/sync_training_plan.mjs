#!/usr/bin/env node

import fs from "node:fs/promises";
import process from "node:process";
import {
  cleanupScheduled,
  normalizeDate,
  normalizeWeek,
  parseCalendarUpcomingFromLines,
  sanitizeUpcoming,
} from "./training_plan_parser.mjs";

const DEFAULT_CDP_URL = "http://127.0.0.1:39222";
const DEFAULT_TRAINING_PLAN_URL = "https://connect.garmin.com/app/training-plan";
const DEFAULT_FILE = "garmin_tracking.json";
const DEFAULT_CONFIG_FILE = "data/config/openclaw.json";

async function loadChromium() {
  try {
    const mod = await import("playwright-core");
    if (mod?.chromium) {
      return mod.chromium;
    }
  } catch {
    // Fall through to image-level fallback.
  }

  try {
    const mod = await import("/app/node_modules/playwright-core/index.js");
    if (mod?.chromium) {
      return mod.chromium;
    }
  } catch {
    // Fall through to explicit error.
  }

  throw new Error(
    "playwright-core is not available. Install it in the workspace (npm install playwright-core) or ensure the OpenClaw image includes /app/node_modules/playwright-core.",
  );
}

function parseArgs(argv) {
  const args = {
    cdpUrl: null,
    configFile: DEFAULT_CONFIG_FILE,
    url: DEFAULT_TRAINING_PLAN_URL,
    file: DEFAULT_FILE,
    write: false,
    timeoutMs: 30000,
    debugDump: null,
    authSource: "auto",
    garminEmail: null,
    garminPassword: null,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--cdp-url") {
      args.cdpUrl = argv[++i];
    } else if (token === "--config") {
      args.configFile = argv[++i];
    } else if (token === "--url") {
      args.url = argv[++i];
    } else if (token === "--file") {
      args.file = argv[++i];
    } else if (token === "--write") {
      args.write = true;
    } else if (token === "--timeout-ms") {
      args.timeoutMs = Number(argv[++i]) || args.timeoutMs;
    } else if (token === "--debug-dump") {
      args.debugDump = argv[++i];
    } else if (token === "--auth-source") {
      args.authSource = argv[++i] ?? args.authSource;
    } else if (token === "--garmin-email") {
      args.garminEmail = argv[++i] ?? null;
    } else if (token === "--garmin-password") {
      args.garminPassword = argv[++i] ?? null;
    } else if (token === "-h" || token === "--help") {
      printHelp();
      process.exit(0);
    }
  }

  return args;
}

function printHelp() {
  console.log(`Usage: node sync_training_plan.mjs [options]

Options:
  --cdp-url <url>      CDP endpoint override (highest priority)
  --config <path>      OpenClaw config path (default: ${DEFAULT_CONFIG_FILE})
  --url <url>          Garmin training plan URL (default: ${DEFAULT_TRAINING_PLAN_URL})
  --file <path>        Tracking JSON file (default: ${DEFAULT_FILE})
  --timeout-ms <n>     Navigation/eval timeout in ms (default: 30000)
  --debug-dump <path>  Write raw extraction payload for parser tuning
  --auth-source <m>    Auth source: auto|browser|credentials (default: auto)
  --garmin-email <v>   Garmin login email (credentials mode)
  --garmin-password <v> Garmin login password (credentials mode)
  --write              Persist changes to file
  -h, --help           Show this help`);
}

async function readJson(path) {
  const raw = await fs.readFile(path, "utf8");
  return JSON.parse(raw);
}

async function writeJson(path, data) {
  await fs.writeFile(path, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

async function resolveTrackingFilePath(inputPath) {
  try {
    await fs.access(inputPath);
    return inputPath;
  } catch (err) {
    if (inputPath.startsWith("persona/")) {
      const stripped = inputPath.slice("persona/".length);
      try {
        await fs.access(stripped);
        return stripped;
      } catch {
        // Fall through to original error.
      }
    }
    throw err;
  }
}

function containsLoginPrompt(extracted) {
  const pool = [extracted.pageTitle, extracted.bodyText, ...(extracted.lines || [])]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return pool.includes("sign in") || pool.includes("entrar");
}

function resolveCdpFromConfig(config) {
  const defaultProfile = config?.browser?.defaultProfile;
  const profiles = config?.browser?.profiles;
  if (defaultProfile && profiles?.[defaultProfile]?.cdpUrl) {
    return String(profiles[defaultProfile].cdpUrl);
  }
  if (profiles?.openclaw?.cdpUrl) {
    return String(profiles.openclaw.cdpUrl);
  }
  return null;
}

async function resolveCdpUrl(args) {
  if (args.cdpUrl) {
    return args.cdpUrl;
  }

  if (args.configFile) {
    try {
      const config = await readJson(args.configFile);
      const resolved = resolveCdpFromConfig(config);
      if (resolved) {
        return resolved;
      }
    } catch {
      // Ignore and use fallback default.
    }
  }

  return DEFAULT_CDP_URL;
}

async function extractTrainingPlan(page, url, timeoutMs) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
  await page.waitForTimeout(1500);
  const detailsLocator = page
    .locator("text=/View Details|Ver detalhes|Ver detalhes do plano/i")
    .first();
  if ((await detailsLocator.count()) > 0) {
    await detailsLocator.click({ timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(2000);
  }
  const calendarLocator = page.locator("text=/\\bCalendar\\b|\\bCalendário\\b/i").first();
  if ((await calendarLocator.count()) > 0) {
    await calendarLocator.click({ timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(2000);
  }

  return page.evaluate(() => {
    const textOf = (el) => (el?.innerText || "").replace(/\s+/g, " ").trim();

    const bodyText = (document.body?.innerText || "").replace(/\s+/g, " ").trim();
    const lines = (document.body?.innerText || "")
      .split("\n")
      .map((line) => line.replace(/\s+/g, " ").trim())
      .filter(Boolean);

    const selectors = [
      "[class*='Training']",
      "[class*='Plan']",
      "[class*='Workout']",
      "[class*='Calendar']",
      "[class*='Day']",
      "article",
      "li",
      "[role='row']",
      "[role='button']",
      "a",
      "button",
    ];

    const candidateTexts = [];
    for (const selector of selectors) {
      for (const el of document.querySelectorAll(selector)) {
        const text = textOf(el);
        if (!text) {
          continue;
        }
        if (text.length < 6 || text.length > 220) {
          continue;
        }
        candidateTexts.push(text);
      }
    }

    const workoutPattern = /\bW\d{1,2}D\d\b/i;
    const workoutKeywords =
      /\b(rest|easy run|steady run|long run|intervals?|tempo|swim|cross training|strength|yoga|pilates|descanso|corrida|natação|força)\b/i;
    const dateAttrKeys = ["aria-label", "data-date", "datetime", "title"];
    const upcomingHints = [];

    const pickContainer = (node) =>
      node.closest(
        "article, li, [role='row'], [role='button'], [class*='Day'], [class*='Calendar'], [class*='Workout'], [class*='Training']",
      ) ?? node.parentElement;

    for (const el of document.querySelectorAll("*")) {
      const text = textOf(el);
      if (!text || text.length < 4 || text.length > 140) {
        continue;
      }
      if (!workoutPattern.test(text) && !workoutKeywords.test(text)) {
        continue;
      }

      const container = pickContainer(el);
      const hostText = textOf(container).slice(0, 260);
      const attrs = [];

      for (const node of [el, container]) {
        if (!node) {
          continue;
        }
        for (const key of dateAttrKeys) {
          const value = node.getAttribute?.(key);
          if (value) {
            attrs.push(`${key}:${value}`);
          }
        }
      }

      upcomingHints.push({
        text,
        hostText,
        attrs,
      });
    }

    return {
      pageTitle: document.title || "",
      bodyText,
      lines: lines.slice(0, 1200),
      candidates: candidateTexts.slice(0, 3000),
      upcomingHints: upcomingHints.slice(0, 1000),
    };
  });
}

async function tryCredentialLogin(page, args, timeoutMs) {
  if (!args.garminEmail || !args.garminPassword) {
    return { attempted: false, success: false, reason: "missing_credentials" };
  }

  try {
    await page.goto("https://connect.garmin.com/signin/", {
      waitUntil: "domcontentloaded",
      timeout: timeoutMs,
    });
    await page.waitForTimeout(1200);

    const emailSelectors = [
      "input[type='email']",
      "input[name='email']",
      "input[id*='email' i]",
      "input[autocomplete='username']",
    ];
    const passwordSelectors = [
      "input[type='password']",
      "input[name='password']",
      "input[id*='password' i]",
      "input[autocomplete='current-password']",
    ];

    let emailFilled = false;
    for (const selector of emailSelectors) {
      const field = page.locator(selector).first();
      if ((await field.count()) > 0) {
        await field.fill(args.garminEmail);
        emailFilled = true;
        break;
      }
    }
    if (!emailFilled) {
      return { attempted: true, success: false, reason: "email_field_not_found" };
    }

    let passwordFilled = false;
    for (const selector of passwordSelectors) {
      const field = page.locator(selector).first();
      if ((await field.count()) > 0) {
        await field.fill(args.garminPassword);
        passwordFilled = true;
        break;
      }
    }
    if (!passwordFilled) {
      return { attempted: true, success: false, reason: "password_field_not_found" };
    }

    const submitLocators = [
      page.locator("button[type='submit']").first(),
      page.locator("text=/^Sign In$|^Entrar$|^Login$/i").first(),
      page.locator("button:has-text('Sign In')").first(),
      page.locator("button:has-text('Entrar')").first(),
    ];
    let clicked = false;
    for (const locator of submitLocators) {
      if ((await locator.count()) > 0) {
        await locator.click({ timeout: 5000 }).catch(() => {});
        clicked = true;
        break;
      }
    }
    if (!clicked) {
      return { attempted: true, success: false, reason: "submit_not_found" };
    }

    await page.waitForTimeout(5000);
    await page.goto(args.url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
    await page.waitForTimeout(1500);
    return { attempted: true, success: true, reason: "login_attempted" };
  } catch {
    return { attempted: true, success: false, reason: "login_exception" };
  }
}

async function main() {
  const chromium = await loadChromium();
  const args = parseArgs(process.argv.slice(2));
  const now = new Date();
  const today = now.toISOString().slice(0, 10);
  const nowYear = now.getUTCFullYear();
  const cdpUrl = await resolveCdpUrl(args);

  const resolvedFilePath = await resolveTrackingFilePath(args.file);
  const fileData = await readJson(resolvedFilePath);

  const browser = await chromium.connectOverCDP(cdpUrl, { timeout: args.timeoutMs });
  try {
    const context = browser.contexts()[0] ?? (await browser.newContext());
    const page = context.pages()[0] ?? (await context.newPage());

    let extracted = await extractTrainingPlan(page, args.url, args.timeoutMs);
    const auth = {
      source: args.authSource,
      loginAttempted: false,
      loginResult: "not_needed",
    };
    const wasSignedOut = containsLoginPrompt(extracted);
    if (wasSignedOut) {
      const useCreds =
        args.authSource === "credentials" ||
        (args.authSource === "auto" && Boolean(args.garminEmail && args.garminPassword));
      if (useCreds) {
        const login = await tryCredentialLogin(page, args, args.timeoutMs);
        auth.loginAttempted = login.attempted;
        auth.loginResult = login.reason;
        if (login.attempted && login.success) {
          extracted = await extractTrainingPlan(page, args.url, args.timeoutMs);
        }
      } else {
        auth.loginResult =
          args.authSource === "credentials" ? "credentials_required" : "browser_login_required";
      }
    }
    if (args.debugDump) {
      await writeJson(args.debugDump, extracted);
    }

    const textPool = [
      extracted.pageTitle,
      extracted.bodyText,
      ...extracted.lines,
      ...extracted.candidates,
    ].filter(Boolean);
    const calendarParsed = parseCalendarUpcomingFromLines(extracted.lines, today);

    let currentWeek = null;
    for (const entry of textPool) {
      currentWeek = normalizeWeek(entry);
      if (currentWeek) {
        break;
      }
    }
    if (!currentWeek && calendarParsed.inferredWeek) {
      currentWeek = calendarParsed.inferredWeek;
    }

    const upcomingCandidates = [...calendarParsed.upcoming];
    for (const entry of textPool) {
      const date = normalizeDate(entry, nowYear);
      const scheduled = cleanupScheduled(entry);
      if (!date || !scheduled) {
        continue;
      }
      if (date >= today) {
        upcomingCandidates.push({ date, scheduled });
      }
    }

    for (const hint of extracted.upcomingHints ?? []) {
      const scheduled = cleanupScheduled(hint.text) ?? cleanupScheduled(hint.hostText);
      if (!scheduled) {
        continue;
      }

      let date = null;
      for (const attr of hint.attrs ?? []) {
        const parsed = normalizeDate(attr, nowYear);
        if (parsed) {
          date = parsed;
          break;
        }
      }
      if (!date) {
        date = normalizeDate(hint.hostText, nowYear);
      }
      if (!date || date < today) {
        continue;
      }
      upcomingCandidates.push({ date, scheduled });
    }

    const upcoming = sanitizeUpcoming(upcomingCandidates).slice(0, 14);

    if (currentWeek) {
      fileData.currentWeek = currentWeek;
    }

    if (upcoming.length > 0) {
      fileData.upcoming = upcoming;
    }

    fileData.lastUpdate = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");

    const result = {
      updated: {
        currentWeek: fileData.currentWeek,
        upcomingCount: Array.isArray(fileData.upcoming) ? fileData.upcoming.length : 0,
      },
      extraction: {
        title: extracted.pageTitle,
        parsedWeek: currentWeek,
        parsedUpcomingCount: upcoming.length,
        cdpUrl,
      },
      auth,
      warnings: [],
    };
    const signedOut = containsLoginPrompt(extracted);

    if (!currentWeek) {
      result.warnings.push(
        "Could not confidently parse currentWeek from training-plan page; kept existing value.",
      );
    }
    if (upcoming.length === 0) {
      result.warnings.push("Could not confidently parse upcoming items; kept existing list.");
    }
    if (signedOut) {
      result.warnings.push(
        `Garmin session appears signed out. Sign in at https://connect.garmin.com/signin/ using the active controlled browser profile (CDP: ${cdpUrl}), then rerun sync. If browser access is impossible, rerun with --auth-source credentials plus --garmin-email/--garmin-password.`,
      );
    }

    if (args.write) {
      if (signedOut) {
        result.skippedWrite = true;
        result.skipReason = "signed_out";
      } else {
        await writeJson(resolvedFilePath, fileData);
        result.wroteFile = resolvedFilePath;
      }
    }

    console.log(JSON.stringify(result, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  const message = error instanceof Error ? error.stack || error.message : String(error);
  console.error(`sync_training_plan failed: ${message}`);
  process.exit(1);
});
