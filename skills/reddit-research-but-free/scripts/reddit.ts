#!/usr/bin/env npx tsx
/**
 * Reddit Research CLI — zero auth, zero dependencies.
 * Usage: npx tsx reddit.ts <command> [args] [options]
 */

import * as api from "./lib/api.js";
import * as cache from "./lib/cache.js";
import * as fmt from "./lib/format.js";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = import.meta.dirname ?? dirname(fileURLToPath(import.meta.url));

const CACHE_TTL = 15 * 60 * 1000; // 15 min
const QUICK_TTL = 60 * 60 * 1000; // 1 hour

const args = process.argv.slice(2);
const command = args[0];

function flag(name: string): boolean {
  return args.includes(`--${name}`);
}

function opt(name: string, fallback?: string): string | undefined {
  const idx = args.indexOf(`--${name}`);
  if (idx === -1 || idx + 1 >= args.length) return fallback;
  return args[idx + 1];
}

function numOpt(name: string, fallback: number): number {
  const v = opt(name);
  return v ? parseInt(v, 10) : fallback;
}

async function main() {
  try {
    switch (command) {
      case "search":
        await cmdSearch();
        break;
      case "hot":
      case "new":
      case "rising":
      case "top":
      case "controversial":
        await cmdFeed(command as api.FeedSort);
        break;
      case "thread":
        await cmdThread();
        break;
      case "user":
        await cmdUser();
        break;
      case "subreddit":
      case "sub":
        await cmdSubreddit();
        break;
      case "multi":
        await cmdMulti();
        break;
      case "duplicates":
      case "crossposts":
        await cmdDuplicates();
        break;
      case "popular":
        await cmdPopular();
        break;
      case "find-subs":
        await cmdFindSubs();
        break;
      case "wiki":
        await cmdWiki();
        break;
      case "comments":
        await cmdComments();
        break;
      case "watchlist":
        await cmdWatchlist();
        break;
      case "cache":
        await cmdCache();
        break;
      default:
        printUsage();
    }
  } catch (err: any) {
    console.error(`❌ Error: ${err.message}`);
    process.exit(1);
  }
}

// ─── Commands ─────────────────────────────────────────

async function cmdSearch() {
  const query = args[1];
  if (!query) return console.error("Usage: reddit.ts search <query> [--sub <subreddit>] [--sort relevance|top|new|hot|comments] [--time hour|day|week|month|year|all] [--limit N] [--provider reddit|pullpush|arctic-shift]");

  const provider = opt("provider", "reddit");
  const sub = opt("sub");
  const sort = (opt("sort", "relevance") as any);
  const time = (opt("time", "week") as any);
  const limit = numOpt("limit", 15);
  const quick = flag("quick");

  const cacheKey = `search:${provider}:${query}:${sub}:${sort}:${time}:${limit}`;
  const ttl = quick ? QUICK_TTL : CACHE_TTL;
  const cached = cache.get<any>(cacheKey, ttl);

  let result;
  if (cached) {
    result = cached;
    console.error("(cached)");
  } else if (provider === "pullpush") {
    result = await api.pullpushSearch(query, { subreddit: sub || undefined, size: limit, sortType: sort === "top" ? "score" : "created_utc" });
  } else if (provider === "arctic-shift") {
    const author = opt("author");
    result = await api.arcticShiftSearch(query, { subreddit: sub || undefined, author, limit });
  } else {
    result = await api.search(query, { subreddit: sub || undefined, sort, time, limit });
  }
  cache.set(cacheKey, result);

  if (flag("json")) return console.log(fmt.toJson(result));
  if (flag("markdown")) return console.log(fmt.toMarkdown(result.posts, `Search: ${query}`));

  const providerTag = provider !== "reddit" ? ` [${provider}]` : "";
  console.log(`\n🔍 "${query}"${sub ? ` in r/${sub}` : ""}${providerTag} | sort: ${sort} | time: ${time} | ${result.posts.length} results\n`);

  const posts = result.posts.filter((p: any) => !p.stickied);
  if (flag("compact")) {
    for (const p of posts) console.log(fmt.formatPostCompact(p));
  } else {
    for (let i = 0; i < posts.length; i++) {
      console.log(fmt.formatPost(posts[i], i));
      console.log();
    }
  }

  if (flag("save")) saveResults(result.posts, `search-${query.replace(/\s+/g, "-")}`);
}

