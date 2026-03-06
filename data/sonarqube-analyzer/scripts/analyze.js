#!/usr/bin/env node
/**
 * SonarQube Analyzer CLI
 * 
 * CLI tool for analyzing SonarQube issues and suggesting solutions
 * 
 * Usage:
 *   node analyze.js --project=my-project [--pr=5] [--action=analyze|report|quality-gate] [--format=json|markdown]
 */

const { analyzeProject } = require('../src/analyzer');
const { getQualityGate } = require('../src/api');
const { generateJsonReport, generateMarkdownReport, generateCliSummary } = require('../src/reporter');

/**
 * Parse CLI arguments
 * @param {string[]} args - Process arguments
 * @returns {Object} Parsed options
 */
function parseArgs(args) {
  const params = {
    project: null,
    pr: null,
    action: 'analyze',
    format: 'json',
    severities: [],
    limit: 100
  };

  args.forEach(arg => {
    if (arg.startsWith('--project=')) {
      params.project = arg.split('=')[1];
    } else if (arg.startsWith('--pr=')) {
      params.pr = arg.split('=')[1];
    } else if (arg.startsWith('--action=')) {
      params.action = arg.split('=')[1];
    } else if (arg.startsWith('--format=')) {
      params.format = arg.split('=')[1];
    } else if (arg.startsWith('--limit=')) {
      params.limit = parseInt(arg.split('=')[1], 10);
    } else if (arg.startsWith('--severities=')) {
      params.severities = arg.split('=')[1].split(',');
    } else if (arg === '--help' || arg === '-h') {
      showHelp();
      process.exit(0);
    }
  });

  return params;
}

/**
 * Show help message
 */
function showHelp() {
  console.log(`
SonarQube Analyzer - CLI Tool

Usage: node analyze.js [options]

Options:
  --project=<name>      Project key in SonarQube (required)
  --pr=<number>         Pull request number (optional)
  --action=<type>       Action to perform:
                         - analyze: Full analysis with suggestions (default)
                         - quality-gate: Check Quality Gate status only
  --format=<type>       Output format: json | markdown | cli (default: json)
  --limit=<number>      Maximum issues to fetch (default: 100)
  --severities=<list>   Comma-separated severity filters
  --help, -h             Show this help message

Environment Variables:
  SONAR_HOST_URL         SonarQube URL (default: http://127.0.0.1:9000)
  SONAR_TOKEN            Authentication token (default: admin)

Examples:
  # Analyze project
  node analyze.js --project=my-project

  # Analyze PR with markdown output
  node analyze.js --project=my-project --pr=5 --format=markdown

  # Check Quality Gate
  node analyze.js --project=my-project --pr=5 --action=quality-gate

  # Filter by severity
  node analyze.js --project=my-project --severities=CRITICAL,MAJOR
`);
}

/**
 * Main execution
 */
async function main() {
  const args = process.argv.slice(2);
  const params = parseArgs(args);

  if (!params.project) {
    console.error('❌ Error: --project is required');
    console.log('\nRun with --help for usage information\n');
    process.exit(1);
  }

  try {
    switch (params.action) {
      case 'analyze': {
        console.log(`🔍 Analyzing ${params.project}${params.pr ? ` (PR #${params.pr})` : ''}...\n`);
        
        const analysis = await analyzeProject(params.project, params.pr, {
          severities: params.severities,
          limit: params.limit
        });

        let output;
        switch (params.format) {
          case 'markdown':
            output = generateMarkdownReport(analysis);
            break;
          case 'cli':
            output = generateCliSummary(analysis);
            break;
          case 'json':
          default:
            output = generateJsonReport(analysis);
            break;
        }

        console.log(output);
        
        // Exit with error code if issues found
        if (analysis.summary.totalIssues > 0) {
          process.exit(1);
        }
        break;
      }

      case 'quality-gate': {
        console.log(`🚪 Checking Quality Gate for ${params.project}${params.pr ? ` (PR #${params.pr})` : ''}...\n`);
        
        const qg = await getQualityGate(params.project, params.pr);
        
        console.log(JSON.stringify(qg, null, 2));
        
        if (qg.status === 'ERROR' || qg.status === 'FAILED') {
          console.log('\n❌ Quality Gate failed');
          process.exit(1);
        } else if (qg.status === 'OK' || qg.status === 'PASSED') {
          console.log('\n✅ Quality Gate passed');
        }
        break;
      }

      default:
        console.error(`❌ Unknown action: ${params.action}`);
        process.exit(1);
    }
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { parseArgs, showHelp };