#!/usr/bin/env node
/**
 * GraphQL TypeScript Generator - CLI Parser
 * Handles command-line argument parsing and validation
 */

import { argv } from 'process';
import { existsSync, lstatSync, readFileSync } from 'fs';
import { join, dirname, resolve } from 'path';
import { loadSchema } from './utils.js';

export interface CLIConfig {
  schemaPaths: string[];
  outputDir: string;
  namespace?: string;
  prefix?: string;
  skipEnums?: boolean;
  skipUnions?: boolean;
  help: boolean;
  version: boolean;
}

const DEFAULT_OUTPUT_DIR = 'dist';
const HELP_TEXT = `
Usage: graphql-ts-generator [options] <schema-file>

Generate TypeScript types from GraphQL schema files.

Arguments:
  <schema-file>               One or more GraphQL schema file paths

Options:
  -o, --output <dir>         Output directory for generated files (default: dist)
  -n, --namespace <name>     Wrap types in a namespace
  -p, --prefix <prefix>      Prefix for generated type names
  --skip-enums               Skip enum generation
  --skip-unions              Skip union generation
  -h, --help                 Show this help message
  -v, --version              Show version number

Examples:
  graphql-ts-generator schema.graphql
  graphql-ts-generator -o types -n API schema.graphql
  graphql-ts-generator schemas/*.graphql
`;

const VERSION = '1.0.0';

/**
 * Parse command line arguments
 */
export function parseArgs(): CLIConfig {
  const args = argv.slice(2);
  const config: CLIConfig = {
    schemaPaths: [],
    outputDir: DEFAULT_OUTPUT_DIR,
    help: false,
    version: false,
  };

  let i = 0;
  while (i < args.length) {
    const arg = args[i];

    switch (arg) {
      case '-h':
      case '--help':
        config.help = true;
        return config;

      case '-v':
      case '--version':
        config.version = true;
        return config;

      case '-o':
      case '--output':
        if (i + 1 >= args.length) {
          throw new Error('Missing output directory argument');
        }
        config.outputDir = args[++i];
        break;

      case '-n':
      case '--namespace':
        if (i + 1 >= args.length) {
          throw new Error('Missing namespace argument');
        }
        config.namespace = args[++i];
        break;

      case '-p':
      case '--prefix':
        if (i + 1 >= args.length) {
          throw new Error('Missing prefix argument');
        }
        config.prefix = args[++i];
        break;

      case '--skip-enums':
        config.skipEnums = true;
        break;

      case '--skip-unions':
        config.skipUnions = true;
        break;

      default:
        // Positional argument - should be a schema file path
        if (arg.startsWith('-')) {
          throw new Error(`Unknown option: ${arg}`);
        }
        config.schemaPaths.push(arg);
        break;
    }
    i++;
  }

  return config;
}

/**
 * Validate CLI configuration
 */
export function validateConfig(config: CLIConfig): void {
  if (config.help || config.version) {
    return;
  }

  if (config.schemaPaths.length === 0) {
    throw new Error('No schema files specified. Use -h for help.');
  }

  // Validate all schema paths exist and are files
  for (const path of config.schemaPaths) {
    if (!existsSync(path)) {
      throw new Error(`Schema file not found: ${path}`);
    }
    const stat = lstatSync(path);
    if (!stat.isFile()) {
      throw new Error(`Schema path is not a file: ${path}`);
    }
  }

  // Ensure output directory exists or can be created
  const outputDir = resolve(config.outputDir);
  try {
    // Will throw if dirname is invalid
    dirname(outputDir);
  } catch (e) {
    throw new Error(`Invalid output directory: ${config.outputDir}`);
  }
}

/**
 * Load and validate all schemas
 */
export async function loadSchemas(schemaPaths: string[]): Promise<any> {
  const schemas: any[] = [];

  for (const path of schemaPaths) {
    try {
      const schema = loadSchema(path);
      schemas.push({
        schema,
        path,
        name: getSchemaName(path)
      });
    } catch (error: any) {
      throw new Error(`Failed to load schema ${path}: ${error.message}`);
    }
  }

  return schemas;
}

/**
 * Extract schema name from file path
 */
function getSchemaName(filePath: string): string {
  const base = filePath.split('/').pop() || filePath.split('\\').pop() || 'schema';
  const name = base.replace(/\.[^/.]+$/, ''); // Remove extension
  return name.replace(/[^a-zA-Z0-9]/g, '_');
}

/**
 * Print help message
 */
export function printHelp(): void {
  console.log(HELP_TEXT);
}

/**
 * Print version
 */
export function printVersion(): void {
  console.log(`graphql-ts-generator v${VERSION}`);
}

export { loadSchema };
