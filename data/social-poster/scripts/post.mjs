#!/usr/bin/env node

/**
 * Social Poster — Post via VibePost API
 * Usage: node post.mjs --text "Hello world" [--platform twitter]
 */

import { parseArgs } from 'node:util';

const { values: args } = parseArgs({
  options: {
    text:     { type: 'string', short: 't' },
    platform: { type: 'string', short: 'p', default: 'twitter' },
  },
  strict: false,
});

if (!args.text) {
  console.error('Usage: node post.mjs --text "Hello world" [--platform twitter]');
  process.exit(1);
}

const API_KEY = 'quack_5c6786fb7ac8f08c638d5db176d60b12b906b78ac63d21cf';
const url = 'https://vibepost-jpaulgrayson.replit.app/api/quack/post';

const res = await fetch(url, {
  method: 'POST',
  headers: {
    'x-quack-api-key': API_KEY,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: args.text,
    platform: args.platform,
  }),
});

if (!res.ok) {
  console.error(`Error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
console.log(JSON.stringify(data, null, 2));
