# Zod Validation Library Documentation Skill

Complete Zod validation library documentation packaged as an OpenClaw AgentSkill.

## Contents

- **API Reference** (complete schema API)
- **Core Concepts** (validation, type inference, parsing)
- **Error Handling** (formatting, customization)
- **Advanced Features** (codecs, JSON Schema, metadata)
- **Ecosystem** (integrations and packages)
- **Version 4** (latest features)

## Structure

```
references/
├── index.mdx                # Introduction
├── basics.mdx               # Getting started
├── api.mdx                  # Complete API reference
├── error-formatting.mdx     # Error handling
├── error-customization.mdx  # Custom errors
├── codecs.mdx               # Serialization
├── json-schema.mdx          # JSON Schema generation
├── ecosystem.mdx            # Integrations
├── library-authors.mdx      # Library guide
└── v4/                      # Version 4 docs
```

## Installation

Via ClawHub:
```bash
clawhub install lb-zod-skill
```

Or manually: Download and extract into your OpenClaw workspace `skills/` folder.

## Usage

This skill triggers automatically when you ask questions about Zod validation, schema definition, type inference, error handling, or form validation.

## Covered Topics

- Schema definition (primitives, objects, arrays, tuples, unions)
- Validation and parsing
- Type inference with TypeScript
- Refinements and transforms
- Error formatting and customization
- Async validation
- Coercion and defaults
- JSON Schema generation
- Integrations (React Hook Form, tRPC, etc.)
- Form validation patterns
- API validation
- Environment variable parsing

## Common Use Cases

- Form validation in React/Next.js
- API request/response validation
- Runtime type checking
- Data transformation
- Environment variable parsing
- Integration with tRPC, React Hook Form, Formik
- Custom error messages

## Source

Documentation extracted from [colinhacks/zod](https://github.com/colinhacks/zod) (latest version).

## License

Documentation content: MIT (from Zod project)
