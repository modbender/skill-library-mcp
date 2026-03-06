/**
 * Memory Tools
 *
 * The six agent-controlled memory operations:
 * - memory_store: Save new memories
 * - memory_update: Modify existing memories
 * - memory_forget: Delete memories
 * - memory_search: Semantic search
 * - memory_summarize: Get topic summary
 * - memory_list: Browse all memories
 */

import { Type } from '@sinclair/typebox';
import type { MemoryStore } from './store.js';
import { MEMORY_CATEGORIES, type MemoryCategory } from './types.js';

// Type helper for string enums (OpenClaw compatible)
function stringEnum<T extends string>(values: readonly T[]) {
  return Type.Unsafe<T>({ type: 'string', enum: [...values] });
}

export function createMemoryTools(store: MemoryStore) {
  return {
    // ═══════════════════════════════════════════════════════════════════════
    // STORE - Add new memory
    // ═══════════════════════════════════════════════════════════════════════
    memory_store: {
      name: 'memory_store',
      label: 'Memory Store',
      description: `Store a new memory about the user. Use when you learn something worth remembering long-term.

WHEN to use:
- User shares personal info (name, birthday, preferences)
- User gives standing instructions ("always summarize emails")
- User mentions relationships ("my wife Sarah")
- User states preferences ("I prefer bullet points")
- Important decisions are made

WHEN NOT to use:
- Trivial conversation (weather, greetings)
- Already stored (use memory_update instead)
- Temporary context (use conversation history)`,

      parameters: Type.Object({
        content: Type.String({
          description: 'The fact/preference/info to remember. Be specific and atomic.'
        }),
        category: stringEnum(MEMORY_CATEGORIES),
        confidence: Type.Optional(Type.Number({
          minimum: 0,
          maximum: 1,
          description: 'How confident this is accurate. 1.0 = explicitly stated, 0.5 = inferred'
        })),
        importance: Type.Optional(Type.Number({
          minimum: 0,
          maximum: 1,
          description: 'How important is this. 1.0 = critical instruction, 0.3 = nice to know'
        })),
        decayDays: Type.Optional(Type.Number({
          description: 'Days until memory becomes stale. Omit for permanent. Events should have decay.'
        })),
        tags: Type.Optional(Type.Array(Type.String(), {
          description: 'Tags for categorization and retrieval'
        })),
        supersedes: Type.Optional(Type.String({
          description: 'ID of memory this replaces (will delete the old one)'
        })),
      }),

      async execute(
        _toolCallId: string,
        params: {
          content: string;
          category: MemoryCategory;
          confidence?: number;
          importance?: number;
          decayDays?: number;
          tags?: string[];
          supersedes?: string;
        },
        ctx?: { messageChannel?: string; }
      ) {
        // Handle explicit supersedes first (user knows what to replace)
        let supersededId: string | undefined = params.supersedes;
        if (params.supersedes) {
          await store.delete(params.supersedes, 'superseded by new memory');
        }

        // Check for similar/conflicting memories
        // Use low threshold (0.4) to catch potential conflicts, then decide based on score
        const similar = await store.findDuplicates(params.content, 0.4);

        if (similar.length > 0 && !params.supersedes) {
          const match = similar[0];
          const isHighSimilarity = match.score > 0.92;
          const isSameCategory = match.memory.category === params.category;

          // High similarity = likely duplicate (exact same info)
          if (isHighSimilarity) {
            return {
              content: [{
                type: 'text' as const,
                text: `Similar memory already exists: "${match.memory.content}" (${(match.score * 100).toFixed(0)}% match). Use memory_update to modify it, or pass supersedes="${match.memory.id}" to replace it.`
              }],
              details: {
                action: 'duplicate',
                existingId: match.memory.id,
                existingContent: match.memory.content,
                similarity: match.score,
              },
            };
          }
          // Same category + moderate similarity = conflicting info -> AUTO-REPLACE
          // This handles corrections like "favorite color is blue" -> "favorite color is purple"
          else if (isSameCategory && match.score > 0.5) {
            await store.delete(match.memory.id, 'auto-superseded by updated info');
            supersededId = match.memory.id;
          }
        }

        const memory = await store.create({
          content: params.content,
          category: params.category,
          confidence: params.confidence ?? 0.8,
          importance: params.importance ?? 0.5,
          decayDays: params.decayDays,
          tags: params.tags ?? [],
          sourceChannel: ctx?.messageChannel,
        });

        // Build response message
        const contentPreview = `${params.content.slice(0, 80)}${params.content.length > 80 ? '...' : ''}`;
        const message = supersededId
          ? `Updated: "${contentPreview}" [${params.category}] (replaced previous entry)`
          : `Stored: "${contentPreview}" [${params.category}]`;

        return {
          content: [{
            type: 'text' as const,
            text: message,
          }],
          details: {
            action: supersededId ? 'replaced' : 'created',
            id: memory.id,
            category: memory.category,
            confidence: memory.confidence,
            supersededId,
          },
        };
      },
    },

    // ═══════════════════════════════════════════════════════════════════════
    // UPDATE - Modify existing memory
    // ═══════════════════════════════════════════════════════════════════════
    memory_update: {
      name: 'memory_update',
      label: 'Memory Update',
      description: `Update an existing memory when information changes or was incorrect.

Use when:
- User corrects previous info ("actually my dog's name is Rex, not Max")
- Information becomes more specific ("my meeting is at 3pm, not just 'afternoon'")
- Confidence changes (user confirms something you inferred)`,

      parameters: Type.Object({
        id: Type.String({
          description: 'ID of memory to update (from memory_search results)'
        }),
        content: Type.Optional(Type.String({
          description: 'Updated content'
        })),
        confidence: Type.Optional(Type.Number({
          minimum: 0,
          maximum: 1,
          description: 'Updated confidence score'
        })),
        importance: Type.Optional(Type.Number({
          minimum: 0,
          maximum: 1,
          description: 'Updated importance score'
        })),
      }),

      async execute(
        _toolCallId: string,
        params: {
          id: string;
          content?: string;
          confidence?: number;
          importance?: number;
        }
      ) {
        const existing = await store.getAsync(params.id);
        if (!existing) {
          return {
            content: [{ type: 'text' as const, text: `Memory ${params.id} not found.` }],
            details: { error: 'not_found' },
          };
        }

        const memory = await store.update(params.id, {
          content: params.content,
          confidence: params.confidence,
          importance: params.importance,
        });

        return {
          content: [{
            type: 'text' as const,
            text: `Updated memory: "${memory.content.slice(0, 80)}${memory.content.length > 80 ? '...' : ''}"`
          }],
          details: {
            action: 'updated',
            id: memory.id,
            content: memory.content,
            confidence: memory.confidence,
          },
        };
      },
    },

    // ═══════════════════════════════════════════════════════════════════════
    // FORGET - Delete memory
    // ═══════════════════════════════════════════════════════════════════════
    memory_forget: {
      name: 'memory_forget',
      label: 'Memory Forget',
      description: `Delete a memory permanently.

Use when:
- User explicitly asks you to forget something
- Information is no longer relevant ("I sold that car")
- Memory was stored in error`,

      parameters: Type.Object({
        id: Type.Optional(Type.String({
          description: 'ID of memory to delete (if known)'
        })),
        query: Type.Optional(Type.String({
          description: 'Search query to find memory to delete (if ID unknown)'
        })),
        reason: Type.Optional(Type.String({
          description: 'Why this memory is being forgotten (for audit log)'
        })),
      }),

      async execute(
        _toolCallId: string,
        params: {
          id?: string;
          query?: string;
          reason?: string;
        }
      ) {
        if (params.id) {
          const existing = await store.getAsync(params.id);
          if (!existing) {
            return {
              content: [{ type: 'text' as const, text: `Memory ${params.id} not found.` }],
              details: { error: 'not_found' },
            };
          }

          await store.delete(params.id, params.reason);
          return {
            content: [{ type: 'text' as const, text: `Forgotten: "${existing.content.slice(0, 60)}..."` }],
            details: { action: 'deleted', id: params.id },
          };
        }

        if (params.query) {
          const results = await store.search({
            query: params.query,
            limit: 5,
            minConfidence: 0.3,
          });

          if (results.length === 0) {
            return {
              content: [{ type: 'text' as const, text: 'No matching memories found.' }],
              details: { found: 0 },
            };
          }

          // Check if query text appears in any result (case-insensitive exact match)
          const queryLower = params.query.toLowerCase();
          const exactMatch = results.find(r =>
            r.memory.content.toLowerCase().includes(queryLower)
          );

          // Auto-delete if:
          // 1. Single high-confidence match (score > 0.9), OR
          // 2. Query text appears literally in top result, OR
          // 3. Top result has significantly higher score than second (clear winner)
          const topResult = results[0];
          const secondScore = results.length > 1 ? results[1].score : 0;
          const clearWinner = topResult.score > 0.5 && topResult.score > secondScore * 1.5;

          if (exactMatch || (results.length === 1 && topResult.score > 0.9) || clearWinner) {
            const toDelete = exactMatch || topResult;
            await store.delete(toDelete.memory.id, params.reason);
            return {
              content: [{
                type: 'text' as const,
                text: `Forgotten: "${toDelete.memory.content.slice(0, 60)}..."`
              }],
              details: { action: 'deleted', id: toDelete.memory.id },
            };
          }

          // Return candidates for user selection
          const list = results
            .map(r => `- [${r.memory.id.slice(0, 8)}] ${r.memory.content.slice(0, 50)}... (${(r.score * 100).toFixed(0)}%)`)
            .join('\n');

          return {
            content: [{
              type: 'text' as const,
              text: `Found ${results.length} candidates. Specify id:\n${list}`
            }],
            details: {
              action: 'candidates',
              candidates: results.map(r => ({
                id: r.memory.id,
                content: r.memory.content,
                score: r.score,
              })),
            },
          };
        }

        return {
          content: [{ type: 'text' as const, text: 'Provide id or query.' }],
          details: { error: 'missing_param' },
        };
      },
    },

    // ═══════════════════════════════════════════════════════════════════════
    // SEARCH - Semantic search
    // ═══════════════════════════════════════════════════════════════════════
    memory_search: {
      name: 'memory_search',
      label: 'Memory Search',
      description: `Search memories by semantic similarity and/or filters.

Use when:
- You need context about the user to answer well
- User references something from the past ("remember when I told you...")
- You want to personalize a response
- Before storing, to check if memory already exists`,

      parameters: Type.Object({
        query: Type.Optional(Type.String({
          description: 'Semantic search query'
        })),
        category: Type.Optional(stringEnum(MEMORY_CATEGORIES)),
        tags: Type.Optional(Type.Array(Type.String(), {
          description: 'Filter by tags (AND logic)'
        })),
        minConfidence: Type.Optional(Type.Number({
          minimum: 0,
          maximum: 1,
          description: 'Minimum confidence threshold (default: 0.5)'
        })),
        limit: Type.Optional(Type.Number({
          maximum: 50,
          description: 'Max results to return (default: 10)'
        })),
      }),

      async execute(
        _toolCallId: string,
        params: {
          query?: string;
          category?: MemoryCategory;
          tags?: string[];
          minConfidence?: number;
          limit?: number;
        }
      ) {
        const results = await store.search({
          query: params.query,
          category: params.category,
          tags: params.tags,
          minConfidence: params.minConfidence ?? 0.5,
          limit: params.limit ?? 10,
          excludeDecayed: true,
        });

        // Update last accessed
        await store.touchManyAsync(results.map(r => r.memory.id));

        if (results.length === 0) {
          return {
            content: [{ type: 'text' as const, text: 'No relevant memories found.' }],
            details: { count: 0 },
          };
        }

        const text = results
          .map((r, i) =>
            `${i + 1}. [${r.memory.category}] ${r.memory.content} (${(r.score * 100).toFixed(0)}% match, ${(r.memory.confidence * 100).toFixed(0)}% confident)`
          )
          .join('\n');

        return {
          content: [{
            type: 'text' as const,
            text: `Found ${results.length} memories:\n\n${text}`
          }],
          details: {
            count: results.length,
            memories: results.map(r => ({
              id: r.memory.id,
              content: r.memory.content,
              category: r.memory.category,
              confidence: r.memory.confidence,
              importance: r.memory.importance,
              score: r.score,
              tags: r.memory.tags,
            })),
          },
        };
      },
    },

    // ═══════════════════════════════════════════════════════════════════════
    // SUMMARIZE - Topic summary
    // ═══════════════════════════════════════════════════════════════════════
    memory_summarize: {
      name: 'memory_summarize',
      label: 'Memory Summarize',
      description: `Get a summary of memories related to a topic.

Use when:
- Starting a conversation and want general context
- Topic is broad ("what do I know about user's work")
- Too many memories would be retrieved with search`,

      parameters: Type.Object({
        topic: Type.String({
          description: 'Topic to summarize memories about'
        }),
        maxMemories: Type.Optional(Type.Number({
          description: 'Max memories to include in summary (default: 20)'
        })),
      }),

      async execute(
        _toolCallId: string,
        params: {
          topic: string;
          maxMemories?: number;
        }
      ) {
        const results = await store.search({
          query: params.topic,
          limit: params.maxMemories ?? 20,
          excludeDecayed: true,
        });

        if (results.length === 0) {
          return {
            content: [{
              type: 'text' as const,
              text: `No memories found about "${params.topic}".`
            }],
            details: { memoryCount: 0 },
          };
        }

        // Group by category
        const byCategory = new Map<string, string[]>();
        for (const r of results) {
          const cat = r.memory.category;
          if (!byCategory.has(cat)) byCategory.set(cat, []);
          byCategory.get(cat)!.push(r.memory.content);
        }

        // Format summary
        const sections = Array.from(byCategory.entries())
          .map(([cat, items]) => `**${cat}**:\n${items.map(i => `- ${i}`).join('\n')}`)
          .join('\n\n');

        return {
          content: [{
            type: 'text' as const,
            text: `Summary of "${params.topic}" (${results.length} memories):\n\n${sections}`
          }],
          details: {
            memoryCount: results.length,
            categories: Object.fromEntries(byCategory),
          },
        };
      },
    },

    // ═══════════════════════════════════════════════════════════════════════
    // LIST - Browse all memories
    // ═══════════════════════════════════════════════════════════════════════
    memory_list: {
      name: 'memory_list',
      label: 'Memory List',
      description: `List all memories, optionally filtered. Use for browsing/auditing, not semantic search.`,

      parameters: Type.Object({
        category: Type.Optional(stringEnum(MEMORY_CATEGORIES)),
        sortBy: Type.Optional(stringEnum([
          'createdAt', 'updatedAt', 'importance', 'confidence', 'lastAccessedAt'
        ] as const)),
        limit: Type.Optional(Type.Number({
          description: 'Max results (default: 20)'
        })),
        offset: Type.Optional(Type.Number({
          description: 'Skip first N results (for pagination)'
        })),
      }),

      async execute(
        _toolCallId: string,
        params: {
          category?: MemoryCategory;
          sortBy?: 'createdAt' | 'updatedAt' | 'importance' | 'confidence' | 'lastAccessedAt';
          limit?: number;
          offset?: number;
        }
      ) {
        const results = await store.listAsync({
          category: params.category,
          sortBy: params.sortBy ?? 'createdAt',
          sortOrder: 'desc',
          limit: params.limit ?? 20,
          offset: params.offset ?? 0,
        });

        if (results.items.length === 0) {
          return {
            content: [{ type: 'text' as const, text: 'No memories found.' }],
            details: { total: 0, count: 0 },
          };
        }

        const text = results.items
          .map((m, i) =>
            `${i + 1}. [${m.category}] ${m.content.slice(0, 60)}${m.content.length > 60 ? '...' : ''} (${(m.confidence * 100).toFixed(0)}%)`
          )
          .join('\n');

        return {
          content: [{
            type: 'text' as const,
            text: `Showing ${results.items.length} of ${results.total} memories:\n\n${text}`
          }],
          details: {
            total: results.total,
            count: results.items.length,
            memories: results.items.map(m => ({
              id: m.id,
              content: m.content,
              category: m.category,
              confidence: m.confidence,
              importance: m.importance,
              createdAt: m.createdAt,
            })),
          },
        };
      },
    },
  };
}

export type MemoryTools = ReturnType<typeof createMemoryTools>;
