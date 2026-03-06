import chalk from 'chalk';
import inquirer from 'inquirer';
import { renderSchema, loadSchema, saveSchema } from '../utils/canvas.js';

export interface RenderOptions {
  schema?: string;
  output?: string;
  format?: string;
  width?: string;
  height?: string;
  outputSchema?: string;
  interactive?: boolean;
}

export async function renderCommand(schemaArg: string | undefined, options: RenderOptions): Promise<void> {
  let schemaPath = schemaArg || options.schema;
  let schemaData: object | undefined;

  if (!schemaPath && !options.interactive) {
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'schemaPath',
        message: 'Enter path to the JSON schema file:',
        validate: (input: string) => input.trim().length > 0 || 'Schema path cannot be empty'
      }
    ]);
    schemaPath = answers.schemaPath;
  }

  if (options.interactive && !schemaPath) {
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'schemaPath',
        message: 'Enter path to the JSON schema file:',
        validate: (input: string) => input.trim().length > 0 || 'Schema path cannot be empty'
      }
    ]);
    schemaPath = answers.schemaPath;
  }

  if (!schemaPath) {
    console.error(chalk.red('Error:') + ' Schema file path is required');
    process.exit(1);
  }

  console.log(chalk.blue('Loading schema from:'), schemaPath);

  try {
    schemaData = await loadSchema(schemaPath);
  } catch (error) {
    console.error(chalk.red('Failed to load schema:'), error instanceof Error ? error.message : String(error));
    process.exit(1);
  }

  const outputPath = options.output || './output.png';
  const format = (options.format as 'png' | 'jpg') || 'png';
  // Use schema dimensions if width/height not explicitly provided
  const width = options.width ? parseInt(options.width, 10) : ((schemaData as any)?.width || 800);
  const height = options.height ? parseInt(options.height, 10) : ((schemaData as any)?.height || 600);

  console.log(chalk.blue('Rendering to:'), outputPath);
  console.log(chalk.gray(`  Format: ${format}`));
  console.log(chalk.gray(`  Size: ${width}x${height}`));

  try {
    await renderSchema({
      schemaPath,
      outputPath,
      format,
      width,
      height,
    });
    console.log(chalk.green('✓') + ` Image rendered successfully: ${outputPath}`);
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    const errorMessage = err.message;
    console.error(chalk.red('Error:'), errorMessage);
    if (err.stack) {
      console.error(chalk.gray('\nDetails:'));
      console.error(chalk.gray(err.stack));
    }
    if (errorMessage.includes('node-canvas') || errorMessage.includes('canvas')) {
      console.error(chalk.yellow('\nTroubleshooting:'));
      console.error('  https://github.com/Automattic/node-canvas#installation');
    }
    process.exit(1);
  }

  if (options.outputSchema) {
    try {
      await saveSchema(schemaData, options.outputSchema);
      console.log(chalk.green('✓') + ` Schema saved to: ${options.outputSchema}`);
    } catch (error) {
      console.error(chalk.red('Failed to save schema:'), error instanceof Error ? error.message : String(error));
    }
  }
}
