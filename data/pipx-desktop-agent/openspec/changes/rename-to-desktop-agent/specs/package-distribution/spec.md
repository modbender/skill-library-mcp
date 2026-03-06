# Package Distribution Specification

## ADDED Requirements

### Requirement: UVX-Compatible Package Structure
The package MUST be structured to support execution via `uvx` without prior installation.

#### Scenario: Zero-Install Execution
**Given** a user without the package installed  
**When** they run `uvx desktop-agent --help`  
**Then** the CLI help text should display  
**And** no manual installation steps should be required

#### Scenario: Command Execution via UVX
**Given** uvx is installed  
**When** user runs `uvx desktop-agent mouse position`  
**Then** the mouse position should be returned  
**And** all dependencies should be automatically resolved

### Requirement: Proper Python Package Structure
The package MUST follow standard Python package conventions for distribution.

#### Scenario: Package Import
**Given** the package is installed  
**When** a Python script imports `desktop_agent`  
**Then** the CLI app should be accessible  
**And** all command modules should be importable

#### Scenario: Module Execution
**Given** the package is installed  
**When** user runs `python -m desktop_agent --help`  
**Then** the CLI help should display  
**And** it should behave identically to `desktop-agent --help`

### Requirement: Entry Point Configuration
The package MUST define correct entry points for CLI execution.

#### Scenario: CLI Entry Point
**Given** the package is installed via pip/uv  
**When** user runs `desktop-agent <command>`  
**Then** the command should execute  
**And** the entry point should resolve to `desktop_agent:app`

## ADDED Requirements

### Requirement: Package Naming Convention
Package naming MUST follow Python and PyPA conventions.

#### Scenario: Module Name
**Given** the Python package  
**When** imported in code  
**Then** it should use `desktop_agent` (underscore)

#### Scenario: Distribution Name  
**Given** the package configuration  
**When** referenced in `pyproject.toml`  
**Then** it should use `desktop-agent` (hyphen)

#### Scenario: CLI Command Name
**Given** the installed CLI  
**When** invoked from terminal  
**Then** it should use `desktop-agent` (hyphen)

### Requirement: Dependency Management
All dependencies MUST be properly declared and automatically resolved.

#### Scenario: Automatic Dependency Installation
**Given** uvx is used to run the package  
**When** dependencies are not present  
**Then** uvx should automatically install them  
**And** the user should not see dependency errors

#### Scenario: Version Compatibility
**Given** the package requirements  
**When** checking Python version  
**Then** it should require Python 3.12+  
**And** should fail gracefully with clear message on older versions
