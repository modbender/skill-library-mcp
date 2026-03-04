---
name: programming-assistant
description: Assist with programming tasks using Claude CLI. Use when OpenClaw needs to perform coding tasks, create new programs, modify existing code, or get programming assistance. Handles project setup, code generation, debugging, refactoring, and code review.
---

# Programming Assistant Skill

## Overview

This skill enables OpenClaw to leverage Claude CLI for sophisticated programming tasks. It provides structured workflows for coding activities including project creation, code modification, debugging, and optimization.

## When to Use This Skill

Use this skill when OpenClaw encounters tasks such as:
- Creating new programs or scripts
- Modifying existing code files
- Debugging code issues
- Refactoring code for better performance/readability
- Performing code reviews
- Setting up new projects or adding features
- Converting code between languages or formats
- Generating documentation for code

## Prerequisites

- Claude CLI must be installed (`claude` command available)
- Claude desktop application should be accessible for IDE integration
- Sufficient permissions to read/write files in the target directory

## Basic Usage Patterns

### Pattern 1: Simple Code Generation
When tasked with creating new code:
1. Identify the target directory for the project
2. Use `claude --ide` to initiate the coding session
3. Provide specific instructions about the desired functionality
4. Review the generated code for correctness

### Pattern 2: Code Modification
When modifying existing code:
1. Determine the files that need to be changed
2. Use `claude --ide --add-dir <project-path>` to focus on the specific project
3. Request specific changes while preserving existing functionality
4. Verify the changes meet requirements

### Pattern 3: Project Setup
When setting up new projects:
1. Create the necessary directory structure
2. Generate initial configuration files
3. Set up basic file templates
4. Ensure dependencies are properly documented

## Workflow Steps

### 1. Assessment
- Determine the scope of the programming task
- Identify the target directory and relevant files
- Assess complexity and potential challenges

### 2. Preparation
- Ensure Claude CLI is available and authenticated
- Prepare any necessary context about the codebase
- Gather requirements and constraints

### 3. Execution
- Use appropriate Claude CLI commands based on the task
- Monitor progress and intervene if needed
- Ensure code quality and adherence to requirements

### 4. Verification
- Review generated code for correctness
- Test functionality if possible
- Validate that requirements were met

## Available Tools Integration

The skill integrates with Claude CLI tools:
- **Bash**: For running commands, tests, and system operations
- **Edit**: For modifying files directly
- **Read**: For reading files to understand context
- **IDE Integration**: For seamless code editing experience

## Error Handling

- If Claude CLI is unavailable, suggest alternative approaches
- If authentication is required, guide through setup process
- For complex projects, break tasks into smaller manageable pieces
- When facing permission issues, suggest alternative approaches

## Best Practices

1. Always consider security implications when generating code
2. Follow language-specific best practices and conventions
3. Include appropriate error handling in generated code
4. Add comments and documentation where appropriate
5. Ensure generated code is maintainable and readable