/**
 * wip-x/core.mjs
 * X Platform API wrapper. Sensor (read) + Actuator (write).
 * Built on @xdevplatform/xdk (official X TypeScript SDK).
 */

import { Client } from '@xdevplatform/xdk';
import { resolveAuth, getClientConfig } from './auth.mjs';
import { readFileSync } from 'node:fs';

// Default fields to request for rich post data
const DEFAULT_TWEET_FIELDS = ['created_at', 'author_id', 'conversation_id', 'public_metrics', 'entities'];
const DEFAULT_USER_FIELDS = ['created_at', 'description', 'public_metrics', 'profile_image_url', 'verified'];
const DEFAULT_EXPANSIONS = ['author_id'];

let _client = null;
let _userId = null;

/**
 * Get or create a configured Client instance.
 */
async function getClient() {
  if (_client) return _client;
  const config = await getClientConfig();
  _client = new Client(config);
  return _client;
}

/**
 * Get the authenticated user's ID (needed for bookmarks, etc).
 */
async function getMyUserId() {
  if (_userId) return _userId;
  const client = await getClient();
  const me = await client.users.getMe({ userFields: DEFAULT_USER_FIELDS });
  _userId = me.data?.id;
  if (!_userId) throw new Error('Could not resolve authenticated user ID. Check your credentials.');
  return _userId;
}

// ---------------------------------------------------------------------------
// Sensor (Read)
// ---------------------------------------------------------------------------

/**
 * Fetch a single post by ID or URL.
 * Accepts a tweet ID or a full URL like https://x.com/user/status/123456
 */
export async function fetch_post({ id_or_url, tweetFields, userFields, expansions } = {}) {
  if (!id_or_url) throw new Error('id_or_url is required');

  // Extract ID from URL if needed
  const id = extractTweetId(id_or_url);
  const client = await getClient();

  const result = await client.posts.getById(id, {
    tweetFields: tweetFields || DEFAULT_TWEET_FIELDS,
    userFields: userFields || DEFAULT_USER_FIELDS,
    expansions: expansions || DEFAULT_EXPANSIONS,
  });

  return {
    data: result.data,
    includes: result.includes,
    errors: result.errors,
  };
}

/**
 * Search recent tweets (last 7 days).
 */
export async function search_recent({ query, max_results, start_time, end_time, sort_order } = {}) {
  if (!query) throw new Error('query is required');
  const client = await getClient();

  const opts = {
    tweetFields: DEFAULT_TWEET_FIELDS,
    userFields: DEFAULT_USER_FIELDS,
    expansions: DEFAULT_EXPANSIONS,
  };
  if (max_results) opts.maxResults = max_results;
  if (start_time) opts.startTime = start_time;
  if (end_time) opts.endTime = end_time;
  if (sort_order) opts.sortOrder = sort_order;

  const result = await client.posts.searchRecent(query, opts);

  return {
    data: result.data,
    includes: result.includes,
    meta: result.meta,
    errors: result.errors,
  };
}

/**
 * Get bookmarks for the authenticated user.
 */
export async function get_bookmarks({ max_results, pagination_token } = {}) {
  const client = await getClient();
  const userId = await getMyUserId();

  const opts = {
    tweetFields: DEFAULT_TWEET_FIELDS,
    userFields: DEFAULT_USER_FIELDS,
    expansions: DEFAULT_EXPANSIONS,
  };
  if (max_results) opts.maxResults = max_results;
  if (pagination_token) opts.paginationToken = pagination_token;

  const result = await client.users.getBookmarks(userId, opts);

  return {
    data: result.data,
    includes: result.includes,
    meta: result.meta,
    errors: result.errors,
  };
}

/**
 * Get user info by username or ID.
 */
