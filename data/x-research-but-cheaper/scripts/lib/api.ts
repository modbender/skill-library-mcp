import { createHash } from 'crypto';

const BASE = 'https://api.twitterapi.io';

function getKey(): string {
  const k = process.env.TWITTERAPI_KEY;
  if (!k) throw new Error('TWITTERAPI_KEY not set');
  return k;
}

function headers() {
  return { 'X-API-Key': getKey(), 'Content-Type': 'application/json' };
}

export interface Tweet {
  id: string;
  url?: string;
  text: string;
  author: {
    userName: string;
    name: string;
    id?: string;
    followers: number;
    isBlueVerified?: boolean;
    profilePicture?: string;
    description?: string;
  };
  createdAt: string;
  likeCount: number;
  retweetCount: number;
  replyCount: number;
  quoteCount: number;
  viewCount: number;
  bookmarkCount: number;
  lang?: string;
  conversationId?: string;
  inReplyToId?: string;
  inReplyToUsername?: string;
  entities?: any;
  quotedTweet?: any;
  isRetweet?: boolean;
  isReply?: boolean;
}

export interface UserInfo {
  id?: string;
  userName: string;
  name: string;
  description: string;
  followers: number;
  following: number;
  tweetsCount: number;
  listedCount: number;
  favouritesCount?: number;
  mediaCount?: number;
  createdAt: string;
  profileImageUrl: string;
  verified: boolean;
  isBlueVerified: boolean;
  location?: string;
  url?: string;
  pinnedTweetIds?: string[];
  isAutomated?: boolean;
}

export interface SearchResult {
  tweets: Tweet[];
  cursor?: string;
  hasNextPage: boolean;
}

export interface UserListResult {
  users: UserInfo[];
  cursor?: string;
  hasNextPage: boolean;
}

export interface TrendItem {
  name: string;
  tweet_count?: number;
  description?: string;
}

let _costAccum = 0;
export function getCost() { return _costAccum; }
export function resetCost() { _costAccum = 0; }

