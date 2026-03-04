#!/usr/bin/env node
// SECURITY MANIFEST:
//   Environment variables accessed: NONE
//   External endpoints called: NONE (search operates on local index only)
//   Local files read: config.yaml, data/index/*
//   Local files written: NONE
/**
 * Curated Search Tool - Phase 4 Implementation
 *
 * Command-line search interface for OpenClaw.
 * Loads index, executes queries, returns JSON results.
 *
 * @version 1.0.0
 */

const fs = require('fs');
const path = require('path');
const yaml = require('yaml');
const MiniSearch = require('minisearch');
const Indexer = require('../src/indexer');

// ============================================================================
// CONSTANTS
// ============================================================================

const VERSION = '1.0.0';
const DEFAULT_CONFIG_PATH = path.resolve(__dirname, '..', 'config.yaml');
const DEFAULT_INDEX_PATH = 'data/index';
const MAX_LIMIT_HARD = 1000; // Internal safety cap
const MAX_QUERY_LENGTH = 1000;
const DEFAULT_LIMIT = 10;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Print help message to stderr
 */
function printHelp() {
  const help = `
Curated Search Tool v${VERSION}
Usage: node scripts/search.js [options] [--query "search terms"]

Options:
  -q, --query <string>       Search query (required unless --stats or --help)
  -l, --limit <number>       Maximum results (default: ${DEFAULT_LIMIT}, max: config.max_limit)
  -d, --domain <string>      Filter to specific domain (e.g., docs.python.org)
  --min-score <number>       Minimum score threshold (0.0 - 1.0)
  --offset <number>         Pagination offset (default: 0)
  --pretty                 Pretty-print JSON output
  --verbose                Show timing and debug information
  --config <path>          Path to config.yaml (default: ${DEFAULT_CONFIG_PATH})
  --stats                  Show index statistics
  --version               Show version information
  --help                  Show this help message

Examples:
  node scripts/search.js --query="python tutorial" --limit=5
  node scripts/search.js "javascript closure" --domain=developer.mozilla.org
  node scripts/search.js --stats

Exit codes:
  0  Success (even if zero results)
  1  Error (missing query, invalid args, etc.)
  2  Configuration error
  3  Index corruption or missing
`;
  console.error(help);
  process.exit(0);
}

/**
 * Print version to stderr
 */
function printVersion() {
  console.error(`Curated Search Tool ${VERSION}`);
  try {
    const pkgPath = path.resolve(__dirname, 'node_modules', 'minisearch', 'package.json');
    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
    console.error('MiniSearch: ' + pkg.version);
  } catch (e) {
    console.error('MiniSearch: (unable to determine version)');
  }
  process.exit(0);
}

/**
 * Format output JSON (pretty or compact)
 */
function formatOutput(data, pretty = false) {
  if (pretty) {
    return JSON.stringify(data, null, 2);
  }
  return JSON.stringify(data);
}

/**
 * Write error message to stderr and exit
 */
function errorExit(code, details) {
  const errorObj = {
    error: details.code,
    message: details.message,
    ...(details.suggestion && { suggestion: details.suggestion }),
    ...(details.details && { details: details.details })
  };
  console.error(JSON.stringify(errorObj));
  process.exit(code);
}

/**
 * Validate domain format (simple check)
 */
function isValidDomain(domain) {
  // Very basic: should have at least one dot and no spaces
  return typeof domain === 'string' &&
         domain.length > 0 &&
         domain.includes('.') &&
         !domain.includes(' ') &&
         !domain.startsWith('.') &&
         !domain.endsWith('.');
}

/**
 * Get effective limit (apply hard cap)
 */
function getEffectiveLimit(userLimit, configLimit, hardCap = MAX_LIMIT_HARD) {
  const effective = userLimit || configLimit || DEFAULT_LIMIT;
  return Math.min(effective, hardCap);
}

// ============================================================================
// ARGUMENT PARSING
// ============================================================================

// Use minimist for robust parsing
const minimist = require('minimist');

const args = minimist(process.argv.slice(2), {
  string: ['query', 'domain', 'config'],
  number: ['limit', 'min-score', 'offset'],
  boolean: ['pretty', 'verbose', 'stats', 'version', 'help'],
  alias: {
    q: 'query',
    l: 'limit',
    d: 'domain',
    v: 'verbose',
    h: 'help'
  },
  default: {
    limit: DEFAULT_LIMIT,
    'min-score': 0,
    offset: 0
  }
});

// ============================================================================
// EARLY EXIT FLAGS (before heavy work)
// ============================================================================

if (args.help) {
  printHelp();
}

if (args.version) {
  printVersion();
}

// ============================================================================
// LOAD CONFIGURATION
// ============================================================================

let config;
const configPath = args.config || DEFAULT_CONFIG_PATH;

try {
  if (!fs.existsSync(configPath)) {
    errorExit(2, {
      code: 'config_missing',
      message: `Configuration file not found: ${configPath}`,
      suggestion: 'Ensure you are running from the skill directory or specify --config path'
    });
  }

  const yamlStr = fs.readFileSync(configPath, 'utf8');
  config = yaml.parse(yamlStr);
} catch (e) {
  errorExit(2, {
    code: 'config_invalid',
    message: `Failed to parse configuration: ${e.message}`,
    suggestion: 'Check YAML syntax in config.yaml',
    details: { path: configPath, error: e.message }
  });
}

// Config sanity checks
if (!config.index || !config.index.path) {
  errorExit(2, {
    code: 'config_missing_index_path',
    message: 'Configuration missing index.path',
    suggestion: 'Add index.path to config.yaml'
  });
}

