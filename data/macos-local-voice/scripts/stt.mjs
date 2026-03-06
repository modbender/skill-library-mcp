#!/usr/bin/env node

// Speech-to-Text using yap (Apple on-device speech recognition).
// Usage:
//   node stt.mjs <audio_file> [locale]
//   node stt.mjs --locales

import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";

const args = process.argv.slice(2);

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

if (!which("yap")) {
  die("yap not found. Install via: brew install finnvoor/tools/yap", 3);
}

// --locales mode
if (args[0] === "--locales") {
  try {
    const out = execFileSync("yap", ["transcribe", "--locale", "INVALID", "/dev/null"], {
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    }).toString();
    const locales = [...out.matchAll(/"([a-z]{2}_[A-Z]{2})"/g)]
      .map((m) => m[1])
      .sort();
    console.log(locales.join("\n"));
  } catch (e) {
    const combined = (e.stdout || "") + (e.stderr || "");
    const locales = [...combined.matchAll(/"([a-z]{2}_[A-Z]{2})"/g)]
      .map((m) => m[1])
      .sort();
    if (locales.length) {
      console.log(locales.join("\n"));
    } else {
      die("could not retrieve locale list from yap");
    }
  }
  process.exit(0);
}

const audioPath = args[0];
let locale = args[1] || "";

if (!audioPath) {
  die("audio file path required\nUsage: node stt.mjs <audio_file> [locale]", 2);
}
if (!existsSync(audioPath)) {
  die(`file not found: ${audioPath}`, 2);
}

// Normalize locale: accept both zh-CN and zh_CN
if (locale) locale = locale.replace("-", "_");

const yapArgs = ["transcribe"];
if (locale) yapArgs.push("--locale", locale);
yapArgs.push("-m", "200", audioPath);

try {
  const result = execFileSync("yap", yapArgs, { encoding: "utf-8", stdio: ["pipe", "pipe", "pipe"] }).trim();
  if (!result) die("transcription returned empty result", 4);
  console.log(result);
} catch (e) {
  const msg = ((e.stderr || "") + (e.stdout || "")).trim();
  die(`yap transcription failed: ${msg}`, 4);
}
