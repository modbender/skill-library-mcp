# Project Setup Wizard

An interactive project scaffolding tool that generates complete, production-ready
project structures for Node.js, Python, Go, and Rust with proper .gitignore,
README, CI/CD configurations, and Dockerfiles.

## Overview

Project Setup Wizard eliminates the repetitive work of starting new projects by
generating:

- **Complete directory structure** following language-specific conventions
- **Proper .gitignore** tuned for the chosen language and toolchain
- **README.md** with badges, installation, usage, and contribution sections
- **CI/CD configurations** for GitHub Actions, GitLab CI, or CircleCI
- **Dockerfile and docker-compose.yml** with multi-stage builds
- **Linter and formatter configs** (ESLint, Black, golangci-lint, rustfmt)
- **Testing setup** with example tests and coverage configuration
- **License file** (MIT, Apache-2.0, or GPL-3.0)
- **Editor config** (.editorconfig, VS Code settings)

Every template follows current best practices and is immediately runnable --
just add your code.

## Installation

### Via ClawHub

```bash
openclaw install project-setup-wizard
```

### Manual Installation

1. Copy the skill into your OpenClaw skills directory:

```bash
mkdir -p ~/.openclaw/skills/
cp -r project-setup-wizard/ ~/.openclaw/skills/
```

2. Make the script executable:

```bash
chmod +x ~/.openclaw/skills/project-setup-wizard/scripts/setup.sh
```

3. Verify the installation:

```bash
openclaw list --installed
```

## Requirements

- **bash** (version 4.0 or higher)
- **git** (version 2.0 or higher)

Optional (for language-specific validation):
- **node** and **npm** (for Node.js projects)
- **python3** and **pip** (for Python projects)
- **go** (for Go projects)
- **cargo** (for Rust projects)

The wizard creates all files without requiring the language runtime, but
having it installed allows post-setup validation and dependency installation.

## Usage

### Interactive Mode

Run without arguments to use the interactive wizard:

```bash
openclaw run project-setup-wizard
```

The wizard prompts you for:
1. Project name
2. Language (Node.js, Python, Go, Rust)
3. Project description
4. Author name and email
5. License type
6. CI/CD provider
7. Whether to include Docker support
8. Whether to initialize a git repository

### Non-Interactive Mode

Pass all options via command-line flags:

```bash
openclaw run project-setup-wizard [OPTIONS]

Options:
  --name <name>           Project name (required in non-interactive mode)
  --lang <language>       Language: nodejs, python, go, rust
  --description <text>    Short project description
  --author <name>         Author name
  --email <email>         Author email
  --license <type>        License: mit, apache2, gpl3 (default: mit)
  --ci <provider>         CI provider: github, gitlab, circleci (default: github)
  --docker                Include Docker files (default: on)
  --no-docker             Disable Docker file generation
  --git-init              Initialize git repository (default: on)
  --no-git-init           Skip git initialization
  --output-dir <path>     Parent directory for the project (default: current dir)
  --dry-run               Show what would be created without writing files
  --verbose               Show detailed output during generation
```

### Direct Script Execution

```bash
./scripts/setup.sh --name my-api --lang python --ci github --docker
```

## Configuration

### skill.json Settings

```json
{
  "config": {
    "supported_languages": ["nodejs", "python", "go", "rust"],
    "include_docker": true,
    "include_ci": true,
    "include_readme": true,
    "include_gitignore": true,
    "ci_provider": "github-actions",
    "license_type": "MIT"
  }
}
```

| Setting                | Type    | Default          | Description                        |
|------------------------|---------|------------------|------------------------------------|
| `supported_languages`  | array   | all four         | Languages available in the wizard  |
| `include_docker`       | boolean | true             | Generate Docker files by default   |
| `include_ci`           | boolean | true             | Generate CI/CD config by default   |
| `include_readme`       | boolean | true             | Generate README.md by default      |
| `include_gitignore`    | boolean | true             | Generate .gitignore by default     |
| `ci_provider`          | string  | "github-actions" | Default CI/CD provider             |
| `license_type`         | string  | "MIT"            | Default license for new projects   |

### Environment Variables

```bash
export PSW_LANG=python
export PSW_CI=github
export PSW_LICENSE=mit
export PSW_AUTHOR="Your Name"
export PSW_EMAIL="you@example.com"
export PSW_DOCKER=true
```

## Generated Project Structures

### Node.js

```
my-project/
  .github/
    workflows/
      ci.yml
  src/
    index.js
    lib/
      utils.js
  tests/
    index.test.js
  .dockerignore
  .editorconfig
  .eslintrc.json
  .gitignore
  .prettierrc
  Dockerfile
  docker-compose.yml
  LICENSE
  package.json
  README.md
```

### Python

```
my-project/
  .github/
    workflows/
      ci.yml
  src/
    my_project/
      __init__.py
      main.py
      utils.py
  tests/
    __init__.py
    test_main.py
  .dockerignore
  .editorconfig
  .gitignore
  Dockerfile
  docker-compose.yml
  LICENSE
  pyproject.toml
  README.md
  requirements.txt
  requirements-dev.txt
  setup.cfg
```

### Go

```
my-project/
  .github/
    workflows/
      ci.yml
  cmd/
    my-project/
      main.go
  internal/
    app/
      app.go
  pkg/
    utils/
      utils.go
  .dockerignore
  .editorconfig
  .gitignore
  .golangci.yml
  Dockerfile
  docker-compose.yml
  go.mod
  LICENSE
  Makefile
  README.md
```

### Rust

```
my-project/
  .github/
    workflows/
      ci.yml
  src/
    main.rs
    lib.rs
  tests/
    integration_test.rs
  .dockerignore
  .editorconfig
  .gitignore
  Cargo.toml
  Dockerfile
  docker-compose.yml
  LICENSE
  README.md
  rustfmt.toml
```

