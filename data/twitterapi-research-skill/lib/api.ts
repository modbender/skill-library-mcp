/**
 * X API wrapper — search, threads, profiles, single tweets.
 * Uses twitterapi.io (third-party) instead of the official X API.
 * Requires API key from env: TWITTERAPI_IO_KEY
 */

import { readFileSync } from "fs";

const BASE = "https://api.twitterapi.io";
const RATE_DELAY_MS = 200; // twitterapi.io supports up to 200 QPS

function getApiKey(): string {
  // Try env first
  if (process.env.TWITTERAPI_IO_KEY) return process.env.TWITTERAPI_IO_KEY;

  // Try global.env
  try {
    const envFile = readFileSync(
      `${process.env.HOME}/.config/env/global.env`,
      "utf-8"
    );
    const match = envFile.match(/TWITTERAPI_IO_KEY=["']?([^"'\n]+)/);
    if (match) return match[1];
  } catch {}

  throw new Error(
    "TWITTERAPI_IO_KEY not found in env or ~/.config/env/global.env"
  );
}

async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export interface Tweet {
  id: string;
  text: string;
  author_id: string;
  username: string;
  name: string;
  created_at: string;
  conversation_id: string;
  metrics: {
    likes: number;
    retweets: number;
    replies: number;
    quotes: number;
    impressions: number;
    bookmarks: number;
  };
  urls: string[];
  mentions: string[];
  hashtags: string[];
  tweet_url: string;
}

/**
 * Parse a twitterapi.io date string ("Tue Dec 10 07:00:30 +0000 2024")
 * into an ISO 8601 string for internal consistency.
 */
function parseTwitterDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    if (!isNaN(d.getTime())) return d.toISOString();
  } catch {}
  return dateStr; // fallback: return as-is
}

/**
 * Parse a single raw tweet from twitterapi.io into our internal Tweet format.
 * twitterapi.io returns flat tweet objects with an embedded `author` field.
 */
function parseTweet(t: any): Tweet {
  const author = t.author || {};
  return {
    id: t.id || "",
    text: t.text || "",
    author_id: author.id || "",
    username: author.userName || "?",
    name: author.name || "?",
    created_at: parseTwitterDate(t.createdAt || ""),
    conversation_id: t.conversationId || "",
    metrics: {
      likes: t.likeCount || 0,
      retweets: t.retweetCount || 0,
      replies: t.replyCount || 0,
      quotes: t.quoteCount || 0,
      impressions: t.viewCount || 0,
      bookmarks: t.bookmarkCount || 0,
    },
    urls: (t.entities?.urls || [])
      .map((u: any) => u.expanded_url || u.url)
      .filter(Boolean),
    mentions: (t.entities?.mentions || [])
      .map((m: any) => m.username || m.userName)
      .filter(Boolean),
    hashtags: (t.entities?.hashtags || [])
      .map((h: any) => h.tag || h.text)
      .filter(Boolean),
    tweet_url: t.url || `https://x.com/${author.userName || "?"}/status/${t.id}`,
  };
}

function parseTweets(rawTweets: any[]): Tweet[] {
  if (!rawTweets || !Array.isArray(rawTweets)) return [];
  return rawTweets.map(parseTweet);
}

/**
 * Parse a "since" value into the twitterapi.io query format.
 * Accepts: "1h", "2h", "6h", "12h", "1d", "2d", "3d", "7d"
 * Or a raw ISO 8601 string.
 * Returns a string like "since:2024-12-10_07:00:30_UTC" for query embedding.
 */
