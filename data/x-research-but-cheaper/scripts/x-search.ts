#!/usr/bin/env tsx
import {
  searchTweets, getUserInfo, getUserTweets, getTweetsById, getThread, getCost, resetCost,
  getUserMentions, getUserFollowers, getUserFollowings, searchUsers,
  getTweetReplies, getTweetQuotes, getTweetRetweeters,
  getTrends, getCommunityInfo, getCommunityTweets,
  type Tweet, type UserInfo,
} from './lib/api.js';
import * as cache from './lib/cache.js';
import {
  formatTweet, formatProfile, formatCost, tweetToMarkdown, profileToMarkdown,
  formatUserCompact, formatTrend, userToMarkdown,
} from './lib/format.js';
import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WATCHLIST_PATH = join(__dirname, '..', 'data', 'watchlist.json');

// --- Arg parsing ---
const args = process.argv.slice(2);
const command = args[0];
const positional: string[] = [];
const flags: Record<string, string | boolean> = {};

for (let i = 1; i < args.length; i++) {
  const a = args[i];
  if (a.startsWith('--')) {
    const key = a.slice(2);
    if (key === 'no-replies') { flags['noReplies'] = true; continue; }
    const next = args[i + 1];
    if (next && !next.startsWith('--')) { flags[key] = next; i++; }
    else flags[key] = true;
  } else {
    positional.push(a);
  }
}

function flag(name: string, def?: string): string | undefined { const v = flags[name]; return typeof v === 'string' ? v : def; }
function bflag(name: string): boolean { return flags[name] === true; }
function nflag(name: string, def: number): number { const v = flag(name); return v ? parseInt(v, 10) : def; }

// --- Since filter ---
function sinceMs(since?: string): number | undefined {
  if (!since) return undefined;
  const map: Record<string, number> = { '1h': 3600000, '3h': 10800000, '6h': 21600000, '12h': 43200000, '1d': 86400000, '3d': 259200000, '7d': 604800000, '30d': 2592000000 };
  return map[since];
}

function filterSince(tweets: Tweet[], since?: string): Tweet[] {
  const ms = sinceMs(since);
  if (!ms) return tweets;
  const cutoff = Date.now() - ms;
  return tweets.filter(t => new Date(t.createdAt).getTime() >= cutoff);
}

// --- Sort ---
function sortTweets(tweets: Tweet[], sort: string): Tweet[] {
  const s = [...tweets];
  switch (sort) {
    case 'likes': return s.sort((a, b) => b.likeCount - a.likeCount);
    case 'retweets': return s.sort((a, b) => b.retweetCount - a.retweetCount);
    case 'impressions': return s.sort((a, b) => b.viewCount - a.viewCount);
    case 'replies': return s.sort((a, b) => b.replyCount - a.replyCount);
    case 'recent': return s.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    default: return s.sort((a, b) => b.likeCount - a.likeCount);
  }
}

function saveOutput(name: string, content: string) {
  const fname = `${name.replace(/[^a-z0-9]/gi, '_').slice(0, 40)}-${Date.now()}.md`;
  const outDir = join(__dirname, '..', 'data');
  mkdirSync(outDir, { recursive: true });
  writeFileSync(join(outDir, fname), content);
  console.log(`\n📁 Saved to data/${fname}`);
}

