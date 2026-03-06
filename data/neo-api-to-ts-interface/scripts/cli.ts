#!/usr/bin/env node

/**
 * CLI Module - Unified command-line interface for api-to-ts-interface
 * Usage: ts-interface [command] [options]
 *
 * Commands:
 *   parse      Parse API response to type definitions
 *   generate   Generate TypeScript interfaces from parsed types
 *   storybook  Generate Storybook documentation
 *   all        Run full pipeline (parse -> generate -> storybook)
 *
 * Examples:
 *   ts-interface parse --input api.json --output types.json
 *   ts-interface generate --input types.json --output interfaces/
 *   ts-interface storybook --input types.json --output docs/
 *   ts-interface all --input api.json --output-dir out/
 */

import * as fs from 'fs';
import * as path from 'path';
import { spawn } from 'child_process';

// Import our modules (in production would use compiled JS)
import { APIParser, ParserOutput } from './parser.js';
import { CodeGenerator } from './generator.js';
import { StorybookGenerator } from './storybook.js';

interface CLIArgs {
  command?: string;
  input?: string;
  output?: string;
  outputDir?: string;
  template?: string;
  reference?: string;
  assets?: string;
  title?: string;
  hints?: string;
  help?: boolean;
  version?: boolean;
}

class CLI {
  private args: CLIArgs;

  constructor(args: string[]) {
    this.args = this.parseArgs(args);
  }

  private parseArgs(args: string[]): CLIArgs {
    const parsed: CLIArgs = {};

    // First non-flag arg is command
    for (const arg of args) {
      if (!arg.startsWith('--') && !parsed.command) {
        parsed.command = arg;
        continue;
      }

      if (arg.startsWith('--')) {
        const [key, value] = arg.slice(2).split('=');
        if (value !== undefined) {
          (parsed as any)[key] = value;
        } else {
          (parsed as any)[key] = true;
        }
      }
    }

    // Default command
    if (!parsed.command && args.length > 0) {
      parsed.command = 'help';
    }

    // Map common aliases
    if (parsed.command === '-h' || parsed.command === '--help') {
      parsed.command = 'help';
    }
    if (parsed.command === '-v' || parsed.command === '--version') {
      parsed.command = 'version';
    }

    return parsed;
  }

  run(): number {
    const { command } = this.args;

    switch (command) {
      case 'parse':
      case 'generatestorybook':
      case 'parse':
        return this.runParse();
      case 'generate':
        return this.runGenerate();
      case 'storybook':
        return this.runStorybook();
      case 'all':
        return this.runAll();
      case 'help':
        this.printHelp();
        return 0;
      case 'version':
        this.printVersion();
        return 0;
      default:
        console.error(`Unknown command: ${command}`);
        this.printHelp();
        return 1;
    }
  }

  private runParse(): number {
    const input = this.args.input;
    const output = this.args.output || 'parsed-types.json';
    const hints = this.args.hints;

    if (!input) {
      console.error('Error: --input is required for parse command');
      return 1;
    }

    try {
      let hintsData: any = {};
      if (hints && fs.existsSync(hints)) {
        hintsData = JSON.parse(fs.readFileSync(hints, 'utf8'));
      }

      // Read input API response
      const content = fs.readFileSync(input, 'utf8');
      let data: any;

      try {
        data = JSON.parse(content);
      } catch (err) {
        console.error('Error: Input must be valid JSON');
        return 1;
      }

      // Parse
      const parser = new APIParser(hintsData);
      const result = parser.parse(data);

      // Write output
      fs.writeFileSync(output, JSON.stringify(result, null, 2), 'utf8');
      console.log(`Parsed types written to: ${output}`);
      console.log(`Root type: ${result.metadata.rootType}`);
      console.log(`Total types: ${result.types.length}`);

      return 0;
    } catch (err) {
      console.error('Parse error:', err);
      return 1;
    }
  }

  private runGenerate(): number {
    const input = this.args.input;
    const output = this.args.output || 'interfaces.ts';
    const template = this.args.template;
    const reference = this.args.reference;

    if (!input) {
      console.error('Error: --input is required for generate command');
      return 1;
    }

    try {
      const content = fs.readFileSync(input, 'utf8');
      const parserOutput: ParserOutput = JSON.parse(content);

      const generator = new CodeGenerator({
        templatePath: template,
        referencePath: reference,
        outputPath: output,
      });

      const result = generator.generate(parserOutput, output);

      console.log(`Generated TypeScript code: ${output}`);
      console.log(`Types generated: ${result.files.join(', ')}`);

      return 0;
    } catch (err) {
      console.error('Generate error:', err);
      return 1;
    }
  }

