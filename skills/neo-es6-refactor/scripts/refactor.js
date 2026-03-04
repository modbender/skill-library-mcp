#!/usr/bin/env node
/**
 * Core refactoring engine for JavaScript
 * Usage (as library): const { refactorCode } = require('./refactor');
 */

const { parse } = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generate = require('@babel/generator').default;
const t = require('@babel/types');
const path = require('path');
const fs = require('fs');

// Default built-in transformation rules
const BUILT_IN_RULES = {
  varToLet: {
    visitor: {
      VariableDeclaration(path) {
        if (path.node.kind === 'var') {
          path.node.kind = 'let';
        }
      }
    }
  },
  functionToArrow: {
    visitor: {
      FunctionExpression(path) {
        const parent = path.parent;
        if (!parent) return;
        // Skip if it's a method (inside object literal or class)
        if (parent.type === 'ObjectProperty' || parent.type === 'ObjectMethod' || parent.type === 'MethodDefinition' || parent.type === 'ClassMethod' || parent.type === 'ClassPrivateMethod') {
          return;
        }
        // Check for this, arguments, super, generator
        let hasThis = false;
        let hasArguments = false;
        let hasSuper = false;
        path.traverse({
          ThisExpression() { hasThis = true; },
          Identifier(id) {
            if (id.node.name === 'arguments') hasArguments = true;
            if (id.node.name === 'super') hasSuper = true;
          }
        });
        if (hasThis || hasArguments || hasSuper) return;
        if (path.node.generator) return;

        // Convert to arrow function
        const params = path.node.params.map(p => t.cloneNode(p));
        const body = path.node.body ? t.cloneNode(path.node.body) : t.blockStatement([]);
        const arrow = t.arrowFunctionExpression(params, body);
        arrow.async = !!path.node.async;
        if (path.node.rest) {
          arrow.rest = t.cloneNode(path.node.rest);
        }
        if (path.node.defaults) {
          arrow.defaults = path.node.defaults.map(d => t.cloneNode(d));
        }
        if (path.node.typeParameters) {
          arrow.typeParameters = t.cloneNode(path.node.typeParameters);
        }
        path.replaceWith(arrow);
      }
    }
  },
  objectShorthand: {
    visitor: {
      ObjectExpression(path) {
        for (const prop of path.node.properties) {
          if (prop.type === 'ObjectProperty' && !prop.shorthand && !prop.computed) {
            const key = prop.key;
            const value = prop.value;
            if (t.isIdentifier(key) && t.isIdentifier(value) && key.name === value.name) {
              prop.shorthand = true;
            }
          }
        }
      }
    }
  },
  templateLiteral: {
    visitor: {
      BinaryExpression(path) {
        if (path.node.operator !== '+') return;

        // Helper to flatten concatenation chain
        const flatten = (node) => {
          if (node.type === 'BinaryExpression' && node.operator === '+') {
            return [...flatten(node.left), ...flatten(node.right)];
          }
          if (t.isStringLiteral(node)) {
            return [{ type: 'string', value: node.value }];
          }
          return [{ type: 'expression', node }];
        };

        const parts = flatten(path.node);
        if (parts.length === 0) return;

        // Build template literal: alternating quasis and expressions
        let quasis = [];
        let expressions = [];
        let currentQuasi = '';

        for (const part of parts) {
          if (part.type === 'string') {
            currentQuasi += part.value;
          } else {
            quasis.push(t.templateElement({ raw: currentQuasi, cooked: currentQuasi }, false));
            expressions.push(t.cloneNode(part.node));
            currentQuasi = '';
          }
        }
        quasis.push(t.templateElement({ raw: currentQuasi, cooked: currentQuasi }, true));

        const template = t.templateLiteral(quasis, expressions);
        path.replaceWith(template);
      }
    }
  }
};

// Load ES6 features matrix (optional)
let ES6_FEATURES = {};
try {
  const featuresPath = path.resolve(__dirname, '../references/es6-features.json');
  ES6_FEATURES = JSON.parse(fs.readFileSync(featuresPath, 'utf8'));
} catch (e) {
  // Silently ignore if file missing
}

// Load enabled patterns from patterns.json (optional)
function loadPatternsFromFile() {
  try {
    const patternsPath = path.resolve(__dirname, '../references/patterns.json');
    const data = fs.readFileSync(patternsPath, 'utf8');
    const parsed = JSON.parse(data);
    if (Array.isArray(parsed)) {
      return parsed;
    } else if (parsed.enabledRules && Array.isArray(parsed.enabledRules)) {
      return parsed.enabledRules;
    } else {
      console.warn('patterns.json format not recognized; using defaults');
      return null;
    }
  } catch (e) {
    return null;
  }
}

function getEnabledRules(overrides) {
  if (overrides && Array.isArray(overrides)) {
    return overrides;
  }
  const fileRules = loadPatternsFromFile();
  if (fileRules) {
    return fileRules;
  }
  return Object.keys(BUILT_IN_RULES);
}

function refactorCode(code, options = {}) {
  const parserPlugins = options.parserPlugins || [];

  // Parse with Babel
  const ast = parse(code, {
    sourceType: 'module',
    plugins: parserPlugins
  });

  const enabledRuleNames = getEnabledRules(options.rules);
  const visitor = {};

  // Start with built-in rules
  enabledRuleNames.forEach(ruleName => {
    const rule = BUILT_IN_RULES[ruleName];
    if (rule && rule.visitor) {
      Object.assign(visitor, rule.visitor);
    } else {
      console.warn(`Rule '${ruleName}' not found or missing visitor.`);
    }
  });

  // Merge extra visitors if provided (for TypeScript-specific transforms)
  if (options.extraVisitors && typeof options.extraVisitors === 'object') {
    Object.assign(visitor, options.extraVisitors);
  }

  traverse(ast, visitor);

  const generateOptions = {
    retainLines: false,
    comments: true,
    compact: false,
    sourceMaps: false
  };
  let output = generate(ast, generateOptions).code;

  // Format with Prettier unless disabled
  if (options.format !== false) {
    try {
      const prettier = require('prettier');
      const parser = parserPlugins.includes('typescript') ? 'typescript' : 'babel';
      output = prettier.format(output, {
        parser,
        semi: true,
        singleQuote: true,
        trailingComma: 'es5',
        printWidth: 80
      });
    } catch (e) {
      // Prettier not available or formatting failed; continue with unformatted
    }
  }

  return output;
}

module.exports = { refactorCode, BUILT_IN_RULES };