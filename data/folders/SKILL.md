---
name: Folders
description: Index important directories and perform safe folder operations with proper security checks.
metadata: {"clawdbot":{"emoji":"📂","os":["linux","darwin","win32"]}}
---

## Folder Index

Maintain a lightweight index at `~/.config/folder-index.json` to know where important things are without rescanning.

```json
{
  "folders": [
    {"path": "/Users/alex/projects/webapp", "type": "project", "note": "Main client project"}
  ]
}
```

When user asks "where is X" or "find my project Y", check the index first. If not found, do targeted discovery then offer to add the result.

## Discovery

When asked to find or index folders:
- Scan likely locations: ~/projects, ~/Documents, ~/code, ~/dev, ~/work
- Detect projects by markers: .git, package.json, pubspec.yaml, Cargo.toml, go.mod, pyproject.toml, *.sln
- Stop at first marker (don't recurse into node_modules, vendor, build)
- Propose what was found, don't auto-add: "Found 8 projects in ~/code. Add to index?"

## Path Security

- Canonicalize paths (resolve `~`, `..`, symlinks) before any operation
- Reject system paths: /, /etc, /var, /usr, /System, /Library, C:\Windows, C:\Program Files
- Skip symlinks during traversal, report them separately

## Destructive Operations

- Use OS trash instead of permanent delete
- State recoverability: "node_modules: recoverable with npm install"
- Build artifacts safe to delete: node_modules, __pycache__, .gradle, build/, target/, Pods/, .next/

## Platform Quirks

- **macOS:** .DS_Store alone = effectively empty. Treat .app as single item.
- **Windows:** Paths >260 chars need `\\?\` prefix.
- **Network drives:** Warn before bulk ops — may be slow or offline.
