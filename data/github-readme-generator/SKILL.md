---
name: github-readme-generator
description: Generate beautiful, professional GitHub README files for your projects. Supports multiple templates, languages, and customization options.
metadata: {"clawdbot":{"emoji":"📝","requires":{},"primaryEnv":""}}
---

# GitHub README Generator

Generate professional GitHub README files for your projects with multiple templates and customization options.

## Features

- 🎨 Multiple templates (Modern, Minimal, Detailed, API-focused)
- 🌐 Multi-language support
- 📋 Auto-generated badges
- 💼 Project type detection (Library, CLI, Web App, etc.)
- 📊 Auto-generated stats sections

## Usage

### Basic Generation

```bash
# Generate with default template
github-readme-generator "Project Name" "Description"

# Specify template
github-readme-generator "Project Name" "Description" --template modern

# Specify language
github-readme-generator "项目名称" "描述" --lang zh
```

### Available Templates

| Template | Use Case |
|----------|----------|
| `modern` | Most projects (default) |
| `minimal` | Simple libraries |
| `detailed` | Complex projects with full documentation |
| `api` | API/REST services |
| `cli` | Command-line tools |

### Options

- `--template, -t` : Template name
- `--lang, -l` : Language (en, zh, ja, es, ko)
- `--badges, -b` : Include badge section (default: true)
- `--toc, -c` : Include table of contents (default: false)
- `--output, -o` : Output file path

## Examples

### Python Library
```bash
github-readme-generator "my-lib" "A powerful Python library" --template modern
```

### CLI Tool
```bash
github-readme-generator "super-cli" "Amazing CLI tool" --template cli
```

### Node.js Package
```bash
github-readme-generator "my-package" "NPM package description" --template modern
```

## Installation

```bash
# No dependencies required
# Uses built-in templates
```

## How It Works

1. Detects project type from name/description
2. Selects appropriate template
3. Generates sections based on project type
4. Adds relevant badges
5. Outputs ready-to-use README.md

## Output Example

The generated README includes:
- Project title and badges
- Description
- Features list
- Installation instructions
- Usage examples
- API reference (if applicable)
- Contributing guidelines
- License
- Contact information
