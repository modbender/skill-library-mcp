---
name: folder-tree-generator
description: Generates an ASCII tree or JSON representation of a directory structure. Use when you need to visualize file hierarchies, document folder contents, or debug directory layouts.
---

# Folder Tree Generator

A utility skill to visualize directory structures in ASCII tree format or JSON.

## Usage

```bash
# Generate ASCII tree for current directory
node skills/folder-tree-generator/index.js

# Generate ASCII tree for specific directory
node skills/folder-tree-generator/index.js /path/to/dir

# Generate JSON output
node skills/folder-tree-generator/index.js --json

# Limit depth
node skills/folder-tree-generator/index.js --depth 2
```

## Options

- `--json`: Output as JSON.
- `--depth <n>`: Limit recursion depth.
- `[dir]`: Directory to scan (default: `.`).

## Examples

**ASCII Output:**
```
.
├── file1.txt
└── dir1
    ├── file2.txt
    └── file3.txt
```

**JSON Output:**
```json
{
  "name": ".",
  "type": "directory",
  "children": [
    { "name": "file1.txt", "type": "file" },
    { "name": "dir1", "type": "directory", "children": [...] }
  ]
}
```
