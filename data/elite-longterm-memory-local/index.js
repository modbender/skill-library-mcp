/**
 * Elite Longterm Memory - OpenClaw Plugin
 * Local edition with Ollama embeddings
 */

const { MemoryManager } = require('./lib/memory');
const path = require('path');
const fs = require('fs').promises;

const plugin = {
  id: 'elite-longterm-memory-local',
  name: 'Elite Longterm Memory (Local)',
  description: 'LanceDB + Ollama local embedding memory system',
  kind: 'memory',

  configSchema: {
    type: 'object',
    properties: {
      ollamaUrl: { type: 'string', default: 'http://localhost:11434' },
      embeddingModel: { type: 'string', default: 'nomic-embed-text' },
      dbPath: { type: 'string', default: './memory/vectors' },
      autoRecall: { type: 'boolean', default: true },
      autoCapture: { type: 'boolean', default: false }
    }
  },

  register(api) {
    const cfg = api.pluginConfig || {};
    const resolvedDbPath = api.resolvePath(cfg.dbPath || './memory/vectors');
    
    const memory = new MemoryManager({
      dbPath: resolvedDbPath,
      ollamaUrl: cfg.ollamaUrl || 'http://localhost:11434',
      embeddingModel: cfg.embeddingModel || 'nomic-embed-text'
    });

    api.logger.info(`elite-ltm: plugin registered (db: ${resolvedDbPath})`);

    // Register tools
    api.registerTool({
      name: 'memory_recall',
      label: 'Memory Recall',
      description: 'Search through long-term memories using local vector search',
      parameters: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'Search query' },
          limit: { type: 'number', description: 'Max results (default: 5)' }
        },
        required: ['query']
      },
      async execute(_toolCallId, params) {
        const { query, limit = 5 } = params;
        await memory.init();
        
        const results = await memory.search(query, limit, 0.3);
        
        if (results.length === 0) {
          return {
            content: [{ type: 'text', text: 'No relevant memories found.' }],
            details: { count: 0 }
          };
        }

        const text = results
          .map((r, i) => `${i + 1}. [${r.entry.category}] ${r.entry.text} (${(r.score * 100).toFixed(0)}%)`)
          .join('\n');

        return {
          content: [{ type: 'text', text: `Found ${results.length} memories:\n\n${text}` }],
          details: { 
            count: results.length, 
            memories: results.map(r => ({
              id: r.entry.id,
              text: r.entry.text,
              category: r.entry.category,
              importance: r.entry.importance,
              score: r.score
            }))
          }
        };
      }
    }, { name: 'memory_recall' });

    api.registerTool({
      name: 'memory_store',
      label: 'Memory Store',
      description: 'Save important information in long-term memory',
      parameters: {
        type: 'object',
        properties: {
          text: { type: 'string', description: 'Information to remember' },
          importance: { type: 'number', description: 'Importance 0-1 (default: 0.7)' },
          category: { type: 'string', description: 'Category: preference, decision, fact, entity, other' }
        },
        required: ['text']
      },
      async execute(_toolCallId, params) {
        const { text, importance = 0.7, category = 'other' } = params;
        await memory.init();
        
        const result = await memory.store(text, { importance, category });
        
        if (result.duplicate) {
          return {
            content: [{ type: 'text', text: `Similar memory already exists.` }],
            details: { action: 'duplicate', existingId: result.id }
          };
        }

        return {
          content: [{ type: 'text', text: `Stored: "${text.slice(0, 100)}..."` }],
          details: { action: 'created', id: result.id }
        };
      }
    }, { name: 'memory_store' });

    api.registerTool({
      name: 'memory_forget',
      label: 'Memory Forget',
      description: 'Delete specific memories',
      parameters: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'Search to find memory' },
          memoryId: { type: 'string', description: 'Specific memory ID' }
        }
      },
      async execute(_toolCallId, params) {
        const { query, memoryId } = params;
        await memory.init();

        if (memoryId) {
          await memory.delete(memoryId);
          return {
            content: [{ type: 'text', text: `Memory ${memoryId} forgotten.` }],
            details: { action: 'deleted', id: memoryId }
          };
        }

        if (query) {
          const results = await memory.search(query, 5, 0.7);
          
          if (results.length === 0) {
            return {
              content: [{ type: 'text', text: 'No matching memories found.' }],
              details: { found: 0 }
            };
          }

          if (results.length === 1 && results[0].score > 0.9) {
            await memory.delete(results[0].entry.id);
            return {
              content: [{ type: 'text', text: `Forgotten: "${results[0].entry.text}"` }],
              details: { action: 'deleted', id: results[0].entry.id }
            };
          }

          const list = results
            .map(r => `- [${r.entry.id.slice(0, 8)}] ${r.entry.text.slice(0, 60)}...`)
            .join('\n');

          return {
            content: [{ type: 'text', text: `Found ${results.length} candidates. Specify memoryId:\n${list}` }],
            details: { action: 'candidates', candidates: results.map(r => ({
              id: r.entry.id,
              text: r.entry.text,
              score: r.score
            })) }
          };
        }

        return {
          content: [{ type: 'text', text: 'Provide query or memoryId.' }],
          details: { error: 'missing_param' }
        };
      }
    }, { name: 'memory_forget' });

    // Auto-recall: inject relevant memories before agent starts
    if (cfg.autoRecall !== false) {
      api.on('before_agent_start', async (event) => {
        if (!event.prompt || event.prompt.length < 5) return;
        
        try {
          await memory.init();
          const results = await memory.search(event.prompt, 3, 0.3);
          
          if (results.length === 0) return;

          const memoryContext = results
            .map(r => `- [${r.entry.category}] ${r.entry.text}`)
            .join('\n');

          api.logger.info?.(`elite-ltm: injecting ${results.length} memories`);

          return {
            prependContext: `<relevant-memories>\nThe following memories may be relevant:\n${memoryContext}\n</relevant-memories>`
          };
        } catch (err) {
          api.logger.warn(`elite-ltm: recall failed: ${String(err)}`);
        }
      });
    }

    // Register service
    api.registerService({
      id: 'elite-longterm-memory-local',
      start: () => {
        api.logger.info(`elite-ltm: started (model: ${cfg.embeddingModel || 'nomic-embed-text'})`);
      },
      stop: () => {
        api.logger.info('elite-ltm: stopped');
      }
    });
  }
};

module.exports = plugin;
