#!/usr/bin/env node
/**
 * Vexa API CLI (reusable skill helper)
 *
 * Env:
 * - VEXA_API_KEY (required)
 * - VEXA_BASE_URL (optional, default https://api.cloud.vexa.ai)
 */

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SKILL_ROOT = path.join(__dirname, "..");
const SKILL_SECRETS_DIR = path.join(SKILL_ROOT, "secrets");
const SECRETS_FILE_SKILL = path.join(SKILL_SECRETS_DIR, "vexa.env");
const STATE_FILE_SKILL = path.join(SKILL_SECRETS_DIR, "vexa-state.json");
const SECRETS_FILE_HOME = path.join(os.homedir(), ".openclaw", "secrets", "vexa.env");
const STATE_FILE_HOME = path.join(os.homedir(), ".openclaw", "secrets", "vexa-state.json");

function getStateFile() {
  return fs.existsSync(STATE_FILE_SKILL) ? STATE_FILE_SKILL : STATE_FILE_HOME;
}

function getStateWriteFile() {
  return STATE_FILE_SKILL;
}

function loadVexaEnv() {
  if (process.env.VEXA_API_KEY?.trim()) return;
  for (const file of [SECRETS_FILE_SKILL, SECRETS_FILE_HOME]) {
    try {
      const raw = fs.readFileSync(file, "utf8");
      for (const line of raw.split("\n")) {
        const rest = line.replace(/^\s*export\s+/, "").trim();
        const m = rest.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$/);
        if (m && !process.env[m[1]]) {
          process.env[m[1]] = m[2].replace(/^["']|["']$/g, "").trim();
        }
      }
      break;
    } catch {}
  }
}

loadVexaEnv();

const BASE_URL = (process.env.VEXA_BASE_URL || "https://api.cloud.vexa.ai").replace(/\/$/, "");
const API_KEY = process.env.VEXA_API_KEY;

function die(msg, code = 1) {
  console.error(msg);
  process.exit(code);
}

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const k = a.slice(2);
      const v = argv[i + 1];
      if (v == null || v.startsWith("--")) out[k] = true;
      else {
        out[k] = v;
        i++;
      }
    } else {
      out._.push(a);
    }
  }
  return out;
}

function readState() {
  const stateFile = getStateFile();
  try {
    const raw = fs.readFileSync(stateFile, "utf8");
    const parsed = JSON.parse(raw);
    return { first_use: parsed?.first_use !== false };
  } catch {
    return { first_use: true };
  }
}

function writeState(state) {
  const stateFile = getStateWriteFile();
  const dir = path.dirname(stateFile);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2) + "\n", { mode: 0o600 });
  try { fs.chmodSync(stateFile, 0o600); } catch {}
}

function forwardOnboardingArgs(args) {
  const keys = ["api_key", "meeting_url", "platform", "native_meeting_id", "passcode", "language", "bot_name", "persist", "wait_seconds", "poll_every_seconds"];
  const out = [];
  for (const k of keys) {
    if (args[k] === undefined) continue;
    out.push(`--${k}`);
    if (args[k] !== true) out.push(String(args[k]));
  }
  return out;
}

function runOnboardingAndExit(args) {
  const onboardScript = path.join(__dirname, "onboard.mjs");
  const result = spawnSync(process.execPath, [onboardScript, ...forwardOnboardingArgs(args)], {
    stdio: "inherit",
    env: process.env
  });
  process.exit(result.status ?? 1);
}

function ensureConfiguredOrOnboard(cmd) {
  if (cmd === "parse:meeting-url" || cmd === "onboard") return;

  const state = readState();

  if (API_KEY) {
    if (state.first_use) {
      writeState({ first_use: false, configured_at: new Date().toISOString() });
    }
    return;
  }

  die("Missing VEXA_API_KEY. Source skills/vexa/secrets/vexa.env or run: node skills/vexa/scripts/onboard.mjs");
}

function csv(value) {
  if (value == null || value === true) return undefined;
  return String(value).split(",").map((s) => s.trim()).filter(Boolean);
}

function assertDeleteGuard(args, scopeLabel) {
  if (!args.confirm) die(`Refusing destructive call (${scopeLabel}). Re-run with --confirm DELETE.`);
  if (String(args.confirm) !== "DELETE") die("Invalid --confirm value. Expected exactly: DELETE");
}

function normalizeGoogleMeetId(raw) {
  if (!raw) return null;
  const v = String(raw).trim();
  if (/^[a-z]{3}-[a-z]{4}-[a-z]{3}$/i.test(v)) return v.toLowerCase();
  try {
    const u = new URL(v);
    if (!/meet\.google\.com$/i.test(u.hostname)) return null;
    const m = u.pathname.match(/\/([a-z]{3}-[a-z]{4}-[a-z]{3})/i);
    return m?.[1]?.toLowerCase() || null;
  } catch {
    return null;
  }
}

