import { mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { homedir } from 'os';
import { MemoryStorage } from './storage.js';

/**
 * OpenClaw Memory System - Database Setup Script
 *
 * Initializes the SQLite database with:
 * - Core memory tables (001-init.sql)
 * - x402 payment tables (002-x402-payments.sql)
 * - WAL mode for better concurrency
 */

async function setup() {
  console.log('\n🧠 OpenClaw Memory System - Database Setup\n');

  try {
    // 1. Determine data directory
    const dataDir = process.env.OPENCLAW_MEMORY_DIR
      || join(homedir(), '.openclaw', 'openclaw-memory');

    console.log(`📁 Data directory: ${dataDir}`);

    // 2. Create data directory if it doesn't exist
    if (!existsSync(dataDir)) {
      console.log('   Creating data directory...');
      mkdirSync(dataDir, { recursive: true });
      console.log('   ✅ Directory created');
    } else {
      console.log('   ✅ Directory exists');
    }

    // 3. Initialize database
    const dbPath = join(dataDir, 'memory.db');
    console.log(`\n💾 Database path: ${dbPath}`);

    const storage = new MemoryStorage(dbPath);

    // 4. Run migrations
    console.log('\n🔧 Running migrations...');

    console.log('   [1/2] Creating core memory tables (001-init.sql)...');
    console.log('   [2/2] Creating x402 payment tables (002-x402-payments.sql)...');

    storage.initialize();

    console.log('   ✅ All migrations completed');

    // 5. Verify setup
    console.log('\n🔍 Verifying database setup...');

    const tables = storage.db.prepare(`
      SELECT name FROM sqlite_master
      WHERE type='table'
      ORDER BY name
    `).all();

    console.log(`   ✅ Found ${tables.length} tables:`);
    tables.forEach(table => {
      console.log(`      - ${table.name}`);
    });

    // 6. Display schema info
    console.log('\n📊 Database Configuration:');
    console.log(`   Journal Mode: ${storage.db.pragma('journal_mode', { simple: true })}`);
    console.log(`   Page Size: ${storage.db.pragma('page_size', { simple: true })} bytes`);
    console.log(`   Encoding: ${storage.db.pragma('encoding', { simple: true })}`);

    // 7. Initialize default quota for test
    console.log('\n🎯 Memory System Features:');
    console.log('   ✅ Semantic search (cosine similarity)');
    console.log('   ✅ Memory relations (graph connections)');
    console.log('   ✅ Access tracking');
    console.log('   ✅ Quota management (free: 100 memories, pro: unlimited)');
    console.log('   ✅ x402 payment protocol (0.5 USDT/month for Pro tier)');

    // 8. Display usage examples
    console.log('\n📚 Usage:');
    console.log('   Import: import { MemoryStorage } from "openclaw-memory";');
    console.log('   Create: const storage = new MemoryStorage(dbPath);');
    console.log('   Store:  storage.recordMemory({ memory_id, content, ... });');
    console.log('   Search: storage.searchMemories(embedding, limit, minScore);');
    console.log('   Quota:  storage.checkQuotaAvailable(agentWallet);');

    // 9. Close database
    storage.close();

    console.log('\n✅ Setup complete! Memory System is ready to use.\n');
    console.log(`📂 Database location: ${dbPath}`);
    console.log(`🌐 Data directory: ${dataDir}\n`);

    return {
      success: true,
      dbPath,
      dataDir,
      tables: tables.map(t => t.name)
    };

  } catch (error) {
    console.error('\n❌ Setup failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run setup if called directly
const isMainModule = process.argv[1] && import.meta.url.endsWith(process.argv[1].replace(/\\/g, '/'));
if (isMainModule || process.argv[1]?.includes('setup.js')) {
  setup().catch(error => {
    console.error('Setup error:', error);
    process.exit(1);
  });
}

export { setup };
