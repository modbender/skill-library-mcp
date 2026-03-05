#!/usr/bin/env node
/**
 * CLI: Run project health check
 * Usage: health-check [<project-dir>] [--json | --markdown]
 */

import { checkHealth, formatHealthJson, formatHealthMarkdown } from '../core/health';
import * as path from 'path';

function main() {
  const args = process.argv.slice(2);
  
  // Parse flags
  const format = args.includes('--markdown') ? 'markdown' : 'json';
  
  // Get project directory (first non-flag arg or current directory)
  const projectDir = args.find(a => !a.startsWith('--')) || '.';
  const resolvedDir = path.resolve(projectDir);
  
  try {
    const result = checkHealth({ projectDir: resolvedDir });
    
    if (format === 'markdown') {
      console.log(formatHealthMarkdown(result));
    } else {
      console.log(formatHealthJson(result));
    }
    
    // Exit with error code if health check failed
    process.exit(result.status === 'RED' ? 1 : 0);
  } catch (err) {
    console.error('Error:', err instanceof Error ? err.message : String(err));
    process.exit(1);
  }
}

main();
