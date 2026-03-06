#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const ARGS = (() => {
  const args = process.argv.slice(2);
  const parsed = { _: [] };
  let argName = null;
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      argName = arg.slice(2);
      parsed[argName] = true;
    } else if (argName) {
      parsed[argName] = arg;
      argName = null;
    } else {
      parsed._.push(arg);
    }
  }
  return parsed;
})();

const MEMORY_FILE = ARGS.file ? path.resolve(ARGS.file) : path.resolve(__dirname, '../../MEMORY.md');

function printHelp() {
  console.log(`
Usage: active-learner <command> [options]

Commands:
  internalize   Write a lesson/concept to MEMORY.md (updates Index table & Details)
  ask           Generate a structured request for help

Options:
  --text <text>      Content to write or ask about
  --category <cat>   Category for internalize (e.g., Protocol, Tech)
  --id <id>          ID for internalize (e.g., L1, P2). Auto-generated if omitted.
`);
}

function generateId(category) {
  // Simple heuristic: C=Crisis, P=Protocol, T=Tech, S=Structure, H=History, L=Lesson
  const prefix = (category[0] || 'L').toUpperCase();
  // Find highest number for this prefix in MEMORY.md
  if (!fs.existsSync(MEMORY_FILE)) return `${prefix}1`;
  
  const content = fs.readFileSync(MEMORY_FILE, 'utf8');
  const regex = new RegExp(`\\| \\*\\*${prefix}(\\d+)\\*\\* \\|`, 'g');
  let max = 0;
  let match;
  while ((match = regex.exec(content)) !== null) {
    const num = parseInt(match[1], 10);
    if (num > max) max = num;
  }
  return `${prefix}${max + 1}`;
}

function internalize(text, category, id) {
  if (!text || !category) {
    console.error("Error: --text and --category are required for 'internalize'.");
    process.exit(1);
  }

  if (!fs.existsSync(MEMORY_FILE)) {
    console.error("Error: MEMORY.md not found.");
    process.exit(1);
  }

  // Auto-generate ID if missing
  if (!id) {
    id = generateId(category);
    console.log(`Auto-generated ID: ${id}`);
  }

  let content = fs.readFileSync(MEMORY_FILE, 'utf8');
  
  // Check if ID already exists
  if (content.includes(`| **${id}** |`)) {
    console.log(`Entry ${id} already exists in MEMORY.md. Skipping.`);
    return;
  }

  // 1. Prepare Table Row
  // | ID | Type | Category | Summary | ~Tok |
  const tokens = Math.ceil(text.length / 4);
  // Extract first sentence or first 50 chars for summary
  const summaryLine = text.split('\n')[0].replace(/[|]/g, '-'); // Escape pipes
  const summary = summaryLine.substring(0, 50) + (summaryLine.length > 50 ? '...' : '');
  const type = "Lesson"; // Default type, could be inferred but hardcoded for safety
  
  const row = `| **${id}** | ${type} | ${category} | **${summary}** | ${tokens} |`;

  // 2. Insert Row into Table
  // Find the last row of the table (starts with | **...) or the separator line
  // We look for the table header `| ID | Type ...` and the separator `|---|---|...`
  // Then we look for the end of the table (blank line or `---`)
  
  const tableEndRegex = /(\|.*\|\n)(\n|#|---)/;
  // If we can find where the table ends, insert there.
  // But wait, the table might be at the very top.
  // Let's try to find the last line starting with `|` that is part of the index table.
  
  // Robust approach: Split by lines, find the index section
  const lines = content.split('\n');
  let tableEndIndex = -1;
  let inTable = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('| ID | Type |')) {
      inTable = true;
    } else if (inTable && line.startsWith('|')) {
      // Still in table
      tableEndIndex = i;
    } else if (inTable && !line.startsWith('|')) {
      // Table ended
      break;
    }
  }

  if (tableEndIndex !== -1) {
    lines.splice(tableEndIndex + 1, 0, row);
    content = lines.join('\n');
  } else {
    console.warn("Could not find Index table in MEMORY.md. Appending row to end of file as fallback.");
    content += `\n${row}\n`;
  }

  // 3. Append Detail Section
  // Find `---` separator or just append
  const detailEntry = `\n### ${id} | ${category} | ${summary}\n**Date:** ${new Date().toISOString().split('T')[0]}\n${text}\n`;
  content += detailEntry;
  
  fs.writeFileSync(MEMORY_FILE, content);
  console.log(`Successfully internalized ${id} to MEMORY.md (Index + Detail)`);
}

function ask(text) {
  if (!text) {
    console.error("Error: --text is required for 'ask'.");
    process.exit(1);
  }
  
  // Format the question
  const output = `
❓ **Active Learning Request**
I need clarification on the following:
> ${text}

Please provide guidance or correct my understanding.
`;
  console.log(output);
}

const command = ARGS._[0];

switch (command) {
  case 'internalize':
    internalize(ARGS.text, ARGS.category, ARGS.id);
    break;
  case 'ask':
    ask(ARGS.text);
    break;
  default:
    printHelp();
    break;
}
