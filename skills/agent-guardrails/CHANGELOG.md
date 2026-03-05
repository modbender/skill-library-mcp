# Changelog

All notable changes to Agent Guardrails will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-02

### Added
- **Deployment Verification System** - Prevents "code complete but not wired to production" failures
  - `create-deployment-check.sh` - Generate deployment verification for any project
  - `deployment-verification-guide.md` - Complete implementation guide
  - `.deployment-check.sh` template with integration point testing
  - Git hook integration for mandatory verification before commit

- **Skill Update Feedback Loop** - Meta-enforcement to ensure improvements flow back to skills
  - `install-skill-feedback-loop.sh` - One-command installation of automatic detection
  - `skill-update-feedback.md` - Full documentation of the feedback loop pattern
  - Automatic detection of enforcement improvements via git hooks
  - Semi-automatic commit system with human confirmation
  - Task queue (`.pending-skill-updates.txt`) for tracking updates
  - Archive system for processed improvements

- **Fourth Failure Mode** - Documented "Skill Update Gap" as meta-enforcement challenge
  - Detection patterns for enforcement-related changes
  - Auto-categorization of which skill should be updated
  - Task generation with actionable steps

### Enhanced
- **SKILL.md** - Now documents all 4 failure modes with enforcement strategies
- **Enforcement Hierarchy** - Added meta-enforcement layer to the reliability stack
- **Documentation** - Added comprehensive guides for deployment and feedback loop

### Fixed
- Improved pattern matching in detection scripts
- Better error handling in git hooks

## [1.0.0] - 2026-02-01

### Added - Initial Release

#### Core Scripts
- `install.sh` - One-command installation for any project
- `pre-create-check.sh` - List existing modules before creating new files
- `post-create-validate.sh` - Detect duplicates, missing imports, bypass patterns
- `check-secrets.sh` - Scan for hardcoded credentials

#### Git Hooks
- Pre-commit hook blocking bypass patterns
- Pre-commit hook blocking hardcoded secrets
- Customizable pattern matching

#### Documentation
- `SKILL.md` - Complete usage guide
- `README.md` - Quick start and overview
- `enforcement-research.md` - Why code > prompts for reliability
- `agents-md-template.md` - Template for project-level enforcement rules
- `SKILL_CN.md` - Chinese translation

#### Assets
- `pre-commit-hook` - Ready-to-install git hook
- `registry-template.py` - Template for module registries

### Failure Modes Addressed (v1.0.0)
1. **Reimplementation** - Agent creates "quick version" instead of importing
2. **Hardcoded Secrets** - Credentials in code instead of env vars
3. **Deployment Gap** - Feature built but not wired to production

## [Unreleased]

### Planned for v1.2.0
- Phase 3: Fully automatic skill updates (AI-powered extraction)
- Visual enforcement dashboard
- Language support beyond bash (Python, Node.js)
- Pre-built templates for common project types
- Community pattern library

### Under Consideration
- Integration with popular project scaffolding tools
- Real-time enforcement monitoring
- Team collaboration features
- Cloud-based pattern sharing

---

## Migration Guides

### Upgrading from 1.0.0 to 1.1.0

No breaking changes. To add new features to existing installations:

```bash
# Add deployment verification
cd your-project/
bash /path/to/agent-guardrails/scripts/create-deployment-check.sh .

# Add skill update feedback loop
bash /path/to/agent-guardrails/scripts/install-skill-feedback-loop.sh .
```

Your existing hooks and scripts will continue to work unchanged.

---

## Credits

Inspired by real production failures and the lesson that **mechanical enforcement > markdown rules**.

Built with contributions from the AI agent development community.

Special thanks to all early adopters who reported issues and suggested improvements.
