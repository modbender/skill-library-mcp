import { mkdirSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { RouterStorage } from './storage.js';

/**
 * OpenClaw Smart Router - Database Setup Script
 *
 * Initializes the SQLite database with:
 * - Core routing tables (001-init.sql)
 * - x402 payment tables (002-x402-payments.sql)
 * - WAL mode for better concurrency
 */

async function setup() {
  console.log('\n🧭 OpenClaw Smart Router - Database Setup\n');

  try {
    // 1. Determine data directory
    const dataDir = process.env.OPENCLAW_ROUTER_DIR
      || join(homedir(), '.openclaw', 'openclaw-smart-router');

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
    const dbPath = join(dataDir, 'smart-router.db');
    console.log(`\n💾 Database path: ${dbPath}`);

    const storage = new RouterStorage(dbPath);

    // 4. Run migrations
    console.log('\n🔧 Running migrations...');

    console.log('   [1/2] Creating routing decision tables (001-init.sql)...');
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

    // 7. Display features
    console.log('\n🎯 Smart Router Features:');
    console.log('   ✅ Intelligent model selection (complexity-based routing)');
    console.log('   ✅ Budget-aware routing (integrate with Cost Governor)');
    console.log('   ✅ Pattern learning (learns from routing outcomes)');
    console.log('   ✅ Model performance tracking (per-model analytics)');
    console.log('   ✅ Quota management (free: 100/day, pro: unlimited)');
    console.log('   ✅ x402 payment protocol (0.5 USDT/month for Pro tier)');

    // 8. Display pricing
    console.log('\n💰 Pricing:');
    console.log('   Free Tier: 100 routing decisions/day (rule-based)');
    console.log('   Pro Tier: Unlimited decisions + ML-enhanced routing');
    console.log('   Pro Price: 0.5 USDT/month (via x402)');

    // 9. Display integration points
    console.log('\n🔗 Integration Points:');
    console.log('   → Cost Governor: Budget constraints & pricing data');
    console.log('   → Memory System: Pattern storage & semantic search');
    console.log('   → Context Optimizer: Task complexity analysis');

    // 10. Display usage examples
    console.log('\n📚 Usage:');
    console.log('   Import: import { RouterStorage } from "openclaw-smart-router";');
    console.log('   Create: const storage = new RouterStorage(dbPath);');
    console.log('   Record: storage.recordDecision({ decision_id, ... });');
    console.log('   Outcome: storage.recordOutcome(decisionId, { was_successful, ... });');
    console.log('   Pattern: storage.getPattern({ agent_wallet, task_type });');
    console.log('   Stats: storage.getRoutingStats(agentWallet, "7 days");');
    console.log('   Quota: storage.checkQuotaAvailable(agentWallet);');

    // 11. Display supported models
    console.log('\n🤖 Supported Models:');
    console.log('   Anthropic: claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5');
    console.log('   OpenAI: gpt-5.2, gpt-4.5');
    console.log('   Google: gemini-2.5-pro');

    // 12. Close database
    storage.close();

    console.log('\n✅ Setup complete! Smart Router is ready to use.\n');
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
