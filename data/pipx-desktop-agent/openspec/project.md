# Project Context

## Purpose
Desktop Control Skill is an AI agent skill that provides desktop automation capabilities through PyAutoGUI. It allows AI agents to control the mouse, keyboard, take screenshots, and interact with the desktop environment programmatically.

## Tech Stack
- Python 3.12+
- PyAutoGUI (desktop automation library)
- Typer (CLI framework)
- UV (Python package installer and manager)

## Project Conventions

### Code Style
- Use descriptive function and variable names
- Include docstrings for all public functions
- Follow PEP 8 naming conventions
- Type hints where applicable

### Architecture Patterns
- Modular command organization: commands organized by category (mouse, keyboard, screen, message)
- CLI structure: Main entry point delegates to sub-applications
- Each command module is a Typer app registered with the main app

### Testing Strategy
- Manual verification of commands
- Integration testing through actual CLI invocation
- Validation of help text and command discovery

### Git Workflow
- Standard Git workflow with feature branches
- Clear commit messages describing changes

## Domain Context
- **Desktop Automation**: Commands interact with OS-level GUI elements
- **AI Agent Integration**: Designed to be easily discoverable and usable by AI agents
- **Cross-platform**: Primary target is Windows, but PyAutoGUI supports macOS and Linux

## Important Constraints
- Requires Python 3.12+
- PyAutoGUI has a fail-safe feature (moving mouse to screen corner aborts)
- Commands may fail if UI state changes between invocation and execution
- Screenshot and image location features depend on screen resolution

## External Dependencies
- PyAutoGUI: Core automation library
- Typer: CLI framework
- UV: Package management and distribution
