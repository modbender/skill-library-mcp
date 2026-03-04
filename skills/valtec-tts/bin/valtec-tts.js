#!/usr/bin/env node

/**
 * Valtec Vietnamese TTS — OpenClaw skill wrapper.
 *
 * Calls the Python inference scripts that live inside VALTEC_TTS_DIR.
 * No Python code is bundled with this wrapper; all scripts are part of
 * the user-installed valtec-tts repository.
 */

const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

function usage(message) {
  if (message) console.error(message);
  console.error(
    "\nUsage: valtec-tts [--speaker <name>] [--zeroshot] [--reference <file>] [-o <file>] \"text\"",
  );
  console.error("\nRequired env:\n  VALTEC_TTS_DIR  Path to valtec-tts repository");
  process.exit(1);
}

function resolveTtsDir(explicit) {
  const value = (explicit || process.env.VALTEC_TTS_DIR || "").trim();
  return value;
}

function resolvePython(ttsDir) {
  // Use the Python that is on PATH
  const name = process.platform === "win32" ? "python" : "python3";
  const r = spawnSync(name, ["--version"], { stdio: "pipe", timeout: 5000 });
  return r.status === 0 ? name : null;
}

// --- Parse arguments ---
const args = process.argv.slice(2);
let speaker = "NF";
let zeroshot = false;
let reference = "";
let output = "tts.wav";
let speed = "1.0";
let ttsDir = "";
const textParts = [];

for (let i = 0; i < args.length; i += 1) {
  const a = args[i];
  if (a === "--speaker") { speaker = args[++i] || "NF"; continue; }
  if (a === "--zeroshot") { zeroshot = true; continue; }
  if (a === "--reference" || a === "-r") { reference = args[++i] || ""; continue; }
  if (a === "-o" || a === "--output") { output = args[++i] || "tts.wav"; continue; }
  if (a === "--speed") { speed = args[++i] || "1.0"; continue; }
  if (a === "--tts-dir") { ttsDir = args[++i] || ""; continue; }
  textParts.push(a);
}

ttsDir = resolveTtsDir(ttsDir);
if (!ttsDir || !fs.existsSync(ttsDir)) {
  usage("VALTEC_TTS_DIR not set or does not exist.");
}

const text = textParts.join(" ").trim();
if (!text) usage("Missing text.");

const python = resolvePython(ttsDir);
if (!python) usage("Python 3 is required but not found in PATH.");

const outputPath = path.isAbsolute(output) ? output : path.join(process.cwd(), output);
fs.mkdirSync(path.dirname(outputPath), { recursive: true });

// --- Build command ---
let script;
let scriptArgs;

if (zeroshot) {
  if (!reference) usage("--reference is required for --zeroshot mode.");
  script = path.join(ttsDir, "infer_zeroshot.py");
  if (!fs.existsSync(script)) usage(`Script not found: ${script}`);

  scriptArgs = [
    script,
    "-t", text,
    "-r", reference,
    "-o", outputPath,
    "--speed", speed,
  ];
} else {
  script = path.join(ttsDir, "infer.py");
  if (!fs.existsSync(script)) usage(`Script not found: ${script}`);

  scriptArgs = [
    script,
    "-t", text,
    "-o", outputPath,
    "-s", speaker,
    "--length_scale", speed,
  ];
}

const child = spawnSync(python, scriptArgs, {
  stdio: "inherit",
  cwd: ttsDir,
});

if (typeof child.status === "number") {
  process.exit(child.status);
}
if (child.error) {
  console.error(child.error.message || String(child.error));
}
process.exit(1);
