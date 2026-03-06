---
name: es6-refactor
description: Automatically refactor JavaScript/TypeScript code to use modern ES6+ patterns and features
---

# Skill: ES6 Refactor

## 1. Description

ES6 Refactor is a code transformation tool that automatically modernizes JavaScript and TypeScript codebases. It converts legacy patterns (var declarations, callbacks, CommonJS) to modern ES6+ equivalents (let/const, async/await, ES modules) while preserving functionality and improving readability.

The skill integrates seamlessly with OpenClaw agent workflows, providing both a CLI for direct use and an API for programmatic access. It's designed for developers who need to upgrade codebases quickly without manual refactoring, ensuring consistency and adherence to modern best practices.

## 2. Core Capabilities

### Syntax Modernization
- Convert `var` declarations to `let` or `const` based on reassignment analysis
- Transform traditional function expressions to arrow functions where appropriate
- Replace string concatenation with template literals
- Convert `for` loops to array methods (`map`, `filter`, `reduce`, `forEach`)
- Modernize object manipulation (computed properties, shorthand methods, destructuring)
- Update conditional patterns (ternary operators, optional chaining, nullish coalescing)

### Module System Transformation
- Convert CommonJS `require()` to ES module `import` statements
- Transform `module.exports` to `export`/`export default` syntax
- Deduplicate and organize imports automatically
- Handle dynamic imports for conditional loading
- Preserve named exports and re-exports

### TypeScript Support
- Preserve type annotations during refactoring
- Improve interface definitions (convert to `type` aliases when appropriate, use generics)
- Enhance type inference opportunities
- Handle JSX syntax for React/TypeScript files
- Maintain declaration file (`.d.ts`) compatibility

### Code Quality Guarantees
- Output code passes syntax validation via AST parsing
- Preserve original comments and formatting where possible
- Generate properly indented, formatted output consistent with Prettier standards
- Maintain 100% functional equivalence (no behavior changes)
- Provide transformation logging for audit trails

### Integration Features
- **CLI Interface**: Accept files via stdin or file paths, output to stdout or files
- **Agent Mode**: Structured input/output for OpenClaw workflow integration
- **Dry Run**: Preview changes without writing files
- **Diff Output**: Show unified diffs of transformations
- **Configuration**: Customizable transformation rules via JSON config

## 3. Out of Scope

The following are explicitly NOT supported:

- **Performance optimization**: Only syntax transformations; no algorithmic improvements
- **Framework patterns**: No React hooks, Vue 3 composition API, Angular-specific patterns
- **Non-JS/TS files**: CSS, HTML, JSON, configuration files are ignored
- **Architectural changes**: No restructuring of project layout or module boundaries
- **Testing**: No test generation, test migration, or validation execution
- **Documentation**: No JSDoc generation or comment enhancement
- **Minification**: Output remains human-readable
- **Polyfills**: No runtime compatibility additions

## 4. Trigger Scenarios

### Natural Language Triggers
- "Refactor this code to use modern JavaScript"
- "Convert this to ES6+ syntax"
- "Update this JavaScript to use arrow functions and destructuring"
- "Modernize this TypeScript code"
- "Automatically refactor legacy JavaScript patterns"
- "Convert CommonJS to ES modules"
- "Replace var with let/const throughout this code"
- "Transform async callbacks to promises/async-await"
- "Upgrade this codebase to ES2020"

### CLI Commands
```bash
# Refactor a single file
es6-refactor input.js --output output.js

# Refactor with stdin/stdout
cat legacy.js | es6-refactor > modern.js

# Dry run with diff
es6-refactor src/ --dry-run --diff

# Agent mode (used by OpenClaw)
es6-refactor --mode=agent --input=stdin --output=json

# TypeScript-specific transformations
es6-refactor component.tsx --typescript --strict

# Batch processing with glob
es6-refactor "src/**/*.js" --output "modernized/{filename}"
```

### Agent API
```json
{
  "action": "refactor",
  "code": "var x = 1; function foo() { return x; }",
  "language": "javascript",
  "target": "es2020",
  "options": {
    "preserveComments": true,
    "formatOutput": true
  }
}
```

## 5. Required Resources

### Script Dependencies
- **@babel/core**: AST parsing and code generation
- **@babel/parser**: JavaScript/TypeScript parser with JSX support
- **@babel/traverse**: AST traversal for transformation passes
- **@babel/generator**: Code generation from transformed AST
- **@babel/preset-env**: Feature detection and polyfill guidance
- **@babel/types**: AST node type definitions
- **prettier**: Code formatting consistency
- **commander**: CLI argument parsing
- **glob**: File pattern matching for batch operations
- **recast**: AST manipulation with source map preservation (optional)

### Reference Data
- **references/patterns.json**: Legacy-to-modern transformation rules
  ```json
  {
    "var-to-const": {
      "pattern": "var {identifier} = {value}",
      "replace": "const {identifier} = {value}",
      "conditions": ["no-reassignment"]
    },
    "callback-to-promise": {
      "pattern": "{func}(arg, function(result) { {body} })",
      "replace": "async function wrapper() { const result = await {func}(arg); {body} }"
    }
  }
  ```
- **references/es6-features.json**: Feature compatibility matrix by Node/Browser version
  ```json
  {
    "optional-chaining": {
      "introduced": "ES2020",
      "node": "14.0.0",
      "browsers": ["Chrome 80+", "Firefox 74+", "Safari 13.1+"]
    }
  }
  ```

### Testing Assets
- **assets/examples/**/*.js: Sample legacy code files for validation
- **assets/**/*.d.ts: TypeScript definition files for type checking
- **tests/**/*.test.js: Unit tests for each transformation rule

### Node.js Runtime
- Minimum Node.js version: 14.x (for optional chaining support)
- Recommended: 18.x or higher (full ES2022 support)

## 6. Technical Implementation Notes

### Transformation Pipeline
1. **Parse**: Use Babel parser to generate AST with accurate location data
2. **Analyze**: Determine code patterns and dependencies (imports, types, reassignments)
3. **Transform**: Apply rule-based modifications to AST nodes
4. **Type-check**: For TypeScript, validate type preservation
5. **Generate**: Output code with formatting and source maps
6. **Validate**: Syntax check output to ensure no errors

### Rule Engine
- Rules stored in `references/patterns.json` match AST node types
- Each rule includes: pattern selector, replacement template, conditional guards
- Guards inspect scope, variable usage, and type information
- Rules applied in priority order to avoid conflicts

### Error Handling
- Syntax errors in input code reported with location and message
- Unsupported patterns logged with suggestions
- Partial transformations rolled back on unrecoverable errors
- Exit codes: 0=success, 1=transformation errors, 2=usage error

## 7. Metadata

- **Skill ID**: es6-refactor-001
- **Version**: 1.0.0
- **License**: MIT
- **Maintainer**: OpenClaw Skill Factory
- **Repository**: https://github.com/openclaw/skills/tree/main/es6-refactor
- **Keywords**: javascript, typescript, refactor, es6, modernize, code-quality, ast, babel
- **OpenClaw Compatibility**: 1.0+
