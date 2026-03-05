#!/usr/bin/env node
/**
 * GraphQL TypeScript Generator - CLI Entry Point
 * Converts GraphQL schemas to TypeScript types
 */

import { mkdirSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { parseArgs, validateConfig, loadSchemas, printHelp, printVersion, CLIConfig } from './cli.js';
import { TypeGenerator, getOutputDir } from './generator.js';

const USAGE = `
GraphQL TypeScript Generator v1.0.0
Generate TypeScript types from GraphQL schemas

Usage: graphql-ts-generator [options] <schema-file>

Examples:
  graphql-ts-generator schema.graphql
  graphql-ts-generator -o types -n API schema.graphql
  graphql-ts-generator schemas/*.graphql

Run with --help for detailed options.
`;

async function main(): Promise<void> {
  try {
    const config = parseArgs();

    if (config.help) {
      printHelp();
      process.exit(0);
    }

    if (config.version) {
      printVersion();
      process.exit(0);
    }

    validateConfig(config);

    // Load all schemas
    const schemas = await loadSchemas(config.schemaPaths);

    if (schemas.length === 0) {
      console.error('Error: No valid schemas to process');
      process.exit(1);
    }

    // Process each schema
    for (const { schema, name } of schemas) {
      console.log(`Processing schema: ${name}`);

      const generator = new TypeGenerator(schema, {
        namespace: config.namespace,
        prefix: config.prefix,
        skipEnums: config.skipEnums,
        skipUnions: config.skipUnions,
        schemaName: name
      });

      const files = generator.generate();
      const outputDir = getOutputDir(config.outputDir);

      // Ensure output directory exists
      if (!existsSync(outputDir)) {
        mkdirSync(outputDir, { recursive: true });
      }

      // Write generated files
      for (const file of files) {
        const outputPath = join(outputDir, file.filename);
        writeFileSync(outputPath, file.content, 'utf-8');
        console.log(`Generated: ${outputPath}`);
      }
    }

    console.log(`\nSuccess! Generated ${schemas.length} file(s) to ${getOutputDir(config.outputDir)}`);
    process.exit(0);

  } catch (error: any) {
    console.error('Error:', error.message);
    console.error('\n' + USAGE);
    process.exit(1);
  }
}

// Run only when executed directly (not when imported)
if (import.meta.url === `file://${process.argv[1]}`) {
  (async () => {
    try {
      await main();
    } catch (error: any) {
      console.error('Fatal error:', error.message);
      process.exit(1);
    }
  })();
}

export { main };
