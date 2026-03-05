#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { hello } from './core.mjs';

const server = new Server(
  { name: 'my-tool', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler({ method: 'tools/list' }, async () => ({
  tools: [{
    name: 'hello',
    description: 'Say hello',
    inputSchema: {
      type: 'object',
      properties: { name: { type: 'string' } },
    },
  }],
}));

server.setRequestHandler({ method: 'tools/call' }, async (req) => ({
  content: [{ type: 'text', text: hello(req.params.arguments) }],
}));

const transport = new StdioServerTransport();
await server.connect(transport);
