#!/usr/bin/env node

/**
 * oktk - OpenClaw Token Killer
 * Main CLI entry point
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Load filters and utilities
const Cache = require('./cache');
const Analytics = require('./analytics');
const GitFilter = require('./filters/GitFilter');
const TestFilter = require('./filters/TestFilter');
const FilesFilter = require('./filters/FilesFilter');
const NetworkFilter = require('./filters/NetworkFilter');
const SearchFilter = require('./filters/SearchFilter');
const DockerFilter = require('./filters/DockerFilter');
const KubectlFilter = require('./filters/KubectlFilter');
const AILearnFilter = require('./filters/AILearnFilter');
const PassthroughFilter = require('./filters/PassthroughFilter');

class OKTK {
  constructor(options = {}) {
    this.options = {
      raw: options.raw || false,
      debug: options.debug || process.env.OKTK_DEBUG === '1',
      cache: options.cache !== false && process.env.OKTK_DISABLE !== 'true',
      ...options
    };

    this.cache = new Cache(this.options);
    this.analytics = new Analytics(this.options);

    // Filter registry: pattern regex -> Filter class
    this.filters = [
      [/^git\s+/i, GitFilter],
      [/^npm\s+(test|run\s+test)/i, TestFilter],
      [/^npm\s+/i, TestFilter], // Generic npm commands
      [/^cargo\s+(test|run\s+test)/i, TestFilter],
      [/^pytest\b/i, TestFilter],
      [/^jest\b/i, TestFilter],
      [/^ls\b/i, FilesFilter],
      [/^find\b/i, FilesFilter],
      [/^tree\b/i, FilesFilter],
      [/^curl\b/i, NetworkFilter],
      [/^wget\b/i, NetworkFilter],
      [/^http\b/i, NetworkFilter],
      [/^grep\b/i, SearchFilter],
      [/^rg\b/i, SearchFilter], // ripgrep
      [/^ack\b/i, SearchFilter],
      // Docker commands
      [/^docker\s+/i, DockerFilter],
      [/^docker-compose\b/i, DockerFilter],
      // Kubernetes commands
      [/^kubectl\s+/i, KubectlFilter],
      [/^k\s+/i, KubectlFilter], // common alias
    ];
  }

  /**
   * Execute command and filter output
   */
  async execute(command, context = {}) {
    // Check for emergency mode
    if (await this.emergencyModeActive()) {
      console.warn('⚠️  Emergency mode active, bypassing filters');
      return this.runCommand(command);
    }

    // User requested raw output
    if (this.options.raw || command.includes('--raw')) {
      return this.runCommand(command);
    }

    // Remove --raw flag if present before executing
    const cleanCommand = command.replace(/\s*--raw\s*/, '').trim();

    try {
      // Execute command
      const result = await this.runCommand(cleanCommand);
      const output = result.stdout || '';
      const exitCode = result.exitCode || 0;

      // Check cache first
      const cacheKey = this.hashCommand(cleanCommand);
      if (this.options.cache) {
        const cached = await this.cache.get(cacheKey);
        if (cached && cached.output) {
          await this.analytics.track(cacheKey, cleanCommand, output.length, cached.output.length, 'cache');
          return { ...result, stdout: cached.output, cached: true };
        }
      }

      // Select and apply filter
      const filterResult = await this.applyFilters(cleanCommand, output, exitCode, context);

      // Store in cache
      if (this.options.cache && filterResult.filtered) {
        await this.cache.set(cacheKey, { output: filterResult.output });
      }

      // Track analytics
      await this.analytics.track(
        cacheKey,
        cleanCommand,
        output.length,
        filterResult.output.length,
        filterResult.filterName
      );

      return {
        ...result,
        stdout: filterResult.output,
        filtered: filterResult.filtered,
        filterName: filterResult.filterName,
        savings: this.calculateSavings(output, filterResult.output),
        cached: false
      };

    } catch (error) {
      // Command execution failed - return as-is
      console.error(`❌ Command failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Run command without filtering
   */
  async runCommand(command) {
    try {
      const stdout = execSync(command, {
        encoding: 'utf8',
        maxBuffer: 10 * 1024 * 1024 // 10MB
      });
      return { stdout, exitCode: 0, success: true };
    } catch (error) {
      return {
        stdout: error.stdout || '',
        stderr: error.stderr || error.message,
        exitCode: error.status || 1,
        success: false
      };
    }
  }

  /**
   * Apply filters with fallback chain
   */
  async applyFilters(command, output, exitCode, context) {
    // Detect filter type
    const Filter = this.selectFilter(command);
    const filterType = Filter.name.replace('Filter', '').toLowerCase();

    try {
      // Try specialized filter
      const filter = new Filter(context);
      const filtered = await filter.apply(output, { ...context, command, exitCode });

      if (this.options.debug) {
        console.log(`🔍 Filter applied: ${Filter.name}`);
      }

      return {
        output: filtered,
        filtered: true,
        filterName: filterType
      };

    } catch (error) {
      console.warn(`⚠️  Filter ${Filter.name} failed: ${error.message}`);

      // Fallback to PassthroughFilter
      try {
        const passthrough = new PassthroughFilter();
        const filtered = await passthrough.apply(output);

        return {
          output: filtered,
          filtered: true,
          filterName: 'passthrough'
        };

      } catch (passthroughError) {
        console.error(`❌ Even passthrough failed: ${passthroughError.message}`);

        // Ultimate fallback: raw output
        return {
          output,
          filtered: false,
          filterName: 'none'
        };
      }
    }
  }

  /**
   * Select filter based on command pattern
   */
  selectFilter(command) {
    for (const [pattern, Filter] of this.filters) {
      if (pattern.test(command)) {
        return Filter;
      }
    }
    
    // Check if AI learning is enabled
    if (process.env.OKTK_AI_LEARN === '1' || this.options.aiLearn) {
      return AILearnFilter;
    }
    
    return PassthroughFilter;
  }

  /**
   * Hash command for cache key
   */
  hashCommand(command) {
    return crypto
      .createHash('sha256')
      .update(command)
      .digest('hex')
      .substring(0, 16);
  }

  /**
   * Calculate token savings percentage
   */
  calculateSavings(original, filtered) {
    const originalTokens = original.split(/\s+/).length;
    const filteredTokens = filtered.split(/\s+/).length;
    const savings = ((originalTokens - filteredTokens) / originalTokens * 100).toFixed(1);
    return {
      original: originalTokens,
      filtered: filteredTokens,
      saved: originalTokens - filteredTokens,
      percentage: parseFloat(savings)
    };
  }

  /**
   * Check if emergency mode is active
   */
  async emergencyModeActive() {
    const emergencyFile = path.join(process.env.HOME, '.oktk', 'EMERGENCY');
    try {
      await fs.promises.access(emergencyFile);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Show savings statistics
   */
  async showStats() {
    return this.analytics.report();
  }

  /**
   * List available filters
   */
  listFilters() {
    console.log('📋 Available Filters:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    this.filters.forEach(([pattern, Filter]) => {
      console.log(`  ${Filter.name.padEnd(20)} ${pattern.toString()}`);
    });
    console.log(`  ${'PassthroughFilter'.padEnd(20)} (fallback)`);
  }

  /**
   * Clear cache
   */
  async clearCache(filter = null) {
    return this.cache.clear(filter);
  }
}

/**
 * CLI entry point
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
oktk - AI Token Killer v1.3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
  oktk <command>              Filter command output
  oktk <command> --raw        Show raw output (no filter)
  oktk gain                   Show savings statistics
  oktk filters                List available filters
  oktk cache --clear          Clear cache
  oktk learn --list           List learned patterns (AI)
  oktk learn --clear          Clear learned patterns (AI)

AI Learning:
  Set OKTK_AI_LEARN=1 to enable automatic pattern learning
  Set OKTK_AI_MODEL=<model> to choose the AI model (default: glm-flash)

Examples:
  oktk git status
  oktk npm test
  oktk docker ps
  oktk kubectl get pods
`);
    process.exit(0);
  }

  // Subcommands
  if (args[0] === 'gain') {
    const oktk = new OKTK();
    const stats = await oktk.showStats();
    console.log(stats);
    return;
  }

  if (args[0] === 'filters') {
    const oktk = new OKTK();
    oktk.listFilters();
    return;
  }

  if (args[0] === 'cache' && args[1] === '--clear') {
    const oktk = new OKTK();
    const filter = args[2] || null;
    await oktk.clearCache(filter);
    console.log(`✅ Cache cleared${filter ? ` for ${filter}` : ''}`);
    return;
  }

  if (args[0] === 'learn') {
    const aiFilter = new AILearnFilter();
    
    if (args[1] === '--list') {
      const learned = aiFilter.listLearned();
      if (learned.length === 0) {
        console.log('📚 No learned patterns yet.');
        console.log('   Enable AI learning with: export OKTK_AI_LEARN=1');
      } else {
        console.log(`📚 Learned Patterns (${learned.length}):`);
        learned.forEach(p => console.log(`   - ${p}`));
      }
      return;
    }
    
    if (args[1] === '--clear') {
      aiFilter.clearLearned();
      console.log('✅ Learned patterns cleared');
      return;
    }
    
    // Show status
    const learned = aiFilter.listLearned();
    const enabled = process.env.OKTK_AI_LEARN === '1';
    console.log(`🧠 AI Learning: ${enabled ? '✅ Enabled' : '❌ Disabled'}`);
    console.log(`   Model: ${process.env.OKTK_AI_MODEL || 'glm-flash (default)'}`);
    console.log(`   Learned patterns: ${learned.length}`);
    if (!enabled) {
      console.log('\n   Enable with: export OKTK_AI_LEARN=1');
    }
    return;
  }

  // Execute command
  const command = args.join(' ');
  const oktk = new OKTK();

  const result = await oktk.execute(command);

  // Output filtered result
  if (result.stdout) {
    console.log(result.stdout);
  }

  if (result.stderr) {
    console.error(result.stderr);
  }

  // Show savings if filtered and debug mode
  if (oktk.options.debug && result.filtered && result.savings) {
    console.error(`\n📊 Saved ${result.savings.percentage}% tokens (${result.savings.saved}/${result.savings.original})`);
  }

  // Exit with command's exit code
  process.exit(result.exitCode);
}

// Export for testing
module.exports = OKTK;

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