// --- Commands ---
async function doSearch() {
  const query = positional[0];
  if (!query) { console.error('Usage: x-search.ts search "<query>" [options]'); process.exit(1); }

  const quick = bflag('quick');
  const pages = quick ? 1 : nflag('pages', 3);
  const limit = quick ? Math.min(nflag('limit', 10), 10) : nflag('limit', 15);
  const sort = flag('sort', 'likes')!;
  const since = flag('since');
  const minLikes = nflag('min-likes', quick ? 5 : 2);
  const minImpressions = nflag('min-impressions', 0);
  const from = flag('from');
  const noReplies = bflag('noReplies');
  const quality = bflag('quality');
  const save = bflag('save');
  const json = bflag('json');
  const markdown = bflag('markdown');
  const queryType = flag('type', 'Latest')!;  // Latest or Top
  const ttl = quick ? 3600000 : 900000;

  // Build query
  let q = query;
  if (from) q = `from:${from} ${q}`;
  if (!q.includes('is:retweet')) q += ' -is:retweet';
  if (noReplies && !q.includes('is:reply')) q += ' -is:reply';
  if (quick) q += ' -is:reply';
  // Server-side min likes filter (much more effective than client-side)
  if (minLikes > 0 && !q.includes('min_faves:')) q += ` min_faves:${minLikes}`;
  // Server-side time filter via since: operator (more reliable than client-side)
  if (since && !q.includes('since:')) {
    const ms = sinceMs(since);
    if (ms) {
      const d = new Date(Date.now() - ms);
      q += ` since:${d.toISOString().split('T')[0]}`;
    }
  }

  // Auto-increase pages when filtering for high engagement (more pages = more chances to find them)
  const effectivePages = (minLikes >= 50 && pages <= 1) ? 3 : pages;

  const cacheKey = `search:${q}:${effectivePages}:${sort}:${since}:${minLikes}:${queryType}`;
  const cached = cache.get(cacheKey, ttl);
  let allTweets: Tweet[];

  if (cached) {
    allTweets = cached;
  } else {
    allTweets = [];
    let cursor: string | undefined;
    for (let p = 0; p < effectivePages; p++) {
      const result = await searchTweets(q, cursor, queryType);
      allTweets.push(...result.tweets);
      cursor = result.cursor;
      if (!result.hasNextPage || !cursor) break;
    }
    cache.set(cacheKey, allTweets);
  }

  // Filter
  allTweets = filterSince(allTweets, since);
  if (minLikes > 0) allTweets = allTweets.filter(t => t.likeCount >= minLikes);
  if (minImpressions > 0) allTweets = allTweets.filter(t => t.viewCount >= minImpressions);
  if (quality) allTweets = allTweets.filter(t => t.likeCount >= 10);

  // Sort & limit
  allTweets = sortTweets(allTweets, sort).slice(0, limit);

  // Output
  if (json) {
    console.log(JSON.stringify(allTweets, null, 2));
  } else if (markdown) {
    const md = `# Search: ${query}\n\n${allTweets.map((t, i) => tweetToMarkdown(t, i)).join('\n')}`;
    if (save) saveOutput(`search-${query}`, md);
    console.log(md);
  } else {
    console.log(`\n🔍 Search: "${query}" (${allTweets.length} results, sorted by ${sort})\n`);
    allTweets.forEach((t, i) => console.log(formatTweet(t, i)));
    if (save) {
      const md = `# Search: ${query}\n\n${allTweets.map((t, i) => tweetToMarkdown(t, i)).join('\n')}`;
      saveOutput(`search-${query}`, md);
    }
  }
  if (!json) console.log(formatCost(getCost()));
}

async function doProfile() {
  const username = positional[0]?.replace('@', '');
  if (!username) { console.error('Usage: x-search.ts profile <username>'); process.exit(1); }

  const count = nflag('count', 20);
  const includeReplies = bflag('replies');
  const json = bflag('json');

  const cacheKey = `profile:${username}:${count}`;
  const cached = cache.get(cacheKey);

  let info: UserInfo, tweets: Tweet[];
  if (cached) {
    ({ info, tweets } = cached);
  } else {
    [info, { tweets }] = await Promise.all([getUserInfo(username), getUserTweets(username)]);
    if (!includeReplies) tweets = tweets.filter(t => !t.isReply);
    tweets = tweets.slice(0, count);
    cache.set(cacheKey, { info, tweets });
  }

  if (json) {
    console.log(JSON.stringify({ info, tweets }, null, 2));
  } else {
    console.log('\n' + formatProfile(info) + '\n');
    console.log(`📝 Recent tweets (${tweets.length}):\n`);
    tweets.forEach((t, i) => console.log(formatTweet(t, i)));
  }
  if (!json) console.log(formatCost(getCost()));
}

