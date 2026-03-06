import chalk from 'chalk';
import inquirer from 'inquirer';
import { loadSchema } from '../utils/canvas.js';

interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

const RENDER_DATA_SCHEMA_FIELDS = {
  RenderData: ['id', 'width', 'height', 'layers'],
  TextRenderData: ['id', 'type', 'x', 'y', 'width', 'height', 'content', 'style'],
  ImgRenderData: ['id', 'type', 'x', 'y'],
  ContainerRenderData: ['id', 'type', 'layers'],
  ShapeRenderData: ['id', 'type', 'shapes'],
};

function validateValue(value: unknown, path: string): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (value === null || value === undefined) {
    errors.push(`${path}: value is null or undefined`);
    return { valid: false, errors, warnings };
  }

  if (typeof value === 'object') {
    if (Array.isArray(value)) {
      if (value.length === 0) {
        warnings.push(`${path}: array is empty`);
      }
      for (let i = 0; i < value.length; i++) {
        const itemResult = validateValue(value[i], `${path}[${i}]`);
        errors.push(...itemResult.errors);
        warnings.push(...itemResult.warnings);
      }
    } else {
      const obj = value as Record<string, unknown>;

      // Check for required fields based on type
      const type = obj.type as string;
      if (type && RENDER_DATA_SCHEMA_FIELDS[type as keyof typeof RENDER_DATA_SCHEMA_FIELDS]) {
        const requiredFields = RENDER_DATA_SCHEMA_FIELDS[type as keyof typeof RENDER_DATA_SCHEMA_FIELDS];
        for (const field of requiredFields) {
          if (!(field in obj)) {
            errors.push(`${path}: missing required field "${field}" for type "${type}"`);
          }
        }
      }

      // Validate field types
      if ('x' in obj && typeof obj.x !== 'number') {
        errors.push(`${path}.x: must be a number`);
      }
      if ('y' in obj && typeof obj.y !== 'number') {
        errors.push(`${path}.y: must be a number`);
      }
      if ('width' in obj && typeof obj.width !== 'number') {
        errors.push(`${path}.width: must be a number`);
      }
      if ('height' in obj && typeof obj.height !== 'number') {
        errors.push(`${path}.height: must be a number`);
      }
      if ('rotate' in obj && typeof obj.rotate !== 'number') {
        errors.push(`${path}.rotate: must be a number`);
      }
      if ('layers' in obj && !Array.isArray(obj.layers)) {
        errors.push(`${path}.layers: must be an array`);
      } else if ('layers' in obj && Array.isArray(obj.layers)) {
        for (let i = 0; i < obj.layers.length; i++) {
          const layerResult = validateValue(obj.layers[i], `${path}.layers[${i}]`);
          errors.push(...layerResult.errors);
          warnings.push(...layerResult.warnings);
        }
      }
    }
  } else if (typeof value === 'string') {
    if (value.trim().length === 0) {
      warnings.push(`${path}: string is empty`);
    }
  }

  return { valid: errors.length === 0, errors, warnings };
}

function validateSchema(schema: unknown): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!schema || typeof schema !== 'object') {
    errors.push('Schema must be an object');
    return { valid: false, errors, warnings };
  }

  const obj = schema as Record<string, unknown>;

  // Check top-level fields
  if (!obj.id) {
    errors.push('Schema missing required field: "id"');
  }

  if (!obj.width) {
    errors.push('Schema missing required field: "width"');
  } else if (typeof obj.width !== 'number') {
    errors.push('Schema field "width" must be a number');
  }

  if (!obj.height) {
    errors.push('Schema missing required field: "height"');
  } else if (typeof obj.height !== 'number') {
    errors.push('Schema field "height" must be a number');
  }

  if (!obj.layers) {
    errors.push('Schema missing required field: "layers"');
  } else if (!Array.isArray(obj.layers)) {
    errors.push('Schema field "layers" must be an array');
  } else {
    // Validate each layer
    for (let i = 0; i < obj.layers.length; i++) {
      const layer = obj.layers[i];
      const layerResult = validateValue(layer, `layers[${i}]`);
      errors.push(...layerResult.errors);
      warnings.push(...layerResult.warnings);

      // Check for type field
      if (layer && typeof layer === 'object') {
        const layerObj = layer as Record<string, unknown>;
        if (!layerObj.type) {
          errors.push(`layers[${i}]: missing required field "type"`);
        }
      }
    }
  }

  return { valid: errors.length === 0, errors, warnings };
}

export interface ValidateOptions {
  schema?: string;
  interactive?: boolean;
}

export async function validateCommand(schemaArg: string | undefined, options: ValidateOptions): Promise<void> {
  let schemaPath = schemaArg || options.schema;

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

  console.log(chalk.blue('Validating schema:'), schemaPath);

  let schema: object;
  try {
    schema = await loadSchema(schemaPath);
  } catch (error) {
    console.error(chalk.red('Failed to load schema:'), error instanceof Error ? error.message : String(error));
    process.exit(1);
  }

  const result = validateSchema(schema);

  if (result.valid) {
    console.log(chalk.green('✓') + ' Schema is valid');
  } else {
    console.log(chalk.red('✗') + ' Schema validation failed');
  }

  if (result.errors.length > 0) {
    console.log(chalk.red('\nErrors:'));
    for (const error of result.errors) {
      console.log(chalk.red('  - ') + error);
    }
  }

  if (result.warnings.length > 0) {
    console.log(chalk.yellow('\nWarnings:'));
    for (const warning of result.warnings) {
      console.log(chalk.yellow('  - ') + warning);
    }
  }

  if (!result.valid) {
    process.exit(1);
  }
}
