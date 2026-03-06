#!/usr/bin/env node

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { x402Client, wrapFetchWithPayment } from '@x402/fetch';
import { registerExactEvmScheme } from '@x402/evm/exact/client';
import { toClientEvmSigner } from '@x402/evm';
import { privateKeyToAccount } from 'viem/accounts';
import { createPublicClient, http } from 'viem';
import { base } from 'viem/chains';
import { z } from 'zod';
import 'dotenv/config';

// ── Config ────────────────────────────────────────────────────────────────────

const API_BASE = process.env.API_BASE ?? 'https://x402.twit.sh';
const privateKey = process.env.WALLET_PRIVATE_KEY as `0x${string}` | undefined;

if (!privateKey) {
  process.stderr.write('Error: WALLET_PRIVATE_KEY environment variable is required.\n');
  process.stderr.write('Fund a wallet with a few USDC on Base and set its private key.\n');
  process.exit(1);
}

// ── x402 payment client ───────────────────────────────────────────────────────

const account = privateKeyToAccount(privateKey);
const publicClient = createPublicClient({ chain: base, transport: http() });
const signer = toClientEvmSigner(account, publicClient);
const client = new x402Client();
registerExactEvmScheme(client, { signer });
const fetchWithPayment = wrapFetchWithPayment(fetch, client);

async function call(path: string): Promise<unknown> {
  const res = await fetchWithPayment(`${API_BASE}${path}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

// ── MCP server ────────────────────────────────────────────────────────────────

const server = new McpServer({
  name: 'twit-mcp',
  version: '1.0.0',
  description: 'Real-time X/Twitter data via x402 micropayments. Pay per request in USDC on Base. No API keys required.',
});

// ── Users ─────────────────────────────────────────────────────────────────────

server.tool(
  'get_user_by_username',
  'Retrieve a Twitter/X user profile by username. Returns id, name, bio, follower count, verified status, and more.',
  {
    username: z.string().describe('Twitter/X username without the @ symbol (e.g. "elonmusk")'),
  },
  async ({ username }) => {
    const data = await call(`/users/by/username?username=${encodeURIComponent(username)}`);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

server.tool(
  'get_user_by_id',
  'Retrieve a Twitter/X user profile by their numeric ID.',
  {
    id: z.string().describe('Numeric Twitter/X user ID (e.g. "44196397")'),
  },
  async ({ id }) => {
    const data = await call(`/users/by/id?id=${id}`);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

server.tool(
  'search_users',
  'Search for Twitter/X users by keyword. Returns up to 20 users per page. Use next_token to paginate.',
  {
    query: z.string().describe('Search query (e.g. "bitcoin developer")'),
    next_token: z.string().optional().describe('Pagination cursor from a previous response meta.next_token'),
  },
  async ({ query, next_token }) => {
    let path = `/users/search?query=${encodeURIComponent(query)}`;
    if (next_token) path += `&next_token=${encodeURIComponent(next_token)}`;
    const data = await call(path);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

server.tool(
  'get_user_followers',
  'Retrieve the followers of a Twitter/X user. Returns ~50 users per page. Use next_token to paginate.',
  {
    id: z.string().describe('Numeric Twitter/X user ID'),
    next_token: z.string().optional().describe('Pagination cursor from a previous response meta.next_token'),
  },
  async ({ id, next_token }) => {
    let path = `/users/followers?id=${id}`;
    if (next_token) path += `&next_token=${encodeURIComponent(next_token)}`;
    const data = await call(path);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

server.tool(
  'get_user_following',
  'Retrieve the accounts a Twitter/X user follows. Returns ~50 users per page. Use next_token to paginate.',
  {
    id: z.string().describe('Numeric Twitter/X user ID'),
    next_token: z.string().optional().describe('Pagination cursor from a previous response meta.next_token'),
  },
  async ({ id, next_token }) => {
    let path = `/users/following?id=${id}`;
    if (next_token) path += `&next_token=${encodeURIComponent(next_token)}`;
    const data = await call(path);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

server.tool(
  'get_users',
  'Retrieve multiple Twitter/X user profiles in a single request (max 50 IDs).',
  {
    ids: z.string().describe('Comma-separated numeric Twitter/X user IDs (max 50, e.g. "44196397,12,783214")'),
  },
  async ({ ids }) => {
    const data = await call(`/users?ids=${encodeURIComponent(ids)}`);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

// ── Tweets ────────────────────────────────────────────────────────────────────

server.tool(
  'get_tweet_by_id',
  'Retrieve a single tweet/post by its ID. Includes author info, text, metrics, and metadata.',
  {
    id: z.string().describe('Numeric tweet ID (e.g. "1110302988")'),
  },
  async ({ id }) => {
    const data = await call(`/tweets/by/id?id=${id}`);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

server.tool(
  'get_user_tweets',
  "Retrieve a user's recent tweets/posts. Returns ~20 tweets per page. Use next_token to paginate.",
  {
    username: z.string().describe('Twitter/X username without the @ symbol'),
    next_token: z.string().optional().describe('Pagination cursor from a previous response meta.next_token'),
  },
  async ({ username, next_token }) => {
    let path = `/tweets/user?username=${encodeURIComponent(username)}`;
    if (next_token) path += `&next_token=${encodeURIComponent(next_token)}`;
    const data = await call(path);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

server.tool(
  'search_tweets',
  'Search the full Twitter/X archive with advanced filters. Returns ~20 tweets per page. At least one filter is required.',
  {
    words:      z.string().optional().describe('All of these words must appear in the tweet'),
    phrase:     z.string().optional().describe('This exact phrase must appear'),
    anyWords:   z.string().optional().describe('Any of these words (space-separated)'),
    noneWords:  z.string().optional().describe('None of these words (space-separated)'),
    hashtags:   z.string().optional().describe('These hashtags (without #, space-separated)'),
    from:       z.string().optional().describe('Tweets from this username (without @)'),
    to:         z.string().optional().describe('Tweets replying to this username (without @)'),
    mentioning: z.string().optional().describe('Tweets mentioning this username (without @)'),
    minReplies: z.number().optional().describe('Minimum reply count'),
    minLikes:   z.number().optional().describe('Minimum like count'),
    minReposts: z.number().optional().describe('Minimum retweet count'),
    since:      z.string().optional().describe('Start date inclusive (YYYY-MM-DD)'),
    until:      z.string().optional().describe('End date exclusive (YYYY-MM-DD)'),
    next_token: z.string().optional().describe('Pagination cursor from a previous response meta.next_token'),
  },
  async (params) => {
    const qs = Object.entries(params)
      .filter(([, v]) => v !== undefined)
      .map(([k, v]) => `${k}=${encodeURIComponent(String(v))}`)
      .join('&');
    const data = await call(`/tweets/search?${qs}`);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

server.tool(
  'get_tweets',
  'Retrieve multiple tweets/posts by their IDs in a single request (max 50 IDs).',
  {
    ids: z.string().describe('Comma-separated tweet IDs (max 50, e.g. "1110302988,1234567890")'),
  },
  async ({ ids }) => {
    const data = await call(`/tweets?ids=${encodeURIComponent(ids)}`);
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  },
);

// ── Start ─────────────────────────────────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);
