#!/usr/bin/env node
'use strict';

/**
 * create-link.js — Create a Linkfuse affiliate link
 *
 * Usage:
 *   node create-link.js --url <url>
 *
 * Requires LINKFUSE_TOKEN environment variable.
 *
 * Exit codes:
 *   0  — success, prints JSON { url, title } to stdout
 *   1  — error (missing token, network failure, API error)
 *   2  — 401 Unauthorized (token invalid or expired)
 */

const config = require('./config');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--url') args.url = argv[++i];
  }
  return args;
}

async function main() {
  const token = process.env.LINKFUSE_TOKEN;
  if (!token) {
    process.stderr.write('LINKFUSE_TOKEN environment variable is not set.\n');
    process.exit(1);
  }

  const { url } = parseArgs(process.argv);
  if (!url) {
    process.stderr.write('Usage: node create-link.js --url <url>\n');
    process.exit(1);
  }

  let response;
  try {
    response = await fetch(config.endpoints.createLink, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'X-API-CLIENT': 'claude-skill',
      },
      body: JSON.stringify({ url, allowRecycle: true }),
    });
  } catch (err) {
    process.stderr.write(`Network error: ${err.message}\n`);
    process.exit(1);
  }

  if (response.status === 401) {
    process.stderr.write('UNAUTHORIZED: LINKFUSE_TOKEN is invalid or expired.\n');
    process.exit(2);
  }

  if (!response.ok) {
    const body = await response.text().catch(() => '');
    process.stderr.write(`API error ${response.status}: ${body}\n`);
    process.exit(1);
  }

  const data = await response.json();
  process.stdout.write(JSON.stringify({ url: data.url, title: data.title }) + '\n');
  process.exit(0);
}

main();
