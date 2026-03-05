#!/usr/bin/env node

/**
 * Generator Module - Generate TypeScript interfaces from parsed types
 * Usage: generator.ts <parserOutput.json> [--template templates/interface.ts] [--reference references/types.json]
 *
 * Takes parser output and produces formatted TypeScript code with proper types.
 * Applies TypeScript best practices and integrates reference types.
 */

import * as fs from 'fs';
import * as path from 'path';

interface ParsedField {
  name: string;
  type: string;
  required?: boolean;
  description?: string;
}

interface ParsedType {
  name: string;
  kind: 'interface' | 'type' | 'enum';
  fields?: ParsedField[];
  values?: string[];
  extends?: string[];
}

interface ParserOutput {
  types: ParsedType[];
  metadata: {
    source: string;
    timestamp: string;
    rootType: string;
  };
}

interface GeneratorOptions {
  templatePath?: string;
  referencePath?: string;
  outputPath?: string;
  generateStorybook?: boolean;
}

interface ReferenceTypes {
  [key: string]: {
    type: string;
    description?: string;
    example?: any;
  };
}

class CodeGenerator {
  private referenceTypes: ReferenceTypes = {};
  private interfaceTemplate: string = `export interface {{name}} {{extends}} {
{{fields}}
}`;
  private typeTemplate: string = `export type {{name}} = {{values}};`;
  private enumTemplate: string = `export enum {{name}} {
{{values}}
}`;

  constructor(options: GeneratorOptions = {}) {
    if (options.referencePath && fs.existsSync(options.referencePath)) {
      try {
        this.referenceTypes = JSON.parse(fs.readFileSync(options.referencePath, 'utf8'));
      } catch (err) {
        console.warn(`Failed to load reference types: ${err}`);
      }
    }

    if (options.templatePath && fs.existsSync(options.templatePath)) {
      try {
        this.interfaceTemplate = fs.readFileSync(options.templatePath, 'utf8').trim();
      } catch (err) {
        console.warn(`Failed to load template: ${err}`);
      }
    }
  }

  generate(parserOutput: ParserOutput, outputDir?: string): { code: string; files: string[] } {
    const { types } = parserOutput;
    const generatedCode: string[] = [];
    const generatedFiles: string[] = [];

    // Generate imports for reference types
    const imports = this.generateImports(types);
    if (imports) {
      generatedCode.push(imports);
    }

    // Generate each type
    for (const type of types) {
      const code = this.generateType(type);
      if (code) {
        generatedCode.push(code);
        generatedFiles.push(`${type.name}.ts`);
      }
    }

    // Add Storybook definitions if requested
    if (parserOutput.metadata) {
      const storybookTypes = this.generateStorybookTypes(parserOutput);
      if (storybookTypes) {
        generatedCode.push('\n// Storybook documentation types\n' + storybookTypes);
        generatedFiles.push('storybook.types.ts');
      }
    }

    const fullCode = generatedCode.join('\n\n');

    if (outputDir) {
      this.writeFiles(outputDir, fullCode, generatedFiles);
    }

    return {
      code: fullCode,
      files: generatedFiles,
    };
  }

  private generateImports(types: ParsedType[]): string {
    const imports: string[] = [];
    const referencedTypes = new Set<string>();

    for (const type of types) {
      if (type.fields) {
        for (const field of type.fields) {
          if (this.referenceTypes[field.type]) {
            referencedTypes.add(field.type);
          }
        }
      }
    }

    if (referencedTypes.size > 0) {
      imports.push(`// Reference type imports`);
      for (const refType of referencedTypes) {
        if (this.referenceTypes[refType]?.module) {
          imports.push(`import { ${refType} } from '${this.referenceTypes[refType].module}';`);
        }
      }
    }

    return imports.join('\n');
  }

  private generateType(type: ParsedType): string {
    switch (type.kind) {
      case 'interface':
        return this.generateInterface(type);
      case 'type':
        return this.generateTypeAlias(type);
      case 'enum':
        return this.generateEnum(type);
      default:
        return '';
    }
  }

  private generateInterface(type: ParsedType): string {
    const fields = type.fields?.map((field) => {
      const optional = !field.required ? '?' : '';
      const description = field.description ? `\n  /** ${field.description} */\n  ` : '  ';
      return `${description}${field.name}${optional}: ${this.resolveType(field.type)};`;
    }) || [];

    const extendsClause = type.extends && type.extends.length > 0
      ? ` extends ${type.extends.map((e) => this.resolveType(e)).join(', ')}`
      : '';

    return this.interfaceTemplate
      .replace(/{{name}}/g, type.name)
      .replace(/{{extends}}/g, extendsClause)
      .replace(/{{fields}}/g, fields.join('\n'));
  }

