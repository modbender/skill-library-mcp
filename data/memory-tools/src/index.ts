/**
 * OpenClaw Memory-as-Tools Plugin v2
 *
 * Agent-controlled memory with QMD-powered search.
 * File-based storage, no external APIs required.
 *
 * Key features:
 * - Six memory tools: store, update, forget, search, summarize, list
 * - File-based storage (markdown with YAML frontmatter)
 * - QMD search (BM25 + vector + reranking, all local)
 * - Auto-migration from v1
 * - No OpenAI dependency
 */

import type { OpenClawPluginApi } from './plugin-types.js';
import { parseConfig } from './config.js';
import { MemoryStoreV2 } from './store.js';
import { createMemoryTools } from './tools.js';
import {
  hasLegacyDatabase,
  hasNewMemories,
  migrateFromV1,
  printMigrationRequired,
  printMigrationSuccess,
} from './migration.js';

// Plugin definition
const memoryToolsPlugin = {
  id: 'memory-tools',
  name: 'Memory Tools',
  description: 'Agent-controlled memory with QMD-powered search (v2)',
  kind: 'memory' as const,

  async register(api: OpenClawPluginApi) {
    const cfg = parseConfig(api.pluginConfig);
    const memoriesPath = api.resolvePath(cfg.memoriesPath!);
    const legacyDbPath = api.resolvePath(cfg.legacyDbPath!);

    // ═══════════════════════════════════════════════════════════════════════
    // Auto-Migration from v1
    // ═══════════════════════════════════════════════════════════════════════

    const hasLegacy = hasLegacyDatabase(legacyDbPath);
    const hasNew = hasNewMemories(memoriesPath);

    if (cfg.autoMigrateLegacy === true && hasLegacy && !hasNew) {
      // Need to migrate
      printMigrationRequired(legacyDbPath);
      api.logger.info('memory-tools: Starting migration from v1...');

      const result = await migrateFromV1(legacyDbPath, memoriesPath);

      if (result.success || result.migratedCount > 0) {
        printMigrationSuccess(result);
        api.logger.info(`memory-tools: Migration complete (${result.migratedCount} memories)`);
      } else {
        api.logger.error(`memory-tools: Migration failed: ${result.errors.join(', ')}`);
        throw new Error(`Migration failed: ${result.errors.join(', ')}`);
      }
    } else if (cfg.autoMigrateLegacy !== true && hasLegacy && !hasNew) {
      api.logger.warn(
        'memory-tools: legacy database detected but autoMigrateLegacy is disabled by default; skipping migration'
      );
    }

    // ═══════════════════════════════════════════════════════════════════════
    // Initialize Store
    // ═══════════════════════════════════════════════════════════════════════

    const store = new MemoryStoreV2(memoriesPath, cfg.qmdCollection);

    // Check QMD availability
    const qmdAvailable = await store.isQMDAvailable();
    if (!qmdAvailable) {
      api.logger.warn(
        'memory-tools: QMD not installed. Install with: npm install -g @tobilu/qmd'
      );
      api.logger.warn('memory-tools: Semantic search will be limited until QMD is installed.');
    } else {
      try {
        await store.init();
        api.logger.info(`memory-tools: initialized with QMD (path: ${memoriesPath})`);
      } catch (err: any) {
        api.logger.warn(
          `memory-tools: QMD initialization failed, continuing in basic mode: ${err?.message || err}`
        );
      }
    }

    const tools = createMemoryTools(store as any); // Cast for compatibility

    // ═══════════════════════════════════════════════════════════════════════
    // Register Tools
    // ═══════════════════════════════════════════════════════════════════════

    api.registerTool(
      {
        name: tools.memory_store.name,
        label: tools.memory_store.label,
        description: tools.memory_store.description,
        parameters: tools.memory_store.parameters,
        execute: (id, params) => tools.memory_store.execute(id, params as any, {}),
      },
      { name: 'memory_store' }
    );

    api.registerTool(
      {
        name: tools.memory_update.name,
        label: tools.memory_update.label,
        description: tools.memory_update.description,
        parameters: tools.memory_update.parameters,
        execute: (id, params) => tools.memory_update.execute(id, params as any),
      },
      { name: 'memory_update' }
    );

    api.registerTool(
      {
        name: tools.memory_forget.name,
        label: tools.memory_forget.label,
        description: tools.memory_forget.description,
        parameters: tools.memory_forget.parameters,
        execute: (id, params) => tools.memory_forget.execute(id, params as any),
      },
      { name: 'memory_forget' }
    );

    api.registerTool(
      {
        name: tools.memory_search.name,
        label: tools.memory_search.label,
        description: tools.memory_search.description,
        parameters: tools.memory_search.parameters,
        execute: (id, params) => tools.memory_search.execute(id, params as any),
      },
      { name: 'memory_search' }
    );

    api.registerTool(
      {
        name: tools.memory_summarize.name,
        label: tools.memory_summarize.label,
        description: tools.memory_summarize.description,
        parameters: tools.memory_summarize.parameters,
        execute: (id, params) => tools.memory_summarize.execute(id, params as any),
      },
      { name: 'memory_summarize' }
    );

    api.registerTool(
      {
        name: tools.memory_list.name,
        label: tools.memory_list.label,
        description: tools.memory_list.description,
        parameters: tools.memory_list.parameters,
        execute: (id, params) => tools.memory_list.execute(id, params as any),
      },
      { name: 'memory_list' }
    );

    // ═══════════════════════════════════════════════════════════════════════
    // Lifecycle Hooks
    // ═══════════════════════════════════════════════════════════════════════

    // Auto-inject standing instructions at conversation start
    if (cfg.autoInjectInstructions === true) {
      api.on('before_agent_start', async (event: { prompt?: string }) => {
        const instructions = store.getByCategory('instruction', 10);

        if (instructions.length === 0) {
          return undefined;
        }

        const instructionList = instructions
          .map((m: { content: string }) => `- ${m.content}`)
          .join('\n');

        api.logger.info?.(`memory-tools: injecting ${instructions.length} standing instructions`);

        return {
          prependContext: `<standing-instructions>\nRemember these user instructions:\n${instructionList}\n</standing-instructions>`,
        };
      });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CLI Commands
    // ═══════════════════════════════════════════════════════════════════════

    api.registerCli(
      ({ program }: { program: any }) => {
        const memory = program
          .command('memory-tools')
          .description('Memory-as-Tools plugin commands (v2)');

        memory
          .command('stats')
          .description('Show memory statistics')
          .action(async () => {
            const total = store.count();
            const instructions = store.getByCategory('instruction').length;
            const facts = store.getByCategory('fact').length;
            const preferences = store.getByCategory('preference').length;

            console.log(`Memory Statistics (v2):`);
            console.log(`  Total: ${total}`);
            console.log(`  Instructions: ${instructions}`);
            console.log(`  Facts: ${facts}`);
            console.log(`  Preferences: ${preferences}`);
            console.log(`  Storage: ${memoriesPath}`);
          });

        memory
          .command('list')
          .description('List memories')
          .option('-c, --category <category>', 'Filter by category')
          .option('-l, --limit <n>', 'Max results', '20')
          .action(async (opts: { category?: string; limit?: string }) => {
            const results = store.list({
              category: opts.category as any,
              limit: parseInt(opts.limit ?? '20'),
            });

            console.log(`Showing ${results.items.length} of ${results.total} memories:\n`);
            for (const m of results.items) {
              console.log(`[${m.id.slice(0, 8)}] [${m.category}] ${m.content.slice(0, 60)}...`);
            }
          });

        memory
          .command('search <query>')
          .description('Search memories using QMD')
          .option('-l, --limit <n>', 'Max results', '10')
          .action(async (query: string, opts: { limit?: string }) => {
            const results = await store.search({
              query,
              limit: parseInt(opts.limit ?? '10'),
            });

            console.log(`Found ${results.length} memories:\n`);
            for (const r of results) {
              console.log(`[${r.memory.id.slice(0, 8)}] (${(r.score * 100).toFixed(0)}%) ${r.memory.content}`);
            }
          });

        memory
          .command('export')
          .description('Export all memories as JSON')
          .action(async () => {
            const results = store.list({ limit: 10000 });
            console.log(JSON.stringify(results.items, null, 2));
          });

        memory
          .command('reindex')
          .description('Force QMD to re-index all memories')
          .action(async () => {
            console.log('Re-indexing memories with QMD...');
            await store.reindex();
            console.log('Done!');
          });

        memory
          .command('path')
          .description('Show memories storage path')
          .action(() => {
            console.log(memoriesPath);
          });
      },
      { commands: ['memory-tools'] }
    );

    // ═══════════════════════════════════════════════════════════════════════
    // Service (lifecycle management)
    // ═══════════════════════════════════════════════════════════════════════

    api.registerService({
      id: 'memory-tools',
      start: async () => {
        const count = store.count();
        api.logger.info(`memory-tools: service started (${count} memories, v2)`);
      },
      stop: () => {
        store.close();
        api.logger.info('memory-tools: service stopped');
      },
    });
  },
};

export default memoryToolsPlugin;

// Re-export types for external use
export * from './types.js';
export { MemoryStoreV2 as MemoryStore } from './store.js';
export { createMemoryTools } from './tools.js';
export { MemoryFileManager } from './file-manager.js';
export { QMDClient } from './qmd.js';
