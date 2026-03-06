# Publishing to ClawHub

This document outlines the steps to publish the EdStem skill to ClawHub.

## Pre-Publishing Checklist

- [x] Remove institution-specific code and documentation
- [x] Add flexible command-line parameters
- [x] Update SKILL.md with general documentation
- [x] Create README.md for repository listing
- [x] Add VERSION file (currently: 1.1.0)
- [x] Create CHANGELOG.md with version history
- [x] Test scripts with --help flag
- [x] Commit all changes to git

## Version: 1.1.0

**Release Date:** 2025-02-17

**Key Changes:**
- Made institution-agnostic (works with any EdStem school)
- Added flexible parameters (course_id, output_dir, --course-name)
- Removed hardcoded Columbia course mappings
- Improved error handling and documentation

## Git Repository Status

```bash
Current branch: master
Recent commits:
  8101fef - Add CHANGELOG.md documenting version history
  d3fa70c - Bump version to 1.1.0 and add README for ClawHub
  e1be476 - Make EdStem skill institution-agnostic
  b9895a1 - Initial EdStem skill (v1.0.0)
```

## Files Ready for Publishing

### Core Files
- `scripts/fetch-edstem.py` - Main Python script
- `scripts/fetch-edstem.sh` - Bash alternative
- `SKILL.md` - OpenClaw skill documentation

### Metadata
- `VERSION` - Version number (1.1.0)
- `README.md` - Repository/ClawHub listing
- `CHANGELOG.md` - Version history
- `PUBLISHING.md` - This file

### Git
- `.git/` - Git repository with full history

## Publishing Steps

### Option 1: Push to Public Git Repository

1. **Create GitHub/GitLab repository:**
   ```bash
   # On GitHub/GitLab, create new repository: openclaw-skill-edstem
   ```

2. **Add remote and push:**
   ```bash
   cd /home/axel/.openclaw/workspace/skills/edstem
   git remote add origin https://github.com/YOUR_USERNAME/openclaw-skill-edstem.git
   git branch -M main
   git push -u origin main
   ```

3. **Create release:**
   - Go to repository releases
   - Create new release with tag `v1.1.0`
   - Title: "EdStem Skill v1.1.0 - Institution-Agnostic"
   - Description: Copy from CHANGELOG.md [1.1.0] section
   - Attach: None needed (git release is sufficient)

### Option 2: Submit to ClawHub Registry

1. **Package the skill:**
   ```bash
   cd /home/axel/.openclaw/workspace/skills
   tar -czf edstem-1.1.0.tar.gz edstem/
   ```

2. **Submit to ClawHub:**
   ```bash
   openclaw skills publish edstem
   # Or manually upload edstem-1.1.0.tar.gz to ClawHub web interface
   ```

3. **Fill out ClawHub listing:**
   - Name: `edstem`
   - Version: `1.1.0`
   - Description: Copy from README.md overview
   - Tags: `edstem`, `education`, `forum`, `api`, `discussion`
   - License: `MIT`
   - Repository: (link to git repo if public)

## Installation Instructions (for users)

### Via ClawHub (when published):
```bash
openclaw skills install edstem
```

### Via Git:
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/YOUR_USERNAME/openclaw-skill-edstem.git edstem
```

### Manual:
1. Download release tarball
2. Extract to `~/.openclaw/workspace/skills/edstem`
3. Update `ED_TOKEN` in `scripts/fetch-edstem.py`

## Post-Publishing

- [ ] Update ClawHub listing with repository URL
- [ ] Announce on OpenClaw community channels
- [ ] Monitor for issues and feature requests
- [ ] Plan next version improvements

## Future Version Ideas (v1.2.0+)

- Better XML parsing for thread content
- Filter by category or date range
- Incremental sync (fetch only new threads)
- Export to HTML or other formats
- Support for multiple authentication tokens
- EdStem webhook integration
- Search and indexing features

## Notes

**Security:** The skill includes a bearer token by default. Users should:
1. Replace with their own token
2. Keep the token private (add to .gitignore if forking)
3. Rotate token periodically for security

**Breaking Changes from v1.0.0:**
- Removed hardcoded Columbia course mappings
- Changed command-line interface (now requires course_id as argument)
- Changed default output location (now `./edstem-<course_id>` instead of fixed paths)

Users upgrading from v1.0.0 should review the new usage in README.md.
