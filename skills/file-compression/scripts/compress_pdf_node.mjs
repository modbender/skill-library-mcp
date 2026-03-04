#!/usr/bin/env node

import path from "node:path";
import process from "node:process";
import { promises as fs } from "node:fs";
import { spawn } from "node:child_process";

const PRESETS = {
  screen: "/screen",
  ebook: "/ebook",
  printer: "/printer",
  prepress: "/prepress",
};

function parseArgs(argv) {
  if (argv.length < 2) {
    throw new Error(
      "Usage: compress_pdf_node.mjs <input.pdf> <output.pdf> [--preset screen|ebook|printer|prepress]"
    );
  }
  const args = {
    input: argv[0],
    output: argv[1],
    preset: "ebook",
  };

  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const val = argv[i + 1];
    if (key === "--preset" && val) {
      if (!Object.keys(PRESETS).includes(val)) {
        throw new Error(`Invalid preset: ${val}`);
      }
      args.preset = val;
      i += 1;
    } else {
      throw new Error(`Unknown or invalid argument: ${key}`);
    }
  }
  return args;
}

function bytesToHuman(value) {
  const units = ["B", "KB", "MB", "GB"];
  let size = Number(value);
  let unit = units[0];
  for (const next of units) {
    unit = next;
    if (size < 1024 || next === units[units.length - 1]) break;
    size /= 1024;
  }
  return `${size.toFixed(2)} ${unit}`;
}

function runCmd(bin, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(bin, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stderr = "";
    let stdout = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve({ stdout, stderr });
      else reject(new Error(stderr.trim() || stdout.trim() || `exit ${code}`));
    });
  });
}

async function run() {
  const { input, output, preset } = parseArgs(process.argv.slice(2));
  const resolvedInput = path.resolve(input);
  const resolvedOutput = path.resolve(output);
  if (resolvedInput === resolvedOutput) {
    throw new Error("Input and output paths must be different");
  }
  if (path.extname(resolvedInput).toLowerCase() !== ".pdf") {
    throw new Error("Input must be a .pdf file");
  }

  const before = await fs.stat(resolvedInput);
  await fs.mkdir(path.dirname(resolvedOutput), { recursive: true });

  const gsArgs = [
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.6",
    `-dPDFSETTINGS=${PRESETS[preset]}`,
    "-dNOPAUSE",
    "-dBATCH",
    "-dQUIET",
    "-dDetectDuplicateImages=true",
    "-dCompressFonts=true",
    "-dSubsetFonts=true",
    `-sOutputFile=${resolvedOutput}`,
    resolvedInput,
  ];

  await runCmd("gs", gsArgs);

  const after = await fs.stat(resolvedOutput);
  const saved = before.size - after.size;
  const ratio = before.size === 0 ? 0 : (saved / before.size) * 100;

  console.log("Backend: node-ghostscript");
  console.log(`Output path: ${resolvedOutput}`);
  console.log(`Input size:  ${bytesToHuman(before.size)}`);
  console.log(`Output size: ${bytesToHuman(after.size)}`);
  console.log(`Saved:       ${bytesToHuman(saved)} (${ratio.toFixed(2)}%)`);
  console.log(
    `From/To:     from ${bytesToHuman(before.size)} to ${bytesToHuman(after.size)}`
  );
  if (after.size >= before.size) {
    console.error(
      "Warning: output is not smaller than input. Try another preset/backend."
    );
  }
}

run().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
