#!/usr/bin/env node
/**
 * GraphQL TypeScript Generator - Utilities
 * Provides GraphQL schema parsing utilities
 */

import { parse, buildASTSchema, GraphQLSchema, GraphQLObjectType, GraphQLInterfaceType, GraphQLUnionType, GraphQLEnumType, GraphQLScalarType, GraphQLFieldConfigMap, GraphQLInputObjectType, GraphQLArgument} from 'graphql';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';

/**
 * Read and parse a GraphQL schema file
 */
export function loadSchema(schemaPath: string): GraphQLSchema {
  if (!existsSync(schemaPath)) {
    throw new Error(`Schema file not found: ${schemaPath}`);
  }

  const schemaText = readFileSync(schemaPath, 'utf-8');
  return buildASTSchema(parse(schemaText));
}

/**
 * Check if a type is a built-in scalar
 */
export function isBuiltInScalar(typeName: string): boolean {
  const builtIns = ['Int', 'Float', 'String', 'Boolean', 'ID'];
  return builtIns.includes(typeName);
}

/**
 * Get the underlying named type from a possibly-wrapped type
 */
export function unwrapType(type: any): any {
  if (type.ofType) {
    return unwrapType(type.ofType);
  }
  return type;
}

/**
 * Get TypeScript type string from GraphQL type
 */
export function graphQLTypeToTS(type: any, schema: GraphQLSchema, nullable: boolean = true): string {
  const unwrapped = unwrapType(type);
  const typeName = unwrapped.name;

  if (isBuiltInScalar(typeName)) {
    const scalarMap: Record<string, string> = {
      'Int': 'number',
      'Float': 'number',
      'String': 'string',
      'Boolean': 'boolean',
      'ID': 'string'
    };
    let tsType = scalarMap[typeName] || 'any';
    if (nullable && !unwrapped.astNode?.loc?.source?.name?.includes('Non-Null')) {
      tsType += ' | null';
    }
    return tsType;
  }

  // Check if it's an object, interface, enum, union, or input type
  const objectType = schema.getType(typeName);
  if (!objectType) {
    return 'any';
  }

  if (objectType instanceof GraphQLEnumType) {
    let tsType = typeName;
    if (nullable) tsType += ' | null';
    return tsType;
  }

  if (objectType instanceof GraphQLUnionType) {
    let tsType = typeName;
    if (nullable) tsType += ' | null';
    return tsType;
  }

  // For objects, interfaces, and input types
  let tsType = typeName;
  if (nullable) tsType += ' | null';
  return tsType;
}

/**
 * Generate a valid TypeScript identifier from a name
 */
export function sanitizeIdentifier(name: string): string {
  // GraphQL names are already valid TS identifiers usually, but handle edge cases
  return name.replace(/[^a-zA-Z0-9_$]/g, '_');
}

/**
 * Format document comment for TypeScript
 */
export function formatDescription(description?: string): string {
  if (!description) return '';
  const lines = description.trim().split('\n');
  const comment = lines.map(line => ` * ${line}`).join('\n');
  return `/**\n${comment}\n */\n`;
}

/**
 * Capitalize first letter
 */
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Check if a string is a valid GraphQL name
 */
export function isValidGraphQLName(name: string): boolean {
  return /^[_a-zA-Z][_a-zA-Z0-9]*$/.test(name);
}
