/**
 * Reddit JSON API wrapper — zero auth, zero dependencies.
 * Uses old.reddit.com/.json endpoints.
 */

const USER_AGENT = "Lozio/1.0 (OpenClaw Reddit Research Skill)";
const BASE = "https://old.reddit.com";

interface FetchOptions {
  maxRetries?: number;
  delayMs?: number;
}

async function redditFetch(path: string, params: Record<string, string> = {}, opts: FetchOptions = {}): Promise<any> {
  const { maxRetries = 2, delayMs = 1000 } = opts;
  const qs = new URLSearchParams(params).toString();
  const url = `${BASE}${path}.json${qs ? `?${qs}` : ""}`;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, {
        headers: { "User-Agent": USER_AGENT },
        signal: AbortSignal.timeout(15000),
      });

      if (res.status === 429) {
        const wait = delayMs * (attempt + 1);
        console.error(`Rate limited, waiting ${wait}ms...`);
        await new Promise((r) => setTimeout(r, wait));
        continue;
      }

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      return await res.json();
    } catch (err: any) {
      if (attempt === maxRetries) throw err;
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }
}

// ─── Search ───────────────────────────────────────────

export interface SearchOptions {
  subreddit?: string;
  sort?: "relevance" | "hot" | "top" | "new" | "comments";
  time?: "hour" | "day" | "week" | "month" | "year" | "all";
  limit?: number;
  after?: string;
  nsfw?: boolean;
}

export async function search(query: string, opts: SearchOptions = {}) {
  const { subreddit, sort = "relevance", time = "all", limit = 25, after, nsfw = false } = opts;
  const path = subreddit ? `/r/${subreddit}/search` : "/search";
  const params: Record<string, string> = {
    q: query,
    sort,
    t: time,
    limit: String(Math.min(limit, 100)),
    restrict_sr: subreddit ? "on" : "off",
  };
  if (after) params.after = after;
  if (!nsfw) params.include_over_18 = "off";

  const data = await redditFetch(path, params);
  return {
    posts: data.data.children.map(parseListing),
    after: data.data.after,
    count: data.data.dist,
  };
}

// ─── Subreddit feeds ──────────────────────────────────

export type FeedSort = "hot" | "new" | "rising" | "top" | "controversial";

export interface FeedOptions {
  sort?: FeedSort;
  time?: "hour" | "day" | "week" | "month" | "year" | "all";
  limit?: number;
  after?: string;
}

export async function subredditFeed(subreddit: string, opts: FeedOptions = {}) {
  const { sort = "hot", time = "day", limit = 25, after } = opts;
  const path = `/r/${subreddit}/${sort}`;
  const params: Record<string, string> = {
    limit: String(Math.min(limit, 100)),
    t: time,
  };
  if (after) params.after = after;

  const data = await redditFetch(path, params);
  return {
    posts: data.data.children.map(parseListing),
    after: data.data.after,
  };
}

// ─── Multi-subreddit feed ─────────────────────────────

export async function multiFeed(subreddits: string[], opts: FeedOptions = {}) {
  const { sort = "hot", time = "day", limit = 25 } = opts;
  const multi = subreddits.join("+");
  const path = `/r/${multi}/${sort}`;
  const params: Record<string, string> = {
    limit: String(Math.min(limit, 100)),
    t: time,
  };

  const data = await redditFetch(path, params);
  return {
    posts: data.data.children.map(parseListing),
    after: data.data.after,
  };
}

// ─── Thread + comments ────────────────────────────────

export interface ThreadOptions {
  sort?: "top" | "best" | "new" | "controversial" | "old" | "qa";
  limit?: number;
  depth?: number;
}

export async function thread(subreddit: string, postId: string, opts: ThreadOptions = {}) {
  const { sort = "top", limit = 50, depth = 3 } = opts;
  const path = `/r/${subreddit}/comments/${postId}`;
  const params: Record<string, string> = {
    sort,
    limit: String(limit),
    depth: String(depth),
  };

  const data = await redditFetch(path, params);
  const post = data[0].data.children[0].data;
  const comments = flattenComments(data[1].data.children, depth);

  return {
    post: parsePost(post),
    comments,
    commentCount: comments.length,
  };
}

// ─── Thread from URL ──────────────────────────────────