async function cmdComments() {
  const query = args[1];
  if (!query) return console.error("Usage: reddit.ts comments <query> [--sub <subreddit>] [--provider pullpush|arctic-shift] [--limit N]");

  const provider = opt("provider", "pullpush");
  const sub = opt("sub");
  const limit = numOpt("limit", 15);

  let result;
  if (provider === "arctic-shift") {
    const author = opt("author");
    result = await api.arcticShiftComments(query, { subreddit: sub || undefined, author, limit });
  } else {
    result = await api.pullpushComments(query, { subreddit: sub || undefined, size: limit });
  }

  if (flag("json")) return console.log(fmt.toJson(result));

  const providerTag = ` [${provider}]`;
  console.log(`\n💬 Comments matching "${query}"${sub ? ` in r/${sub}` : ""}${providerTag} | ${result.comments.length} results\n`);

  for (const c of result.comments) {
    console.log(fmt.formatComment(c));
    console.log();
  }
}

async function cmdFeed(sort: api.FeedSort) {
  const subreddit = args[1];
  if (!subreddit) return console.error(`Usage: reddit.ts ${sort} <subreddit> [--time hour|day|week|month|year|all] [--limit N]`);

  const time = (opt("time", "day") as any);
  const limit = numOpt("limit", 15);

  const cacheKey = `feed:${subreddit}:${sort}:${time}:${limit}`;
  const cached = cache.get<any>(cacheKey, CACHE_TTL);

  let result;
  if (cached) {
    result = cached;
    console.error("(cached)");
  } else {
    result = await api.subredditFeed(subreddit, { sort, time, limit });
    cache.set(cacheKey, result);
  }

  if (flag("json")) return console.log(fmt.toJson(result));
  if (flag("markdown")) return console.log(fmt.toMarkdown(result.posts, `r/${subreddit} — ${sort}`));

  console.log(`\n📋 r/${subreddit} — ${sort} | time: ${time} | ${result.posts.length} posts\n`);

  const posts = result.posts.filter((p: any) => !p.stickied);
  if (flag("compact")) {
    for (const p of posts) console.log(fmt.formatPostCompact(p));
  } else {
    for (let i = 0; i < posts.length; i++) {
      console.log(fmt.formatPost(posts[i], i));
      console.log();
    }
  }

  if (flag("save")) saveResults(result.posts, `${subreddit}-${sort}`);
}

async function cmdThread() {
  const input = args[1];
  if (!input) return console.error("Usage: reddit.ts thread <url|post_id> [--sub <subreddit>] [--sort top|best|new|controversial] [--limit N] [--depth N]");

  const sort = (opt("sort", "top") as any);
  const limit = numOpt("limit", 30);
  const depth = numOpt("depth", 3);

  let result;
  if (input.includes("reddit.com")) {
    result = await api.threadFromUrl(input, { sort, limit, depth });
  } else {
    const sub = opt("sub");
    if (!sub) return console.error("Need --sub <subreddit> when using post ID");
    result = await api.thread(sub, input, { sort, limit, depth });
  }

  if (flag("json")) return console.log(fmt.toJson(result));

  console.log();
  console.log(fmt.formatThread(result));
}

async function cmdUser() {
  const username = args[1];
  if (!username) return console.error("Usage: reddit.ts user <username> [--posts|--comments] [--sort new|top|hot] [--limit N]");

  const profile = await api.userProfile(username);

  if (flag("json")) return console.log(fmt.toJson(profile));

  console.log();
  console.log(fmt.formatUser(profile));
  console.log();

  const type = flag("comments") ? "comments" as const : flag("posts") ? "links" as const : "overview" as const;
  const sort = (opt("sort", "new") as any);
  const limit = numOpt("limit", 10);

  const posts = await api.userPosts(username, { sort, limit, type });

  console.log(`--- Recent ${type} (${posts.items.length}) ---\n`);
  for (const item of posts.items) {
    if (item.title) {
      console.log(fmt.formatPost(item));
    } else {
      console.log(fmt.formatComment(item));
    }
    console.log();
  }
}

async function cmdSubreddit() {
  const subreddit = args[1];
  if (!subreddit) return console.error("Usage: reddit.ts subreddit <name>");

  const info = await api.subredditInfo(subreddit);

  if (flag("json")) return console.log(fmt.toJson(info));

  console.log();
  console.log(fmt.formatSubreddit(info));
}