function parseSince(since: string): string | null {
  let date: Date | null = null;

  // Check for shorthand like "1h", "3h", "1d"
  const match = since.match(/^(\d+)(m|h|d)$/);
  if (match) {
    const num = parseInt(match[1]);
    const unit = match[2];
    const ms =
      unit === "m" ? num * 60_000 :
      unit === "h" ? num * 3_600_000 :
      num * 86_400_000;
    date = new Date(Date.now() - ms);
  }

  // Check if it's already ISO 8601
  if (!date && (since.includes("T") || since.includes("-"))) {
    try {
      date = new Date(since);
      if (isNaN(date.getTime())) date = null;
    } catch {
      date = null;
    }
  }

  if (!date) return null;

  // Format as "YYYY-MM-DD_HH:MM:SS_UTC" for twitterapi.io query operator
  const y = date.getUTCFullYear();
  const mo = String(date.getUTCMonth() + 1).padStart(2, "0");
  const d = String(date.getUTCDate()).padStart(2, "0");
  const h = String(date.getUTCHours()).padStart(2, "0");
  const mi = String(date.getUTCMinutes()).padStart(2, "0");
  const s = String(date.getUTCSeconds()).padStart(2, "0");
  return `since:${y}-${mo}-${d}_${h}:${mi}:${s}_UTC`;
}

/**
 * Parse a "since" value into a Date object for client-side filtering.
 */
function parseSinceDate(since: string): Date | null {
  const match = since.match(/^(\d+)(m|h|d)$/);
  if (match) {
    const num = parseInt(match[1]);
    const unit = match[2];
    const ms =
      unit === "m" ? num * 60_000 :
      unit === "h" ? num * 3_600_000 :
      num * 86_400_000;
    return new Date(Date.now() - ms);
  }
  if (since.includes("T") || since.includes("-")) {
    try {
      const d = new Date(since);
      if (!isNaN(d.getTime())) return d;
    } catch {}
  }
  return null;
}

async function apiGet(path: string, params: Record<string, string> = {}): Promise<any> {
  const apiKey = getApiKey();
  const qs = new URLSearchParams(params).toString();
  const url = `${BASE}${path}${qs ? `?${qs}` : ""}`;

  const res = await fetch(url, {
    headers: { "x-api-key": apiKey },
  });

  if (res.status === 429) {
    throw new Error("Rate limited by twitterapi.io. Try again shortly.");
  }

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`twitterapi.io ${res.status}: ${body.slice(0, 200)}`);
  }

  return res.json();
}

/**
 * Search tweets via twitterapi.io Advanced Search.
 * Uses the same query operators as Twitter's native advanced search.
 * Each page returns up to 20 tweets. No time-range limit (full archive).
 */
export async function search(
  query: string,
  opts: {
    maxResults?: number; // trims results to this count (page size fixed at ~20 by twitterapi.io)
    pages?: number;
    sortOrder?: "relevancy" | "recency";
    since?: string; // shorthand like "1h", "3h", "1d" or ISO 8601
  } = {}
): Promise<Tweet[]> {
  const pages = opts.pages || 1;
  const queryType = opts.sortOrder === "recency" ? "Latest" : "Top";

  // Embed since as a query operator if provided
  let fullQuery = query;
  if (opts.since) {
    const sinceOp = parseSince(opts.since);
    if (sinceOp && !query.includes("since:")) {
      fullQuery += ` ${sinceOp}`;
    }
  }

  let allTweets: Tweet[] = [];
  let cursor = "";

  for (let page = 0; page < pages; page++) {
    const params: Record<string, string> = {
      query: fullQuery,
      queryType,
    };
    if (cursor) params.cursor = cursor;

    const raw = await apiGet("/twitter/tweet/advanced_search", params);
    const tweets = parseTweets(raw.tweets);
    allTweets.push(...tweets);

    if (!raw.has_next_page || !raw.next_cursor) break;
    cursor = raw.next_cursor;
    if (page < pages - 1) await sleep(RATE_DELAY_MS);
  }

  // Client-side date filtering when `since` is set, because the API
  // since: operator occasionally lets older tweets through.
  if (opts.since) {
    const sinceDate = parseSinceDate(opts.since);
    if (sinceDate) {
      allTweets = allTweets.filter(
        (t) => new Date(t.created_at).getTime() >= sinceDate.getTime()
      );
    }
  }

  if (opts.maxResults) {
    allTweets = allTweets.slice(0, opts.maxResults);
  }

  return allTweets;
}