export async function threadFromUrl(url: string, opts: ThreadOptions = {}) {
  // Extract subreddit and post ID from URL
  const match = url.match(/reddit\.com\/r\/(\w+)\/comments\/(\w+)/);
  if (!match) throw new Error(`Invalid Reddit URL: ${url}`);
  return thread(match[1], match[2], opts);
}

// ─── Subreddit info ───────────────────────────────────

export async function subredditInfo(subreddit: string) {
  const data = await redditFetch(`/r/${subreddit}/about`);
  const d = data.data;
  return {
    name: d.display_name,
    title: d.title,
    description: d.public_description || d.description?.slice(0, 300),
    subscribers: d.subscribers,
    activeUsers: d.accounts_active,
    created: new Date(d.created_utc * 1000).toISOString(),
    nsfw: d.over18,
    type: d.subreddit_type,
    url: `https://reddit.com/r/${d.display_name}`,
  };
}

// ─── User profile ─────────────────────────────────────

export async function userProfile(username: string) {
  const data = await redditFetch(`/user/${username}/about`);
  const d = data.data;
  return {
    name: d.name,
    karma: d.link_karma + d.comment_karma,
    linkKarma: d.link_karma,
    commentKarma: d.comment_karma,
    created: new Date(d.created_utc * 1000).toISOString(),
    verified: d.verified,
    suspended: d.is_suspended || false,
    iconUrl: d.icon_img?.split("?")[0] || null,
  };
}

// ─── User posts ───────────────────────────────────────

export interface UserPostsOptions {
  sort?: "hot" | "new" | "top" | "controversial";
  time?: "hour" | "day" | "week" | "month" | "year" | "all";
  limit?: number;
  type?: "links" | "comments" | "overview";
}

export async function userPosts(username: string, opts: UserPostsOptions = {}) {
  const { sort = "new", time = "all", limit = 25, type = "overview" } = opts;
  const path = type === "overview" ? `/user/${username}` : `/user/${username}/${type === "links" ? "submitted" : "comments"}`;
  const params: Record<string, string> = {
    sort,
    t: time,
    limit: String(Math.min(limit, 100)),
  };

  const data = await redditFetch(path, params);
  return {
    items: data.data.children.map((c: any) => {
      if (c.kind === "t1") return parseComment(c.data);
      return parseListing(c);
    }),
    after: data.data.after,
  };
}

// ─── Duplicates / Cross-posts ─────────────────────────

export async function duplicates(postId: string) {
  const data = await redditFetch(`/duplicates/${postId}`);
  const original = data[0].data.children[0].data;
  const dupes = data[1].data.children.map(parseListing);
  return {
    original: parsePost(original),
    crossPosts: dupes,
    count: dupes.length,
  };
}

// ─── Trending subreddits ──────────────────────────────

export async function popular(opts: FeedOptions = {}) {
  const { limit = 25 } = opts;
  const data = await redditFetch("/subreddits/popular", { limit: String(limit) });
  return data.data.children.map((c: any) => ({
    name: c.data.display_name,
    title: c.data.title,
    subscribers: c.data.subscribers,
    activeUsers: c.data.accounts_active,
    nsfw: c.data.over18,
    description: c.data.public_description?.slice(0, 150),
  }));
}

// ─── Search subreddits ────────────────────────────────

export async function searchSubreddits(query: string, limit = 10) {
  const data = await redditFetch("/subreddits/search", {
    q: query,
    limit: String(limit),
  });
  return data.data.children.map((c: any) => ({
    name: c.data.display_name,
    title: c.data.title,
    subscribers: c.data.subscribers,
    activeUsers: c.data.accounts_active,
    nsfw: c.data.over18,
    description: c.data.public_description?.slice(0, 150),
  }));
}

// ─── Wiki page ────────────────────────────────────────

export async function wiki(subreddit: string, page = "index") {
  const data = await redditFetch(`/r/${subreddit}/wiki/${page}`);
  return {
    content: data.data.content_md,
    revisionDate: data.data.revision_date,
    revisionBy: data.data.revision_by?.data?.name,
  };
}

// ─── Helpers ──────────────────────────────────────────

function parseListing(item: any) {
  const d = item.data;
  return parsePost(d);
}

