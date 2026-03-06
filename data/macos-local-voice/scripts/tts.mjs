#!/usr/bin/env node

// Text-to-Speech using macOS native `say` command.
// Usage:
//   node tts.mjs "<text>" [voice_name] [output_path]
//
// Auto-detects language and picks best voice if voice_name is omitted.
// Outputs the final audio file path to stdout.

import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, statSync, unlinkSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const [text, voiceArg, outputArg] = process.argv.slice(2);

function die(msg, code = 1) {
  process.stderr.write(`ERROR: ${msg}\n`);
  process.exit(code);
}

function which(cmd) {
  try {
    execFileSync("which", [cmd], { stdio: ["pipe", "pipe", "pipe"] });
    return true;
  } catch {
    return false;
  }
}

if (!text) die('text required\nUsage: node tts.mjs "<text>" [voice_name] [output_path]', 2);
if (!which("say")) die("say not found (not on macOS?)", 3);

// Detect language from text
function detectLocale(t) {
  let cjk = 0;
  for (const ch of t) {
    const cp = ch.codePointAt(0);
    if ((cp >= 0x4e00 && cp <= 0x9fff) || (cp >= 0x3400 && cp <= 0x4dbf)) cjk++;
  }
  const total = t.trim().length;
  if (total === 0) return "en-US";
  return cjk / total > 0.3 ? "zh-CN" : "en-US";
}

// Resolve voice
let voice = voiceArg || "";

if (!voice) {
  const locale = detectLocale(text);
  try {
    voice = execFileSync("node", [join(__dirname, "voices.mjs"), "best", locale], {
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();
  } catch {
    process.stderr.write("WARNING: could not auto-select voice, using system default\n");
    voice = "";
  }
}

// Validate voice
if (voice) {
  try {
    execFileSync("node", [join(__dirname, "voices.mjs"), "check", voice], {
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    });
  } catch {
    die(
      `Voice '${voice}' is not available.\nGo to System Settings → Accessibility → Spoken Content → System Voice → Manage Voices to download it.`,
      5,
    );
  }
}

// Prepare output path
const outDir = join(process.env.HOME, ".openclaw", "media", "outbound");
mkdirSync(outDir, { recursive: true });

const basePath = outputArg || join(outDir, `tts-${Date.now()}`);
const aiffPath = `${basePath}.aiff`;

// Generate speech
const sayArgs = [];
if (voice) sayArgs.push("-v", voice);
sayArgs.push("-o", aiffPath, text);

try {
  execFileSync("say", sayArgs, { stdio: ["pipe", "pipe", "pipe"] });
} catch (e) {
  die(`say failed: ${((e.stderr || "") + (e.stdout || "")).trim()}`, 6);
}

if (!existsSync(aiffPath) || statSync(aiffPath).size === 0) {
  die("say produced empty output", 6);
}

// Convert to ogg/opus if ffmpeg available
if (which("ffmpeg")) {
  const oggPath = `${basePath}.ogg`;
  try {
    execFileSync(
      "ffmpeg",
      ["-hide_banner", "-loglevel", "error", "-y", "-i", aiffPath, "-c:a", "libopus", "-b:a", "48k", "-vbr", "on", "-compression_level", "10", oggPath],
      { stdio: ["pipe", "pipe", "pipe"] },
    );
    unlinkSync(aiffPath);
    console.log(oggPath);
  } catch {
    // ffmpeg failed, keep aiff
    console.log(aiffPath);
  }
} else {
  console.log(aiffPath);
}
