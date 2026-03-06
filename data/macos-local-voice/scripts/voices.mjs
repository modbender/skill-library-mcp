#!/usr/bin/env node

// Voice management using macOS AVFoundation via osascript (JXA).
// Usage:
//   node voices.mjs list [locale]       — list available voices
//   node voices.mjs check "<name>"      — check if a voice is ready
//   node voices.mjs best <locale>       — print the best quality voice name

import { execFileSync } from "node:child_process";

const [action = "list", arg = ""] = process.argv.slice(2);

function die(msg, code = 1) {
  process.stderr.write(`ERROR: ${msg}\n`);
  process.exit(code);
}

const QUALITY_LABELS = { 1: "compact", 2: "enhanced", 3: "premium" };

function getVoices() {
  const jxa = `
ObjC.import("AVFoundation");
var voices = $.AVSpeechSynthesisVoice.speechVoices;
var result = [];
for (var i = 0; i < voices.count; i++) {
  var v = voices.objectAtIndex(i);
  result.push({
    name: ObjC.unwrap(v.name),
    language: ObjC.unwrap(v.language),
    quality: parseInt(v.quality),
    identifier: ObjC.unwrap(v.identifier)
  });
}
JSON.stringify(result);
`;
  const out = execFileSync("osascript", ["-l", "JavaScript", "-e", jxa], {
    encoding: "utf-8",
    stdio: ["pipe", "pipe", "pipe"],
  }).trim();
  return JSON.parse(out);
}

function formatVoice(v) {
  const q = QUALITY_LABELS[v.quality] || "unknown";
  return `${v.name}  ${v.language}  quality=${q}(${v.quality})  id=${v.identifier}`;
}

switch (action) {
  case "list": {
    const voices = getVoices();
    const locale = arg.replace("_", "-").toLowerCase();
    const filtered = locale
      ? voices.filter((v) => v.language.toLowerCase().startsWith(locale))
      : voices;
    filtered
      .sort((a, b) => {
        if (locale) return b.quality - a.quality || a.name.localeCompare(b.name);
        return a.language.localeCompare(b.language) || b.quality - a.quality || a.name.localeCompare(b.name);
      })
      .forEach((v) => console.log(formatVoice(v)));
    break;
  }

  case "check": {
    if (!arg) die('voice name required\nUsage: node voices.mjs check "Voice Name"', 2);
    const voices = getVoices();
    const found = voices.find((v) => v.name.toLowerCase() === arg.toLowerCase());
    if (found) {
      console.log(`READY: ${formatVoice(found)}`);
    } else {
      console.log(`NOT READY: Voice '${arg}' is not downloaded or does not exist.`);
      console.log("Go to System Settings → Accessibility → Spoken Content → System Voice → Manage Voices to download it.");
      process.exit(1);
    }
    break;
  }

  case "best": {
    if (!arg) die("locale required (e.g. zh-CN, en-US)", 2);
    const locale = arg.replace("_", "-").toLowerCase();
    const voices = getVoices();
    let candidates = voices.filter((v) => v.language.toLowerCase().startsWith(locale));
    if (!candidates.length) {
      const lang = locale.split("-")[0];
      candidates = voices.filter((v) => v.language.toLowerCase().startsWith(lang));
    }
    if (!candidates.length) die(`No voice available for locale ${arg}`);
    const best = candidates.reduce((a, b) => (b.quality > a.quality ? b : a));
    console.log(best.name);
    break;
  }

  default:
    die("Usage: node voices.mjs <list|check|best> [arg]", 2);
}