function normalizeTeamsInfo(raw) {
  if (!raw) return null;
  const v = String(raw).trim();
  if (/^\d{10,15}$/.test(v)) return { native_meeting_id: v, passcode: null };
  try {
    const u = new URL(v);
    if (!/teams\./i.test(u.hostname)) return null;
    const m = u.pathname.match(/\/meet\/(\d{10,15})/i);
    const native_meeting_id = m?.[1] || null;
    const passcode = u.searchParams.get("p") || null;
    if (!native_meeting_id) return null;
    return { native_meeting_id, passcode };
  } catch {
    return null;
  }
}

function parseMeetingInput({ meeting_url, platform, native_meeting_id, passcode }) {
  // Explicit platform/id wins.
  if (platform && native_meeting_id) {
    return {
      platform,
      native_meeting_id: String(native_meeting_id),
      passcode: passcode ? String(passcode) : undefined
    };
  }

  if (!meeting_url) return null;

  const g = normalizeGoogleMeetId(meeting_url);
  if (g) return { platform: "google_meet", native_meeting_id: g };

  const t = normalizeTeamsInfo(meeting_url);
  if (t) return {
    platform: "teams",
    native_meeting_id: t.native_meeting_id,
    passcode: t.passcode || (passcode ? String(passcode) : undefined)
  };

  return null;
}

async function vexaFetch(path, { method = "GET", body } = {}) {
  if (!API_KEY) die("Missing VEXA_API_KEY. Source ~/.openclaw/secrets/vexa.env or run: node skills/vexa/scripts/onboard.mjs");

  const url = `${BASE_URL}${path}`;
  const headers = {
    "X-API-Key": API_KEY,
    Accept: "application/json"
  };
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const res = await fetch(url, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body)
  });

  const text = await res.text();
  let json;
  try { json = text ? JSON.parse(text) : null; } catch { json = { raw: text }; }

  if (!res.ok) {
    const msg = typeof json === "object" ? JSON.stringify(json, null, 2) : String(json);
    die(`Vexa API error ${res.status} ${res.statusText}\n${msg}`);
  }

  return json;
}

