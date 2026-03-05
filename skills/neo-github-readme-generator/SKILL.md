---
name: github-readme-generator
description: Automatically generates comprehensive README files from GitHub repositories with installation, API docs, and usage examples.
version: 1.0.0
---

# GitHub README Generator

## One-Sentence Description
Automatically generates comprehensive READMEs from GitHub repos including installation instructions, API documentation, and usage examples.

## Core Capabilities
- Analyze GitHub repository structure and extract key information
- Generate comprehensive README files with proper sections and formatting
- Create installation instructions based on package.json, requirements.txt, and project structure
- Generate API documentation from code comments and function signatures
- Create usage examples from existing code patterns
- Handle various programming languages and frameworks automatically
- Provide clean CLI interface for direct usage and agent integration
- Validate generated READMEs for completeness and quality
- Handle errors gracefully with meaningful messages and exit codes

## Triggers
- "Generate a README for this GitHub repository"
- "Create documentation for my project"
- "Analyze this repo and write a comprehensive README"
- "Help me document my GitHub project"
- "Generate installation instructions and API docs for this repository"
- "Create a professional README for my open-source project"
- "Automatically generate documentation from my GitHub codebase"

## Out of Scope
- Replace manual writing of READMEs (generates drafts requiring review)
- Deep analysis of complex algorithms or business logic
- Generate documentation for non-GitHub repositories
- Handle proprietary or private repositories without proper access
- Create marketing or promotional content
- Generate code from scratch (only analyzes existing code)
- Replace existing READMEs without explicit user confirmation

## Required Resources
- `scripts/` — Main functionality, CLI interface, and GitHub API integration
- `references/` — README templates for different project types and documentation standards
- `assets/` — Example READMEs and configuration files for consistency

## Key Files
- `SKILL.md` — Skill documentation and configuration
- `README.md` — Usage documentation and examples
- `scripts/main.js` — Entry point and CLI interface
- `scripts/github-api.js` — GitHub API integration and repository access
- `scripts/readme-generator.js` — Core README generation logic
- `scripts/analyzer.js` — Repository structure and code analysis
- `scripts/validator.js` — Quality checks for generated README
- `references/templates/` — README templates for different project types
- `references/standards/` — Documentation standards and style guidelines
- `assets/examples/` — Sample README outputs for reference

## Acceptance Criteria
- The skill triggers correctly when users ask about README generation
- Scripts run end-to-end without errors on a real-world GitHub repository
- Generated READMEs include all required sections (installation, usage, API docs)
- Output is immediately useful without extensive manual editing
- CLI interface works for direct usage with proper error handling
- Error handling provides meaningful messages and appropriate exit codes
- Skill handles various repository types and programming languages
- Generated READMEs follow common documentation standards and best practices
