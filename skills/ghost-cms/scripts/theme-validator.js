#!/usr/bin/env node

/**
 * Ghost Theme Validator
 * Validates Ghost themes using official gscan validator
 * 
 * NOTE: Requires optional dependency 'gscan'
 * Install with: cd scripts && npm install gscan
 */

import { basename, extname, resolve } from 'path';
import { existsSync, statSync } from 'fs';

// Check if gscan is available (optional dependency)
let gscan;
try {
  gscan = (await import('gscan')).default;
} catch (err) {
  console.error(`
❌ Error: gscan is not installed

Theme validation requires the optional 'gscan' dependency.

To install:
  cd scripts
  npm install gscan

Then run this command again.
`);
  process.exit(1);
}

// Parse CLI arguments
const args = process.argv.slice(2);
const themePath = args.find(a => !a.startsWith('--'));
const flags = {
  version: args.includes('--version') ? args[args.indexOf('--version') + 1] : 'v5',
  json: args.includes('--json'),
  errorsOnly: args.includes('--errors-only'),
  help: args.includes('--help') || args.includes('-h')
};

// Help text
if (flags.help || !themePath) {
  console.log(`
Ghost Theme Validator

Validates Ghost themes using the official gscan validator.
Same validation used by Ghost Admin and Ghost Marketplace.

Usage:
  node theme-validator.js <theme-path> [options]

Arguments:
  <theme-path>    Path to theme directory or ZIP file

Options:
  --version <v>   Target Ghost version (v5, v6, latest) [default: v5]
  --json          Output JSON format (for automation)
  --errors-only   Show only errors (hide warnings and recommendations)
  --help, -h      Show this help

Examples:
  # Validate theme directory
  node theme-validator.js ~/themes/my-theme/

  # Validate ZIP file
  node theme-validator.js theme.zip

  # Target Ghost v6
  node theme-validator.js theme.zip --version v6

  # JSON output for CI/CD
  node theme-validator.js theme.zip --json

  # Show only blocking errors
  node theme-validator.js theme.zip --errors-only

Exit Codes:
  0   Theme is valid (no errors)
  1   Theme has errors (must fix before upload)
  2   Invalid arguments or file not found

What gscan validates:
  ✅ Required files (package.json, index.hbs, post.hbs)
  ✅ package.json format and required fields
  ✅ Handlebars syntax validity
  ✅ Ghost helper usage (finds deprecated helpers)
  ✅ Template structure and compatibility
  ✅ Ghost version compatibility
  ✅ Best practices and accessibility
  ✅ Performance recommendations

See: https://github.com/TryGhost/gscan
`);
  process.exit(themePath ? 0 : 2);
}

// Validate theme path
const absolutePath = resolve(themePath);
if (!existsSync(absolutePath)) {
  console.error(`❌ Error: Theme not found: ${themePath}`);
  process.exit(2);
}

// Determine if directory or ZIP
const isZip = extname(absolutePath) === '.zip';
const isDir = !isZip && statSync(absolutePath).isDirectory();

if (!isZip && !isDir) {
  console.error(`❌ Error: Theme must be a directory or ZIP file`);
  process.exit(2);
}

// Color helpers (only for non-JSON output)
const colors = {
  red: (text) => flags.json ? text : `\x1b[31m${text}\x1b[0m`,
  yellow: (text) => flags.json ? text : `\x1b[33m${text}\x1b[0m`,
  green: (text) => flags.json ? text : `\x1b[32m${text}\x1b[0m`,
  blue: (text) => flags.json ? text : `\x1b[34m${text}\x1b[0m`,
  gray: (text) => flags.json ? text : `\x1b[90m${text}\x1b[0m`,
  bold: (text) => flags.json ? text : `\x1b[1m${text}\x1b[0m`
};

