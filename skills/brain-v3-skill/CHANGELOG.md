# Changelog

## [3.1.0] - 2026-02-07

### 🚀 PyPI Installation & CLI

ClawBrain is now available on PyPI! No more `curl | bash` - just pip install:

```bash
pip install clawbrain[all]
clawbrain setup
clawbrain backup-key --all
```

### ✨ New Features

#### Command-Line Interface (CLI)

New `clawbrain` CLI for setup and key management:

| Command | Description |
|---------|-------------|
| `clawbrain setup` | Interactive setup - generates key, installs hooks |
| `clawbrain generate-key` | Generate new encryption key |
| `clawbrain show-key` | Display current encryption key |
| `clawbrain backup-key` | Backup key (file, QR code, clipboard) |
| `clawbrain migrate-secrets` | Migrate unencrypted secrets to encrypted storage |
| `clawbrain health` | Check health status |
| `clawbrain info` | Show installation info |

#### Migration for Existing Installations

**Automatic Migration:** When encryption is enabled for the first time (new key generated), existing unencrypted secrets are automatically migrated to encrypted storage. No manual intervention required.

**Manual Migration:** If you prefer to control the migration process:

```bash
# Check for unencrypted secrets (dry run)
clawbrain migrate-secrets --dry-run

# Migrate all unencrypted secrets
clawbrain migrate-secrets
```

The `setup` command will automatically detect and notify you about unencrypted secrets.

#### Secure Key Backup Options

Multiple ways to backup your encryption key:

```bash
# Backup to file
clawbrain backup-key --output ~/my_backup.txt

# Display as QR code (scan with phone)
clawbrain backup-key --qr

# Copy to clipboard
clawbrain backup-key --clipboard

# All methods at once
clawbrain backup-key --all
```

#### Optional Dependencies

Install only what you need:

```bash
pip install clawbrain[encryption]  # Just encryption
pip install clawbrain[postgres]    # PostgreSQL support
pip install clawbrain[redis]       # Redis caching
pip install clawbrain[embeddings]  # Semantic search
pip install clawbrain[qr]          # QR code key backup
pip install clawbrain[all]         # Everything
```

### 📦 Package Improvements

- **PyPI compliant** - Proper package metadata and classifiers
- **Entry points** - `clawbrain` command available after install
- **MANIFEST.in** - All necessary files included in distribution
- **Optional dependencies** - Install only what you need

### 🔒 Security Improvements

- **Centralized key storage** - Keys stored in `~/.config/clawbrain/.brain_key`
- **Automatic key generation** - Secure keys generated during setup
- **Secure permissions** - Key files created with 0600 permissions
- **Multiple backup methods** - File, QR code, clipboard options

### 📁 New Files

- `clawbrain_cli.py` - Command-line interface module
- `MANIFEST.in` - Package manifest for distribution

### 📝 Documentation Updates

- Updated installation instructions for PyPI
- Added CLI command documentation
- Removed `curl | bash` as primary install method
- Added key backup instructions

---

## [3.0.1] - 2026-02-07

### 🔒 Security Fixes (CRITICAL)

This release addresses critical security vulnerabilities identified in v0.1.6:

#### 1. Encrypted Secrets Support ✅
- **Fixed**: Sensitive data (API keys, credentials) now properly encrypted
- Implemented Fernet symmetric encryption using `cryptography` library
- Added automatic encryption for `memory_type="secret"`
- Auto-generates secure encryption keys with restricted permissions (0600)
- Automatic decryption when retrieving encrypted memories

**Usage:**
```python
# Store encrypted secret
brain.remember(
    agent_id="assistant",
    memory_type="secret",
    content="sk-1234567890abcdef",
    key="openai_api_key"
)

# Retrieve automatically decrypts
secrets = brain.recall(agent_id="assistant", memory_type="secret")
api_key = secrets[0].content  # Decrypted
```

#### 2. Secure Installation Method ✅
- **Fixed**: Reduced supply chain attack risk
- Documentation now recommends manual git clone first
- Added security warnings to `curl | bash` installation method
- Added interactive confirmation to remote-install.sh
- Display commit hash and author for verification

**Recommended Installation:**
```bash
# Secure method (recommended)
cd ~/.openclaw/skills
git clone https://github.com/clawcolab/clawbrain.git
cd clawbrain
./install.sh
```

### 📦 New Features

- **Encryption support**: New `BRAIN_ENCRYPTION_KEY` environment variable
- **Optional dependencies**: Added cryptography as optional dependency in pyproject.toml
- **Test suite**: Added test_encryption.py for verification
- **Security documentation**: Added SECURITY_FIXES.md

### 🔧 Configuration

New environment variable:

| Variable | Description | Default |
|----------|-------------|---------|
| `BRAIN_ENCRYPTION_KEY` | Fernet key for encryption | Auto-generated |

### 📁 Files Modified

- `clawbrain.py` - Added encryption methods
- `brain/clawbrain.py` - Added encryption methods
- `README.md` - Updated installation instructions
- `SKILL.md` - Updated installation instructions
- `remote-install.sh` - Added security prompts
- `pyproject.toml` - Added optional dependencies
- `skill.json` - Updated version and environment vars

### 📁 New Files

- `SECURITY_FIXES.md` - Detailed security fix documentation
- `test_encryption.py` - Encryption functionality tests

### ⚠️ Important Notes

- **Backup encryption keys**: Lost keys = lost encrypted data
- Existing unencrypted memories remain unencrypted
- Install cryptography: `pip install cryptography`
- For production: set custom `BRAIN_ENCRYPTION_KEY`

---

## [0.1.6] - 2026-02-04

### 🚀 One-Command Install

ClawBrain is now truly plug-and-play. Install with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/clawcolab/clawbrain/main/remote-install.sh | bash
```

Then restart your service:
```bash
sudo systemctl restart clawdbot  # or openclaw
```

**That's it!** No configuration required. Works out of the box with SQLite.

---

### ✨ New Features

- **Auto-refresh on startup** - Brain automatically loads memories when service restarts
- **Session save on /new** - Saves conversation context when user starts new session
- **Native hooks support** - Works with both ClawdBot and OpenClaw
- **Auto-detection** - Detects platform, skills directory, and storage backend automatically
- **PostgreSQL datetime fix** - Properly handles datetime serialization from PostgreSQL

### 🔧 Configuration (Optional)

All configuration is optional. Set environment variables only if needed:

| Variable | Description | Default |
|----------|-------------|---------|
| `BRAIN_AGENT_ID` | Unique ID for memories | `default` |
| `BRAIN_POSTGRES_HOST` | PostgreSQL host | SQLite used |
| `BRAIN_REDIS_HOST` | Redis for caching | Disabled |

### 📁 New Files

- `install.sh` - Local installer script
- `remote-install.sh` - Curl-based remote installer
- `hooks/clawbrain-startup/` - Native hook for gateway events
- `scripts/brain_bridge.py` - Python bridge for hook→brain communication
- `scripts/migrate_agent_id.py` - Utility to migrate memories between agent IDs

### 🐛 Bug Fixes

- Fixed PostgreSQL datetime objects not serializing to JSON
- Fixed UserProfile datetime fields from PostgreSQL
- Fixed skills directory detection for different platform layouts

---

**Full Changelog**: https://github.com/clawcolab/clawbrain/compare/v0.1.5...v0.1.6
