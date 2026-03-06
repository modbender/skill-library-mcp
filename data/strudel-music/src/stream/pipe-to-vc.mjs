#!/usr/bin/env node

import { createWriteStream, existsSync } from "node:fs";
import { spawn } from "node:child_process";
import process from "node:process";

function usage() {
  console.error("Usage: node src/stream/pipe-to-vc.mjs <input.wav> [bridge-endpoint] [--file]");
}

const rawArgs = process.argv.slice(2);
const fileOutput = rawArgs.includes("--file");
const args = rawArgs.filter((arg) => arg !== "--file");
const inputWav = args[0];
const bridgeEndpoint = args[1] || process.env.DISCORD_VC_BRIDGE_ENDPOINT;

if (!inputWav) {
  usage();
  process.exit(1);
}

if (!existsSync(inputWav)) {
  console.error(`Input WAV not found: ${inputWav}`);
  process.exit(1);
}

if (bridgeEndpoint) {
  console.error(`Bridge endpoint: ${bridgeEndpoint}`);
}

const ffmpegArgs = [
  "-i",
  inputWav,
  "-c:a",
  "libopus",
  "-b:a",
  "128k",
  "-ar",
  "48000",
  "-f",
  "opus",
  "pipe:1",
];

const ffmpeg = spawn("ffmpeg", ffmpegArgs, {
  stdio: ["ignore", "pipe", "inherit"],
});

if (fileOutput) {
  const out = createWriteStream("output.opus");
  ffmpeg.stdout.pipe(out);
  out.on("finish", () => {
    console.error("Wrote output.opus");
  });
} else {
  ffmpeg.stdout.pipe(process.stdout);
}

ffmpeg.on("error", (error) => {
  console.error(`Failed to launch ffmpeg: ${error.message}`);
  process.exit(1);
});

ffmpeg.on("close", (code) => {
  process.exit(code ?? 1);
});

