#!/usr/bin/env node

/**
 * wip-x/mcp-server.mjs
 * MCP server exposing X Platform API as tools.
 * 7 tools: x_fetch_post, x_search_recent, x_get_bookmarks, x_get_user,
 *          x_post_tweet, x_delete_tweet, x_upload_media
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  fetch_post,
  search_recent,
  get_bookmarks,
  get_user,
  post_tweet,
  delete_tweet,
  upload_media,
} from './core.mjs';

const server = new Server(
  { name: 'wip-x', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

const TOOLS = [
  {
    name: 'x_fetch_post',
    description: 'Fetch a single X/Twitter post by ID or URL. Returns full post data with author info.',
    inputSchema: {
      type: 'object',
      properties: {
        id_or_url: { type: 'string', description: 'Tweet ID or full URL (e.g. https://x.com/user/status/123)' },
      },
      required: ['id_or_url'],
    },
  },
  {
    name: 'x_search_recent',
    description: 'Search recent tweets (last 7 days). Uses X API v2 search endpoint.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query (supports X search operators)' },
        max_results: { type: 'number', description: 'Max results (10-100, default 10)' },
        start_time: { type: 'string', description: 'Start time (ISO 8601)' },
        end_time: { type: 'string', description: 'End time (ISO 8601)' },
      },
      required: ['query'],
    },
  },
  {
    name: 'x_get_bookmarks',
    description: 'Get bookmarked posts for the authenticated user.',
    inputSchema: {
      type: 'object',
      properties: {
        max_results: { type: 'number', description: 'Max results (default 20)' },
      },
    },
  },
  {
    name: 'x_get_user',
    description: 'Get user profile by username or ID.',
    inputSchema: {
      type: 'object',
      properties: {
        username_or_id: { type: 'string', description: 'Username (with or without @) or numeric user ID' },
      },
      required: ['username_or_id'],
    },
  },
  {
    name: 'x_post_tweet',
    description: 'Post a new tweet. Requires OAuth credentials (not just bearer token).',
    inputSchema: {
      type: 'object',
      properties: {
        text: { type: 'string', description: 'Tweet text (max 280 characters)' },
        reply_to: { type: 'string', description: 'Tweet ID to reply to' },
        quote_tweet_id: { type: 'string', description: 'Tweet ID to quote' },
        media_ids: { type: 'array', items: { type: 'string' }, description: 'Media IDs to attach (upload first with x_upload_media)' },
      },
      required: ['text'],
    },
  },
  {
    name: 'x_delete_tweet',
    description: 'Delete a tweet by ID. Requires OAuth credentials.',
    inputSchema: {
      type: 'object',
      properties: {
        id: { type: 'string', description: 'Tweet ID to delete' },
      },
      required: ['id'],
    },
  },
  {
    name: 'x_upload_media',
    description: 'Upload media (image/video/gif) for use in tweets. Returns a media ID.',
    inputSchema: {
      type: 'object',
      properties: {
        file_path: { type: 'string', description: 'Path to the file to upload' },
        media_type: { type: 'string', description: 'MIME type (auto-detected from extension if omitted)' },
      },
      required: ['file_path'],
    },
  },
];

server.setRequestHandler({ method: 'tools/list' }, async () => ({
  tools: TOOLS,
}));

server.setRequestHandler({ method: 'tools/call' }, async (request) => {
  const { name, arguments: params } = request.params;

  try {
    let result;
    switch (name) {
      case 'x_fetch_post':
        result = await fetch_post(params);
        break;
      case 'x_search_recent':
        result = await search_recent(params);
        break;
      case 'x_get_bookmarks':
        result = await get_bookmarks(params);
        break;
      case 'x_get_user':
        result = await get_user(params);
        break;
      case 'x_post_tweet':
        result = await post_tweet(params);
        break;
      case 'x_delete_tweet':
        result = await delete_tweet(params);
        break;
      case 'x_upload_media':
        result = await upload_media(params);
        break;
      default:
        return {
          content: [{ type: 'text', text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }

    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
    };
  } catch (err) {
    return {
      content: [{ type: 'text', text: `Error: ${err.message}` }],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