async function doTweet() {
  const id = positional[0];
  if (!id) { console.error('Usage: x-search.ts tweet <tweet_id>'); process.exit(1); }

  const tweets = await getTweetsById([id]);
  if (!tweets.length) { console.error('Tweet not found'); process.exit(1); }

  if (bflag('json')) {
    console.log(JSON.stringify(tweets[0], null, 2));
  } else {
    console.log('\n' + formatTweet(tweets[0]));
  }
  console.log(formatCost(getCost()));
}

async function doThread() {
  const id = positional[0];
  if (!id) { console.error('Usage: x-search.ts thread <tweet_id>'); process.exit(1); }

  const tweets = await getThread(id);
  if (!tweets.length) { console.error('Thread not found'); process.exit(1); }

  if (bflag('json')) {
    console.log(JSON.stringify(tweets, null, 2));
  } else {
    console.log(`\n🧵 Thread (${tweets.length} tweets):\n`);
    tweets.forEach((t, i) => console.log(formatTweet(t, i)));
  }
  console.log(formatCost(getCost()));
}

async function doReplies() {
  const id = positional[0];
  if (!id) { console.error('Usage: x-search.ts replies <tweet_id>'); process.exit(1); }

  const limit = nflag('limit', 20);
  const sort = flag('sort', 'likes')!;
  const result = await getTweetReplies(id);
  let tweets = sortTweets(result.tweets, sort).slice(0, limit);

  if (bflag('json')) {
    console.log(JSON.stringify(tweets, null, 2));
  } else {
    console.log(`\n💬 Replies (${tweets.length}):\n`);
    tweets.forEach((t, i) => console.log(formatTweet(t, i)));
  }
  console.log(formatCost(getCost()));
}

async function doQuotes() {
  const id = positional[0];
  if (!id) { console.error('Usage: x-search.ts quotes <tweet_id>'); process.exit(1); }

  const limit = nflag('limit', 20);
  const sort = flag('sort', 'likes')!;
  const result = await getTweetQuotes(id);
  let tweets = sortTweets(result.tweets, sort).slice(0, limit);

  if (bflag('json')) {
    console.log(JSON.stringify(tweets, null, 2));
  } else {
    console.log(`\n📎 Quote tweets (${tweets.length}):\n`);
    tweets.forEach((t, i) => console.log(formatTweet(t, i)));
  }
  console.log(formatCost(getCost()));
}

async function doMentions() {
  const username = positional[0]?.replace('@', '');
  if (!username) { console.error('Usage: x-search.ts mentions <username>'); process.exit(1); }

  const limit = nflag('limit', 20);
  const sort = flag('sort', 'recent')!;
  const since = flag('since');

  const cacheKey = `mentions:${username}`;
  const cached = cache.get(cacheKey);
  let tweets: Tweet[];

  if (cached) {
    tweets = cached;
  } else {
    const result = await getUserMentions(username);
    tweets = result.tweets;
    cache.set(cacheKey, tweets);
  }

  tweets = filterSince(tweets, since);
  tweets = sortTweets(tweets, sort).slice(0, limit);

  if (bflag('json')) {
    console.log(JSON.stringify(tweets, null, 2));
  } else {
    console.log(`\n📢 Mentions of @${username} (${tweets.length}):\n`);
    tweets.forEach((t, i) => console.log(formatTweet(t, i)));
  }
  console.log(formatCost(getCost()));
}

async function doFollowers() {
  const username = positional[0]?.replace('@', '');
  if (!username) { console.error('Usage: x-search.ts followers <username>'); process.exit(1); }

  const limit = nflag('limit', 20);
  const result = await getUserFollowers(username);
  const users = result.users.slice(0, limit);

  if (bflag('json')) {
    console.log(JSON.stringify(users, null, 2));
  } else {
    console.log(`\n👥 Followers of @${username} (${users.length}):\n`);
    users.forEach((u, i) => console.log(formatUserCompact(u, i)));
  }
  console.log(formatCost(getCost()));
}