async function cmdMulti() {
  const subs = args[1];
  if (!subs) return console.error("Usage: reddit.ts multi <sub1+sub2+sub3> [--sort hot|new|top] [--time day|week] [--limit N]");

  const subreddits = subs.split("+");
  const sort = (opt("sort", "hot") as any);
  const time = (opt("time", "day") as any);
  const limit = numOpt("limit", 15);

  const result = await api.multiFeed(subreddits, { sort, time, limit });

  if (flag("json")) return console.log(fmt.toJson(result));

  console.log(`\n📋 Multi: ${subreddits.map((s) => `r/${s}`).join(" + ")} | ${sort} | ${result.posts.length} posts\n`);

  for (let i = 0; i < result.posts.length; i++) {
    console.log(fmt.formatPost(result.posts[i], i));
    console.log();
  }
}

async function cmdDuplicates() {
  const postId = args[1];
  if (!postId) return console.error("Usage: reddit.ts duplicates <post_id>");

  const result = await api.duplicates(postId);

  if (flag("json")) return console.log(fmt.toJson(result));

  console.log(`\n🔗 Cross-posts of "${result.original.title}" (${result.count} found)\n`);
  for (const p of result.crossPosts) {
    console.log(fmt.formatPostCompact(p));
  }
}

async function cmdPopular() {
  const limit = numOpt("limit", 25);
  const subs = await api.popular({ limit });

  if (flag("json")) return console.log(fmt.toJson(subs));

  console.log("\n🔥 Popular Subreddits\n");
  for (const s of subs) {
    console.log(`  r/${s.name.padEnd(22)} | ${String(s.subscribers).padStart(10)} subs | ${String(s.activeUsers).padStart(6)} online | ${s.title.slice(0, 40)}`);
  }
}

async function cmdFindSubs() {
  const query = args[1];
  if (!query) return console.error("Usage: reddit.ts find-subs <query> [--limit N]");

  const limit = numOpt("limit", 10);
  const subs = await api.searchSubreddits(query, limit);

  if (flag("json")) return console.log(fmt.toJson(subs));

  console.log(`\n🔍 Subreddits matching "${query}"\n`);
  for (const s of subs) {
    console.log(`  r/${s.name.padEnd(22)} | ${String(s.subscribers).padStart(10)} subs | ${s.description?.slice(0, 50) || ""}`);
  }
}

async function cmdWiki() {
  const subreddit = args[1];
  if (!subreddit) return console.error("Usage: reddit.ts wiki <subreddit> [page]");

  const page = args[2] || "index";
  const result = await api.wiki(subreddit, page);

  if (flag("json")) return console.log(fmt.toJson(result));

  console.log(`\n📖 r/${subreddit}/wiki/${page}\n`);
  console.log(result.content?.slice(0, 5000) || "(empty)");
}

async function cmdWatchlist() {
  const sub = args[1];
  const dataDir = join(__dirname, "..", "data");
  const watchFile = join(dataDir, "watchlist.json");

  let watchlist: { subreddits: { name: string; note?: string }[] } = { subreddits: [] };
  try {
    watchlist = JSON.parse(readFileSync(watchFile, "utf-8"));
  } catch {}

  if (!sub || sub === "show") {
    if (watchlist.subreddits.length === 0) return console.log("Watchlist is empty. Use: reddit.ts watchlist add <subreddit>");
    console.log("\n📋 Watchlist\n");
    for (const s of watchlist.subreddits) {
      console.log(`  r/${s.name}${s.note ? ` — ${s.note}` : ""}`);
    }
    return;
  }

  if (sub === "add") {
    const name = args[2];
    if (!name) return console.error("Usage: reddit.ts watchlist add <subreddit> [note]");
    const note = args.slice(3).join(" ") || undefined;
    if (watchlist.subreddits.some((s) => s.name === name)) return console.log(`r/${name} already in watchlist`);
    watchlist.subreddits.push({ name, note });
    writeFileSync(watchFile, JSON.stringify(watchlist, null, 2));
    console.log(`✅ Added r/${name} to watchlist`);
    return;
  }

  if (sub === "remove") {
    const name = args[2];
    if (!name) return console.error("Usage: reddit.ts watchlist remove <subreddit>");
    watchlist.subreddits = watchlist.subreddits.filter((s) => s.name !== name);
    writeFileSync(watchFile, JSON.stringify(watchlist, null, 2));
    console.log(`✅ Removed r/${name} from watchlist`);
    return;
  }

  if (sub === "check") {
    if (watchlist.subreddits.length === 0) return console.log("Watchlist is empty.");
    console.log(`\n🔍 Checking ${watchlist.subreddits.length} subreddits...\n`);
    for (const s of watchlist.subreddits) {
      try {
        const result = await api.subredditFeed(s.name, { sort: "hot", limit: 5 });
        const hot = result.posts.filter((p: any) => !p.stickied);
        console.log(`📋 r/${s.name}${s.note ? ` (${s.note})` : ""}`);
        for (const p of hot.slice(0, 3)) {
          console.log(`  ⬆️ ${String(p.score).padStart(5)} | 💬 ${String(p.numComments).padStart(4)} | ${p.title.slice(0, 70)}`);
        }
        console.log();
      } catch (err: any) {
        console.error(`  ❌ r/${s.name}: ${err.message}`);
      }
    }
    return;
  }
}