export async function get_user({ username_or_id } = {}) {
  if (!username_or_id) throw new Error('username_or_id is required');
  const client = await getClient();

  // If it starts with a digit, treat as ID
  if (/^\d+$/.test(username_or_id)) {
    const result = await client.users.getById(username_or_id, {
      userFields: DEFAULT_USER_FIELDS,
    });
    return { data: result.data, errors: result.errors };
  }

  // Strip @ if present
  const username = username_or_id.replace(/^@/, '');
  const result = await client.users.getByUsername(username, {
    userFields: DEFAULT_USER_FIELDS,
  });
  return { data: result.data, errors: result.errors };
}

/**
 * Get the authenticated user's profile.
 */
export async function get_me() {
  const client = await getClient();
  const result = await client.users.getMe({
    userFields: DEFAULT_USER_FIELDS,
  });
  return { data: result.data, errors: result.errors };
}

// ---------------------------------------------------------------------------
// Actuator (Write)
// ---------------------------------------------------------------------------

/**
 * Post a tweet.
 */
export async function post_tweet({ text, reply_to, media_ids, quote_tweet_id } = {}) {
  if (!text) throw new Error('text is required');
  const client = await getClient();

  const body = { text };
  if (reply_to) body.reply = { inReplyToTweetId: reply_to };
  if (media_ids && media_ids.length > 0) body.media = { mediaIds: media_ids };
  if (quote_tweet_id) body.quoteTweetId = quote_tweet_id;

  const result = await client.posts.create(body);
  return { data: result.data, errors: result.errors };
}

/**
 * Delete a tweet.
 */
export async function delete_tweet({ id } = {}) {
  if (!id) throw new Error('id is required');
  const client = await getClient();
  const result = await client.posts.delete(id);
  return { data: result.data, errors: result.errors };
}

/**
 * Bookmark a post.
 */
export async function bookmark_post({ tweet_id } = {}) {
  if (!tweet_id) throw new Error('tweet_id is required');
  const client = await getClient();
  const userId = await getMyUserId();
  const result = await client.users.createBookmark(userId, { tweetId: tweet_id });
  return { data: result.data, errors: result.errors };
}

/**
 * Remove a bookmark.
 */
export async function unbookmark_post({ tweet_id } = {}) {
  if (!tweet_id) throw new Error('tweet_id is required');
  const client = await getClient();
  const userId = await getMyUserId();
  const result = await client.users.deleteBookmark(userId, tweet_id);
  return { data: result.data, errors: result.errors };
}

/**
 * Upload media (image, video, gif).
 * The X API v2 media upload takes base64-encoded data.
 */
export async function upload_media({ file_path, media_data, media_type, alt_text } = {}) {
  if (!file_path && !media_data) throw new Error('file_path or media_data is required');
  const client = await getClient();

  let data = media_data;
  if (file_path && !data) {
    const buffer = readFileSync(file_path);
    data = buffer.toString('base64');
  }

  // Detect media type from extension if not provided
  if (!media_type && file_path) {
    const ext = file_path.split('.').pop().toLowerCase();
    const types = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', mp4: 'video/mp4', webp: 'image/webp' };
    media_type = types[ext] || 'application/octet-stream';
  }

  const body = {
    mediaData: data,
    mediaType: media_type,
  };

  const result = await client.media.upload({ body });

  // Set alt text if provided and we got a media ID
  if (alt_text && result.data?.id) {
    try {
      // Alt text would need a separate metadata endpoint... SDK may not expose it yet
      // For now we return without alt text
    } catch { /* ignore */ }
  }

  return { data: result.data, errors: result.errors };
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

/**
 * Extract tweet ID from a URL or return as-is if already an ID.
 * Handles: https://x.com/user/status/123, https://twitter.com/user/status/123, plain 123
 */
function extractTweetId(input) {
  if (/^\d+$/.test(input)) return input;
  const match = input.match(/(?:twitter\.com|x\.com)\/\w+\/status\/(\d+)/);
  if (match) return match[1];
  throw new Error(`Cannot extract tweet ID from: ${input}`);
}

/**
 * Reset the cached client (useful for testing or credential rotation).
 */
export function resetClient() {
  _client = null;
  _userId = null;
}
