#!/usr/bin/env node

/**
 * Interview Summarization Script
 */

const fs = require('fs');
const path = require('path');

const notesPath = process.argv[2];

if (!notesPath) {
  console.error('Usage: node summarize_interview.js <path_to_notes_file>');
  process.exit(1);
}

try {
  const content = fs.readFileSync(notesPath, 'utf8');
  console.log('--- INTERVIEW NOTES START ---');
  console.log(content);
  console.log('--- INTERVIEW NOTES END ---');
  console.log('\n[AGENT INSTRUCTION]: Summarize these interview notes into the format defined in assets/report-template.md. Be objective and concise.');
} catch (e) {
  console.error('Error reading file:', e.message);
  process.exit(1);
}
