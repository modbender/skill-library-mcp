#!/usr/bin/env node
/**
 * PMC Harvest CLI
 * Fetch articles from PubMed Central using NCBI APIs
 * 
 * Usage:
 *   node pmc-harvest.js --search "J Stroke[journal]" --year 2025
 *   node pmc-harvest.js --fetch PMC12345678
 *   node pmc-harvest.js --test
 */

const pmc = require('../lib/api.js');

// ANSI colors
const c = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  dim: '\x1b[2m',
  reset: '\x1b[0m',
};

function log(msg, color = 'reset') {
  console.log(`${c[color]}${msg}${c.reset}`);
}

function error(msg) {
  console.error(`${c.red}Error: ${msg}${c.reset}`);
  process.exit(1);
}

function printUsage() {
  console.log(`
${c.cyan}PMC Harvest${c.reset} - Full text retrieval from PubMed Central

${c.yellow}Usage:${c.reset}
  node pmc-harvest.js <command> [options]

${c.yellow}Commands:${c.reset}
  search    Search PMC for articles
  fetch     Fetch full text for a PMCID
  test      Run test with sample journals

${c.yellow}Options:${c.reset}
  --query <text>     Search query (e.g., "J Stroke[journal]")
  --year <year>      Filter by publication year
  --max <n>          Max results (default: 100)
  --pmcid <id>       PMC ID to fetch

${c.yellow}Examples:${c.reset}
  node pmc-harvest.js search --query "J Stroke[journal]" --year 2025
  node pmc-harvest.js fetch --pmcid PMC12345678
  node pmc-harvest.js test
`);
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    printUsage();
    process.exit(0);
  }
  
  const command = args[0];
  
  // Parse options
  const getOpt = (name) => {
    const idx = args.indexOf(name);
    return idx >= 0 ? args[idx + 1] : null;
  };
  
  try {
    switch (command) {
      case 'search':
        await cmdSearch({
          query: getOpt('--query'),
          year: getOpt('--year'),
          max: getOpt('--max') || 100
        });
        break;
        
      case 'fetch':
        await cmdFetch({ pmcid: getOpt('--pmcid') });
        break;
        
      case 'test':
        await cmdTest();
        break;
        
      default:
        // Support legacy flag format too
        if (command === '--search') {
          await cmdSearch({
            query: args[1],
            year: getOpt('--year'),
            max: getOpt('--max') || 100
          });
        } else if (command === '--fetch') {
          await cmdFetch({ pmcid: args[1] });
        } else if (command === '--test') {
          await cmdTest();
        } else {
          error(`Unknown command: ${command}`);
        }
    }
  } catch (e) {
    error(e.message);
  }
}

async function cmdSearch(options) {
  if (!options.query) error('--query required');
  
  const year = options.year ? parseInt(options.year) : null;
  const max = parseInt(options.max);
  
  log(`\n🔍 Searching PMC: ${options.query}${year ? ` (${year})` : ''}`, 'cyan');
  
  const result = await pmc.searchPMC(options.query, { year, retmax: max });
  log(`   Found ${result.count} articles\n`, 'yellow');
  
  if (result.pmcids.length > 0) {
    const summaries = await pmc.getSummaries(result.pmcids);
    
    summaries.forEach((s, i) => {
      console.log(`  ${i + 1}. ${c.cyan}${s.pmcid}${c.reset} - ${s.title?.substring(0, 60)}...`);
      console.log(`     ${c.dim}${s.journal} | ${s.pubdate}${c.reset}`);
    });
  }
}

async function cmdFetch(options) {
  if (!options.pmcid) error('--pmcid required');
  
  const pmcid = options.pmcid.startsWith('PMC') ? options.pmcid : `PMC${options.pmcid}`;
  
  log(`\n📥 Fetching full text: ${pmcid}`, 'cyan');
  
  const result = await pmc.fetchFullText(pmcid);
  
  if (!result.available) {
    log(`   ⚠️  Not available: ${result.reason}`, 'yellow');
    return;
  }
  
  const parsed = pmc.parseJATS(result.xml);
  
  log(`\n📄 ${parsed.title}`, 'green');
  console.log(`   ${c.dim}Type: ${parsed.articleType} | Keywords: ${parsed.keywords?.slice(0, 5).join(', ') || 'none'}${c.reset}`);
  
  console.log(`\n${c.yellow}Abstract:${c.reset}`);
  console.log(parsed.abstract?.substring(0, 500) + (parsed.abstract?.length > 500 ? '...' : ''));
  
  console.log(`\n${c.dim}Body: ${(parsed.body?.length || 0).toLocaleString()} characters${c.reset}`);
}

async function cmdTest() {
  log('\n🧪 Testing with Journal of Stroke, 2025...\n', 'cyan');
  
  const result = await pmc.searchPMC('"J Stroke"[journal]', { year: 2025, retmax: 10 });
  
  if (result.pmcids.length === 0) {
    log('No articles found', 'yellow');
    return;
  }
  
  const summaries = await pmc.getSummaries(result.pmcids);
  
  log(`📚 Sample articles (${summaries.length}):`, 'green');
  summaries.forEach((s, i) => {
    console.log(`   ${i + 1}. ${c.cyan}${s.pmcid}${c.reset} - ${s.title?.substring(0, 50)}...`);
  });
  
  // Test full text fetch on first
  log('\n🔬 Testing full text fetch...', 'cyan');
  const fullText = await pmc.fetchFullText(summaries[0].pmcid);
  
  if (fullText.available) {
    const parsed = pmc.parseJATS(fullText.xml);
    log(`✅ Success: ${parsed.title?.substring(0, 60)}...`, 'green');
    log(`   Body: ${(parsed.body?.length || 0).toLocaleString()} chars`, 'dim');
  } else {
    log(`⚠️  Full text not available: ${fullText.reason}`, 'yellow');
  }
}

main();
