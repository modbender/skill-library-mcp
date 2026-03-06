# PROJECT-SCAN.md - Codebase Analysis Skill

**Teach your agent to understand the project it's working on.**

This module provides logic and patterns for scanning a local directory to extract key project metadata. This context is crucial for generating relevant token names, symbols, and descriptions.

> **Note:** This is the **first step** in the TokenBroker workflow. Scan results are passed to `METADATA.md` for token proposal generation, which are then delegated to `nadfun` for on-chain token creation.

> **Security Note**: Project scanning is a **read-only** operation. No credentials are required for codebase analysis.

## Capabilities

1.  **Identity Extraction**: Find project name and version.
2.  **Context Understanding**: Read descriptions and summaries.
3.  **Tech Stack Detection**: Identify dependencies and frameworks.
4.  **Social Discovery**: Locate links to Twitter, Telegram, Discord, etc.

## Agent Instructions

When asked to "scan this project" or "analyze this codebase":

1.  **Locate Root**: Identify the root directory (look for `package.json`, `.git`, `go.mod`, etc.).
2.  **Parse Manifests**: Read structured files like `package.json` first.
3.  **Read Documentation**: Analyze `README.md` for high-level summaries.
4.  **Search Configs**: Look for `docusaurus.config.js` or `site.config.ts` for social links.

## Code Examples

### Scanning `package.json` (Node.js)

```typescript
import * as fs from 'fs';
import * as path from 'path';

function scanPackageJson(root: string) {
  const pkgPath = path.join(root, 'package.json');
  if (!fs.existsSync(pkgPath)) return null;

  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  return {
    name: pkg.name,
    description: pkg.description,
    keywords: pkg.keywords || [],
    dependencies: { ...pkg.dependencies, ...pkg.devDependencies },
    repository: pkg.repository
  };
}
```

### Parsing `README.md` for Context

Agents can use a simple heuristic to find the "elevator pitch" in a README.

```typescript
function scanReadme(root: string) {
  const readmePath = path.join(root, 'README.md');
  if (!fs.existsSync(readmePath)) return null;

  const content = fs.readFileSync(readmePath, 'utf8');
  const lines = content.split('\n');
  
  // Find first non-header paragraph
  let description = "";
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#') && !trimmed.startsWith('![')) {
      description = trimmed;
      break;
    }
  }
  return description;
}
```

### Output Schema

The scan result should map to this JSON structure:

```json
{
  "name": "Project Name",
  "description": "One-line summary of the project.",
  "techStack": ["Next.js", "Tailwind", "Supabase"],
  "keywords": ["ai", "gentic", "automation"],
  "socials": {
    "twitter": "https://x.com/...",
    "github": "https://github.com/..."
  }
}
```

## Workflow Integration

```
PROJECT-SCAN.md → METADATA.md → LAUNCH.md (delegates to nadfun)
```

1. **Scan**: Extract project context
2. **Generate**: Create token metadata proposals
3. **Delegate**: Pass metadata to nadfun for creation

## Next Steps

Once the project is scanned:
- Go to **METADATA.md** to generate token ideas based on this data.
- Go to **STATS.md** to check the builder's reputation if an author address is found.

## Security Considerations

Project scanning operates entirely in read-only mode:

| Aspect | Behavior |
|--------|----------|
| **File Access** | Read-only; never modifies project files |
| **Credentials Required** | None for scanning local directories |
| **Remote Access** | Only via GitHub OAuth/PAT (handled separately) |
| **Data Storage** | Scan results held in memory only |

The scanner only reads project files to extract metadata:
- `package.json`, `go.mod`, `pyproject.toml` (manifest files)
- `README.md` for descriptions
- Configuration files for social links

No sensitive data (credentials, keys, secrets) is extracted or processed.