  private runStorybook(): number {
    const input = this.args.input;
    const output = this.args.output || 'storybook-docs';
    const template = this.args.template;
    const assets = this.args.assets;
    const title = this.args.title;

    if (!input) {
      console.error('Error: --input is required for storybook command');
      return 1;
    }

    try {
      const content = fs.readFileSync(input, 'utf8');
      const parserOutput: ParserOutput = JSON.parse(content);

      const storybook = new StorybookGenerator({
        templatePath: template,
        assetsPath: assets,
        outputPath: output,
        title,
      });

      storybook.generate(parserOutput, output);

      console.log(`Storybook documentation generated in: ${output}`);
      console.log(`Open ${path.join(output, 'storybook.html')} in a browser`);

      return 0;
    } catch (err) {
      console.error('Storybook error:', err);
      return 1;
    }
  }

  private runAll(): number {
    const input = this.args.input;
    const outputDir = this.args.outputDir || 'output';
    const template = this.args.template;
    const reference = this.args.reference;
    const assets = this.args.assets;
    const title = this.args.title;

    if (!input) {
      console.error('Error: --input is required for all command');
      return 1;
    }

    try {
      console.log('=== Running full pipeline ===\n');

      // Step 1: Parse
      console.log('Step 1/3: Parsing API response...');
      let data: any;
      try {
        const content = fs.readFileSync(input, 'utf8');
        data = JSON.parse(content);
      } catch (err) {
        console.error('Error: Failed to read/parse input JSON');
        return 1;
      }

      let hintsData: any = {};
      if (reference && fs.existsSync(reference)) {
        try {
          hintsData = JSON.parse(fs.readFileSync(reference, 'utf8'));
        } catch (err) {
          console.warn(`Warning: Could not load reference types from ${reference}`);
        }
      }

      const parser = new APIParser(hintsData);
      const parsed = parser.parse(data);

      const parsedFile = path.join(outputDir, 'parsed-types.json');
      fs.mkdirSync(outputDir, { recursive: true });
      fs.writeFileSync(parsedFile, JSON.stringify(parsed, null, 2), 'utf8');
      console.log(`✓ Parsed types to: ${parsedFile}\n`);

      // Step 2: Generate
      console.log('Step 2/3: Generating TypeScript interfaces...');
      const generator = new CodeGenerator({
        templatePath: template,
        referencePath: reference,
      });

      const interfacesDir = path.join(outputDir, 'interfaces');
      const { files } = generator.generate(parsed, interfacesDir);
      console.log(`✓ Generated ${files.length} type file(s) to: ${interfacesDir}\n`);

      // Step 3: Storybook
      console.log('Step 3/3: Generating Storybook documentation...');
      const storybook = new StorybookGenerator({
        templatePath: template,
        assetsPath: assets,
        title,
      });

      const docsDir = path.join(outputDir, 'docs');
      storybook.generate(parsed, docsDir);
      console.log(`✓ Storybook docs to: ${docsDir}\n`);

      console.log('=== Pipeline complete ===');
      console.log(`Output directory: ${outputDir}`);
      console.log(`- ${path.relative(process.cwd(), parsedFile)}`);
      console.log(`- ${path.relative(process.cwd(), interfacesDir)}/`);
      console.log(`- ${path.relative(process.cwd(), docsDir)}/`);

      return 0;
    } catch (err) {
      console.error('Pipeline error:', err);
      return 1;
    }
  }

  private printHelp(): void {
    const help = `api-to-ts-interface - Generate TypeScript interfaces from API responses

USAGE:
  ts-interface <command> [options]

COMMANDS:
  parse        Parse API response JSON to type definitions
  generate     Generate TypeScript interfaces from parsed types
  storybook    Generate Storybook documentation
  all          Run full pipeline (parse -> generate -> storybook)
  help         Show this help message
  version      Show version information

OPTIONS:
  --input=<file>          Input file (JSON) [required for all commands]
  --output=<file>         Output file for parse/generate (default: parsed-types.json or interfaces.ts)
  --output-dir=<dir>      Output directory for 'all' command (default: output)
  --template=<file>       Custom template file path
  --reference=<file>      Reference types JSON file (types.json)
  --assets=<dir>          Storybook assets directory (assets/ui)
  --title=<string>        Storybook documentation title
  --hints=<file>          Schema hints for parser (optional)

EXAMPLES:
  ts-interface parse --input api-response.json --output types.json
  ts-interface generate --input types.json --output-dir src/types/ --reference references/types.json
  ts-interface storybook --input types.json --output docs/ --title "My API Docs"
  ts-interface all --input api.json --output-dir build/ --title "Generated API Types"

NOTE:
  This CLI can be used standalone or integrated into agent workflows.
  For the full pipeline, 'all' command is recommended.`;

    console.log(help);
  }

  private printVersion(): void {
    // In production, this would read from package.json
    console.log('api-to-ts-interface v1.0.0');
    console.log('TypeScript interface generator with Storybook documentation');
    console.log('Built for OpenClaw skill system');
  }
}

// Entry point
if (require.main === module) {
  const cli = new CLI(process.argv.slice(2));
  const exitCode = cli.run();
  process.exit(exitCode);
}

export { CLI };