async function doFollowing() {
  const username = positional[0]?.replace('@', '');
  if (!username) { console.error('Usage: x-search.ts following <username>'); process.exit(1); }

  const limit = nflag('limit', 20);
  const result = await getUserFollowings(username);
  const users = result.users.slice(0, limit);

  if (bflag('json')) {
    console.log(JSON.stringify(users, null, 2));
  } else {
    console.log(`\n👤 @${username} is following (${users.length}):\n`);
    users.forEach((u, i) => console.log(formatUserCompact(u, i)));
  }
  console.log(formatCost(getCost()));
}

async function doSearchUsers() {
  const query = positional[0];
  if (!query) { console.error('Usage: x-search.ts users "<query>"'); process.exit(1); }

  const limit = nflag('limit', 20);
  const result = await searchUsers(query);
  const users = result.users.slice(0, limit);

  if (bflag('json')) {
    console.log(JSON.stringify(users, null, 2));
  } else {
    console.log(`\n🔍 User search: "${query}" (${users.length}):\n`);
    users.forEach((u, i) => console.log(formatUserCompact(u, i)));
  }
  console.log(formatCost(getCost()));
}

async function doTrending() {
  const woeid = nflag('woeid', 1);  // 1 = worldwide
  const count = nflag('count', 30);

  const cacheKey = `trends:${woeid}`;
  const cached = cache.get(cacheKey, 300000); // 5 min cache for trends
  let trends: any[];

  if (cached) {
    trends = cached;
  } else {
    trends = await getTrends(woeid, count);
    cache.set(cacheKey, trends);
  }

  if (bflag('json')) {
    console.log(JSON.stringify(trends, null, 2));
  } else {
    console.log(`\n📈 Trending${woeid === 1 ? ' (Worldwide)' : ` (woeid: ${woeid})`}:\n`);
    trends.forEach((t, i) => console.log(formatTrend(t, i)));
  }
  console.log(formatCost(getCost()));
}

async function doCommunity() {
  const sub = positional[0];
  const id = positional[1] || positional[0];

  if (sub === 'tweets' && positional[1]) {
    const communityId = positional[1];
    const limit = nflag('limit', 20);
    const sort = flag('sort', 'likes')!;
    const result = await getCommunityTweets(communityId);
    let tweets = sortTweets(result.tweets, sort).slice(0, limit);

    if (bflag('json')) {
      console.log(JSON.stringify(tweets, null, 2));
    } else {
      console.log(`\n🏘 Community tweets (${tweets.length}):\n`);
      tweets.forEach((t, i) => console.log(formatTweet(t, i)));
    }
    console.log(formatCost(getCost()));
    return;
  }

  if (id && id !== 'tweets') {
    const info = await getCommunityInfo(id);
    if (bflag('json')) {
      console.log(JSON.stringify(info, null, 2));
    } else {
      console.log(`\n🏘 Community: ${info.name || id}`);
      if (info.description) console.log(`   ${info.description}`);
      console.log(`   Members: ${info.member_count || '?'}  Moderators: ${info.moderator_count || '?'}`);
      if (info.primary_topic) console.log(`   Topic: ${info.primary_topic.name}`);
    }
    console.log(formatCost(getCost()));
    return;
  }

  console.error('Usage: x-search.ts community <id> | community tweets <id>');
}

// --- Watchlist ---
function loadWatchlist(): Array<{ username: string; note: string; addedAt: string }> {
  if (!existsSync(WATCHLIST_PATH)) return [];
  return JSON.parse(readFileSync(WATCHLIST_PATH, 'utf-8'));
}

function saveWatchlist(list: any[]) {
  mkdirSync(dirname(WATCHLIST_PATH), { recursive: true });
  writeFileSync(WATCHLIST_PATH, JSON.stringify(list, null, 2));
}