async function apiFetch(path: string, params: Record<string, string>): Promise<any> {
  const url = new URL(path, BASE);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== '') url.searchParams.set(k, v);
  }
  const res = await fetch(url.toString(), { headers: headers() });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${body}`);
  }
  const data = await res.json();
  // Check for API-level errors
  if (data.status === 'error') {
    throw new Error(`API error: ${data.message || data.msg || 'unknown'}`);
  }
  return data;
}

function normalizeTweet(t: any): Tweet {
  return {
    id: t.id,
    url: t.url,
    text: t.text,
    author: t.author || {
      userName: t.user?.userName || t.user?.screen_name || '',
      name: t.user?.name || '',
      id: t.user?.id,
      followers: t.user?.followers || 0,
      isBlueVerified: t.user?.isBlueVerified,
    },
    createdAt: t.createdAt,
    likeCount: t.likeCount || 0,
    retweetCount: t.retweetCount || 0,
    replyCount: t.replyCount || 0,
    quoteCount: t.quoteCount || 0,
    viewCount: t.viewCount || 0,
    bookmarkCount: t.bookmarkCount || 0,
    lang: t.lang,
    conversationId: t.conversationId,
    inReplyToId: t.inReplyToId,
    inReplyToUsername: t.inReplyToUsername,
    entities: t.entities,
    quotedTweet: t.quoted_tweet,
    isReply: t.isReply,
    isRetweet: t.isRetweet,
  };
}

function normalizeUser(raw: any): UserInfo {
  return {
    id: raw.id,
    userName: raw.userName || raw.screen_name || '',
    name: raw.name || '',
    description: raw.description || raw.profile_bio?.description || '',
    followers: raw.followers || raw.followersCount || 0,
    following: raw.following || raw.followingCount || 0,
    tweetsCount: raw.tweetsCount || raw.statusesCount || 0,
    listedCount: raw.listedCount || 0,
    favouritesCount: raw.favouritesCount,
    mediaCount: raw.mediaCount,
    createdAt: raw.createdAt || '',
    profileImageUrl: raw.profilePicture || raw.profileImageUrl || '',
    verified: raw.verified || false,
    isBlueVerified: raw.isBlueVerified || false,
    location: raw.location,
    url: raw.url,
    pinnedTweetIds: raw.pinnedTweetIds,
    isAutomated: raw.isAutomated,
  };
}

// --- Tweet endpoints ---

export async function searchTweets(query: string, cursor?: string, queryType: string = 'Latest'): Promise<SearchResult> {
  const params: Record<string, string> = { query, queryType };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/tweet/advanced_search', params);
  const tweets: Tweet[] = (data.tweets || []).map(normalizeTweet);
  _costAccum += Math.max(tweets.length, 1) * 0.00015;
  return { tweets, cursor: data.next_cursor, hasNextPage: !!data.has_next_page };
}

export async function getUserInfo(userName: string): Promise<UserInfo> {
  const data = await apiFetch('/twitter/user/info', { userName });
  _costAccum += 0.00018;
  const raw = data.data || data;
  return normalizeUser(raw);
}

export async function getUserTweets(userName: string, cursor?: string): Promise<SearchResult> {
  const params: Record<string, string> = { userName };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/user/last_tweets', params);
  const raw = data.tweets || data.data?.tweets || [];
  const tweets: Tweet[] = raw.map(normalizeTweet);
  _costAccum += Math.max(tweets.length, 1) * 0.00015;
  return {
    tweets,
    cursor: data.next_cursor || data.data?.next_cursor,
    hasNextPage: !!data.has_next_page || !!data.data?.has_next_page,
  };
}

export async function getTweetsById(ids: string[]): Promise<Tweet[]> {
  const data = await apiFetch('/twitter/tweets', { tweet_ids: ids.join(',') });
  const tweets = (data.tweets || []).map(normalizeTweet);
  _costAccum += Math.max(tweets.length, 1) * 0.00015;
  return tweets;
}

export async function getTweetReplies(tweetId: string, cursor?: string): Promise<SearchResult> {
  const params: Record<string, string> = { tweetId };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/tweet/replies', params);
  const tweets = (data.replies || []).map(normalizeTweet);
  _costAccum += Math.max(tweets.length, 1) * 0.00015;
  return { tweets, cursor: data.next_cursor, hasNextPage: !!data.has_next_page };
}

export async function getTweetQuotes(tweetId: string, cursor?: string): Promise<SearchResult> {
  const params: Record<string, string> = { tweetId };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/tweet/quotes', params);
  const tweets = (data.tweets || []).map(normalizeTweet);
  _costAccum += Math.max(tweets.length, 1) * 0.00015;
  return { tweets, cursor: data.next_cursor, hasNextPage: !!data.has_next_page };
}

export async function getTweetRetweeters(tweetId: string, cursor?: string): Promise<UserListResult> {
  const params: Record<string, string> = { tweetId };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/tweet/retweeters', params);
  const users = (data.users || []).map(normalizeUser);
  _costAccum += Math.max(users.length, 1) * 0.00015;
  return { users, cursor: data.next_cursor, hasNextPage: !!data.has_next_page };
}

// --- User endpoints ---

export async function getUserMentions(userName: string, cursor?: string): Promise<SearchResult> {
  const params: Record<string, string> = { userName };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/user/mentions', params);
  const tweets = (data.tweets || []).map(normalizeTweet);
  _costAccum += Math.max(tweets.length, 1) * 0.00015;
  return { tweets, cursor: data.next_cursor, hasNextPage: !!data.has_next_page };
}

export async function getUserFollowers(userName: string, cursor?: string): Promise<UserListResult> {
  const params: Record<string, string> = { userName };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/user/followers', params);
  const users = (data.followers || []).map(normalizeUser);
  _costAccum += Math.max(users.length, 1) * 0.00015;
  return { users, cursor: data.next_cursor, hasNextPage: !!data.has_next_page };
}

export async function getUserFollowings(userName: string, cursor?: string): Promise<UserListResult> {
  const params: Record<string, string> = { userName };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/user/followings', params);
  const users = (data.followings || data.following || []).map(normalizeUser);
  _costAccum += Math.max(users.length, 1) * 0.00015;
  return { users, cursor: data.next_cursor, hasNextPage: !!data.has_next_page };
}

export async function searchUsers(query: string, cursor?: string): Promise<UserListResult> {
  const params: Record<string, string> = { query };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/user/search', params);
  const users = (data.users || []).map(normalizeUser);
  _costAccum += Math.max(users.length, 1) * 0.00018;
  return { users, cursor: data.next_cursor, hasNextPage: !!data.has_next_page };
}

// --- Trends ---

export async function getTrends(woeid: number = 1, count: number = 30): Promise<TrendItem[]> {
  const data = await apiFetch('/twitter/trends', { woeid: String(woeid), count: String(count) });
  _costAccum += 0.00015;
  // Normalize: API returns [{trend: {name, target, rank}}, ...]
  const raw = data.trends || [];
  return raw.map((t: any) => {
    const inner = t.trend || t;
    return { name: inner.name, tweet_count: inner.tweet_count, description: inner.description };
  });
}

// --- Community ---

export async function getCommunityInfo(communityId: string): Promise<any> {
  const data = await apiFetch('/twitter/community/info', { communityId });
  _costAccum += 0.00018;
  return data.community_info || data;
}

export async function getCommunityTweets(communityId: string, cursor?: string): Promise<SearchResult> {
  const params: Record<string, string> = { communityId };
  if (cursor) params.cursor = cursor;
  const data = await apiFetch('/twitter/community/tweets', params);
  const tweets = (data.tweets || []).map(normalizeTweet);
  _costAccum += Math.max(tweets.length, 1) * 0.00015;
  return { tweets, cursor: data.next_cursor, hasNextPage: !!data.has_next_page };
}

// --- Thread (improved: use dedicated replies endpoint) ---

export async function getThread(tweetId: string): Promise<Tweet[]> {
  // Get root tweet
  const roots = await getTweetsById([tweetId]);
  if (!roots.length) return [];
  const root = roots[0];

  // Use dedicated replies endpoint for better results
  const result = await getTweetReplies(tweetId);
  
  // Also try conversation search for thread continuations by the same author
  const convId = root.conversationId || root.id;
  let authorThreadTweets: Tweet[] = [];
  if (root.author?.userName) {
    try {
      const convResult = await searchTweets(`conversation_id:${convId} from:${root.author.userName}`);
      authorThreadTweets = convResult.tweets.filter(t => t.id !== root.id);
    } catch { /* fallback: just use replies */ }
  }

  // Merge: root + author's thread tweets + replies (deduped)
  const seen = new Set<string>([root.id]);
  const all: Tweet[] = [root];
  for (const t of [...authorThreadTweets, ...result.tweets]) {
    if (!seen.has(t.id)) { seen.add(t.id); all.push(t); }
  }
  all.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
  return all;
}
