#!/usr/bin/env node
/**
 * parse-webhook-payload.js - Parse SendGrid Inbound Parse webhook payload
 * 
 * Usage:
 *   node parse-webhook-payload.js < payload.txt
 *   curl https://webhook.example.com/parse | node parse-webhook-payload.js
 * 
 * Reads multipart/form-data from stdin and outputs structured JSON
 */

const readline = require('readline');

function parseMultipartFormData(input) {
  const lines = input.split('\n');
  const result = {
    headers: {},
    from: null,
    to: null,
    cc: null,
    subject: null,
    text: null,
    html: null,
    attachments: [],
    envelope: null,
  };

  let currentField = null;
  let currentValue = [];
  let inHeaders = false;
  let boundary = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Detect boundary
    if (!boundary && line.startsWith('--')) {
      boundary = line.trim();
      continue;
    }

    // End of part
    if (boundary && line.trim() === boundary) {
      if (currentField && currentValue.length > 0) {
        const value = currentValue.join('\n').trim();
        
        // Store field
        if (currentField === 'headers') {
          result.headers = parseEmailHeaders(value);
        } else if (currentField === 'envelope') {
          try {
            result.envelope = JSON.parse(value);
          } catch (e) {
            result.envelope = value;
          }
        } else if (currentField.startsWith('attachment')) {
          result.attachments.push({
            field: currentField,
            content: value,
          });
        } else {
          result[currentField] = value;
        }
      }
      currentField = null;
      currentValue = [];
      continue;
    }

    // Content-Disposition line
    if (line.startsWith('Content-Disposition:')) {
      const match = line.match(/name="([^"]+)"/);
      if (match) {
        currentField = match[1];
      }
      continue;
    }

    // Skip Content-Type and other headers
    if (line.startsWith('Content-')) {
      continue;
    }

    // Empty line after headers
    if (line.trim() === '' && currentField) {
      continue;
    }

    // Collect content
    if (currentField) {
      currentValue.push(line);
    }
  }

  return result;
}

function parseEmailHeaders(headersText) {
  const headers = {};
  const lines = headersText.split('\n');
  
  let currentHeader = null;
  
  for (const line of lines) {
    if (line.startsWith(' ') || line.startsWith('\t')) {
      // Continuation of previous header
      if (currentHeader) {
        headers[currentHeader] += ' ' + line.trim();
      }
    } else {
      const colonIndex = line.indexOf(':');
      if (colonIndex > 0) {
        const name = line.substring(0, colonIndex).trim();
        const value = line.substring(colonIndex + 1).trim();
        currentHeader = name;
        headers[name] = value;
      }
    }
  }
  
  return headers;
}

// Help
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log('Usage: node parse-webhook-payload.js < payload.txt');
  console.log('');
  console.log('Parse SendGrid Inbound Parse webhook payload from stdin.');
  console.log('Outputs structured JSON with email fields.');
  console.log('');
  console.log('Examples:');
  console.log('  node parse-webhook-payload.js < payload.txt');
  console.log('  curl https://webhook.example.com/parse | node parse-webhook-payload.js');
  console.log('');
  console.log('Output fields:');
  console.log('  - from, to, cc, subject');
  console.log('  - text (plain text body)');
  console.log('  - html (HTML body)');
  console.log('  - headers (parsed email headers)');
  console.log('  - envelope (SMTP envelope data)');
  console.log('  - attachments (array of attachment data)');
  process.exit(0);
}

// Read from stdin
let input = '';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', (line) => {
  input += line + '\n';
});

rl.on('close', () => {
  try {
    const parsed = parseMultipartFormData(input);
    console.log(JSON.stringify(parsed, null, 2));
  } catch (error) {
    console.error('Error parsing payload:', error.message);
    process.exit(1);
  }
});