function parsePost(d: any) {
  return {
    id: d.id,
    title: d.title,
    author: d.author,
    subreddit: d.subreddit,
    score: d.score,
    upvoteRatio: d.upvote_ratio,
    numComments: d.num_comments,
    created: new Date(d.created_utc * 1000).toISOString(),
    url: d.url,
    permalink: `https://reddit.com${d.permalink}`,
    selftext: d.selftext?.slice(0, 2000) || "",
    isSelf: d.is_self,
    isNsfw: d.over_18,
    flair: d.link_flair_text,
    domain: d.domain,
    thumbnail: d.thumbnail !== "self" && d.thumbnail !== "default" ? d.thumbnail : null,
    awards: d.total_awards_received || 0,
    crosspostCount: d.num_crossposts || 0,
    stickied: d.stickied,
  };
}

function parseComment(d: any) {
  return {
    id: d.id,
    author: d.author,
    body: d.body?.slice(0, 2000) || "",
    score: d.score,
    created: new Date(d.created_utc * 1000).toISOString(),
    permalink: d.permalink ? `https://reddit.com${d.permalink}` : null,
    isOp: d.is_submitter || false,
    awards: d.total_awards_received || 0,
    controversiality: d.controversiality || 0,
    depth: d.depth || 0,
    edited: d.edited ? true : false,
  };
}

function flattenComments(children: any[], maxDepth: number, depth = 0): any[] {
  const result: any[] = [];
  for (const child of children) {
    if (child.kind !== "t1") continue;
    const comment = parseComment(child.data);
    comment.depth = depth;
    result.push(comment);
    if (depth < maxDepth && child.data.replies?.data?.children) {
      result.push(...flattenComments(child.data.replies.data.children, maxDepth, depth + 1));
    }
  }
  return result;
}

// ─── Alternative Providers ────────────────────────────

/**
 * PullPush — free historical Reddit archive.
 * No auth. Searches posts and comments across all of Reddit.
 * May be intermittently down. Great for deleted/old content.
 * API: https://api.pullpush.io
 */
export async function pullpushSearch(query: string, opts: { subreddit?: string; size?: number; sort?: "asc" | "desc"; sortType?: "score" | "created_utc"; after?: string; before?: string } = {}) {
  const { subreddit, size = 25, sort = "desc", sortType = "score", after, before } = opts;
  const params: Record<string, string> = {
    q: query,
    size: String(Math.min(size, 100)),
    sort,
    sort_type: sortType,
  };
  if (subreddit) params.subreddit = subreddit;
  if (after) params.after = after;
  if (before) params.before = before;

  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`https://api.pullpush.io/reddit/search/submission/?${qs}`, {
    headers: { "User-Agent": USER_AGENT },
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) throw new Error(`PullPush HTTP ${res.status}: ${res.statusText}`);
  const data = await res.json();

  return {
    posts: (data.data || []).map(parsePullpush),
    provider: "pullpush" as const,
  };
}

export async function pullpushComments(query: string, opts: { subreddit?: string; size?: number; sort?: "asc" | "desc"; sortType?: "score" | "created_utc" } = {}) {
  const { subreddit, size = 25, sort = "desc", sortType = "score" } = opts;
  const params: Record<string, string> = {
    q: query,
    size: String(Math.min(size, 100)),
    sort,
    sort_type: sortType,
  };
  if (subreddit) params.subreddit = subreddit;

  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`https://api.pullpush.io/reddit/search/comment/?${qs}`, {
    headers: { "User-Agent": USER_AGENT },
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) throw new Error(`PullPush HTTP ${res.status}: ${res.statusText}`);
  const data = await res.json();

  return {
    comments: (data.data || []).map(parsePullpushComment),
    provider: "pullpush" as const,
  };
}

/**
 * Arctic Shift — free historical Reddit archive.
 * No auth. Requires subreddit or author filter for search.
 * Great for archived/historical data.
 * API: https://arctic-shift.photon-reddit.com/api
 */
