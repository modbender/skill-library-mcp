---
name: bool-cli
description: "Deploy sites to Bool.com via the bool CLI. Use when creating, deploying, updating, or managing Bool projects."
homepage: "https://bool.com"
source: "https://github.com/codehs/bool-cli"
metadata:
  openclaw:
    emoji: "🚀"
    requires:
      bins: ["bool"]
      env:
        - name: BOOL_API_KEY
          description: "API key for Bool.com (optional if using `bool auth login`)"
          required: false
    config_paths:
      - path: "~/.config/bool-cli/config.json"
        description: "Stores API key and global CLI config"
      - path: ".bool/config"
        description: "Per-project config (slug, name, secret). Add .bool/ to .gitignore"
    install:
      - id: npm
        kind: npm
        package: bool-cli
        global: true
        bins: ["bool"]
        label: "Install bool-cli (npm)"
---

# Using bool-cli

CLI tool for managing projects on [Bool.com](https://bool.com). Requires Node.js >=18.

## Prerequisites

1. **Install**: `npm install -g bool-cli`
2. **Authenticate**: Set `BOOL_API_KEY` env var, or run `bool auth login` interactively
3. **Verify**: Run `bool auth status` to confirm the connection

The API key is saved to `~/.config/bool-cli/config.json`. The `BOOL_API_KEY` environment variable takes precedence over the saved config.

## Important: Non-Interactive Commands

The `bool auth login` and `bool bools delete <slug>` commands are **interactive** (they prompt for input). When using them from an agent:

- **Auth**: Set the `BOOL_API_KEY` environment variable instead of running `bool auth login`
- **Delete**: Always pass `-y` / `--yes` to skip the confirmation prompt: `bool bools delete <slug> -y`

## Commands Reference

### Authentication

```bash
bool auth login          # Interactive: prompts for API key
bool auth status         # Check auth + API health (non-interactive)
```

### Managing Bools

```bash
bool bools list [count]        # List Bools (default: 5)
bool bools create <name>       # Create a new Bool
bool bools info [slug]         # Show Bool details + latest version info
bool bools update [slug] --name "New Name" --description "desc" --visibility public
bool bools delete [slug] -y    # Delete a Bool (always use -y to skip prompt)
bool bools open [slug]         # Open Bool in browser
bool bools visibility [slug]         # Show current visibility
bool bools visibility [slug] --set private    # Change visibility
```

Visibility options: `private`, `team`, `unlisted`, `public`

### Versions & Deployment

```bash
bool versions [slug]                           # List version history
bool deploy [slug] [dir] -m "commit message"   # Deploy local files (auto-creates Bool if needed)
bool pull [slug] [dir] --version N             # Download files locally
```

### Quick Ship (Anonymous Bools)

Ship a project without needing an API key:

```bash
bool shipit [directory]                        # Create anonymous Bool + deploy
bool shipit --slug <slug> -m "update message"  # Update existing anonymous Bool
bool shipit --name "My Project"                # Set a custom name
```

The `shipit` command stores the slug and secret in `.bool/config` so subsequent runs in the same directory automatically update the same Bool.

### JSON Output

All commands support `--json` for machine-readable output. **Always use `--json` when you need to parse output programmatically.**

```bash
bool bools list --json
bool bools info my-project --json
bool versions my-project --json
```

## Project Config (`.bool/config`)

When you deploy, pull, or shipit in a directory, bool-cli stores project metadata in `.bool/config`:

```json
{
  "slug": "my-project",
  "name": "My Project",
  "secret": "optional_anonymous_secret"
}
```

This allows you to omit the `[slug]` argument on subsequent commands when working in the same directory. For example:

```bash
# First time: specify slug explicitly
bool deploy my-project ./src -m "Initial deploy"

# After that, run from the same directory and slug is read from .bool/config
bool deploy -m "Another deploy"
bool versions
bool bools info
```

Add `.bool/` to your `.gitignore` to keep secrets local.

## Common Workflows

### Create and deploy a new Bool (Option A: explicit)

```bash
bool bools create "My Project"
# note the slug from the output, e.g. "my-project"
bool deploy my-project ./src -m "Initial deploy"
```

### Create and deploy a new Bool (Option B: auto-create)

```bash
# Deploy without a slug—a new Bool is created automatically
bool deploy ./src -m "Initial deploy"
```

This creates a Bool named after the directory and displays the live URL.

### Quick anonymous ship (no API key needed)

```bash
bool shipit ./my-project
# outputs: https://<slug>.bool01.com
# subsequent updates from same directory:
bool shipit ./my-project -m "Updated version"
```

### Pull, edit, and redeploy

```bash
bool pull my-project ./my-project
# ... make changes to files in ./my-project/ ...
bool deploy my-project ./my-project -m "Updated files"
```

### Check what's deployed

```bash
bool bools info my-project            # See latest version summary
bool versions my-project              # See full version history
bool pull my-project ./tmp            # Download current files to inspect
```

### Manage visibility

```bash
bool bools visibility my-project                 # Show current visibility
bool bools visibility my-project --set private    # Make it private
bool bools visibility my-project --set public     # Make it public
```

### Deploy a specific subdirectory with exclusions

```bash
bool deploy my-project ./src --exclude "*.test.js" --exclude "*.spec.js" -m "Production build"
```

## Deploy Behavior

- `bool deploy` recursively reads the directory and uploads all text files
- **Auto-create Bool**: If no slug is provided (and no `.bool/config` exists), a new Bool is created automatically, named after the directory
- **Live URL**: The live deployment URL is displayed in the output after successful deployment
- **Binary files** (images, PDFs, archives, fonts, etc.) are automatically skipped
- **Default excludes**: `.git`, `node_modules`, `__pycache__`, `.DS_Store`, `.bool`
- **Custom excludes**: Use `--exclude <pattern>` (repeatable) for additional patterns
- **`.boolignore`**: If a `.boolignore` file exists in the deploy directory, it is respected (gitignore syntax)
- File paths in the payload are **relative** to the deploy directory

## Pull Behavior

- `bool pull <slug>` downloads files to `./<slug>/` by default
- Specify a custom output directory: `bool pull <slug> ./my-dir`
- Pull a specific version: `bool pull <slug> --version 3`
- Creates subdirectories as needed

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `BOOL_API_KEY` | API key (overrides saved config) | — |
| `BOOL_API_URL` | API base URL | `https://bool.com/api` |
| `BOOL_BASE_URL` | Base URL for shipit | `https://bool.com` |

## Error Handling

- All errors print to stderr with a non-zero exit code
- API errors surface the server's error message (e.g., `"Bool not found"`)
- If no API key is configured, commands fail with: `No API key configured. Run: bool auth login`

## Tips

- Use `bool bools list --json | jq '.[].slug'` to get all slugs for scripting
- The Bool **slug** (not name) is the identifier used in all commands
- After `bool bools create`, the slug is derived from the name (e.g., "My Project" -> `my-project`)
- Use `bool bools info <slug> --json` to get the latest version number programmatically
- The live URL for any Bool is `https://<slug>.bool01.com`
