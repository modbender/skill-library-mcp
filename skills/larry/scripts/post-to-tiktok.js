#!/usr/bin/env node
/**
 * Post a 6-slide TikTok slideshow via Postiz API.
 * 
 * Usage: node post-to-tiktok.js --config <config.json> --dir <slides-dir> --caption "caption text" --title "post title"
 * 
 * Uploads slide1.png through slide6.png, then creates a TikTok slideshow post.
 * Posts as SELF_ONLY (draft) by default — user adds music then publishes.
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
function getArg(name) {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : null;
}

const configPath = getArg('config');
const dir = getArg('dir');
const caption = getArg('caption');
const title = getArg('title') || '';

if (!configPath || !dir || !caption) {
  console.error('Usage: node post-to-tiktok.js --config <config.json> --dir <dir> --caption "text" [--title "text"]');
  process.exit(1);
}

const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
const BASE_URL = 'https://api.postiz.com/public/v1';

async function uploadImage(filePath) {
  const form = new FormData();
  const blob = new Blob([fs.readFileSync(filePath)], { type: 'image/png' });
  form.append('file', blob, path.basename(filePath));

  const res = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    headers: { 'Authorization': config.postiz.apiKey },
    body: form
  });
  return res.json();
}

(async () => {
  console.log('📤 Uploading slides...');
  const images = [];
  for (let i = 1; i <= 6; i++) {
    const filePath = path.join(dir, `slide${i}.png`);
    if (!fs.existsSync(filePath)) {
      console.error(`  ❌ Missing: ${filePath}`);
      process.exit(1);
    }
    console.log(`  Uploading slide ${i}...`);
    const resp = await uploadImage(filePath);
    if (resp.error) {
      console.error(`  ❌ Upload error: ${JSON.stringify(resp.error)}`);
      process.exit(1);
    }
    images.push({ id: resp.id, path: resp.path });
    console.log(`  ✅ ${resp.id}`);
    // Rate limit buffer
    if (i < 6) await new Promise(r => setTimeout(r, 1500));
  }

  console.log('\n📱 Creating TikTok post...');
  const privacy = config.posting?.privacyLevel || 'SELF_ONLY';
  
  const postRes = await fetch(`${BASE_URL}/posts`, {
    method: 'POST',
    headers: {
      'Authorization': config.postiz.apiKey,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: 'now',
      date: new Date().toISOString(),
      shortLink: false,
      tags: [],
      posts: [{
        integration: { id: config.postiz.integrationId },
        value: [{ content: caption, image: images }],
        settings: {
          __type: 'tiktok',
          title: title,
          privacy_level: privacy,
          duet: false,
          stitch: false,
          comment: true,
          autoAddMusic: 'no',
          brand_content_toggle: false,
          brand_organic_toggle: false,
          video_made_with_ai: true,
          content_posting_method: 'UPLOAD'
        }
      }]
    })
  });

  const result = await postRes.json();
  console.log('✅ Posted!', JSON.stringify(result));

  // Save metadata
  const metaPath = path.join(dir, 'meta.json');
  const meta = {
    postId: result[0]?.postId,
    caption,
    title,
    privacy,
    postedAt: new Date().toISOString(),
    images: images.length
  };
  fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));
  console.log(`📋 Metadata saved to ${metaPath}`);
})();
