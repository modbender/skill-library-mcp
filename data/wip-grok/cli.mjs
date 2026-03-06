#!/usr/bin/env node
// wip-grok/cli.mjs
// Thin CLI wrapper. argv -> core -> stdout.

import { writeFileSync } from 'node:fs';
import {
  search_web, search_x,
  generate_image, edit_image,
  generate_video, poll_video, wait_for_video,
} from './core.mjs';

const args = process.argv.slice(2);
const command = args[0];

function getFlag(name) {
  const prefix = `--${name}=`;
  const arg = args.find(a => a.startsWith(prefix));
  return arg ? arg.slice(prefix.length) : null;
}

function getPositional(index) {
  // Skip flags, return nth non-flag arg after command
  const positionals = args.slice(1).filter(a => !a.startsWith('--'));
  return positionals[index] || null;
}

function usage() {
  console.error(`wip-grok - xAI Grok API. Sensor (search) + Actuator (generate).

Usage:
  wip-grok search-web "query" [--domains=a.com,b.com] [--exclude=x.com]
  wip-grok search-x "query" [--handles=user1,user2] [--from=2026-01-01] [--to=2026-02-20]
  wip-grok imagine "prompt" [--output=file.png] [--n=1] [--aspect=16:9]
  wip-grok edit "prompt" --image=source.png [--output=out.png]
  wip-grok video "prompt" [--duration=10] [--resolution=720p] [--output=out.mp4]
  wip-grok video-status <request_id>

Environment:
  XAI_API_KEY    xAI API key (or use 1Password: op://Agent Secrets/X API/api key)
`);
  process.exit(1);
}

async function main() {
  if (!command) usage();

  try {
    switch (command) {
      case 'search-web': {
        const query = getPositional(0);
        if (!query) { console.error('Error: query required'); usage(); }
        const opts = { query };
        const domains = getFlag('domains');
        const exclude = getFlag('exclude');
        if (domains) opts.allowed_domains = domains.split(',');
        if (exclude) opts.excluded_domains = exclude.split(',');

        const result = await search_web(opts);
        console.log(result.content);
        if (result.citations?.length) {
          console.log('\nSources:');
          result.citations.forEach((c, i) => console.log(`  ${i + 1}. ${c.title || 'Untitled'} - ${c.url || ''}`));
        }
        break;
      }

      case 'search-x': {
        const query = getPositional(0);
        if (!query) { console.error('Error: query required'); usage(); }
        const opts = { query };
        const handles = getFlag('handles');
        const from = getFlag('from');
        const to = getFlag('to');
        if (handles) opts.allowed_x_handles = handles.split(',');
        if (from) opts.from_date = from;
        if (to) opts.to_date = to;

        const result = await search_x(opts);
        console.log(result.content);
        if (result.citations?.length) {
          console.log('\nSources:');
          result.citations.forEach((c, i) => console.log(`  ${i + 1}. ${c.title || 'Untitled'} - ${c.url || ''}`));
        }
        break;
      }

      case 'imagine': {
        const prompt = getPositional(0);
        if (!prompt) { console.error('Error: prompt required'); usage(); }
        const opts = { prompt };
        const n = getFlag('n');
        const aspect = getFlag('aspect');
        const output = getFlag('output');
        if (n) opts.n = parseInt(n, 10);
        if (aspect) opts.aspect_ratio = aspect;

        const result = await generate_image(opts);
        for (const img of result.images) {
          if (output && img.url) {
            const res = await fetch(img.url);
            const buf = Buffer.from(await res.arrayBuffer());
            writeFileSync(output, buf);
            console.log(`Saved to ${output}`);
          } else {
            console.log(img.url || '[base64 data]');
          }
          if (img.revised_prompt) console.log(`Revised prompt: ${img.revised_prompt}`);
        }
        break;
      }

      case 'edit': {
        const prompt = getPositional(0);
        const image = getFlag('image');
        if (!prompt) { console.error('Error: prompt required'); usage(); }
        if (!image) { console.error('Error: --image required'); usage(); }
        const output = getFlag('output');

        const result = await edit_image({ prompt, image });
        for (const img of result.images) {
          if (output && img.url) {
            const res = await fetch(img.url);
            const buf = Buffer.from(await res.arrayBuffer());
            writeFileSync(output, buf);
            console.log(`Saved to ${output}`);
          } else {
            console.log(img.url || '[base64 data]');
          }
        }
        break;
      }

      case 'video': {
        const prompt = getPositional(0);
        if (!prompt) { console.error('Error: prompt required'); usage(); }
        const opts = { prompt };
        const duration = getFlag('duration');
        const resolution = getFlag('resolution');
        const aspect = getFlag('aspect');
        const image = getFlag('image');
        const output = getFlag('output');
        const wait = args.includes('--wait');
        if (duration) opts.duration = parseInt(duration, 10);
        if (resolution) opts.resolution = resolution;
        if (aspect) opts.aspect_ratio = aspect;
        if (image) opts.image = image;

        const result = await generate_video(opts);
        console.log(`Video generation started. Request ID: ${result.request_id}`);

        if (wait || output) {
          console.log('Waiting for completion...');
          const video = await wait_for_video({ request_id: result.request_id });
          console.log(`Status: ${video.status}`);
          if (video.url) {
            if (output) {
              const res = await fetch(video.url);
              const buf = Buffer.from(await res.arrayBuffer());
              writeFileSync(output, buf);
              console.log(`Saved to ${output}`);
            } else {
              console.log(`URL: ${video.url}`);
            }
          }
        } else {
          console.log(`Check status: wip-grok video-status ${result.request_id}`);
        }
        break;
      }

      case 'video-status': {
        const request_id = getPositional(0);
        if (!request_id) { console.error('Error: request_id required'); usage(); }
        const result = await poll_video({ request_id });
        console.log(JSON.stringify(result, null, 2));
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
        usage();
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
