<!--
Sync Impact Report:
- Version change: None -> 1.0.0 (Initial Ratification)
- List of modified principles: N/A
- Added sections: I. OpenClaw Native, II. Automation First, III. Frictionless Adoption, IV. Upstream Alignment, V. Test-Driven Validation
- Removed sections: N/A
- Templates requiring updates: ✅ None (Standard templates align with these principles)
- Follow-up TODOs: None
-->

# speckit-agent-skills-for-openclaw Constitution

## Core Principles

### I. OpenClaw Native
Skills must be adapted to run natively within the OpenClaw ecosystem, respecting its directory structures (`.openclaw/skills`) and execution models without requiring user hacks or manual path adjustments. The end-user experience must be indistinguishable from a native OpenClaw skill.

### II. Automation First
All transformations from upstream `spec-kit` to OpenClaw format must be scriptable and reproducible. We explicitly reject manual editing of generated files as a sustainable practice. Changes must be applied via patches or transformation scripts to ensure future upstream releases can be ingested with minimal effort.

### III. Frictionless Adoption
The setup process must be a single command (`init-speckit-openclaw.sh`). Documentation must be high-quality ("lucrative") and comprehensive to encourage adoption on ClawHub. If a user has to read the source code to install it, we have failed.

### IV. Upstream Alignment
The upstream repository (or `.claude/skills` equivalent) is the single source of truth for skill logic. We do not fork logic unless necessary for the port; we adapt interfaces. Enhancements to core skill logic should ideally be contributed upstream rather than diverged locally.

### V. Test-Driven Validation (NON-NEGOTIABLE)
We must verify that the ported skills actually work. A "successful port" is not just file existence; it is the successful execution of the skill by an OpenClaw agent. Changes are not complete until they are verified against an agent (or a faithful simulation).

## Technical Constraints

The solution must operate within the standard POSIX shell environment (bash/zsh) for initialization scripts to ensure broad compatibility (macOS/Linux). No heavy external dependencies (like Python/Node.js) should be required for the *end-user* installation process, though they may be used for the developer's build/transformation process if necessary.

## Development Workflow

1. **Analyze Upstream**: Check `spec-kit` for changes.
2. **Transform**: Run automation scripts to generate OpenClaw artifacts.
3. **Verify**: Test with OpenClaw agent context.
4. **Publish**: Update `init` script and README for ClawHub.

## Governance

This constitution supersedes all other practices. Amendments require a documented pull request and semantic version bump.

**Version**: 1.0.0 | **Ratified**: 2026-02-20 | **Last Amended**: 2026-02-20