  private generateTypeAlias(type: ParsedType): string {
    const values = type.values?.map((v) => v.includes(' ') ? `'${v}'` : v).join(' | ') || 'unknown';

    return this.typeTemplate
      .replace(/{{name}}/g, type.name)
      .replace(/{{values}}/g, values);
  }

  private generateEnum(type: ParsedType): string {
    const values = type.values?.map((v, i) => `  ${v}${i < (type.values?.length || 0) - 1 ? ',' : ''}`).join('\n') || '';

    return this.enumTemplate
      .replace(/{{name}}/g, type.name)
      .replace(/{{values}}/g, values);
  }

  private resolveType(typeName: string): string {
    // Check if it's a reference type with custom mapping
    if (this.referenceTypes[typeName]) {
      return this.referenceTypes[typeName].type || typeName;
    }

    // Handle array types
    if (typeName.endsWith('[]')) {
      const base = typeName.slice(0, -2);
      return `${this.resolveType(base)}[]`;
    }

    // Union types
    if (typeName.includes('|')) {
      return typeName.split('|').map((t) => this.resolveType(t.trim())).join(' | ');
    }

    return typeName;
  }

  private generateStorybookTypes(parserOutput: ParserOutput): string {
    const lines: string[] = [];

    lines.push('// Auto-generated Storybook documentation types');
    lines.push('export interface StorybookTypeDoc {');
    lines.push('  name: string;');
    lines.push('  description?: string;');
    lines.push('  type: string;');
    lines.push('  properties?: StorybookPropertyDoc[];');
    lines.push('  example?: any;');
    lines.push('}');

    lines.push('');
    lines.push('export interface StorybookPropertyDoc {');
    lines.push('  name: string;');
    lines.push('  type: string;');
    lines.push('  required: boolean;');
    lines.push('  description?: string;');
    lines.push('  example?: any;');
    lines.push('}');

    lines.push('');
    lines.push('export const storybookDocs: Record<string, StorybookTypeDoc> = {');

    for (const type of parserOutput.types) {
      if (type.kind === 'interface' && type.fields) {
        lines.push(`  '${type.name}': {`);
        lines.push(`    name: '${type.name}',`);
        lines.push(`    type: 'interface',`);
        if (type.extends) {
          lines.push(`    extends: ['${type.extends.join("', '")}'],`);
        }
        lines.push(`    properties: [`);
        for (let i = 0; i < type.fields.length; i++) {
          const field = type.fields[i];
          lines.push(`      {`);
          lines.push(`        name: '${field.name}',`);
          lines.push(`        type: '${field.type}',`);
          lines.push(`        required: ${field.required},`);
          if (field.description) {
            lines.push(`        description: '${field.description}',`);
          }
          lines.push(`      }${i < type.fields.length - 1 ? ',' : ''}`);
        }
        lines.push(`    ],`);
        lines.push(`  },`);
      }
    }

    lines.push('};');

    return lines.join('\n');
  }

  private writeFiles(outputDir: string, code: string, files: string[]): void {
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Write main output file
    const outputFile = path.join(outputDir, 'generated-interfaces.ts');
    fs.writeFileSync(outputFile, code, 'utf8');
    console.log(`Generated: ${outputFile}`);

    // Optionally write individual files per type (if needed)
    // Currently writing consolidated output only
  }
}

// CLI entry point
function main(): void {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error('Usage: generator.ts <parserOutput.json> [--template <path>] [--reference <path>] [--output <dir>]');
    process.exit(1);
  }

  const inputFile = args[0];
  const options: GeneratorOptions = {};

  // Parse arguments
  for (const arg of args.slice(1)) {
    if (arg.startsWith('--template=')) {
      options.templatePath = arg.split('=')[1];
    } else if (arg.startsWith('--reference=')) {
      options.referencePath = arg.split('=')[1];
    } else if (arg.startsWith('--output=')) {
      options.outputPath = arg.split('=')[1];
    } else if (arg === '--storybook') {
      options.generateStorybook = true;
    }
  }

  try {
    const content = fs.readFileSync(inputFile, 'utf8');
    const parserOutput: ParserOutput = JSON.parse(content);

    const generator = new CodeGenerator(options);
    const result = generator.generate(parserOutput, options.outputPath);

    if (!options.outputPath) {
      console.log(result.code);
    }

    console.log(`Files generated: ${result.files.join(', ')}`);
  } catch (err) {
    console.error('Generator error:', err);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { CodeGenerator, ParsedType, ParsedField, ParserOutput, GeneratorOptions };
