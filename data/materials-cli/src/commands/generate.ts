import chalk from 'chalk';
import inquirer from 'inquirer';
import { renderSchema } from '../utils/canvas.js';

export interface GenerateOptions {
  output?: string;
  format?: string;
  width?: string;
  height?: string;
  outputSchema?: string;
  model?: string;
  apiKey?: string;
  baseUrl?: string;
  interactive?: boolean;
}

export async function generateCommand(
  promptArg: string | undefined,
  options: GenerateOptions
): Promise<void> {
  let prompt = promptArg;

  if (!prompt && !options.interactive) {
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'prompt',
        message: 'Describe the image to generate:',
        validate: (input: string) => input.trim().length > 0 || 'Prompt cannot be empty',
      },
    ]);
    prompt = answers.prompt;
  }

  if (options.interactive && !prompt) {
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'prompt',
        message: 'Describe the image to generate:',
        validate: (input: string) => input.trim().length > 0 || 'Prompt cannot be empty',
      },
    ]);
    prompt = answers.prompt;
  }

  if (!prompt || !prompt.trim()) {
    console.error(chalk.red('Error:') + ' Prompt is required');
    process.exit(1);
  }

  const apiKey = options.apiKey || process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error(chalk.red('Error:') + ' OPENAI_API_KEY is required for generate. Set it in env or use --api-key.');
    process.exit(1);
  }

  let schema: object;
  try {
    const agents = await import('materials-agents');
    const generateSchema = (agents as any).generateSchema ?? (agents as any).default?.generateSchema;
    if (typeof generateSchema !== 'function') {
      console.error(chalk.red('Error:') + ' materials-agents does not export generateSchema. Install materials-agents for AI generate.');
      process.exit(1);
    }
    schema = await generateSchema(prompt.trim(), {
      apiKey,
      model: options.model || process.env.OPENAI_MODEL,
      baseUrl: options.baseUrl || process.env.OPENAI_BASE_URL,
    });
  } catch (err: any) {
    if (err?.code === 'MODULE_NOT_FOUND' || err?.message?.includes('materials-agents')) {
      console.error(chalk.red('Error:') + ' materials-agents not installed. Run: pnpm add materials-agents');
      console.error(chalk.gray('  Then use OPENAI_API_KEY and run: materials generate "<prompt>"'));
      process.exit(1);
    }
    throw err;
  }

  const outputPath = options.output || './output.png';
  const format = (options.format as 'png' | 'jpg') || 'png';
  const width = options.width ? parseInt(options.width, 10) : (schema as any)?.width ?? 800;
  const height = options.height ? parseInt(options.height, 10) : (schema as any)?.height ?? 600;

  console.log(chalk.blue('Rendering generated schema to:'), outputPath);
  try {
    await renderSchema({
      schemaData: schema,
      outputPath,
      format,
      width,
      height,
    });
    console.log(chalk.green('✓') + ` Image rendered: ${outputPath}`);
  } catch (error) {
    console.error(chalk.red('Error:'), error instanceof Error ? error.message : String(error));
    process.exit(1);
  }

  if (options.outputSchema) {
    const { writeFile } = await import('fs/promises');
    await writeFile(options.outputSchema, JSON.stringify(schema, null, 2), 'utf-8');
    console.log(chalk.green('✓') + ` Schema saved: ${options.outputSchema}`);
  }
}
