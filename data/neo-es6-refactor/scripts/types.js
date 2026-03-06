#!/usr/bin/env node
/**
 * TypeScript-specific refactoring transformations
 * Usage (as library): const { refactorTypeScript } = require('./types');
 */

const { refactorCode } = require('./refactor');
const t = require('@babel/types');

// TypeScript-specific transformation: convert simple interfaces to type aliases
function tsInterfaceToType(path) {
  const node = path.node;
  if (node.type !== 'TSInterfaceDeclaration') return;
  // Skip if extends other interfaces
  if (node.extends && node.extends.length > 0) return;
  // Check for method signatures, call/construct signatures, index signatures
  if (node.body && node.body.body) {
    for (const element of node.body.body) {
      const type = element.type;
      if (type === 'TSMethodSignature' || type === 'TSCallSignature' || type === 'TSConstructSignature' || type === 'TSIndexSignature') {
        return;
      }
    }
  }

  // Collect TSPropertySignature elements
  const properties = [];
  for (const element of node.body.body) {
    if (element.type === 'TSPropertySignature') {
      properties.push(t.cloneNode(element));
    }
  }

  // Build TSObjectType from the property signatures
  const objectType = t.tsObjectType(properties);
  // Create a type alias: type <id> = <objectType>
  const typeAlias = t.tsTypeAlias(node.id, node.typeParameters, objectType);
  path.replaceWith(typeAlias);
}

function refactorTypeScript(code, options = {}) {
  // Ensure TypeScript parser plugin
  const parserPlugins = Array.isArray(options.parserPlugins) ? [...options.parserPlugins] : [];
  if (!parserPlugins.includes('typescript')) {
    parserPlugins.push('typescript');
  }
  // Also include common modern TypeScript/ES features if not already present
  const additionalPlugins = ['classProperties', 'decorators-legacy', 'optionalChaining', 'nullishCoalescingOperator'];
  for (const plugin of additionalPlugins) {
    if (!parserPlugins.includes(plugin)) {
      parserPlugins.push(plugin);
    }
  }

  // Add TypeScript-specific visitors
  const extraVisitors = {
    TSInterfaceDeclaration: tsInterfaceToType
  };

  // Use the common refactor engine with extra visitors
  return refactorCode(code, {
    ...options,
    parserPlugins,
    extraVisitors
  });
}

module.exports = { refactorTypeScript };