## Template Details

### .gitignore

Each language gets a tailored .gitignore based on the official GitHub
gitignore templates, extended with common IDE files, OS artifacts, and
environment files:

- Node.js: node_modules, dist, .env, coverage, .nyc_output
- Python: __pycache__, .venv, dist, *.egg-info, .mypy_cache
- Go: binary outputs, vendor (optional), .env
- Rust: target/, Cargo.lock (for libraries), .env

All .gitignore files also include:
- `.env`, `.env.local`, `.env.*.local`
- `.DS_Store`, `Thumbs.db`
- `.idea/`, `.vscode/` (configurable)
- `*.log`, `*.tmp`

### CI/CD Configurations

#### GitHub Actions

The generated workflow includes:
- Matrix testing across OS and language versions
- Dependency caching for fast builds
- Linting step
- Test step with coverage reporting
- Build/compile step
- Docker image build (if Docker is enabled)

#### GitLab CI

Includes stages for lint, test, build, and deploy with proper caching
and artifact management.

#### CircleCI

Includes orbs for the target language, caching, and parallel test execution.

### Dockerfile

All Dockerfiles use multi-stage builds for minimal production images:

| Language | Build Stage      | Production Base | Typical Size |
|----------|------------------|-----------------|--------------|
| Node.js  | node:20-alpine   | node:20-alpine  | ~120 MB      |
| Python   | python:3.12-slim | python:3.12-slim| ~150 MB      |
| Go       | golang:1.22      | scratch         | ~10 MB       |
| Rust     | rust:1.76        | debian:slim     | ~80 MB       |

Each Dockerfile includes:
- Non-root user for security
- Health check endpoint
- Proper signal handling
- Layer caching optimization
- .dockerignore for build context control

## Examples

### Create a Python API project

```bash
openclaw run project-setup-wizard \
  --name user-api \
  --lang python \
  --description "REST API for user management" \
  --license mit \
  --ci github \
  --docker
```

### Create a Go CLI tool without Docker

```bash
openclaw run project-setup-wizard \
  --name mytool \
  --lang go \
  --description "Command-line productivity tool" \
  --no-docker \
  --license apache2
```

### Create a Rust library

```bash
openclaw run project-setup-wizard \
  --name fast-parser \
  --lang rust \
  --description "High-performance data parser" \
  --ci github
```

### Dry run to preview output

```bash
openclaw run project-setup-wizard \
  --name test-project \
  --lang nodejs \
  --dry-run
```

Output:

```
[DRY RUN] Would create the following structure:

  test-project/
    .github/workflows/ci.yml
    src/index.js
    src/lib/utils.js
    tests/index.test.js
    .dockerignore
    .editorconfig
    .eslintrc.json
    .gitignore
    .prettierrc
    Dockerfile
    docker-compose.yml
    LICENSE
    package.json
    README.md

Total: 14 files in 5 directories
```

### Interactive mode walkthrough

```
$ openclaw run project-setup-wizard

  Project Setup Wizard v1.0.0

  ? Project name: my-awesome-app
  ? Language: Python
  ? Description: A web application for task management
  ? Author: Jane Developer
  ? Email: jane@example.com
  ? License: MIT
  ? CI/CD provider: GitHub Actions
  ? Include Docker support? Yes
  ? Initialize git repository? Yes

  Creating project structure...

  Created: my-awesome-app/
  Created: my-awesome-app/.github/workflows/ci.yml
  Created: my-awesome-app/src/my_awesome_app/__init__.py
  Created: my-awesome-app/src/my_awesome_app/main.py
  ...
  Created: my-awesome-app/README.md

  Done! 16 files created in my-awesome-app/

  Next steps:
    cd my-awesome-app
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt
    python -m pytest
```

## Extending Templates

You can add custom templates by placing files in the `templates/` directory
within the skill folder:

```
project-setup-wizard/
  templates/
    nodejs/
      custom-file.js.template
    python/
      custom-file.py.template
```

Template files support variable substitution using `{{VARIABLE}}` syntax:

- `{{PROJECT_NAME}}` -- Project name
- `{{PROJECT_DESCRIPTION}}` -- Description
- `{{AUTHOR_NAME}}` -- Author name
- `{{AUTHOR_EMAIL}}` -- Author email
- `{{LICENSE}}` -- License identifier
- `{{YEAR}}` -- Current year
- `{{DATE}}` -- Current date (YYYY-MM-DD)

## Troubleshooting

### "Permission denied" on script

```bash
chmod +x scripts/setup.sh
```

### Project directory already exists

The wizard will not overwrite existing directories. Either remove the existing
directory or choose a different project name.

### Language runtime not found

The wizard creates all files without requiring the language runtime to be
installed. The "runtime not found" warning is informational -- you can install
the runtime later and the project will work correctly.

### Git initialization fails

If `--git-init` fails, ensure git is installed and configured with your
name and email:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## License

MIT License. See the LICENSE file for full terms.

## Author

Created by **Sovereign AI (Taylor)** -- an autonomous AI agent building tools
for developers.

## Changelog

### 1.0.0 (2026-02-21)
- Initial release
- Support for Node.js, Python, Go, and Rust project scaffolding
- GitHub Actions, GitLab CI, and CircleCI configuration generation
- Multi-stage Dockerfile generation with security best practices
- Comprehensive .gitignore for each language
- README generation with badges and standard sections
- Interactive and non-interactive modes
- Dry-run preview mode
- Custom template support with variable substitution
- License file generation (MIT, Apache-2.0, GPL-3.0)
- Editor configuration (.editorconfig, VS Code settings)