async function doWatchlist() {
  const sub = positional[0];
  const list = loadWatchlist();

  if (!sub) {
    if (!list.length) { console.log('Watchlist is empty'); return; }
    console.log('\n📋 Watchlist:\n');
    list.forEach(w => console.log(`  @${w.username} — ${w.note || ''} (added ${w.addedAt})`));
    return;
  }

  if (sub === 'add') {
    const user = positional[1]?.replace('@', '');
    const note = positional.slice(2).join(' ') || '';
    if (!user) { console.error('Usage: watchlist add <user> [note]'); process.exit(1); }
    if (list.find(w => w.username === user)) { console.log(`@${user} already in watchlist`); return; }
    list.push({ username: user, note, addedAt: new Date().toISOString().split('T')[0] });
    saveWatchlist(list);
    console.log(`✅ Added @${user} to watchlist`);
    return;
  }

  if (sub === 'remove') {
    const user = positional[1]?.replace('@', '');
    if (!user) { console.error('Usage: watchlist remove <user>'); process.exit(1); }
    const filtered = list.filter(w => w.username !== user);
    if (filtered.length === list.length) { console.log(`@${user} not in watchlist`); return; }
    saveWatchlist(filtered);
    console.log(`🗑 Removed @${user} from watchlist`);
    return;
  }

  if (sub === 'check') {
    if (!list.length) { console.log('Watchlist is empty'); return; }
    console.log(`\n🔍 Checking ${list.length} watchlist accounts...\n`);
    for (const w of list) {
      try {
        const { tweets } = await getUserTweets(w.username);
        const recent = tweets.filter(t => !t.isReply).slice(0, 3);
        console.log(`\n${'─'.repeat(50)}`);
        console.log(`@${w.username} ${w.note ? `(${w.note})` : ''}`);
        if (recent.length) {
          recent.forEach(t => console.log(formatTweet(t)));
        } else {
          console.log('  No recent tweets');
        }
      } catch (e: any) {
        console.error(`  Error fetching @${w.username}: ${e.message}`);
      }
    }
    console.log(formatCost(getCost()));
    return;
  }

  console.error('Unknown watchlist command. Use: add, remove, check');
}

async function doCacheClear() {
  const n = cache.clear();
  console.log(`🗑 Cleared ${n} cache files`);
}

// --- Main ---
async function main() {
  resetCost();
  switch (command) {
    case 'search': return doSearch();
    case 'profile': return doProfile();
    case 'tweet': return doTweet();
    case 'thread': return doThread();
    case 'replies': return doReplies();
    case 'quotes': return doQuotes();
    case 'mentions': return doMentions();
    case 'followers': return doFollowers();
    case 'following': return doFollowing();
    case 'users': return doSearchUsers();
    case 'trending': return doTrending();
    case 'community': return doCommunity();
    case 'watchlist': return doWatchlist();
    case 'cache': if (positional[0] === 'clear') return doCacheClear(); break;
    default:
      console.log(`x-search — X/Twitter research tool

Commands:
  search "<query>"       Search tweets (--sort, --since, --pages, --quick, --type Top|Latest)
  profile <username>     User profile + recent tweets
  tweet <tweet_id>       Get single tweet
  thread <tweet_id>      Get full thread
  replies <tweet_id>     Get tweet replies
  quotes <tweet_id>      Get quote tweets
  mentions <username>    Get tweets mentioning a user
  followers <username>   List followers
  following <username>   List who user follows
  users "<query>"        Search for users
  trending               Get trending topics (--woeid N)
  community <id>         Get community info
  community tweets <id>  Get community tweets
  watchlist [cmd]        Manage watchlist (add/remove/check)
  cache clear            Clear cache

Global flags: --json, --limit N, --sort likes|retweets|impressions|recent`);
  }
}

main().catch(e => { console.error('Error:', e.message); process.exit(1); });