/**
 * Fetch a full conversation thread by tweet ID.
 * Uses the dedicated thread_context endpoint.
 */
export async function thread(
  tweetId: string,
  opts: { pages?: number } = {}
): Promise<Tweet[]> {
  const pages = opts.pages || 2;
  let allTweets: Tweet[] = [];
  let cursor = "";

  for (let page = 0; page < pages; page++) {
    const params: Record<string, string> = { tweetId };
    if (cursor) params.cursor = cursor;

    const raw = await apiGet("/twitter/tweet/thread_context", params);
    const tweets = parseTweets(raw.replies);
    allTweets.push(...tweets);

    if (!raw.has_next_page || !raw.next_cursor) break;
    cursor = raw.next_cursor;
    if (page < pages - 1) await sleep(RATE_DELAY_MS);
  }

  return allTweets;
}

/**
 * Get recent tweets from a specific user.
 * Uses the dedicated last_tweets endpoint instead of search.
 */
export async function profile(
  username: string,
  opts: { count?: number; includeReplies?: boolean } = {}
): Promise<{ user: any; tweets: Tweet[] }> {
  // Fetch user info
  const userRaw = await apiGet("/twitter/user/info", { userName: username });

  if (!userRaw.data || userRaw.status === "error") {
    throw new Error(`User @${username} not found`);
  }

  const user = userRaw.data;
  // Normalize user fields to match format expected by formatters
  user.username = user.userName;
  user.public_metrics = {
    followers_count: user.followers || 0,
    following_count: user.following || 0,
    tweet_count: user.statusesCount || 0,
    like_count: user.favouritesCount || 0,
  };

  await sleep(RATE_DELAY_MS);

  // Fetch recent tweets using last_tweets endpoint
  const count = opts.count || 20;
  const pagesToFetch = Math.ceil(count / 20); // 20 tweets per page
  let allTweets: Tweet[] = [];
  let cursor = "";

  for (let page = 0; page < pagesToFetch; page++) {
    const params: Record<string, string> = {
      userName: username,
      includeReplies: String(opts.includeReplies || false),
    };
    if (cursor) params.cursor = cursor;

    const raw = await apiGet("/twitter/user/last_tweets", params);
    const tweets = parseTweets(raw.tweets);
    allTweets.push(...tweets);

    if (!raw.has_next_page || !raw.next_cursor) break;
    cursor = raw.next_cursor;
    if (page < pagesToFetch - 1) await sleep(RATE_DELAY_MS);
  }

  // Trim to requested count
  allTweets = allTweets.slice(0, count);

  return { user, tweets: allTweets };
}

/**
 * Fetch a single tweet by ID.
 */
export async function getTweet(tweetId: string): Promise<Tweet | null> {
  const raw = await apiGet("/twitter/tweets", { tweet_ids: tweetId });

  if (raw.tweets && raw.tweets.length > 0) {
    return parseTweet(raw.tweets[0]);
  }
  return null;
}

/**
 * Sort tweets by engagement metric.
 */
export function sortBy(
  tweets: Tweet[],
  metric: "likes" | "impressions" | "retweets" | "replies" = "likes"
): Tweet[] {
  return [...tweets].sort((a, b) => b.metrics[metric] - a.metrics[metric]);
}

/**
 * Filter tweets by minimum engagement.
 */
export function filterEngagement(
  tweets: Tweet[],
  opts: { minLikes?: number; minImpressions?: number }
): Tweet[] {
  return tweets.filter((t) => {
    if (opts.minLikes && t.metrics.likes < opts.minLikes) return false;
    if (opts.minImpressions && t.metrics.impressions < opts.minImpressions)
      return false;
    return true;
  });
}

/**
 * Deduplicate tweets by ID.
 */
export function dedupe(tweets: Tweet[]): Tweet[] {
  const seen = new Set<string>();
  return tweets.filter((t) => {
    if (seen.has(t.id)) return false;
    seen.add(t.id);
    return true;
  });
}
