#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const args = process.argv.slice(2);
let clientName = args[0];

if (!clientName) {
  console.error("❌ Error: Client Name is required.");
  console.log("Usage: npx flwr-branding-kit \"Client Name\"");
  process.exit(1);
}

const baseDir = process.cwd();
const safeClientName = clientName.replace(/[^a-zA-Z0-9 \-_]/g, '').trim().replace(/ /g, '_');

const clientDir = path.join(baseDir, 'clients', safeClientName);
const dirs = [
  path.join(clientDir, 'client_intel'),
  path.join(clientDir, 'creative_assets'),
  path.join(clientDir, 'strategy_output', 'brand_assets_md')
];

console.log(`\n🚀 Initializing Branding Project for: ${clientName}...\n`);

// Create directories
dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`✅ Created: ${path.relative(baseDir, dir)}`);
  }
});

// Copy templates
const templateSrc = path.join(__dirname, '..', '.agent', 'templates', 'brand_assets');
const templateDest = path.join(clientDir, 'strategy_output', 'brand_assets_md');

if (fs.existsSync(templateSrc)) {
  const files = fs.readdirSync(templateSrc);
  files.forEach(file => {
    const srcFile = path.join(templateSrc, file);
    const destFile = path.join(templateDest, file);
    if (fs.lstatSync(srcFile).isFile()) {
      fs.copyFileSync(srcFile, destFile);
      console.log(`📋 Copied Template: ${file}`);
    }
  });
} else {
  console.warn(`⚠️ Warning: Templates not found at ${templateSrc}. Skipping copy.`);
}

console.log(`\n🎉 Project setup complete for: ${clientName}`);
console.log(`📂 Location: clients/${safeClientName}/`);
console.log(`\n👉 Next Step: Drop your briefing files into clients/${safeClientName}/client_intel/`);