// Validate theme
async function validateTheme() {
  try {
    if (!flags.json) {
      console.log(`🔍 Validating theme: ${colors.bold(basename(absolutePath))}`);
      console.log(`   ${colors.gray(`Target: Ghost ${flags.version}`)}\n`);
    }
    
    // Run gscan
    const results = await gscan.check(absolutePath, {
      checkVersion: flags.version,
      onlyFatalErrors: false
    });
    
    // Count issues
    const errorCount = Object.keys(results.results.error || {}).length;
    const warningCount = Object.keys(results.results.warning || {}).length;
    const recommendationCount = Object.keys(results.results.recommendation || {}).length;
    
    // JSON output mode
    if (flags.json) {
      const output = {
        valid: errorCount === 0,
        version: flags.version,
        theme: basename(absolutePath),
        counts: {
          errors: errorCount,
          warnings: warningCount,
          recommendations: recommendationCount
        },
        results: {
          error: Object.values(results.results.error || {}),
          warning: Object.values(results.results.warning || {}),
          recommendation: Object.values(results.results.recommendation || {})
        }
      };
      
      console.log(JSON.stringify(output, null, 2));
      process.exit(errorCount > 0 ? 1 : 0);
      return;
    }
    
    // User-friendly output
    
    // Structure validation
    if (errorCount === 0 && warningCount === 0 && recommendationCount === 0) {
      console.log(colors.green('✅ Theme is perfect! No issues found.\n'));
      process.exit(0);
      return;
    }
    
    // Errors (blocking)
    if (errorCount > 0) {
      console.log(colors.red(`❌ Errors (${errorCount}):`));
      console.log(colors.red('   These must be fixed before uploading:\n'));
      
      Object.entries(results.results.error || {}).forEach(([code, issues]) => {
        if (Array.isArray(issues)) {
          issues.forEach(issue => {
            console.log(`   ${colors.red('•')} ${issue.rule || code}`);
            if (issue.details) {
              console.log(`     ${colors.gray(issue.details)}`);
            }
            if (issue.failures && issue.failures.length > 0) {
              issue.failures.forEach(f => {
                const location = f.ref ? ` (${f.ref})` : '';
                console.log(`     ${colors.gray('→')} ${f.message || f.helper}${location}`);
              });
            }
          });
        }
      });
      console.log();
    }
    
    // Warnings (should fix)
    if (warningCount > 0 && !flags.errorsOnly) {
      console.log(colors.yellow(`⚠️  Warnings (${warningCount}):`));
      console.log(colors.yellow('   Should be fixed for best compatibility:\n'));
      
      Object.entries(results.results.warning || {}).forEach(([code, issues]) => {
        if (Array.isArray(issues)) {
          issues.forEach(issue => {
            console.log(`   ${colors.yellow('•')} ${issue.rule || code}`);
            if (issue.details) {
              console.log(`     ${colors.gray(issue.details)}`);
            }
            if (issue.failures && issue.failures.length > 0) {
              issue.failures.forEach(f => {
                const location = f.ref ? ` (${f.ref})` : '';
                console.log(`     ${colors.gray('→')} ${f.message || f.helper}${location}`);
              });
            }
          });
        }
      });
      console.log();
    }
    
    // Recommendations (nice to have)
    if (recommendationCount > 0 && !flags.errorsOnly) {
      console.log(colors.blue(`💡 Recommendations (${recommendationCount}):`));
      console.log(colors.blue('   Best practices and optimizations:\n'));
      
      Object.entries(results.results.recommendation || {}).forEach(([code, issues]) => {
        if (Array.isArray(issues)) {
          issues.slice(0, 5).forEach(issue => {  // Show first 5 to avoid spam
            console.log(`   ${colors.blue('•')} ${issue.rule || code}`);
            if (issue.details) {
              console.log(`     ${colors.gray(issue.details)}`);
            }
          });
        }
      });
      
      if (recommendationCount > 5) {
        console.log(`\n   ${colors.gray(`... and ${recommendationCount - 5} more recommendations`)}`);
      }
      console.log();
    }
    
    // Summary
    if (errorCount === 0) {
      console.log(colors.green('✅ Theme is valid! Safe to upload.'));
      if (warningCount > 0) {
        console.log(colors.yellow(`   Note: ${warningCount} warning(s) found - consider fixing for best compatibility.`));
      }
    } else {
      console.log(colors.red(`❌ Validation failed (${errorCount} error(s) must be fixed)`));
    }
    
    // Exit with appropriate code
    process.exit(errorCount > 0 ? 1 : 0);
    
  } catch (error) {
    if (flags.json) {
      console.error(JSON.stringify({
        valid: false,
        error: error.message
      }, null, 2));
    } else {
      console.error(`\n❌ Validation error: ${error.message}`);
      if (error.stack) {
        console.error(colors.gray(error.stack));
      }
    }
    process.exit(2);
  }
}

// Run validation
validateTheme().catch(error => {
  console.error('Fatal error:', error.message);
  process.exit(2);
});
