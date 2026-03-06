#!/usr/bin/env node

import { Command } from 'commander';
import { renderCommand } from './commands/render.js';
import { validateCommand } from './commands/validate.js';

const program = new Command();

program
  .name('materials')
  .description('Render JSON schemas to images, validate schemas, or generate from prompts')
  .version('1.0.0');

program
  .command('render [schema]')
  .description('Render a JSON schema file to an image')
  .option('-s, --schema <path>', 'Path to schema file')
  .option('-o, --output <path>', 'Output image path', './output.png')
  .option('-f, --format <png|jpg>', 'Output format', 'png')
  .option('-w, --width <px>', 'Canvas width')
  .option('-h, --height <px>', 'Canvas height')
  .option('--output-schema <path>', 'Save normalized schema to path')
  .option('-i, --interactive', 'Prompt for inputs')
  .action(async (schemaArg: string | undefined, options) => {
    await renderCommand(schemaArg, options);
  });

program
  .command('validate [schema]')
  .description('Validate a schema against the render data schema')
  .option('-s, --schema <path>', 'Path to schema file')
  .option('-i, --interactive', 'Prompt for schema path')
  .action(async (schemaArg: string | undefined, options) => {
    await validateCommand(schemaArg, options);
  });

program
  .command('generate [prompt]')
  .description('Use AI to generate a schema from a prompt, then render')
  .option('-o, --output <path>', 'Output image path', './output.png')
  .option('-f, --format <png|jpg>', 'Output format', 'png')
  .option('-w, --width <px>', 'Canvas width')
  .option('-h, --height <px>', 'Canvas height')
  .option('--output-schema <path>', 'Save generated schema to path')
  .option('--model <name>', 'OpenAI model')
  .option('--api-key <key>', 'OpenAI API key')
  .option('--base-url <url>', 'OpenAI API base URL')
  .option('-i, --interactive', 'Prompt for inputs')
  .action(async (promptArg: string | undefined, options) => {
    const mod = await import('./commands/generate.js');
    await mod.generateCommand(promptArg, options);
  });

program.parse();
