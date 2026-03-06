#!/usr/bin/env node

/**
 * x-extract: Extract tweet content from x.com URLs without credentials
 * 
 * Usage:
 *   ./extract.mjs <x.com-url> [--output <file>] [--download-media]
 * 
 * Examples:
 *   ./extract.mjs https://x.com/vista8/status/2019651804062241077
 *   ./extract.mjs https://x.com/user/status/123 --output tweet.md
 *   ./extract.mjs https://x.com/user/status/123 --download-media
 */

import { spawn } from 'child_process';
import { writeFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Parse arguments
const args = process.argv.slice(2);
const url = args[0];
const outputIndex = args.indexOf('--output');
const outputFile = outputIndex !== -1 ? args[outputIndex + 1] : null;
const downloadMedia = args.includes('--download-media');

if (!url || !url.includes('x.com')) {
  console.error('Usage: ./extract.mjs <x.com-url> [--output <file>] [--download-media]');
  process.exit(1);
}

// Extract tweet ID from URL
const tweetIdMatch = url.match(/status\/(\d+)/);
const tweetId = tweetIdMatch ? tweetIdMatch[1] : 'unknown';

console.log(`Extracting tweet ${tweetId}...`);

// Use OpenClaw browser tool to extract content
const browserCommand = `
const { exec } = require('child_process');
const url = "${url}";

// Create browser snapshot request
const snapshotRequest = {
  action: 'open',
  profile: 'openclaw',
  targetUrl: url
};

console.log(JSON.stringify(snapshotRequest));
`;

// For now, output instructions for manual extraction
// In production, this would integrate with OpenClaw's browser tool via API

const instructions = `
# Tweet Extraction Instructions

Since this is a standalone script, you need to use OpenClaw's browser tool directly.

Run these commands in your OpenClaw session:

\`\`\`
1. Open the URL:
   browser action=open profile=openclaw targetUrl="${url}"

2. Take a snapshot to extract content:
   browser action=snapshot targetId=<TARGET_ID> snapshotFormat=aria

3. Look for these elements in the snapshot:
   - Tweet text: role=article
   - Author: role=link with author name
   - Timestamp: role=time
   - Media: role=img or role=link[href contains /photo/]
   - Metrics: like count, retweet count, reply count
\`\`\`

## Expected Output Format

\`\`\`markdown
# Tweet by @username

**Posted:** YYYY-MM-DD HH:MM

Tweet text goes here...

**Media:**
- [Image 1](url)
- [Image 2](url)

**Engagement:**
- Likes: 123
- Retweets: 45
- Replies: 67

**Source:** ${url}
\`\`\`

## Integration Note

This script requires OpenClaw's browser tool. For full automation, run via OpenClaw agent with browser tool access.
`;

if (outputFile) {
  mkdirSync(dirname(outputFile), { recursive: true });
  writeFileSync(outputFile, instructions);
  console.log(`Instructions written to ${outputFile}`);
} else {
  console.log(instructions);
}
