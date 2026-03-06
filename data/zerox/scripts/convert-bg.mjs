#!/usr/bin/env node

import { spawn } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function usage() {
  console.error(`Usage: convert-bg.mjs <filePath> [outputPath]`);
  console.error(`  filePath:   Path to the document (PDF, DOCX, PPTX, etc.)`);
  console.error(`  outputPath: Optional path to save the markdown output`);
  console.error(`              (defaults to: {skillDir}/output/{filename}.md)`);
  console.error(`\nRuns conversion in background. Logs saved to {skillDir}/output/convert-bg.log`);
  console.error(`System notification sent when complete.`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const filePath = args[0];

// Determine output path
let outputPath = args[1];
if (!outputPath) {
  const skillDir = path.resolve(__dirname, "..");
  const outputDir = path.join(skillDir, "output");
  const inputFileName = path.basename(filePath, path.extname(filePath));
  outputPath = path.join(outputDir, `${inputFileName}.md`);
}

// Ensure output directory exists
const outputDir = path.dirname(outputPath);
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const logPath = path.join(outputDir, "convert-bg.log");
const logStream = fs.createWriteStream(logPath, { flags: "a" });

const timestamp = new Date().toISOString();
logStream.write(`\n[${timestamp}] Starting conversion: ${filePath}\n`);
logStream.write(`[${timestamp}] Output: ${outputPath}\n\n`);

console.log(`🚀 Starting background conversion...`);
console.log(`   File: ${filePath}`);
console.log(`   Output: ${outputPath}`);
console.log(`   Log: ${logPath}`);
console.log(`\nUse 'tail -f ${logPath}' to monitor progress`);

// Spawn the actual converter in background
const converterPath = path.join(__dirname, "convert.mjs");
const child = spawn("node", [converterPath, filePath, outputPath], {
  detached: true,
  stdio: ["ignore", "pipe", "pipe"]
});

child.stdout.pipe(logStream);
child.stderr.pipe(logStream);

child.unref();

// Monitor completion and send notification
child.on("exit", (code) => {
  const endTimestamp = new Date().toISOString();
  
  if (code === 0) {
    logStream.write(`\n[${endTimestamp}] Conversion completed successfully\n`);
    
    // Send macOS notification
    const notifyScript = `
      display notification "File converted successfully" with title "Zerox Converter" subtitle "${path.basename(filePath)}"
    `;
    spawn("osascript", ["-e", notifyScript]).unref();
  } else {
    logStream.write(`\n[${endTimestamp}] Conversion failed with code ${code}\n`);
    
    const notifyScript = `
      display notification "Conversion failed (code ${code})" with title "Zerox Converter" subtitle "${path.basename(filePath)}"
    `;
    spawn("osascript", ["-e", notifyScript]).unref();
  }
  
  logStream.end();
});

console.log(`\n✅ Process detached (PID: ${child.pid})`);
process.exit(0);
