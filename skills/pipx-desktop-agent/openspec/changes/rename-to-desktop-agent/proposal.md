# Proposal: Rename to Desktop-Agent and Configure UVX Distribution

## Summary
Rename the project from `desktop-skill` to `desktop-agent` and configure it for easy distribution via `uvx desktop-agent`, enabling one-command installation and execution.

## Motivation
- **Clearer naming**: "desktop-agent" better reflects that this is an AI agent skill for desktop control
- **Easy distribution**: Using `uvx` allows users and AI agents to run the tool without manual installation
- **Better discoverability**: Standard Python package naming improves searchability
- **Simplified usage**: `uvx desktop-agent <command>` is more intuitive than `python main.py <command>`

## Proposed Changes

### 1. Package Renaming
- Rename package from `desktop-skill` to `desktop-agent`
- Update all references in documentation, code, and configuration files
- Ensure backwards compatibility notes are added to README

### 2. UVX Distribution Configuration
- Configure `pyproject.toml` to support uvx execution
- Set up proper entry points for CLI execution
- Ensure the package can be installed from:
  - Local directory: `uv pip install .`
  - UVX direct execution: `uvx desktop-agent <command>`
  - Standard pip: `pip install desktop-agent` (future PyPI publication)

### 3. CLI Invocation Updates
- Primary invocation: `uvx desktop-agent <category> <command>`
- Alternative (local install): `desktop-agent <category> <command>`
- Development mode: `python -m desktop_agent <category> <command>`
- Backwards compat (dev only): `python main.py <category> <command>`

### 4. Documentation Updates
- Update SKILL.md with new invocation patterns
- Update README.md with uvx installation instructions
- Update examples to use `uvx desktop-agent` or `desktop-agent`
- Add migration guide for existing users (if any)

## Benefits
1. **One-command execution**: `uvx desktop-agent mouse move 100 200` works instantly
2. **No installation required**: uvx handles dependencies automatically
3. **Version control**: uvx can run specific versions: `uvx desktop-agent@0.2.0`
4. **Better for AI agents**: Clearer command structure and automatic dependency resolution

## Trade-offs
- Requires renaming files and updating all documentation
- Users with current installation will need to migrate
- Slightly longer command vs `python main.py` (but more explicit)

## Success Criteria
- [ ] Project renamed to `desktop-agent`
- [ ] `uvx desktop-agent --help` works without prior installation
- [ ] `uvx desktop-agent mouse position` executes successfully
- [ ] All documentation reflects new naming
- [ ] Installation script updated for new structure

## Out of Scope
- Publishing to PyPI (can be done later)
- Changing command structure or API
- Adding new features