function print(obj) {
  process.stdout.write(JSON.stringify(obj, null, 2) + "\n");
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0];

  ensureConfiguredOrOnboard(cmd);

  switch (cmd) {
    case "onboard": {
      runOnboardingAndExit(args);
      return;
    }
    case "parse:meeting-url": {
      const parsed = parseMeetingInput({
        meeting_url: args.meeting_url,
        platform: args.platform,
        native_meeting_id: args.native_meeting_id,
        passcode: args.passcode
      });
      if (!parsed) {
        die("Unable to parse meeting input. Pass --meeting_url (Google Meet/Teams) or --platform + --native_meeting_id.");
      }
      return print({ ok: true, ...parsed });
    }

    case "bots:status": {
      return print(await vexaFetch("/bots/status"));
    }

    case "meetings:list": {
      return print(await vexaFetch("/meetings"));
    }

    case "bots:start": {
      const parsed = parseMeetingInput({
        meeting_url: args.meeting_url,
        platform: args.platform,
        native_meeting_id: args.native_meeting_id,
        passcode: args.passcode
      });

      if (!parsed) {
        die("Usage: bots:start (--meeting_url <url> | --platform <google_meet|teams> --native_meeting_id <id>) [--passcode ...] [--bot_name ...] [--language ...]");
      }

      if (parsed.platform === "teams" && !parsed.passcode) {
        die("Teams bot join requires passcode. Provide --passcode or a Teams URL containing ?p=...");
      }

      const body = {
        platform: parsed.platform,
        native_meeting_id: parsed.native_meeting_id,
        passcode: parsed.passcode ?? undefined,
        bot_name: args.bot_name ?? undefined,
        language: args.language ?? undefined
      };

      return print(await vexaFetch("/bots", { method: "POST", body }));
    }

    case "bots:stop": {
      const parsed = parseMeetingInput({
        meeting_url: args.meeting_url,
        platform: args.platform,
        native_meeting_id: args.native_meeting_id,
        passcode: args.passcode
      });
      if (!parsed) {
        die("Usage: bots:stop (--meeting_url <url> | --platform <google_meet|teams> --native_meeting_id <id>)");
      }
      return print(await vexaFetch(`/bots/${encodeURIComponent(parsed.platform)}/${encodeURIComponent(parsed.native_meeting_id)}`, { method: "DELETE" }));
    }

    case "bots:config:update": {
      const { platform, native_meeting_id, language } = args;
      if (!platform || !native_meeting_id || !language) {
        die("Usage: bots:config:update --platform <google_meet|teams> --native_meeting_id <id> --language <code>");
      }
      return print(await vexaFetch(`/bots/${encodeURIComponent(platform)}/${encodeURIComponent(native_meeting_id)}/config`, {
        method: "PUT",
        body: { language }
      }));
    }

    case "transcripts:get": {
      const parsed = parseMeetingInput({
        meeting_url: args.meeting_url,
        platform: args.platform,
        native_meeting_id: args.native_meeting_id,
        passcode: args.passcode
      });
      if (!parsed) {
        die("Usage: transcripts:get (--meeting_url <url> | --platform <google_meet|teams> --native_meeting_id <id>)");
      }
      return print(await vexaFetch(`/transcripts/${encodeURIComponent(parsed.platform)}/${encodeURIComponent(parsed.native_meeting_id)}`));
    }

    case "transcripts:share": {
      const { platform, native_meeting_id, meeting_id, ttl_seconds } = args;
      if (!platform || !native_meeting_id) {
        die("Usage: transcripts:share --platform <google_meet|teams> --native_meeting_id <id> [--meeting_id <int>] [--ttl_seconds <int>]");
      }
      const qs = new URLSearchParams();
      if (meeting_id !== undefined) qs.set("meeting_id", String(meeting_id));
      if (ttl_seconds !== undefined) qs.set("ttl_seconds", String(ttl_seconds));
      const suffix = qs.toString() ? `?${qs.toString()}` : "";
      return print(await vexaFetch(`/transcripts/${encodeURIComponent(platform)}/${encodeURIComponent(native_meeting_id)}/share${suffix}`, { method: "POST" }));
    }

    case "meetings:update": {
      const { platform, native_meeting_id, name, notes } = args;
      const participants = csv(args.participants);
      const languages = csv(args.languages);
      if (!platform || !native_meeting_id) {
        die("Usage: meetings:update --platform <google_meet|teams> --native_meeting_id <id> [--name ...] [--participants a,b] [--languages en,es] [--notes ...]");
      }
      const data = {};
      if (name !== undefined) data.name = String(name);
      if (notes !== undefined) data.notes = String(notes);
      if (participants !== undefined) data.participants = participants;
      if (languages !== undefined) data.languages = languages;
      if (Object.keys(data).length === 0) die("Nothing to update. Provide at least one updatable field.");
      return print(await vexaFetch(`/meetings/${encodeURIComponent(platform)}/${encodeURIComponent(native_meeting_id)}`, {
        method: "PATCH",
        body: { data }
      }));
    }

    case "meetings:delete": {
      const { platform, native_meeting_id } = args;
      if (!platform || !native_meeting_id) {
        die("Usage: meetings:delete --platform <google_meet|teams> --native_meeting_id <id> --confirm DELETE");
      }
      assertDeleteGuard(args, `meeting ${platform}/${native_meeting_id}`);
      return print(await vexaFetch(`/meetings/${encodeURIComponent(platform)}/${encodeURIComponent(native_meeting_id)}`, { method: "DELETE" }));
    }

    case "report":
    case "meetings:report": {
      const parsed = parseMeetingInput({
        meeting_url: args.meeting_url,
        platform: args.platform,
        native_meeting_id: args.native_meeting_id
      });
      if (!parsed) {
        die("Usage: report (--meeting_url <url> | --platform <google_meet|teams> --native_meeting_id <id>)");
      }
      const ingestScript = path.join(__dirname, "ingest.mjs");
      const ingestArgs = args.meeting_url
        ? ["--meeting_url", args.meeting_url]
        : ["--platform", parsed.platform, "--native_meeting_id", parsed.native_meeting_id];
      const result = spawnSync(process.execPath, [ingestScript, ...ingestArgs], {
        stdio: "inherit",
        env: process.env
      });
      process.exit(result.status ?? 1);
    }

    case "user:webhook:set": {
      const { webhook_url } = args;
      if (!webhook_url) die("Usage: user:webhook:set --webhook_url https://example.com/path");
      return print(await vexaFetch("/user/webhook", { method: "PUT", body: { webhook_url: String(webhook_url) } }));
    }

    default: {
      die([
        "Unknown or missing command.",
        "Commands:",
        "  parse:meeting-url --meeting_url <url>",
        "  bots:status",
        "  bots:start (--meeting_url <url> | --platform ... --native_meeting_id ...) [--passcode ...] [--bot_name ...] [--language ...]",
        "  bots:stop --platform ... --native_meeting_id ...",
        "  bots:config:update --platform ... --native_meeting_id ... --language ...",
        "  meetings:list",
        "  meetings:update --platform ... --native_meeting_id ... [--name ...] [--participants a,b] [--languages en,es] [--notes ...]",
        "  meetings:delete --platform ... --native_meeting_id ... --confirm DELETE",
        "  report (--meeting_url <url> | --platform ... --native_meeting_id ...)",
        "  transcripts:get --platform ... --native_meeting_id ...",
        "  transcripts:share --platform ... --native_meeting_id ... [--meeting_id ...] [--ttl_seconds ...]",
        "  user:webhook:set --webhook_url https://...",
      ].join("\n"));
    }
  }
}

main().catch((err) => {
  console.error(err?.stack || String(err));
  process.exit(1);
});
