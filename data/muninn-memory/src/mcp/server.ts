/**
 * OpenClaw Memory System - MCP Server
 * Provides memory tools to OpenClaw agents
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { MemoryStore, Memory, MemoryType, Procedure } from '../storage/index.js';
import { extract, routeContent } from '../extractors/index.js';
import { consolidate } from '../consolidation/index.js';

// Initialize store
const store = new MemoryStore();

// Server instance
const server = new Server(
  {
    name: 'openclaw-memory',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool definitions
const tools = [
  {
    name: 'memory_remember',
    description: 'Store a memory with auto-extraction of entities and topics. Automatically classifies as episodic, semantic, or procedural.',
    inputSchema: {
      type: 'object',
      properties: {
        content: {
          type: 'string',
          description: 'The content to remember'
        },
        type: {
          type: 'string',
          enum: ['episodic', 'semantic', 'procedural'],
          description: 'Memory type (auto-detected if not specified)'
        },
        title: {
          type: 'string',
          description: 'Optional title for the memory'
        },
        context: {
          type: 'string',
          description: 'Additional context for routing'
        }
      },
      required: ['content']
    }
  },
  {
    name: 'memory_recall',
    description: 'Retrieve relevant memories via semantic search across all memory types.',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query'
        },
        types: {
          type: 'array',
          items: { type: 'string', enum: ['episodic', 'semantic', 'procedural'] },
          description: 'Filter by memory types'
        },
        entities: {
          type: 'array',
          items: { type: 'string' },
          description: 'Filter by entities'
        },
        limit: {
          type: 'number',
          description: 'Maximum results to return',
          default: 10
        }
      },
      required: ['query']
    }
  },
  {
    name: 'memory_briefing',
    description: 'Get a structured session briefing with key facts, commitments, and recent activity.',
    inputSchema: {
      type: 'object',
      properties: {
        context: {
          type: 'string',
          description: 'Context for the briefing (e.g., "morning standup")'
        },
        limit: {
          type: 'number',
          description: 'Number of recent memories to include',
          default: 10
        }
      }
    }
  },
  {
    name: 'memory_stats',
    description: 'Get vault statistics - memory counts by type, entity count, and graph edges.',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'memory_entities',
    description: 'List all tracked entities with memory counts.',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'memory_forget',
    description: 'Forget a memory (soft delete by default, hard delete with force flag).',
    inputSchema: {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'Memory ID to forget'
        },
        hard: {
          type: 'boolean',
          description: 'Hard delete (permanent) vs soft delete',
          default: false
        }
      },
      required: ['id']
    }
  },
  {
    name: 'memory_procedure_create',
    description: 'Create a new procedure/workflow with steps.',
    inputSchema: {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          description: 'Procedure title'
        },
        description: {
          type: 'string',
          description: 'Optional description'
        },
        steps: {
          type: 'array',
          items: { type: 'string' },
          description: 'Array of step descriptions'
        }
      },
      required: ['title', 'steps']
    }
  },
  {
    name: 'memory_procedure_feedback',
    description: 'Record success or failure for a procedure. Failures auto-create new versions.',
    inputSchema: {
      type: 'object',
      properties: {
        procedureId: {
          type: 'string',
          description: 'Procedure ID'
        },
        success: {
          type: 'boolean',
          description: 'Whether the procedure succeeded'
        },
        failedAtStep: {
          type: 'number',
          description: 'Step number that failed (if any)'
        },
        context: {
          type: 'string',
          description: 'Additional context about what happened'
        }
      },
      required: ['procedureId', 'success']
    }
  },
  {
    name: 'memory_procedure_list',
    description: 'List all procedures.',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'memory_connect',
    description: 'Create a relationship between two memories in the knowledge graph.',
    inputSchema: {
      type: 'object',
      properties: {
        sourceId: {
          type: 'string',
          description: 'Source memory ID'
        },
        targetId: {
          type: 'string',
          description: 'Target memory ID'
        },
        relationship: {
          type: 'string',
          description: 'Relationship type (e.g., "related_to", "causes", "depends_on")'
        }
      },
      required: ['sourceId', 'targetId', 'relationship']
    }
  },
  {
    name: 'memory_neighbors',
    description: 'Get connected memories (graph neighbors) for a given memory.',
    inputSchema: {
      type: 'object',
      properties: {
        memoryId: {
          type: 'string',
          description: 'Memory ID'
        },
        depth: {
          type: 'number',
          description: 'Graph traversal depth',
          default: 1
        }
      },
      required: ['memoryId']
    }
  },
  {
    name: 'memory_consolidate',
    description: 'Run memory consolidation - distills episodes into facts, discovers entities, finds contradictions.',
    inputSchema: {
      type: 'object',
      properties: {
        batchSize: {
          type: 'number',
          description: 'Number of memories to process',
          default: 10
        }
      }
    }
  }
];

// Handle tool calls
async function handleToolCall(name: string, args: any): Promise<any> {
  switch (name) {
    case 'memory_remember': {
      const { content, type, title, context } = args;
      
      // Auto-route if no type specified
      let memoryType: MemoryType = type || 'semantic';
      if (!type) {
        const routing = await routeContent(content, context);
        if (routing.episodic) memoryType = 'episodic';
        else if (routing.procedural) memoryType = 'procedural';
        else memoryType = 'semantic';
      }
      
      const result = await store.remember(content, memoryType, { title });
      return {
        success: true,
        id: result.id,
        type: result.type,
        message: `Memory stored as ${result.type}`
      };
    }
    
    case 'memory_recall': {
      const { query, types, entities, limit } = args;
      const memories = await store.recall(query, { types, entities, limit });
      return {
        count: memories.length,
        memories: memories.map(m => ({
          id: m.id,
          type: m.type,
          content: m.content,
          title: m.title,
          summary: m.summary,
          entities: m.entities,
          topics: m.topics,
          salience: m.salience,
          created_at: m.created_at
        }))
      };
    }
    
    case 'memory_briefing': {
      const { context, limit } = args;
      const recentMemories = await store.recall(context || '', { limit: limit || 10 });
      
      // Separate by type
      const keyFacts = recentMemories.filter(m => m.type === 'semantic');
      const recentActivity = recentMemories.filter(m => m.type === 'episodic');
      const procedures = recentMemories.filter(m => m.type === 'procedural');
      
      // Generate summary
      const summary = `Session context: ${context || 'general'}. Found ${keyFacts.length} key facts, ${recentActivity.length} recent events, ${procedures.length} relevant procedures.`;
      
      return {
        summary,
        keyFacts: keyFacts.map(f => ({ content: f.content, salience: f.salience })),
        recentActivity: recentActivity.map(a => ({ content: a.content, timestamp: a.created_at })),
        relevantProcedures: procedures.map(p => ({ title: p.title, summary: p.summary }))
      };
    }
    
    case 'memory_stats': {
      return store.getStats();
    }
    
    case 'memory_entities': {
      const entities = store.getEntities();
      return { count: entities.length, entities };
    }
    
    case 'memory_forget': {
      const { id, hard } = args;
      const deleted = store.forget(id, hard);
      return { success: deleted, id, hard };
    }
    
    case 'memory_procedure_create': {
      const { title, description, steps } = args;
      const procedure = await store.createProcedure(title, steps, description);
      return {
        success: true,
        id: procedure.id,
        version: procedure.version,
        message: `Procedure "${title}" created (v${procedure.version})`
      };
    }
    
    case 'memory_procedure_feedback': {
      const { procedureId, success, failedAtStep, context } = args;
      const procedure = await store.procedureFeedback(procedureId, success, failedAtStep, context);
      return {
        success: true,
        id: procedure.id,
        version: procedure.version,
        success_count: procedure.success_count,
        failure_count: procedure.failure_count,
        is_reliable: procedure.is_reliable,
        message: success 
          ? `Success recorded. Total: ${procedure.success_count}. ${procedure.is_reliable ? 'Promoted to reliable!' : ''}`
          : `Failure recorded. New version v${procedure.version} created.`
      };
    }
    
    case 'memory_procedure_list': {
      const procedures = store.getAllProcedures();
      return {
        count: procedures.length,
        procedures: procedures.map(p => ({
          id: p.id,
          title: p.title,
          description: p.description,
          version: p.version,
          success_count: p.success_count,
          failure_count: p.failure_count,
          is_reliable: p.is_reliable,
          steps: p.steps.map(s => s.description),
          created_at: p.created_at,
          updated_at: p.updated_at
        }))
      };
    }
    
    case 'memory_connect': {
      const { sourceId, targetId, relationship } = args;
      const edge = store.connect(sourceId, targetId, relationship);
      return { success: true, edge };
    }
    
    case 'memory_neighbors': {
      const { memoryId, depth } = args;
      const neighbors = store.getNeighbors(memoryId, depth);
      return {
        count: neighbors.length,
        memories: neighbors.map(m => ({
          id: m.id,
          type: m.type,
          content: m.content,
          title: m.title
        }))
      };
    }
    
    case 'memory_consolidate': {
      const { batchSize } = args;
      const result = await consolidate(store, { batchSize });
      return {
        success: true,
        ...result
      };
    }
    
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// Register handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    const result = await handleToolCall(name, args);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: error.message }, null, 2)
        }
      ],
      isError: true
    };
  }
});

// Start server
async function main() {
  console.log('🧠 OpenClaw Memory System v1 - MCP Server');
  console.log('Starting server...');
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.log('✅ MCP Server ready');
}

main().catch(console.error);
