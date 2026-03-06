#!/usr/bin/env node

import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  if (argv.length < 2) {
    throw new Error(
      "Usage: compress_image_node.mjs <input> <output> [--quality 75] [--format keep|jpeg|png|webp] [--max-width N] [--max-height N]"
    );
  }
  const args = {
    input: argv[0],
    output: argv[1],
    quality: 75,
    format: "keep",
    maxWidth: null,
    maxHeight: null,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const val = argv[i + 1];
    if (key === "--quality" && val) {
      args.quality = Number(val);
      i += 1;
    } else if (key === "--format" && val) {
      args.format = val;
      i += 1;
    } else if (key === "--max-width" && val) {
      args.maxWidth = Number(val);
      i += 1;
    } else if (key === "--max-height" && val) {
      args.maxHeight = Number(val);
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

function normalizeFormat(input, requested) {
  if (requested !== "keep") return requested;
  const ext = path.extname(input).toLowerCase().replace(".", "");
  if (ext === "jpg") return "jpeg";
  return ext || "jpeg";
}

async function run() {
  const { input, output, quality, format, maxWidth, maxHeight } = parseArgs(
    process.argv.slice(2)
  );
  const sharp = (await import("sharp")).default;
  const fs = await import("node:fs/promises");

  const resolvedInput = path.resolve(input);
  const resolvedOutput = path.resolve(output);
  if (resolvedInput === resolvedOutput) {
    throw new Error("Input and output paths must be different");
  }

  const beforeStat = await fs.stat(resolvedInput);
  const outFmt = normalizeFormat(resolvedInput, format);
  let pipeline = sharp(resolvedInput);

  if (maxWidth || maxHeight) {
    pipeline = pipeline.resize({
      width: maxWidth || null,
      height: maxHeight || null,
      fit: "inside",
      withoutEnlargement: true,
    });
  }

  const safeQuality = Math.max(1, Math.min(100, quality));
  if (outFmt === "jpeg") {
    pipeline = pipeline.jpeg({ quality: safeQuality, mozjpeg: true });
  } else if (outFmt === "png") {
    pipeline = pipeline.png({ compressionLevel: 9 });
  } else if (outFmt === "webp") {
    pipeline = pipeline.webp({ quality: safeQuality });
  } else {
    throw new Error(`Unsupported output format: ${outFmt}`);
  }

  await fs.mkdir(path.dirname(resolvedOutput), { recursive: true });
  await pipeline.toFile(resolvedOutput);

  const afterStat = await fs.stat(resolvedOutput);
  const saved = beforeStat.size - afterStat.size;
  const ratio = beforeStat.size === 0 ? 0 : (saved / beforeStat.size) * 100;

  console.log("Backend: node-sharp");
  console.log(`Output path: ${resolvedOutput}`);
  console.log(`Input size:  ${bytesToHuman(beforeStat.size)}`);
  console.log(`Output size: ${bytesToHuman(afterStat.size)}`);
  console.log(`Saved:       ${bytesToHuman(saved)} (${ratio.toFixed(2)}%)`);
  console.log(
    `From/To:     from ${bytesToHuman(beforeStat.size)} to ${bytesToHuman(afterStat.size)}`
  );
  if (afterStat.size >= beforeStat.size) {
    console.error(
      "Warning: output is not smaller than input. Try another quality/format/backend."
    );
  }
}

run().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
