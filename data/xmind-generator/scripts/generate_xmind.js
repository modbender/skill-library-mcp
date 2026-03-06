#!/usr/bin/env node
/**
 * generate_xmind.js
 *
 * Usage:
 *   node generate_xmind.js --input input.md --output /path/to/output.xmind
 *   node generate_xmind.js --text "Root\n- Branch1\n  - Leaf1\n- Branch2" --output output.xmind
 *   echo "..." | node generate_xmind.js --output output.xmind
 *
 * Input format (Markdown outline or plain indented text):
 *   # Root Topic
 *   - Main Branch 1
 *     - Sub topic 1
 *     - Sub topic 2
 *   - Main Branch 2
 */

const fs = require('fs');
const path = require('path');
const { Workbook, Topic, Zipper } = require('xmind');

// Parse arguments
const args = process.argv.slice(2);
const getArg = (flag) => {
  const idx = args.indexOf(flag);
  return idx !== -1 ? args[idx + 1] : null;
};

const inputFile = getArg('--input');
const outputArg  = getArg('--output') || 'output.xmind';
const textInput  = getArg('--text');

// Resolve output path and filename
const outputPath = path.resolve(outputArg);
const outputDir  = path.dirname(outputPath);
const outputName = path.basename(outputPath, '.xmind');

// Read input
let rawText = '';
if (inputFile) {
  rawText = fs.readFileSync(inputFile, 'utf-8');
} else if (textInput) {
  rawText = textInput.replace(/\\n/g, '\n');
} else {
  try { rawText = fs.readFileSync('/dev/stdin', 'utf-8'); } catch(e) {}
}

if (!rawText.trim()) {
  console.error('Error: No input provided. Use --input, --text, or pipe via stdin.');
  process.exit(1);
}

/**
 * Parse Markdown/plain outline into tree
 * Returns: { title, children: [...] }
 */
function parseOutline(text) {
  const lines = text.split('\n');
  let root = null;
  const stack = []; // [{node, indent}]

  for (const line of lines) {
    if (!line.trim()) continue;
    const indent = line.match(/^(\s*)/)[1].length;
    const clean = line.trim()
      .replace(/^#+\s*/, '')      // # headings
      .replace(/^[-*]\s*/, '')    // - or * bullets
      .replace(/^\d+\.\s*/, ''); // 1. numbered

    if (!clean) continue;

    const node = { title: clean, children: [] };

    if (!root) {
      root = node;
      stack.push({ node, indent: -1 });
      continue;
    }

    // Pop until we find a parent with strictly less indent
    while (stack.length > 1 && stack[stack.length - 1].indent >= indent) {
      stack.pop();
    }

    stack[stack.length - 1].node.children.push(node);
    stack.push({ node, indent });
  }

  return root || { title: 'Mind Map', children: [] };
}

/**
 * Recursively build XMind topics from tree node using topic.on(cid) navigation
 * Uses a stack-based approach with explicit CID tracking
 */
function buildTopics(topic, nodes, parentCid) {
  for (const node of nodes) {
    // Focus on parent before adding
    topic.on(parentCid);
    topic.add({ title: node.title });
    const cid = topic.cid(); // CID of the just-added node

    if (node.children.length > 0) {
      buildTopics(topic, node.children, cid);
    }
  }
}

// Parse
const tree = parseOutline(rawText);

// Build XMind
const workbook = new Workbook();
const sheet = workbook.createSheet('Sheet 1', tree.title);
const topic = new Topic({ sheet });
const zipper = new Zipper({ path: outputDir, workbook, filename: outputName });

// Get the central topic CID
const centralCid = topic.cid();

// Build all branches recursively
if (tree.children.length > 0) {
  buildTopics(topic, tree.children, centralCid);
}

// Save
zipper.save().then(status => {
  if (status) {
    console.log(`✅ XMind file saved: ${outputPath}`);
    console.log(`   Root: "${tree.title}"`);
    console.log(`   Branches: ${tree.children.length}`);
  } else {
    console.error('❌ Failed to save XMind file.');
    process.exit(1);
  }
}).catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
