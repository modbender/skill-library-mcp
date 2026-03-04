#!/usr/bin/env node
/**
 * TikTok Analytics Checker
 * 
 * Connects Postiz posts to their TikTok video IDs and pulls per-post analytics.
 * 
 * How it works:
 * 1. Fetches all Postiz posts in the date range
 * 2. For posts with releaseId="missing", calls /posts/{id}/missing to get TikTok video list
 * 3. Matches posts to videos chronologically (TikTok IDs are sequential: higher = newer)
 * 4. Connects each post to its TikTok video via PUT /posts/{id}/release-id
 * 5. Pulls per-post analytics (views, likes, comments, shares)
 * 
 * IMPORTANT: TikTok's API takes 1-2 hours to index new videos. Don't run this
 * on posts published less than 2 hours ago — the video won't be in the list yet.
 * The daily cron runs in the morning, checking posts from the last 3 days, which
 * avoids this timing issue entirely.
 * 
 * Usage: node check-analytics.js --config <config.json> [--days 3] [--connect] [--app snugly]
 * 
 * --connect: Actually connect release IDs (without this flag, it's dry-run)
 * --app: Filter to a specific app/integration name
 * --days: How many days back to check (default: 3)
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
function getArg(name) {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : null;
}

const configPath = getArg('config');
const days = parseInt(getArg('days') || '3');
const shouldConnect = args.includes('--connect');
const appFilter = getArg('app');

if (!configPath) {
  console.error('Usage: node check-analytics.js --config <config.json> [--days 3] [--connect] [--app name]');
  process.exit(1);
}

const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
const BASE_URL = 'https://api.postiz.com/public/v1';
const API_KEY = config.postiz.apiKey;

async function api(method, endpoint, body = null) {
  const opts = {
    method,
    headers: { 'Authorization': API_KEY, 'Content-Type': 'application/json' }
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE_URL}${endpoint}`, opts);
  return res.json();
}

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  const now = new Date();
  const startDate = new Date(now - days * 86400000);
  // Don't check posts from the last 2 hours (TikTok indexing delay)
  const cutoffDate = new Date(now - 2 * 3600000);

  console.log(`📊 Checking analytics (last ${days} days, cutoff: posts before ${cutoffDate.toISOString().slice(11, 16)} UTC)\n`);

  // 1. Get all posts in range
  const postsData = await api('GET', `/posts?startDate=${startDate.toISOString()}&endDate=${now.toISOString()}`);
  let posts = postsData.posts || [];

  // Filter by app if specified
  if (appFilter) {
    posts = posts.filter(p => p.integration?.name?.toLowerCase().includes(appFilter.toLowerCase()));
  }

  // Filter to TikTok posts only
  posts = posts.filter(p => p.integration?.providerIdentifier === 'tiktok');

  // Sort by publish date (oldest first)
  posts.sort((a, b) => new Date(a.publishDate) - new Date(b.publishDate));

  console.log(`Found ${posts.length} TikTok posts\n`);

  // 2. Separate connected vs unconnected
  const connected = posts.filter(p => p.releaseId && p.releaseId !== 'missing');
  const unconnected = posts.filter(p => !p.releaseId || p.releaseId === 'missing');
  
  // Filter unconnected to only posts older than 2 hours
  const connectableUnconnected = unconnected.filter(p => new Date(p.publishDate) < cutoffDate);
  const tooNew = unconnected.filter(p => new Date(p.publishDate) >= cutoffDate);

  console.log(`  Connected: ${connected.length}`);
  console.log(`  Unconnected (ready): ${connectableUnconnected.length}`);
  if (tooNew.length > 0) {
    console.log(`  Too new (< 2h, skipping): ${tooNew.length}`);
    tooNew.forEach(p => console.log(`    ⏳ "${(p.content || '').substring(0, 50)}..." — wait for TikTok to index`));
  }
  console.log('');

  // 3. If there are connectable unconnected posts, get the TikTok video list
  if (connectableUnconnected.length > 0 && shouldConnect) {
    // Use the first unconnected post to get the missing list
    const referencePost = connectableUnconnected[0];
    console.log(`🔍 Fetching TikTok video list via post ${referencePost.id}...`);
    const tiktokVideos = await api('GET', `/posts/${referencePost.id}/missing`);

    if (Array.isArray(tiktokVideos) && tiktokVideos.length > 0) {
      // TikTok IDs are sequential (higher = newer). Sort ascending.
      const videoIds = tiktokVideos.map(v => v.id).sort();
      
      // Get already-connected IDs to exclude them
      const connectedIds = new Set(connected.map(p => p.releaseId));
      const availableIds = videoIds.filter(id => !connectedIds.has(id));

      console.log(`  Found ${videoIds.length} TikTok videos, ${availableIds.length} unconnected\n`);

      // Sort unconnected posts by publish date (oldest first)
      // Sort available IDs ascending (oldest first)
      // Match them up chronologically
      const sortedAvailable = availableIds.sort();
      
      // We need to match the N most recent available IDs to the N unconnected posts
      // Take the last N available IDs (newest) to match with the unconnected posts
      const idsToUse = sortedAvailable.slice(-connectableUnconnected.length);

      for (let i = 0; i < connectableUnconnected.length; i++) {
        const post = connectableUnconnected[i];
        const videoId = idsToUse[i];
        
        if (!videoId) {
          console.log(`  ⚠️ No matching video ID for "${(post.content || '').substring(0, 50)}..."`);
          continue;
        }

        console.log(`  🔗 Connecting: "${(post.content || '').substring(0, 50)}..."`);
        console.log(`     Post: ${post.id} (${post.publishDate})`);
        console.log(`     TikTok: ${videoId}`);

        const result = await api('PUT', `/posts/${post.id}/release-id`, { releaseId: videoId });
        if (result.releaseId === videoId) {
          console.log(`     ✅ Connected`);
        } else {
          console.log(`     ⚠️ Connection returned: ${JSON.stringify(result.releaseId)}`);
        }
        await sleep(1000);
      }
      console.log('');
    } else {
      console.log(`  ⚠️ No TikTok videos found in missing list. Videos may need more time to index.\n`);
    }
  } else if (connectableUnconnected.length > 0 && !shouldConnect) {
    console.log(`  ℹ️ ${connectableUnconnected.length} posts need connecting. Run with --connect to auto-connect.\n`);
  }

  // 4. Pull analytics for all connected posts
  console.log('📈 Per-Post Analytics:\n');
  
  // Re-fetch posts to get updated release IDs
  const updatedData = await api('GET', `/posts?startDate=${startDate.toISOString()}&endDate=${now.toISOString()}`);
  let updatedPosts = (updatedData.posts || []).filter(p => 
    p.integration?.providerIdentifier === 'tiktok' &&
    p.releaseId && p.releaseId !== 'missing'
  );
  if (appFilter) {
    updatedPosts = updatedPosts.filter(p => p.integration?.name?.toLowerCase().includes(appFilter.toLowerCase()));
  }
  updatedPosts.sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate)); // newest first

  const results = [];
  for (const post of updatedPosts) {
    const analytics = await api('GET', `/analytics/post/${post.id}`);
    const metrics = {};
    if (Array.isArray(analytics)) {
      analytics.forEach(m => {
        const latest = m.data?.[m.data.length - 1];
        if (latest) metrics[m.label.toLowerCase()] = parseInt(latest.total) || 0;
      });
    }

    const result = {
      id: post.id,
      date: post.publishDate?.slice(0, 10),
      hook: (post.content || '').substring(0, 60),
      app: post.integration?.name,
      views: metrics.views || 0,
      likes: metrics.likes || 0,
      comments: metrics.comments || 0,
      shares: metrics.shares || 0,
      releaseId: post.releaseId
    };
    results.push(result);

    const viewStr = result.views > 1000 ? `${(result.views / 1000).toFixed(1)}K` : result.views;
    console.log(`  ${result.date} | ${viewStr} views | ${result.likes} likes | ${result.comments} comments | ${result.shares} shares`);
    console.log(`    "${result.hook}..."`);
    console.log(`    ${result.app} | TikTok: ${result.releaseId}\n`);

    await sleep(500);
  }

  // 5. Save results
  const baseDir = path.dirname(configPath);
  const analyticsPath = path.join(baseDir, 'analytics-snapshot.json');
  const snapshot = {
    date: now.toISOString(),
    posts: results
  };
  fs.writeFileSync(analyticsPath, JSON.stringify(snapshot, null, 2));
  console.log(`💾 Saved analytics snapshot to ${analyticsPath}`);

  // 6. Summary
  console.log('\n📊 Summary:');
  const totalViews = results.reduce((s, r) => s + r.views, 0);
  const totalLikes = results.reduce((s, r) => s + r.likes, 0);
  console.log(`  Total views: ${totalViews.toLocaleString()}`);
  console.log(`  Total likes: ${totalLikes.toLocaleString()}`);
  console.log(`  Posts tracked: ${results.length}`);
  
  if (results.length > 0) {
    const best = results.reduce((a, b) => a.views > b.views ? a : b);
    const worst = results.reduce((a, b) => a.views < b.views ? a : b);
    console.log(`  Best: ${best.views.toLocaleString()} views — "${best.hook}..."`);
    console.log(`  Worst: ${worst.views.toLocaleString()} views — "${worst.hook}..."`);
  }
})();
