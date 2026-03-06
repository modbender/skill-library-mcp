#!/usr/bin/env node
/**
 * Smoke test: verify discord-voice plugin structure and core-bridge.
 * Run: node scripts/smoke-test.mjs
 * For full test: OPENCLAW_ROOT=/path/to/openclaw node scripts/smoke-test.mjs
 */

import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";
import { existsSync, readFileSync } from "node:fs";

const require = createRequire(import.meta.url);
const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

const results = [];
function ok(msg) {
  results.push({ ok: true, msg });
  console.log("  ✓", msg);
}
function fail(msg) {
  results.push({ ok: false, msg });
  console.log("  ✗", msg);
}

console.log("\n[discord-voice] Smoke test\n");

// 1. Package manifest
const pkg = require(join(root, "package.json"));
if (pkg.openclaw?.extensions?.length) {
  ok("package.json: openclaw.extensions present");
} else {
  fail("package.json: openclaw.extensions missing");
}

// 2. Plugin manifest
const pluginPath = join(root, "openclaw.plugin.json");
if (existsSync(pluginPath)) {
  const manifest = require(pluginPath);
  if (manifest.id === "discord-voice" && manifest.configSchema) {
    ok("openclaw.plugin.json: id and configSchema present");
  } else {
    fail("openclaw.plugin.json: invalid structure");
  }
} else {
  fail("openclaw.plugin.json missing");
}

// 3. Entry file
const entryPath = join(root, pkg.openclaw?.extensions?.[0] || "index.ts");
if (existsSync(entryPath)) {
  ok("Entry file exists: " + (pkg.openclaw?.extensions?.[0] || "index.ts"));
} else {
  fail("Entry file missing");
}

// 4. Core bridge API alignment (extensionAPI expectations) (extensionAPI exports)
const expectedExports = [
  "resolveAgentDir",
  "resolveAgentWorkspaceDir",
  "resolveAgentIdentity",
  "resolveThinkingDefault",
  "runEmbeddedPiAgent",
  "resolveAgentTimeoutMs",
  "ensureAgentWorkspace",
  "resolveStorePath",
  "loadSessionStore",
  "saveSessionStore",
  "resolveSessionFilePath",
  "DEFAULT_MODEL",
  "DEFAULT_PROVIDER",
];
const coreBridgePath = join(root, "src/core-bridge.ts");
if (existsSync(coreBridgePath)) {
  const content = readFileSync(coreBridgePath, "utf8");
  const missing = expectedExports.filter((e) => !content.includes(e));
  if (missing.length === 0) {
    ok("core-bridge.ts: expects all extensionAPI exports");
  } else {
    fail("core-bridge.ts: missing refs: " + missing.join(", "));
  }
  if (content.includes("openclaw") && content.includes("extensionAPI.js")) {
    ok("core-bridge.ts: uses openclaw + extensionAPI.js");
  } else {
    fail("core-bridge.ts: not aligned with OpenClaw extensionAPI");
  }
  if (!content.includes("clawdbot") && !content.includes("CLAWDBOT_ROOT")) {
    ok("core-bridge.ts: no clawdbot/CLAWDBOT_ROOT remnants");
  } else {
    fail("core-bridge.ts: still references clawdbot");
  }
} else {
  fail("src/core-bridge.ts missing");
}

// 5. Local providers (local-whisper, kokoro) from PR #2
const sttPath = join(root, "src", "stt.ts");
const ttsPath = join(root, "src", "tts.ts");
if (existsSync(sttPath)) {
  const sttContent = readFileSync(sttPath, "utf8");
  if (sttContent.includes("LocalWhisperSTT") && sttContent.includes('case "local-whisper"')) {
    ok("stt.ts: LocalWhisperSTT and local-whisper provider present");
  } else {
    fail("stt.ts: LocalWhisperSTT or local-whisper case missing");
  }
  if (sttContent.includes("WyomingWhisperSTT") && sttContent.includes('case "wyoming-whisper"')) {
    ok("stt.ts: WyomingWhisperSTT and wyoming-whisper provider present");
  } else {
    fail("stt.ts: WyomingWhisperSTT or wyoming-whisper case missing");
  }
} else {
  fail("src/stt.ts missing");
}
if (existsSync(ttsPath)) {
  const ttsContent = readFileSync(ttsPath, "utf8");
  if (ttsContent.includes("KokoroTTSProvider") && ttsContent.includes('case "kokoro"')) {
    ok("tts.ts: KokoroTTSProvider and kokoro provider present");
  } else {
    fail("tts.ts: KokoroTTSProvider or kokoro case missing");
  }
  if (ttsContent.includes("EdgeTTSProvider") && ttsContent.includes('case "edge"')) {
    ok("tts.ts: EdgeTTSProvider and edge provider present");
  } else {
    fail("tts.ts: EdgeTTSProvider or edge case missing");
  }
  if (ttsContent.includes("DeepgramTTS") && ttsContent.includes('case "deepgram"')) {
    ok("tts.ts: DeepgramTTS and deepgram provider present");
  } else {
    fail("tts.ts: DeepgramTTS or deepgram case missing");
  }
  if (ttsContent.includes("PollyTTS") && ttsContent.includes('case "polly"')) {
    ok("tts.ts: PollyTTS and polly provider present");
  } else {
    fail("tts.ts: PollyTTS or polly case missing");
  }
} else {
  fail("src/tts.ts missing");
}

// 6. Optional: load extensionAPI if OPENCLAW_ROOT set
const openclawRoot = process.env.OPENCLAW_ROOT?.trim();
if (openclawRoot) {
  const extPath = join(openclawRoot, "dist", "extensionAPI.js");
  if (existsSync(extPath)) {
    try {
      const ext = await import(pathToFileURL(extPath).href);
      const hasAll = expectedExports.every((e) => typeof ext[e] === "function" || typeof ext[e] === "string");
      if (hasAll) {
        ok("extensionAPI.js: all exports present (OPENCLAW_ROOT)");
      } else {
        const missing = expectedExports.filter((e) => typeof ext[e] !== "function" && typeof ext[e] !== "string");
        fail("extensionAPI.js: missing " + missing.join(", "));
      }
    } catch (err) {
      fail("extensionAPI.js load failed: " + err.message);
    }
  } else {
    fail("OPENCLAW_ROOT/dist/extensionAPI.js not found (run 'pnpm build' in OpenClaw)");
  }
} else {
  console.log("  (skip) OPENCLAW_ROOT not set – extensionAPI load not tested");
}

const failed = results.filter((r) => !r.ok);
console.log("\n" + (failed.length === 0 ? "All checks passed." : `Failed: ${failed.length}`) + "\n");
process.exit(failed.length > 0 ? 1 : 0);
