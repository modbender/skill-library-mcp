#!/usr/bin/env node
import { encode, decode } from '../src/emoji-encoder.js';

function usage() {
  console.log(`cashu-emoji

Usage:
  cashu-emoji decode <text|-> [--metadata] [--json]
  cashu-emoji encode <emoji> <text|->

Notes:
  - Use '-' to read from stdin.
  - decode: pass the whole message (it will ignore non-variation-selector chars).
  - --json: emit a single JSON object to stdout (more agent-friendly).
`);
}

async function readArgOrStdin(value) {
  if (value !== '-') return value;
  return await new Promise((resolve, reject) => {
    let buf = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (d) => (buf += d));
    process.stdin.on('end', () => resolve(buf));
    process.stdin.on('error', reject);
  });
}

const [,, cmd, ...args] = process.argv;
if (!cmd || cmd === '--help' || cmd === '-h') {
  usage();
  process.exit(0);
}

if (cmd === 'decode') {
  const input = args[0];
  if (!input) {
    usage();
    process.exit(2);
  }

  const wantMeta = args.includes('--metadata');
  const wantJson = args.includes('--json');

  const text = (await readArgOrStdin(input)).trimEnd();
  const out = decode(text);

  const isCashu = out.startsWith('cashu');

  let meta = null;
  let metaError = null;

  if (wantMeta && isCashu) {
    try {
      const { getTokenMetadata } = await import('@cashu/cashu-ts');
      meta = getTokenMetadata(out);
    } catch (e) {
      metaError = (e && e.message) ? e.message : String(e);
    }
  }

  if (wantJson) {
    const payload = {
      text: out,
      isCashu,
      ...(wantMeta ? { metadata: meta, metadataError: metaError } : {}),
    };
    process.stdout.write(JSON.stringify(payload) + '\n');
    process.exit(0);
  }

  // Default human-friendly output (pipeable): decoded text to stdout, metadata to stderr.
  process.stdout.write(out + '\n');

  if (wantMeta) {
    if (!isCashu) {
      process.stderr.write('metadata: decoded text does not look like a cashu token (does not start with "cashu")\n');
    } else if (metaError) {
      process.stderr.write(`metadata error: ${metaError}\n`);
    } else if (meta) {
      process.stderr.write(`mint: ${meta.mint}\nunit: ${meta.unit}\namount: ${meta.amount}\n`);
    }
  }

  process.exit(0);
}

if (cmd === 'encode') {
  const emoji = args[0];
  const input = args[1];
  if (!emoji || !input) {
    usage();
    process.exit(2);
  }

  const text = await readArgOrStdin(input);
  const out = encode(emoji, text.trimEnd());
  process.stdout.write(out + '\n');
  process.exit(0);
}

usage();
process.exit(2);
