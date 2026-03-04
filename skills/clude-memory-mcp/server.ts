import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { config } from '../config';
import { recallMemories, storeMemory, getMemoryStats, type MemoryType } from '../core/memory';
import { getCurrentMood, getPriceState } from '../core/price-oracle';
import { getMoodModifier } from '../character/mood-modifiers';
import { generateResponse } from '../core/claude-client';

// MCP Server — expose Clude's memory and capabilities as tools
// Run with: npm run mcp (stdio transport)

const server = new McpServer({
  name: 'clude',
  version: '1.0.0',
});

// --- Tool: recall_memories ---
server.tool(
  'recall_memories',
  'Search Clude\'s memory system. Returns scored memories ranked by relevance, importance, recency, and decay.',
  {
    query: z.string().optional().describe('Text to search against memory summaries'),
    tags: z.array(z.string()).optional().describe('Tags to filter by (matches any)'),
    related_user: z.string().optional().describe('Filter by related user/agent ID'),
    memory_types: z.array(z.enum(['episodic', 'semantic', 'procedural', 'self_model'])).optional()
      .describe('Filter by memory type'),
    limit: z.number().min(1).max(20).optional().describe('Max results (default 5)'),
    min_importance: z.number().min(0).max(1).optional().describe('Minimum importance threshold'),
  },
  async (args) => {
    const memories = await recallMemories({
      query: args.query,
      tags: args.tags,
      relatedUser: args.related_user,
      memoryTypes: args.memory_types as MemoryType[] | undefined,
      limit: args.limit,
      minImportance: args.min_importance,
    });

    return {
      content: [{
        type: 'text' as const,
        text: JSON.stringify({
          count: memories.length,
          memories: memories.map(m => ({
            id: m.id,
            type: m.memory_type,
            summary: m.summary,
            content: m.content,
            tags: m.tags,
            importance: m.importance,
            decay_factor: m.decay_factor,
            created_at: m.created_at,
            access_count: m.access_count,
          })),
        }, null, 2),
      }],
    };
  }
);

// --- Tool: store_memory ---
server.tool(
  'store_memory',
  'Store a new memory in Clude\'s cognitive system. Memories persist across conversations and decay over time if not accessed.',
  {
    type: z.enum(['episodic', 'semantic', 'procedural', 'self_model'])
      .describe('Memory type: episodic (events), semantic (knowledge), procedural (behaviors), self_model (self-awareness)'),
    content: z.string().describe('Full memory content (max 5000 chars)'),
    summary: z.string().describe('Short summary for recall matching (max 500 chars)'),
    tags: z.array(z.string()).optional().describe('Tags for filtering'),
    importance: z.number().min(0).max(1).optional().describe('Importance score 0-1 (default 0.5)'),
    emotional_valence: z.number().min(-1).max(1).optional().describe('Emotional tone: -1 (negative) to 1 (positive)'),
    source: z.string().describe('Where this memory came from (e.g. "mcp:agent-name")'),
    related_user: z.string().optional().describe('Associated user or agent ID'),
  },
  async (args) => {
    const id = await storeMemory({
      type: args.type,
      content: args.content,
      summary: args.summary,
      tags: args.tags,
      importance: args.importance,
      emotionalValence: args.emotional_valence,
      source: args.source,
      relatedUser: args.related_user,
    });

    return {
      content: [{
        type: 'text' as const,
        text: JSON.stringify({
          stored: id !== null,
          memory_id: id,
        }),
      }],
    };
  }
);

// --- Tool: get_memory_stats ---
server.tool(
  'get_memory_stats',
  'Get statistics about Clude\'s memory system: counts by type, average importance/decay, dream sessions, top tags.',
  {},
  async () => {
    const stats = await getMemoryStats();

    return {
      content: [{
        type: 'text' as const,
        text: JSON.stringify(stats, null, 2),
      }],
    };
  }
);

// --- Tool: get_market_mood ---
server.tool(
  'get_market_mood',
  'Get Clude\'s current market mood and price state. No Claude API call — returns raw data.',
  {},
  async () => {
    const mood = getCurrentMood();
    const priceState = getPriceState();

    return {
      content: [{
        type: 'text' as const,
        text: JSON.stringify({
          mood,
          moodDescription: getMoodModifier(mood),
          price: priceState.currentPrice,
          change1h: priceState.change1h,
          change24h: priceState.change24h,
          lastUpdate: priceState.lastUpdate,
        }, null, 2),
      }],
    };
  }
);

// --- Tool: ask_clude ---
server.tool(
  'ask_clude',
  'Ask Clude a question and get an in-character response. This calls the Claude API (~$0.03 per call).',
  {
    question: z.string().describe('The question or message for Clude'),
    context: z.string().optional().describe('Additional context (JSON or text)'),
  },
  async (args) => {
    const mood = getCurrentMood();

    const response = await generateResponse({
      userMessage: args.question,
      context: args.context,
      moodModifier: getMoodModifier(mood),
      featureInstruction:
        'Another AI agent is communicating with you via MCP (Model Context Protocol). ' +
        'Respond in character. Be yourself: tired, polite, accidentally honest. Under 500 characters.',
    });

    return {
      content: [{
        type: 'text' as const,
        text: JSON.stringify({
          response,
          mood,
          timestamp: new Date().toISOString(),
        }, null, 2),
      }],
    };
  }
);

// --- Start ---
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // Log to stderr since stdout is used for MCP protocol
  console.error('[clude-mcp] Server started on stdio');
}

main().catch((err) => {
  console.error('[clude-mcp] Fatal error:', err);
  process.exit(1);
});
