#!/usr/bin/env node

/**
 * Question Generation Script
 */

const fs = require('fs');
const path = require('path');

const inputPath = process.argv[2];

if (!inputPath) {
  console.error('Usage: node generate_questions.js <path_to_screening_result_json>');
  process.exit(1);
}

try {
  const content = fs.readFileSync(inputPath, 'utf8');
  console.log('--- SCREENING RESULT START ---');
  console.log(content);
  console.log('--- SCREENING RESULT END ---');
  console.log('\n[AGENT INSTRUCTION]: Based on the screening result above, generate 5-8 deep-dive technical interview questions. Focus on the candidate\'s experience with Go/PHP and specific projects mentioned.');
} catch (e) {
  console.error('Error reading file:', e.message);
  process.exit(1);
}
