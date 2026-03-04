#!/usr/bin/env node

/**
 * Parser Module - Extract TypeScript type definitions from API responses
 * Usage: parser.ts <inputFile> [--hint schema.json]
 *
 * Reads JSON/XML API responses and recursively infers TypeScript types.
 * Outputs parsed type definitions as JSON to stdout.
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

class APIParser {
  private visited: Set<string> = new Set();
  private typeCounter: Map<string, number> = new Map();
  private referenceTypes: Record<string, any> = {};

  constructor(private hints?: any) {
    if (hints) {
      this.referenceTypes = hints;
    }
  }

  parse(data: any, rootName: string = 'ApiResponse'): ParserOutput {
    this.visited.clear();
    this.typeCounter.clear();

    const rootType = this.inferType(data, rootName, true);
    const types = this.collectTypes();

    return {
      types,
      metadata: {
        source: 'parser',
        timestamp: new Date().toISOString(),
        rootType,
      },
    };
  }

  private inferType(value: any, name: string, isRoot: boolean = false): string {
    if (value === null || value === undefined) {
      return 'any';
    }

    const typeStr = typeof value;

    if (typeStr === 'string') {
      // Try to infer more specific types
      if (this.isISO8601(value)) return 'Date';
      if (this.isEmail(value)) return 'string'; // could be Email type if desired
      return 'string';
    }

    if (typeStr === 'number') {
      if (Number.isInteger(value)) return 'number';
      return 'number'; // could distinguish float
    }

    if (typeStr === 'boolean') {
      return 'boolean';
    }

    if (Array.isArray(value)) {
      if (value.length === 0) {
        return 'any[]';
      }
      const elementType = this.inferType(value[0], `${name}Item`);
      return `${elementType}[]`;
    }

    if (typeStr === 'object') {
      // Check if it matches a reference type
      const refTypeName = this.matchReferenceType(value);
      if (refTypeName) {
        return refTypeName;
      }

      // Generate interface name
      const ifaceName = this.generateUniqueName(name);

      // Avoid re-parsing same structure (circular reference handling)
      const fingerprint = this.getFingerprint(value);
      if (this.visited.has(fingerprint)) {
        return ifaceName;
      }
      this.visited.add(fingerprint);

      // Parse object structure
      const fields: ParsedField[] = [];
      for (const [key, val] of Object.entries(value)) {
        const fieldType = this.inferType(val, this.toPascalCase(key));
        const required = val !== null && val !== undefined;

        fields.push({
          name: key,
          type: fieldType,
          required,
        });
      }

      // Store type for later collection
      if (!this.typeCounter.has(ifaceName)) {
        this.typeCounter.set(ifaceName, 0);
      }
      const count = this.typeCounter.get(ifaceName)! + 1;
      this.typeCounter.set(ifaceName, count);

      // Only add if first occurrence (avoid duplicates)
      if (count === 1) {
        this.addType({
          name: ifaceName,
          kind: 'interface',
          fields,
        });
      }

      // Process nested objects recursively (already handled in inferType calls)
      return ifaceName;
    }

    return 'any';
  }

  private generateUniqueName(base: string): string {
    const pascal = this.toPascalCase(base);
    const count = this.typeCounter.get(pascal) || 0;
    return count === 0 ? pascal : `${pascal}${count}`;
  }

  private toPascalCase(str: string): string {
    return str
      .replace(/([-_][a-z])/g, (g) => g.toUpperCase().replace('-', '').replace('_', ''))
      .replace(/^[a-z]/, (c) => c.toUpperCase())
      .replace(/[^a-zA-Z0-9]/g, '');
  }

  private isISO8601(str: string): boolean {
    return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$/.test(str);
  }

  private isEmail(str: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str);
  }

  private matchReferenceType(obj: any): string | null {
    // Simple heuristic matching against reference types
    for (const [name, schema] of Object.entries(this.referenceTypes)) {
      if (this.structurallyMatches(obj, schema)) {
        return name;
      }
    }
    return null;
  }

  private structurallyMatches(obj: any, schema: any): boolean {
    if (!schema || typeof schema !== 'object') return false;

    const objKeys = Object.keys(obj);
    const schemaKeys = Object.keys(schema);

    // All schema keys must exist in object
    if (!schemaKeys.every((k) => objKeys.includes(k))) {
      return false;
    }

    // Basic type matching
    for (const key of schemaKeys) {
      const expectedType = schema[key];
      const actualValue = obj[key];

      if (expectedType === 'string' && typeof actualValue !== 'string') return false;
      if (expectedType === 'number' && typeof actualValue !== 'number') return false;
      if (expectedType === 'boolean' && typeof actualValue !== 'boolean') return false;
      if (expectedType === 'array' && !Array.isArray(actualValue)) return false;
      if (expectedType === 'object' && typeof actualValue !== 'object') return false;
    }

    return true;
  }

  private getFingerprint(obj: any): string {
    const keys = Object.keys(obj).sort();
    const parts: string[] = [];
    for (const key of keys) {
      const val = obj[key];
      const valType = val === null ? 'null' : typeof val;
      parts.push(`${key}:${valType}`);
    }
    return `{${parts.join('|')}}`;
  }

  private types: ParsedType[] = [];
  private typeMap: Map<string, ParsedType> = new Map();

  private addType(type: ParsedType): void {
    if (!this.typeMap.has(type.name)) {
      this.typeMap.set(type.name, type);
      this.types.push(type);
    }
  }

  private collectTypes(): ParsedType[] {
    // Sort types: interfaces first, then dependent types
    return this.types.sort((a, b) => {
      // Root type first
      if (a.name === 'ApiResponse') return -1;
      if (b.name === 'ApiResponse') return 1;

      // Types referenced by others should come after dependents
      const aRefCount = this.types.filter((t) => t.fields?.some((f) => f.type === a.name)).length;
      const bRefCount = this.types.filter((t) => t.fields?.some((f) => f.type === b.name)).length;
      return aRefCount - bRefCount;
    });
  }
}

// CLI entry point
function main(): void {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error('Usage: parser.ts <inputFile> [--hint schema.json]');
    process.exit(1);
  }

  const inputFile = args[0];
  const hintFile = args.find((arg) => arg.startsWith('--hint='))?.split('=')[1];

  let hints: any = {};
  if (hintFile && fs.existsSync(hintFile)) {
    try {
      hints = JSON.parse(fs.readFileSync(hintFile, 'utf8'));
    } catch (err) {
      console.warn(`Failed to load hints from ${hintFile}:`, err);
    }
  }

  try {
    const content = fs.readFileSync(inputFile, 'utf8');
    let data: any;

    // Try to parse as JSON
    try {
      data = JSON.parse(content);
    } catch {
      // For XML, would need additional parser - for now, try to extract JSON-like structure
      console.error('Only JSON input is currently supported');
      process.exit(1);
    }

    const parser = new APIParser(hints);
    const result = parser.parse(data);

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('Parser error:', err);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { APIParser, ParsedType, ParsedField, ParserOutput };
