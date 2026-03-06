---
name: json-toolkit
description: Swiss-army knife for JSON files. Pretty-print, validate, minify, sort keys, and query with dot-notation paths. Zero dependencies.
triggers:
  - format json
  - pretty print json
  - validate json
  - query json
  - minify json
  - json tool
---

# JSON Toolkit

A zero-dependency Python utility for working with JSON data. Validates, formats, minifies, queries, and inspects JSON files — all with Python's standard library.

## Features

- **Pretty-print** with configurable indentation (2, 4, or any number of spaces)
- **Minify** JSON to reduce file size for APIs and storage
- **Validate** JSON and get structural stats (type, key count, size)
- **Query** nested data with dot-notation paths including array indices
- **Sort keys** alphabetically for deterministic output and easier diffs
- **Stdin support** for use in shell pipelines with other tools

## Usage Examples

Pretty-print a JSON file:
```bash
python main.py data.json
```

Validate without output:
```bash
python main.py config.json --validate
# ✓ Valid JSON
#   Type: object (12 keys)
#   Size: 4832 bytes
```

Query a nested value:
```bash
python main.py users.json --query data.users.0.name
# "Alice"
```

Minify for production:
```bash
python main.py config.json --minify -o config.min.json
```

Sort keys for consistent diffs:
```bash
python main.py package.json --sort-keys -o package-sorted.json
```

Pipe from curl:
```bash
curl -s https://api.example.com/data | python main.py - --query results.0
```

## Query Syntax

Use dot notation to navigate nested structures. Array indices are numbers:

- `name` — top-level key
- `data.users` — nested object key
- `data.users.0` — first element of an array
- `data.users.0.email` — field of the first array element
- `config.servers.2.host` — deeply nested value

## Command Line Options

- `input` — JSON file path, or `-` for stdin
- `-o, --output` — Output file (defaults to stdout)
- `--indent N` — Indentation spaces (default: 2)
- `--minify` — Output minified JSON (no whitespace)
- `--query PATH` / `-q PATH` — Extract a value at the given dot-notation path
- `--validate` — Only validate and print stats, no output
- `--sort-keys` — Sort object keys alphabetically
- `--json` — (implicit) Output is always valid JSON