export async function arcticShiftSearch(query: string, opts: { subreddit?: string; author?: string; limit?: number; sort?: "asc" | "desc"; after?: string; before?: string } = {}) {
  const { subreddit, author, limit = 25, sort = "desc", after, before } = opts;
  if (!subreddit && !author) throw new Error("Arctic Shift requires --sub <subreddit> or --author <username>");

  const params: Record<string, string> = {
    query,
    limit: String(Math.min(limit, 100)),
    sort,
  };
  if (subreddit) params.subreddit = subreddit;
  if (author) params.author = author;
  if (after) params.after = after;
  if (before) params.before = before;

  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`https://arctic-shift.photon-reddit.com/api/posts/search?${qs}`, {
    headers: { "User-Agent": USER_AGENT },
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) throw new Error(`Arctic Shift HTTP ${res.status}: ${res.statusText}`);
  const data = await res.json();

  if (data.error) throw new Error(`Arctic Shift: ${data.error}`);

  return {
    posts: (data.data || []).map(parseArcticShift),
    provider: "arctic-shift" as const,
  };
}

export async function arcticShiftComments(query: string, opts: { subreddit?: string; author?: string; limit?: number; sort?: "asc" | "desc" } = {}) {
  const { subreddit, author, limit = 25, sort = "desc" } = opts;
  if (!subreddit && !author) throw new Error("Arctic Shift requires --sub <subreddit> or --author <username>");

  const params: Record<string, string> = {
    query,
    limit: String(Math.min(limit, 100)),
    sort,
  };
  if (subreddit) params.subreddit = subreddit;
  if (author) params.author = author;

  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`https://arctic-shift.photon-reddit.com/api/comments/search?${qs}`, {
    headers: { "User-Agent": USER_AGENT },
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) throw new Error(`Arctic Shift HTTP ${res.status}: ${res.statusText}`);
  const data = await res.json();

  if (data.error) throw new Error(`Arctic Shift: ${data.error}`);

  return {
    comments: (data.data || []).map(parseArcticShiftComment),
    provider: "arctic-shift" as const,
  };
}

// ─── Provider parsers ─────────────────────────────────

function parsePullpush(d: any) {
  return {
    id: d.id,
    title: d.title,
    author: d.author,
    subreddit: d.subreddit,
    score: d.score || 0,
    upvoteRatio: d.upvote_ratio || 0,
    numComments: d.num_comments || 0,
    created: new Date((d.created_utc || 0) * 1000).toISOString(),
    url: d.url,
    permalink: d.permalink ? `https://reddit.com${d.permalink}` : `https://reddit.com/r/${d.subreddit}/comments/${d.id}`,
    selftext: d.selftext?.slice(0, 2000) || "",
    isSelf: d.is_self,
    isNsfw: d.over_18,
    flair: d.link_flair_text,
    domain: d.domain,
    thumbnail: null,
    awards: 0,
    crosspostCount: 0,
    stickied: false,
  };
}

function parsePullpushComment(d: any) {
  return {
    id: d.id,
    author: d.author,
    body: d.body?.slice(0, 2000) || "",
    score: d.score || 0,
    created: new Date((d.created_utc || 0) * 1000).toISOString(),
    permalink: d.permalink ? `https://reddit.com${d.permalink}` : null,
    isOp: false,
    awards: 0,
    controversiality: d.controversiality || 0,
    depth: 0,
    edited: d.edited ? true : false,
    subreddit: d.subreddit,
  };
}

function parseArcticShift(d: any) {
  return {
    id: d.id,
    title: d.title,
    author: d.author,
    subreddit: d.subreddit,
    score: d.score || 0,
    upvoteRatio: d.upvote_ratio || 0,
    numComments: d.num_comments || 0,
    created: new Date((d.created_utc || 0) * 1000).toISOString(),
    url: d.url,
    permalink: d.permalink ? `https://reddit.com${d.permalink}` : `https://reddit.com/r/${d.subreddit}/comments/${d.id}`,
    selftext: d.selftext?.slice(0, 2000) || "",
    isSelf: d.is_self,
    isNsfw: d.over_18,
    flair: d.link_flair_text,
    domain: d.domain,
    thumbnail: null,
    awards: 0,
    crosspostCount: 0,
    stickied: false,
  };
}

function parseArcticShiftComment(d: any) {
  return {
    id: d.id,
    author: d.author,
    body: d.body?.slice(0, 2000) || "",
    score: d.score || 0,
    created: new Date((d.created_utc || 0) * 1000).toISOString(),
    permalink: d.permalink ? `https://reddit.com${d.permalink}` : null,
    isOp: false,
    awards: 0,
    controversiality: d.controversiality || 0,
    depth: 0,
    edited: d.edited ? true : false,
    subreddit: d.subreddit,
  };
}
