---
name: graphql-ts-generator
description: Automatically generates TypeScript types from GraphQL schema files with CLI integration for developers and AI agents.
---

# GraphQL TypeScript Generator Skill

## Product Plan

### One-Sentence Description
Automatically generates TypeScript types from GraphQL schema files with CLI integration for developers and AI agents.

### Core Capabilities
- Convert GraphQL schema (.graphql, .gql) files to TypeScript interfaces and types
- Generate client-side TypeScript types for GraphQL queries and mutations
- Provide command-line interface for direct file processing
- Handle complex GraphQL types including unions, interfaces, and enums
- Validate GraphQL schemas before TypeScript generation
- Integrate with OpenClaw agent workflows for automation
- Support batch processing of multiple schema files

### Out of Scope
- GraphQL server implementation
- Database schema management
- Runtime GraphQL client code generation
- Documentation generation beyond type definitions
- Performance optimization for very large schemas
- Custom code formatting beyond TypeScript standards
- Integration with specific frameworks (React, Angular, etc.)

### Trigger Scenarios
- "Generate TypeScript types from this GraphQL schema"
- "Create TypeScript interfaces from GraphQL schema file"
- "Convert .graphql file to TypeScript types"
- "Auto-generate types for my GraphQL API"
- "Generate client types from GraphQL schema"
- "Transform GraphQL schema to TypeScript"

### Required Resources
- **scripts/**: Contains the main TypeScript generation logic and CLI entry point
- **references/**: GraphQL schema examples and test cases
- **assets/**: CLI help text, configuration templates, and documentation assets

### Key Files
- **scripts/index.ts**: Main CLI entry point
- **scripts/generator.ts**: Core type generation logic
- **scripts/cli.ts**: Command-line interface implementation
- **scripts/utils.ts**: Utility functions for GraphQL parsing
- **references/sample.graphql**: Example GraphQL schema for testing
- **references/test-schema.graphql**: Complex test case with various GraphQL features
- **assets/README.md**: User documentation
- **assets/package.json**: Skill package configuration
- **assets/tsconfig.json**: TypeScript configuration for the skill
- **assets/cli-help.txt**: CLI help text and usage examples

### Acceptance Criteria
- Skill correctly processes simple GraphQL schemas and generates valid TypeScript types
- Skill handles complex GraphQL features (unions, interfaces, enums)
- CLI interface accepts schema file paths and outputs TypeScript files
- Error handling for invalid GraphQL schemas
- Integration with OpenClaw agent workflows for automated processing
- Documentation includes usage examples and troubleshooting
- Test cases pass for all sample GraphQL schemas
- Generated TypeScript types are immediately usable in TypeScript projects

## Architecture Overview

### Directory Layout
```
├── scripts/
│   ├── index.ts        # CLI entry point
│   ├── generator.ts    # Type generation logic (Unions, Interfaces, Enums)
│   ├── cli.ts          # Command-line argument parsing
│   └── utils.ts        # GraphQL parsing utilities
├── references/
│   ├── sample.graphql  # Basic schema example
│   └── test-schema.graphql  # Complex test cases
├── assets/
│   ├── README.md       # User documentation
│   ├── package.json    # Skill package metadata
│   ├── tsconfig.json   # TypeScript config
│   └── cli-help.txt    # CLI usage examples
```

### Scripts Design

#### `scripts/index.ts`
- Language: TypeScript
- Inputs: `argv` (script arguments via CLI)
- Outputs: Generates TypeScript files in output directory
- Core Logic: Parses CLI args → Loads schema → Calls `generator.ts` → Writes output

#### `scripts/generator.ts`
- Language: TypeScript
- Inputs: GraphQL schema AST (parsed from file)
- Outputs: TypeScript interfaces, types
- Core Logic: Type transformation rules for:
  - Scalar types → TS primitives
  - Object types → TS interfaces
  - Union types → Discriminated unions
  - Enum types → TS enum

#### `scripts/cli.ts`
- Language: TypeScript
- Inputs: Raw command-line arguments
- Outputs: Processed schema file paths
- Core Logic: Argument validation → Schema file reading → Result routing

#### `scripts/utils.ts`
- Language: TypeScript
- Inputs: Raw GraphQL text
- Outputs: Parsed AST
- Core Logic: GraphQL parser implementation with error handling

### References Design

#### `references/sample.graphql`
- Content: Basic schema with Query/Mutation
- Usage: Demonstration for new users

#### `references/test-schema.graphql`
- Content: Features unions, interfaces, nested enums
- Usage: Testing boundary cases during development

### Data Flow
1. CLI receives schema path via arguments
2. `cli.ts` validates and loads schema file
3. `utils.ts` parses schema to AST
4. `generator.ts` processes AST using transformation rules
5. Outputs TypeScript files to `dist/` directory

### Integration Points

#### Agent Workflow Example:
1. User requests: "Generate types from schema at /docs/api.graphql"
2. Agent triggers CLI via `exec "graphql-ts-generator /docs/api.graphql"`
3. CLI processes schema, calls generator logic
4. Generated .ts files returned to agent as attachment
5. Agent presents files to user in chat interface

#### CLI Automation:
- Agent can schedule batch processing
- "Generate types for all .graphql in /schemas/" → `exec "graphql-ts-generator /schemas/*.graphql"`

## Usage Instructions

### Installation
```bash
npm install -g graphql-ts-generator
```

### Basic Usage
```bash
# Generate types from a single schema file
graphql-ts-generator schema.graphql

# Generate types and specify output directory
graphql-ts-generator schema.graphql --output dist/

# Process multiple schema files
graphql-ts-generator "schemas/*.graphql"
```

### Options
- `-o, --output <dir>`: Output directory for generated TypeScript files (default: `./generated`)
- `-f, --format <style>`: Code formatting style (default: standard)
- `-v, --verbose`: Enable verbose logging
- `--no-validate`: Skip schema validation (not recommended)
- `-h, --help`: Show help message

### Output
The generator produces TypeScript files containing:
- Interfaces for GraphQL object types
- Type aliases for GraphQL unions
- Enums for GraphQL enums
- Proper nullability handling (TypeScript `| null`)

### Integration with OpenClaw
This skill integrates seamlessly with OpenClaw agent workflows. Trigger via:
- Direct CLI execution in agent sessions
- Scheduled batch generation jobs
- Automated pipeline processing

See `assets/README.md` for complete documentation.
