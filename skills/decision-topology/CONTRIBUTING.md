# Contributing to Decision Topology

Thanks for your interest in improving this skill. Here's how to contribute.

## Getting Started

1. Fork the repo
2. Clone your fork
3. Create a branch: `git checkout -b my-change`
4. Make your changes
5. Test locally (see below)
6. Commit and push
7. Open a pull request

## Local Testing

The skill is a standalone Node.js script with zero dependencies. Test it directly:

```bash
# Set a temp trees directory
export TOPOLOGY_TREES_DIR=/tmp/test-trees

# Create a tree (args piped via stdin)
echo '{"topic": "test topic"}' | node scripts/topology.js init

# Add nodes, render, etc.
node scripts/topology.js list
echo '{"file": "<path from init>"}' | node scripts/topology.js render
```

Clean up after testing:
```bash
rm -rf /tmp/test-trees
```

## What to Contribute

**Welcome:**
- Bug fixes
- New export formats (beyond ASCII and Mermaid)
- Performance improvements for large trees
- Better association/matching algorithms
- New analysis commands
- Documentation improvements

**Please discuss first** (open an issue):
- Changes to the tree schema (v2)
- New node types or status values
- Changes to the concept index format
- Anything that breaks backward compatibility with existing tree files

## Code Style

- No external dependencies — the script must stay zero-dep (Node.js built-ins only)
- Keep functions focused and small
- Error messages should be clear and actionable
- JSON output for machine-readable commands, plain text for human-readable commands

## SKILL.md Changes

If you modify `scripts/topology.js` (add commands, change behavior), update `SKILL.md` to match. The SKILL.md is the contract that OpenClaw agents read — if it's wrong, agents will call commands incorrectly.

Also update `references/schema.md` if the tree/node schema changes.

## Pull Request Guidelines

- One logical change per PR
- Describe what and why in the PR description
- If fixing a bug, include steps to reproduce
- If adding a feature, include a usage example
- Make sure existing commands still work after your changes

## Releasing

After a PR is merged, the maintainer publishes to ClawHub:

```bash
clawhub publish . --slug decision-topology --version <new-version> --changelog "what changed"
```

Version bumps follow semver:
- **Patch** (1.0.x): bug fixes, docs
- **Minor** (1.x.0): new commands, non-breaking features
- **Major** (x.0.0): schema changes, breaking changes
