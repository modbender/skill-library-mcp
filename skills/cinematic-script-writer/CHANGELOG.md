# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-02-10

### Added
- **Google Drive Storage Integration**
  - Save all generated content to Google Drive
  - Organized folders with story title
  - OAuth authentication
  - Local storage option (downloads)
  - Complete project export (script, prompts, consistency, voice, metadata)
  - Shareable links

### New Files
- `storage-adapter.ts` - Storage adapters (Google Drive, Local)
- `storage-manager.ts` - File organization and saving
- `EXAMPLE-STORAGE.md` - Storage usage examples

## [1.2.0] - 2026-02-10

### Added
- **Consistency System**
  - Character reference sheets for visual consistency
  - Voice profiles for dialogue consistency
  - Environment style guides for era-appropriate content
  - Prompt builder with consistency enforcement
  - Anachronism detection (validates era-appropriate elements)
  - Validation system for prompts

### New Files
- `consistency-system.ts` - Consistency management
- `prompt-builder.ts` - Consistent prompt generation
- `EXAMPLE-CONSISTENCY.md` - Consistency examples

## [1.1.0] - 2026-02-10

### Added
- **Comprehensive Cinematography Database**
  - 20+ camera angles with emotional impact
  - 20+ camera movements
  - 25+ shot types
  - 30+ lighting techniques
  - 20+ composition rules
  - 20+ color grading styles
  - 25+ visual aesthetics
  - 15+ genre cinematography guides
  - Indian cinematography styles

### New Files
- `cinematography-db.ts` - Camera techniques database
- `cinematography-api.ts` - Unified API
- `lighting-db.ts` - Lighting and composition
- `visual-styles-db.ts` - Visual aesthetics

## [1.0.0] - 2026-02-10

### Added
- Initial release of Cinematic Script Writer Skill
- Context management (characters, era, settings)
- Story idea generation
- Cinematic script creation with shots and camera angles
- Image/Video generation prompts
- YouTube metadata generation
- Basic camera techniques

### Files
- `skill-template/` - Template for creating new skills
- `examples/` - Example skills (weather, todo, file-manager)
- `skills/cinematic-script-writer/` - Main skill implementation
- `EXAMPLE-KUTIL.md` - Complete usage example
