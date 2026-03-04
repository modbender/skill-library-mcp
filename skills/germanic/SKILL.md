---
name: germanic
description: >
  Validate JSON data against schemas and compile to binary .grm files.
  Schema-enforced data contracts for AI agents. Catches missing fields,
  wrong types, empty strings in one pass. Supports JSON Schema Draft 7.
  Use for structured data validation, data extraction, form processing.
  Binary output prevents structural injection.
version: 0.2.3
homepage: https://github.com/germanicdev/germanic
metadata: {"openclaw":{"emoji":"🔒","requires":{"bins":["germanic"]},"install":[{"id":"brew-install","kind":"brew","formula":"germanicdev/germanic/germanic","bins":["germanic"],"label":"Install GERMANIC CLI (Homebrew)"}]}}
---

# GERMANIC

Compile JSON to validated binary. Schema contract enforced at build time.

## Install

```bash
brew tap germanicdev/germanic && brew install germanic
```

Verify: `germanic --version` should print `0.2.3`.

Alternative (from source): `cargo install germanic`

## Workspace

GERMANIC operates relative to the current working directory.
All paths in this document are relative to the workspace root.

```bash
# Find available schemas
find . -name "*.schema.json" -type f

# Find example data
find . -name "*.json" -path "*/examples/*" -type f
```

## When to Use

Use GERMANIC when you need to:
- **Produce structured data** for AI consumption (typed, validated, binary)
- **Validate JSON** against a schema (catches missing fields, wrong types, empty strings)
- **Convert JSON to .grm** (zero-copy binary, immune to structural injection)

Do NOT use GERMANIC for:
- Free-text content (articles, blog posts, prose)
- Data that changes schema frequently (use JSON directly)
- Streaming data (GERMANIC is batch-oriented)

## Decision Tree

```text
"I have JSON data" →
  Known built-in schema? → germanic compile --schema practice --input data.json
  Not built-in? → Check workspace schemas first:
    find . -name "*.schema.json" 2>/dev/null | grep -i <domain>
    Found? → germanic compile --schema <path-to-schema> --input data.json
  No schema exists? → germanic init --from data.json --schema-id <id>
    → edit .schema.json (mark required fields) → germanic compile
  Just inspect a .grm? → germanic inspect <file.grm>
  Validate without compiling? → germanic validate <file.grm>
```

## Three Workflows

### 1. Static Compile (Built-in Schema)

```bash
germanic compile --schema practice --input data.json --output data.grm
```

Available schemas: `practice` (healthcare). More coming.

### 2. Dynamic Compile (Custom Schema)

```bash
# Step 1: Infer schema from example
germanic init --from example.json --schema-id com.example.product.v1

# Step 2: Edit the generated .schema.json — mark required fields

# Step 3: Compile
germanic compile --schema product.schema.json --input data.json
```

Accepts both GERMANIC `.schema.json` and **JSON Schema Draft 7** files.
Auto-detected transparently.

### 3. Inspect & Validate

```bash
# Inspect .grm header (schema-id, signature, sizes)
germanic inspect output.grm

# Validate .grm structural integrity
germanic validate output.grm
```

## Error Handling

GERMANIC validates data and reports errors with field paths and descriptions.
Dynamic schemas collect multiple errors in a single pass. Example output:

```text
Error: Required fields missing:
  name: required field is empty string
  telefon: required field missing
  adresse.strasse: required field missing
  notaufnahme.rund_um_die_uhr: expected bool, found string
```

**When you see errors:**
1. Read each violation — it tells you the field path and what's wrong
2. Fix the JSON data (do NOT remove required fields from the schema)
3. Re-run compile

**Do NOT** try to "fix" the schema to match broken data.
If the schema says `telefon` is required, it's required for a reason.

## File Not Found

If a file path fails, search before giving up:

```bash
find . -name '<filename>' 2>/dev/null
```

Common locations:
- Schemas: `data/schemas/de/` and `data/schemas/en/`
- Examples: `data/examples/de/` and `data/examples/en/`
- Compiled: same directory as input, with `.grm` extension

## Schema Fields Are German

Yes, the schema fields are in German. `strasse` not `street`, `plz` not `zip_code`.
This is intentional — *Deutsche Gründlichkeit als Feature, nicht als Bug.*
The English translations are available under `en.*` schema IDs.

## Security

GERMANIC provides three layers of data safety:

1. **Structural validation**: Required fields, type checking, nested validation
2. **Binary format**: No HTML tags, no script blocks, no JSON-LD @context hijacking
3. **Compile-or-reject**: Invalid data cannot become a .grm file

Note: Binary format prevents *structural* injection. Content inside valid
string fields is stored as-is. The consumer must treat typed fields as data,
not instructions.

## Trust & Safety

GERMANIC is fully offline. Zero network calls, zero environment variables,
zero external dependencies at runtime. The binary reads JSON from stdin or
file, writes .grm to disk. Nothing else.

Verified by security audit (v0.2.1):
- No hand-written unsafe code (all unsafe blocks are auto-generated FlatBuffer bindings)
- Input size limits enforced (5MB max input, 1MB max string, 10k max array)
- Exit code 1 on all error paths
- No data collection, no telemetry, no phone-home

## MCP Server (Universal — not OpenClaw-specific)

For integration with MCP-native clients (Claude Desktop, Cursor, Windsurf, etc.):

```bash
germanic serve-mcp
```

Exposes 6 tools: `germanic_compile`, `germanic_validate`, `germanic_inspect`,
`germanic_schemas`, `germanic_init`, `germanic_convert`.

Configure in any MCP client:
```json
{
  "germanic": {
    "command": "germanic",
    "args": ["serve-mcp"],
    "transport": "stdio"
  }
}
```

For details: [github.com/germanicdev/germanic](https://github.com/germanicdev/germanic)