async function cmdCache() {
  const sub = args[1];
  if (sub === "clear") {
    const n = cache.clear();
    console.log(`🗑️ Cleared ${n} cached entries`);
  } else if (sub === "stats") {
    const s = cache.stats();
    console.log(`📊 Cache: ${s.count} entries, ${s.sizeKb} KB`);
  } else {
    console.error("Usage: reddit.ts cache clear|stats");
  }
}

// ─── Helpers ──────────────────────────────────────────

function saveResults(posts: any[], name: string) {
  const dir = join(__dirname, "..", "data");
  const file = join(dir, `${name}-${new Date().toISOString().slice(0, 10)}.md`);
  writeFileSync(file, fmt.toMarkdown(posts, name));
  console.error(`\n💾 Saved to ${file}`);
}

function printUsage() {
  console.log(`
Reddit Research CLI — zero auth, zero dependencies.

COMMANDS:

  Search & Discovery
    search <query>           Search Reddit (global or within subreddit)
    comments <query>         Search comments (via PullPush/Arctic Shift)
    find-subs <query>        Find subreddits by keyword
    popular                  List popular subreddits

  Subreddit Feeds
    hot <subreddit>          Hot posts
    new <subreddit>          New posts
    rising <subreddit>       Rising posts
    top <subreddit>          Top posts (use --time day|week|month|year|all)
    controversial <sub>      Controversial posts
    multi <sub1+sub2+sub3>   Combined feed from multiple subreddits

  Content
    thread <url|id>          Read post + top comments
    wiki <subreddit> [page]  Read subreddit wiki
    duplicates <post_id>     Find cross-posts

  Users
    user <username>          Profile + recent activity

  Subreddit Info
    subreddit <name>         Subreddit details

  Monitoring
    watchlist                Show watched subreddits
    watchlist add <sub>      Add subreddit to watchlist
    watchlist remove <sub>   Remove from watchlist
    watchlist check          Check hot posts from all watched

  Cache
    cache stats              Cache statistics
    cache clear              Clear all cached data

GLOBAL OPTIONS:
    --json                   Raw JSON output
    --markdown               Markdown formatted output
    --compact                Compact one-line format
    --save                   Save results to file
    --limit N                Max results (default: 15)
    --time hour|day|week|month|year|all
    --sort relevance|top|new|hot|comments
    --sub <subreddit>        Restrict search to subreddit
    --author <username>      Filter by author (Arctic Shift)
    --depth N                Comment tree depth (default: 3)
    --provider <name>        Data provider (see below)

PROVIDERS:
    reddit (default)         old.reddit.com JSON — real-time, no auth
    pullpush                 PullPush API — historical/deleted data, global search
    arctic-shift             Arctic Shift — historical archive, requires --sub or --author

EXAMPLES:
    npx tsx reddit.ts search "pumpfun scam" --sort top --time month
    npx tsx reddit.ts search "openclaw" --provider pullpush --limit 10
    npx tsx reddit.ts search "agent" --provider arctic-shift --sub openclaw
    npx tsx reddit.ts comments "memecoin" --sub solana --provider pullpush
    npx tsx reddit.ts hot solana --limit 10
    npx tsx reddit.ts thread https://reddit.com/r/solana/comments/abc123/...
    npx tsx reddit.ts multi solana+cryptocurrency+defi --sort top --time week
    npx tsx reddit.ts user vbuterin --posts --limit 5
    npx tsx reddit.ts find-subs "artificial intelligence"
    npx tsx reddit.ts watchlist add solana "Solana ecosystem"
    npx tsx reddit.ts watchlist check
`);
}

main();
