# Common Workflows

## Fix a Type Error

```
1. Find errors
   → vscode.diagnostics.get

2. Understand the type at error location
   → vscode.lang.hover {"path": "src/main.ts", "line": 10, "character": 5}

3. Find where the type is defined
   → vscode.lang.definition {"path": "src/main.ts", "line": 10, "character": 5}

4. Fix the code
   → vscode.file.edit {"path": "src/main.ts", "oldText": "...", "newText": "..."}

5. Verify fix
   → vscode.diagnostics.get

6. Format
   → vscode.code.format {"path": "src/main.ts"}
```

## Safe Cross-File Refactor

```
1. Find all usages
   → vscode.lang.references {"path": "src/main.ts", "line": 10, "character": 5}

2. Rename using language server (safe, cross-file)
   → vscode.lang.rename {"path": "src/main.ts", "line": 10, "character": 5, "newName": "newName"}

3. Check for breakage
   → vscode.diagnostics.get

4. Run tests
   → vscode.test.run

5. Review changes
   → vscode.git.diff

6. Commit
   → vscode.git.stage {"paths": ["src/main.ts", "src/utils.ts"]}
   → vscode.git.commit {"message": "refactor: rename X to Y"}
```

## Delegate Complex Task to Cursor Agent

```
1. Understand current state
   → vscode.workspace.info
   → vscode.git.status

2. Plan first (read-only analysis)
   → vscode.agent.run {"prompt": "Analyze how to add error handling", "mode": "plan"}
   (invokeTimeoutMs: 180000, timeoutMs: 185000)

3. Review plan output, then execute
   → vscode.agent.run {"prompt": "Add try-catch to all API endpoints", "mode": "agent"}
   (invokeTimeoutMs: 300000, timeoutMs: 305000)

4. Review changes
   → vscode.git.diff
   → vscode.diagnostics.get
```

## Explore Unfamiliar Codebase

```
1. Get workspace overview
   → vscode.workspace.info

2. List project structure
   → vscode.dir.list {"recursive": true, "pattern": "**/*.ts"}

3. Read entry point
   → vscode.file.read {"path": "src/index.ts"}

4. Navigate to key types
   → vscode.lang.symbols {"query": "Config"}
   → vscode.lang.definition {"path": "...", "line": ..., "character": ...}

5. Ask Cursor for summary (if available)
   → vscode.agent.run {"prompt": "Explain the architecture of this project", "mode": "ask"}
```