if (!config.search) {
  config.search = {};
}

// ============================================================================
// VALIDATION
// ============================================================================

const validationErrors = [];

// Query validation
if (!args.stats && !args.query) {
  validationErrors.push({
    code: 'missing_query',
    message: 'Search query is required (use --query or positional argument)',
    suggestion: 'curated-search --query="python" or curated-search "python"'
  });
}

if (args.query && typeof args.query === 'string' && args.query.length > MAX_QUERY_LENGTH) {
  validationErrors.push({
    code: 'query_too_long',
    message: `Query exceeds ${MAX_QUERY_LENGTH} character limit`,
    suggestion: 'Shorten your query',
    details: { length: args.query.length }
  });
}

// Limit validation
const effectiveLimit = getEffectiveLimit(args.limit, config.search.default_limit);
if (args.limit && args.limit > (config.search.max_limit || 100)) {
  validationErrors.push({
    code: 'limit_exceeded',
    message: `Limit cannot exceed ${config.search.max_limit || 100}`,
    suggestion: `Use --limit <= ${config.search.max_limit || 100}`
  });
}

// Domain validation
if (args.domain && !isValidDomain(args.domain)) {
  validationErrors.push({
    code: 'invalid_domain',
    message: `Invalid domain format: ${args.domain}`,
    suggestion: 'Use format like "docs.python.org" (no protocol)'
  });
}

// Mutually exclusive flags
if (args.stats && args.query) {
  validationErrors.push({
    code: 'conflicting_flags',
    message: 'Cannot use --stats with --query',
    suggestion: 'Use --stats alone to show index statistics'
  });
}

// Report validation errors
if (validationErrors.length > 0) {
  errorExit(1, validationErrors[0]);
}

// ============================================================================
// INITIALIZE INDEXER
// ============================================================================

let indexer;
try {
  // Resolve index path (relative to skill directory)
  const indexPath = path.isAbsolute(config.index.path)
    ? config.index.path
    : path.resolve(__dirname, '..', config.index.path);

  // Check index file exists
  const indexFile = indexPath + '.json';
  if (!fs.existsSync(indexFile)) {
    errorExit(3, {
      code: 'index_not_found',
      message: 'Search index not found. The index has not been built yet.',
      suggestion: 'Run the crawler first: npm run crawl',
      details: { path: indexFile }
    });
  }

  // Create indexer with resolved path
  const indexerConfig = { ...config.index, path: indexPath };
  indexer = new Indexer(indexerConfig);

  const loaded = indexer.open();
  // Note: open() returns false if it created a fresh index (no existing data)
  // That's okay for search (we'll get zero results)
} catch (e) {
  // Distinguish corruption errors
  if (e.message && e.message.includes('loadJSON')) {
    errorExit(3, {
      code: 'index_corrupted',
      message: 'Index file is corrupted or incompatible with this version',
      suggestion: 'Rebuild the index by running: npm run crawl',
      details: { error: e.message }
    });
  }

  console.error(JSON.stringify({
    error: 'index_init_failed',
    message: `Failed to initialize index: ${e.message}`,
    suggestion: 'Check index files and permissions'
  }));
  process.exit(1);
}

// ============================================================================
// HANDLE --stats MODE
// ============================================================================

if (args.stats) {
  try {
    const stats = indexer.getStats();
    const output = {
      documents: stats.documents,
      domains: stats.domain_breakdown ? Object.keys(stats.domain_breakdown).length : stats.domains,
      domain_breakdown: stats.domain_breakdown || {},
      oldest_crawl: stats.oldest_crawl ? new Date(stats.oldest_crawl).toISOString() : null,
      newest_crawl: stats.newest_crawl ? new Date(stats.newest_crawl).toISOString() : null,
      index_path: config.index.path
    };
    console.log(formatOutput(output, args.pretty));
    indexer.close();
    process.exit(0);
  } catch (e) {
    errorExit(1, {
      code: 'stats_failed',
      message: `Failed to get statistics: ${e.message}`
    });
  }
}

// ============================================================================
// PERFORM SEARCH
// ============================================================================

const startTime = Date.now();

try {
  // Prepare search options
  const searchOptions = {
    limit: effectiveLimit,
    offset: args.offset || 0,
    minScore: args['min-score'] !== undefined ? args['min-score'] : (config.search.min_score || 0)
  };

  if (args.domain) {
    searchOptions.domainFilter = args.domain;
  }

  // Execute search
  const result = indexer.search(args.query, searchOptions);

  // Build response
  const response = {
    query: args.query,
    total: result.total,
    results: result.results,
    took_ms: Date.now() - startTime,
    limit: effectiveLimit,
    offset: searchOptions.offset
  };

  // Output on stdout
  console.log(formatOutput(response, args.pretty));

  // Verbose logging to stderr
  if (args.verbose) {
    console.error(`[INFO] Search completed in ${response.took_ms}ms`);
    console.error(`[INFO] Query: "${args.query}"`);
    console.error(`[INFO] Options: ${JSON.stringify(searchOptions)}`);
    console.error(`[INFO] Found ${result.total} results, returning ${result.results.length} (limit ${effectiveLimit})`);
  }

  indexer.close();
  process.exit(0);

} catch (e) {
  console.error(JSON.stringify({
    error: 'search_failed',
    message: `Search execution failed: ${e.message}`,
    suggestion: 'Check query syntax and index integrity',
    details: { query: args.query, stack: args.verbose ? e.stack : undefined }
  }));
  indexer.close();
  process.exit(1);
}
