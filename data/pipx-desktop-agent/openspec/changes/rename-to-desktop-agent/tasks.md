# Tasks: Rename to Desktop-Agent

## Phase 1: Package Structure
- [ ] Rename package directory from root to `desktop_agent` (Python package naming)
- [ ] Update `pyproject.toml` with new package name and entry points
- [ ] Configure `pyproject.toml` for uvx compatibility
- [ ] Create `desktop_agent/__init__.py` with CLI app
- [ ] Move `main.py` logic to `desktop_agent/__main__.py`

## Phase 2: Module Updates
- [ ] Update imports in all command modules (`commands/` → `desktop_agent/commands/`)
- [ ] Ensure all internal imports use new package name
- [ ] Update any hardcoded references to "desktop-skill"

## Phase 3: Documentation
- [ ] Update SKILL.md with new command invocations (`uvx desktop-agent`)
- [ ] Update README.md with uvx installation instructions
- [ ] Update examples/automation_examples.md with new command format
- [ ] Add migration notes for existing users

## Phase 4: Scripts
- [ ] Update `scripts/install.py` to reference new package name
- [ ] Add uvx-based installation verification
- [ ] Update quick start examples in install script

## Phase 5: Verification
- [ ] Test `uvx desktop-agent --help` (external invocation)
- [ ] Test `uvx desktop-agent mouse position`
- [ ] Test `uvx desktop-agent screen size`
- [ ] Test all command categories work via uvx
- [ ] Verify local development mode still works
- [ ] Run full command suite regression test

## Phase 6: Final Touches
- [ ] Update .gitignore if needed for new structure
- [ ] Verify README quickstart works end-to-end
- [ ] Archive old walkthrough and create new one
