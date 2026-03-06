# Changelog

All notable changes to Rune (Self-Improving AI Memory System) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.5] - 2026-02-25

### 🔧 METADATA INTEGRITY FIX

#### Fixed
- **Registry metadata mismatch** - Resolved inconsistency where registry claimed "No install spec / instruction-only" but package contains install.sh and setup components
- **ClawHub display name** - Now properly shows "Rune - Self-Improving AI Memory" instead of generic "Skill"
- **Installation metadata** - Ensured skill.json install specifications are correctly published to registry

#### Changed
- **Clear installation documentation** - Explicitly documents that this is an installable skill with system-level integration
- **Metadata consistency** - All package files and registry metadata now accurately reflect installation requirements

#### Technical
- **Publishing process** - Fixed ClawHub publication to include proper --name parameter and installation metadata
- **Registry sync** - Resolved metadata inconsistencies caused by previous failed publications

## [1.1.3] - 2026-02-25

### 🚨 CRITICAL SECURITY FIX

#### Security
- **FIXED RCE vulnerability in context-inject.sh** - Added input sanitization to prevent shell injection attacks
- **CVE Impact**: Unsanitized $TOPIC parameter was vulnerable to command injection (e.g., `'; rm -rf / #'`)
- **Resolution**: Applied same sanitization pattern as rune-session-handler.sh to workflow scripts
- **Scope**: Fixed both local scripts and setup-workflow.sh generated scripts

#### Changed
- **setup-workflow.sh** - Now creates secure context-inject.sh with input sanitization
- **Security documentation** - Enhanced warnings about input validation in workflow scripts

#### Lessons
- **Shell injection prevention** - ALL user inputs in shell scripts must be sanitized
- **Security review process** - Third-party security analysis caught vulnerability we missed

## [1.1.2] - 2026-02-25

### 📋 Documentation Accuracy & Housekeeping

#### Fixed
- **Version inconsistencies** - Synchronized all version numbers to v1.1.2 across SKILL.md, package.json, skill.json, _meta.json
- **Documentation accuracy** - Corrected SECURITY.md claims about "no external downloads" to accurately reflect npm install process
- **Session hook arguments** - Fixed sessionHooks in skill.json to use correct start/end arguments (from previous security scan)

#### Changed
- **SECURITY.md** - Updated to accurately describe npm dependency installation process
- **Version synchronization** - All package files now consistently show v1.1.2

#### Security
- **Session hook fix** - Ensures proper automated session hook invocation (prevents unexpected behavior)
- **Accurate documentation** - No false security claims about installation process

## [1.0.3] - 2026-02-25

### 📋 Documentation Fixes (ClawHub Security Review Response)

#### Fixed
- **Repository URL inconsistencies** in SKILL.md (placeholder URLs updated)
- **Naming clarification** - Added section explaining Rune (skill) vs brokkr-mem (CLI)
- **Installation disclosure** - Clear documentation of installation side effects

#### Added
- **Installation warning section** with detailed disclosure of what installation does
- **Enhanced security documentation** including NPM dependency considerations  
- **Privacy recommendations** for high-security environments
- **Better explanation** of the relationship between skill name and CLI name

#### Changed
- Updated placeholder repository URLs from `github.com/your-org/brokkr-mem` to `github.com/TheBobLoblaw/rune`
- Enhanced installation section with security considerations
- Improved security & privacy documentation based on ClawHub review feedback

#### Security
- **No functional changes** - this is purely documentation improvement
- All security fixes from v1.0.2 (CVE-2026-0001) remain intact
- Added better disclosure of npm installation security considerations

## [1.0.2] - 2026-02-24

### 🔒 SECURITY

**CRITICAL SECURITY FIX** - CVE-2026-0001

#### Fixed
- **Shell injection vulnerability** in session hooks that allowed remote code execution
- Direct use of unsanitized `$MESSAGE` variable in `brokkr-mem` commands
- Potential for arbitrary command execution through crafted user input

#### Added
- **Secure session handler** (`rune-session-handler.sh`) with comprehensive input sanitization
- Input length limits and dangerous character filtering
- Safe command execution patterns throughout
- Security documentation and usage guidance

#### Changed
- Session hooks now use secure wrapper instead of direct command execution
- `sessionStart` and `sessionEnd` hooks route through sanitization layer
- Updated SKILL.md with security best practices and warnings

#### Security Details
```bash
# BEFORE (Vulnerable):
"sessionStart": {"commands": ["brokkr-mem recall \"$MESSAGE\" --limit 10"]}

# AFTER (Secure):  
"sessionStart": {"commands": ["./rune-session-handler.sh start"]}
```

**Attack Vector**: Malicious input like `test"; rm -rf /; echo "hacked` could execute arbitrary commands
**Impact**: Complete system compromise possible
**Fix**: All user input now sanitized before shell execution

---

## [1.0.1] - 2026-02-24

### Added
- Enhanced extraction engine with multi-format support
- Session-aware context injection
- Improved fact consolidation algorithms
- Autonomous task detection and recommendations

### Changed
- Optimized memory retrieval performance
- Enhanced CLI usability and error handling
- Improved fact scoring accuracy

### Fixed
- Memory consolidation edge cases
- CLI argument parsing improvements

---

## [1.0.0] - 2026-02-23

### Added
- **Initial Release** - Self-Improving AI Memory System
- SQLite-based persistent memory storage
- Local-first design with Ollama integration
- Intelligent fact extraction and scoring
- Session-aware context management
- CLI tools: `brokkr-mem` and `rune`
- OpenClaw skill integration
- Heartbeat maintenance automation
- Memory categories: person, project, tool, lesson, decision, preference
- Local and cloud LLM support (Ollama, OpenAI, Anthropic)

### Features
- **Intelligent Storage**: Facts auto-categorized and scored for relevance
- **Smart Retrieval**: Semantic and keyword search with LLM ranking
- **Self-Improvement**: System learns from usage patterns and adapts
- **Privacy-First**: Works completely offline with local models
- **Agent Integration**: Designed for AI orchestration workflows

### Security
- No credential storage in memory database
- Local-first processing for privacy
- Optional cloud API integration
- Transparent data handling