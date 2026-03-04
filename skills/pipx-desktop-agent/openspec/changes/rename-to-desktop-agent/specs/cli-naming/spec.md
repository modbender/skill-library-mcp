# CLI Naming Specification

## MODIFIED Requirements

### Requirement: CLI Command Naming
The CLI MUST be invoked using `desktop-agent` instead of `desktop-skill`.

#### Scenario: Primary Invocation
**Given** uvx or local installation  
**When** user runs `desktop-agent --help`  
**Then** help text should display  
**And** command should be recognized

#### Scenario: Category Commands
**Given** the CLI is available  
**When** user runs `desktop-agent mouse position`  
**Then** mouse position should be returned  
**And** same structure as before but with new name

### Requirement: Documentation Consistency  
All documentation MUST reference the new CLI name `desktop-agent`.

#### Scenario: SKILL.md References
**Given** an AI agent reading SKILL.md  
**When** looking for command examples  
**Then** all examples should use `desktop-agent`  
**And** no references to `desktop-skill` should exist

#### Scenario: README Instructions
**Given** a new user reading README  
**When** following installation instructions  
**Then** all commands should use `desktop-agent`  
**And** uvx invocation should be primary method

## REMOVED Requirements

### Requirement: Python Script Invocation (Deprecated)
The pattern `python main.py <command>` is DEPRECATED for production use.

#### Scenario: Development Only
**Given** development environment  
**When** using `python main.py`  
**Then** it may still work (backwards compat)  
**But** should not be documented as primary method
