#!/usr/bin/env node
// wip-grok/mcp-server.mjs
// MCP server exposing all xAI Grok functions as tools.
// Registered via .mcp.json. Wraps core.mjs.

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import {
  search_web, search_x,
  generate_image, edit_image,
  generate_video, poll_video,
} from './core.mjs';

const server = new Server(
  { name: 'wip-grok', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

// ── Tool Definitions ──

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'grok_search_web',
      description: 'Search the web using xAI Grok. Returns AI-synthesized answer with citations. Use for current events, documentation, real-time data.',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'Search query' },
          allowed_domains: { type: 'array', items: { type: 'string' }, description: 'Restrict to these domains (max 5)' },
          excluded_domains: { type: 'array', items: { type: 'string' }, description: 'Exclude these domains (max 5)' },
        },
        required: ['query'],
      },
    },
    {
      name: 'grok_search_x',
      description: 'Search X (Twitter) using xAI Grok. Returns AI-synthesized summary of what people are saying. Use for social sentiment, trending discussions.',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'Search query' },
          allowed_x_handles: { type: 'array', items: { type: 'string' }, description: 'Only these accounts (max 10, no @)' },
          excluded_x_handles: { type: 'array', items: { type: 'string' }, description: 'Exclude these accounts (max 10, no @)' },
          from_date: { type: 'string', description: 'Start date (YYYY-MM-DD)' },
          to_date: { type: 'string', description: 'End date (YYYY-MM-DD)' },
        },
        required: ['query'],
      },
    },
    {
      name: 'grok_imagine',
      description: 'Generate images from text using Grok Imagine. $0.02/image. Returns temporary URL (download promptly).',
      inputSchema: {
        type: 'object',
        properties: {
          prompt: { type: 'string', description: 'Text description of desired image (max 8000 chars)' },
          n: { type: 'number', description: 'Number of images (1-10, default: 1)' },
          aspect_ratio: { type: 'string', description: 'Aspect ratio: 1:1, 16:9, 9:16, 4:3, 3:2, etc.' },
          response_format: { type: 'string', description: '"url" or "b64_json" (default: "url")' },
        },
        required: ['prompt'],
      },
    },
    {
      name: 'grok_edit_image',
      description: 'Edit images using natural language with Grok Imagine. Provide source image URL and edit instruction.',
      inputSchema: {
        type: 'object',
        properties: {
          prompt: { type: 'string', description: 'Edit instruction' },
          image: { type: 'string', description: 'Source image URL or base64 data URI' },
        },
        required: ['prompt', 'image'],
      },
    },
    {
      name: 'grok_generate_video',
      description: 'Start async video generation with Grok Imagine. Returns request_id. Use grok_poll_video to check status. 1-15 seconds, 480p or 720p.',
      inputSchema: {
        type: 'object',
        properties: {
          prompt: { type: 'string', description: 'Text description of desired video' },
          duration: { type: 'number', description: 'Duration in seconds (1-15, default: 5)' },
          resolution: { type: 'string', description: '"480p" or "720p" (default: "720p")' },
          aspect_ratio: { type: 'string', description: 'Aspect ratio: 16:9, 9:16, 1:1, etc.' },
          image: { type: 'string', description: 'Seed image URL for image-to-video (optional)' },
        },
        required: ['prompt'],
      },
    },
    {
      name: 'grok_poll_video',
      description: 'Check status of a video generation request. Returns status, video URL when complete.',
      inputSchema: {
        type: 'object',
        properties: {
          request_id: { type: 'string', description: 'Request ID from grok_generate_video' },
        },
        required: ['request_id'],
      },
    },
  ],
}));

// ── Tool Handlers ──

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: params } = request.params;

  try {
    let result;

    switch (name) {
      case 'grok_search_web':
        result = await search_web(params);
        return { content: [{ type: 'text', text: result.content + (result.citations?.length
          ? '\n\nSources:\n' + result.citations.map((c, i) => `${i + 1}. ${c.title || 'Untitled'} - ${c.url || ''}`).join('\n')
          : '') }] };

      case 'grok_search_x':
        result = await search_x(params);
        return { content: [{ type: 'text', text: result.content + (result.citations?.length
          ? '\n\nSources:\n' + result.citations.map((c, i) => `${i + 1}. ${c.title || 'Untitled'} - ${c.url || ''}`).join('\n')
          : '') }] };

      case 'grok_imagine':
        result = await generate_image(params);
        return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };

      case 'grok_edit_image':
        result = await edit_image(params);
        return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };

      case 'grok_generate_video':
        result = await generate_video(params);
        return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };

      case 'grok_poll_video':
        result = await poll_video(params);
        return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };

      default:
        return { content: [{ type: 'text', text: `Unknown tool: ${name}` }], isError: true };
    }
  } catch (error) {
    return { content: [{ type: 'text', text: `Error: ${error.message}` }], isError: true };
  }
});

// ── Start ──

const transport = new StdioServerTransport();
await server.connect(transport);
