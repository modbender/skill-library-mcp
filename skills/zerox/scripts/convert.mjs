#!/usr/bin/env node

import { zerox } from "zerox";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function usage() {
  console.error(`Usage: convert.mjs <filePath> [outputPath]`);
  console.error(`  filePath:   Path to the document (PDF, DOCX, PPTX, etc.)`);
  console.error(`  outputPath: Optional path to save the markdown output`);
  console.error(`              (defaults to: {skillDir}/output/{filename}.md)`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const filePath = args[0];

// Determine output path
let outputPath = args[1];
if (!outputPath) {
  // Default to skill's output directory
  const skillDir = path.resolve(__dirname, "..");
  const outputDir = path.join(skillDir, "output");
  const inputFileName = path.basename(filePath, path.extname(filePath));
  outputPath = path.join(outputDir, `${inputFileName}.md`);
}

// Check if file exists
if (!fs.existsSync(filePath)) {
  console.error(`❌ File not found: ${filePath}`);
  process.exit(1);
}

// Read API key from ~/.openclaw/.env if not in environment
let apiKey = (process.env.APIYI_API_KEY ?? "").trim();

if (!apiKey) {
  try {
    const envPath = path.join(process.env.HOME || "~", ".openclaw", ".env");
    const envContent = fs.readFileSync(envPath, "utf-8");
    const match = envContent.match(/APIYI_API_KEY\s*=\s*(.+)/);
    if (match) {
      apiKey = match[1].trim();
    }
  } catch (e) {
    // Ignore read errors
  }
}

if (!apiKey) {
  console.error("❌ Missing APIYI_API_KEY environment variable or .env entry");
  process.exit(1);
}

const processDocument = async () => {
  try {
    console.log(`🔄 Converting: ${filePath}`);
    
    const result = await zerox({
      filePath: filePath,
      modelProvider: "OPENAI",
      model: "gpt-4o",
      credentials: {
        apiKey: apiKey,
      }
    });

    // Extract markdown content from result
    const pages = result.pages || [];
    const markdownContent = pages.map(p => p.content).join("\n\n");
    
    if (outputPath) {
      // Ensure output directory exists
      const outputDir = path.dirname(outputPath);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      fs.writeFileSync(outputPath, markdownContent, "utf-8");
      console.log(`✅ Markdown saved to: ${outputPath}`);
    } else {
      // Print to stdout
      console.log(markdownContent);
    }
    
    return result;
  } catch (error) {
    console.error("\n❌ Conversion failed:", error.message);
    if (error.cause) {
      console.error("❌ Underlying error:", error.cause);
    }
    process.exit(1);
  }
};

processDocument();