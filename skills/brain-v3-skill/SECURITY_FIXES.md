# Security Fixes - Version 0.1.6 → 0.1.7

## Summary

This document outlines the security improvements made to ClawBrain to address vulnerabilities identified in the security scan.

## Issues Addressed

### 1. ✅ Unencrypted Sensitive Data Storage (CRITICAL)

**Problem:**
- The `remember()` method consistently set `content_encrypted=False`
- Sensitive data (API keys, credentials) stored in plaintext in the database
- Documentation claimed encryption but implementation was missing

**Solution:**
- Implemented Fernet symmetric encryption using `cryptography` library
- Added automatic encryption for `memory_type="secret"`
- Auto-generates and securely stores encryption keys with 0600 permissions
- Automatic decryption when retrieving encrypted memories
- Added encryption methods: `_setup_encryption()`, `_encrypt()`, `_decrypt()`

**Files Modified:**
- `clawbrain.py`
- `brain/clawbrain.py`

**Changes:**
1. Added cryptography import and availability check
2. Added `BRAIN_ENCRYPTION_KEY` configuration option
3. Implemented encryption key management (auto-generation with secure storage)
4. Modified `remember()` to encrypt content when `memory_type="secret"`
5. Modified `_row_to_memory()` to automatically decrypt encrypted content
6. Updated `Memory` dataclass usage to properly set `content_encrypted` field

**Usage Example:**
```python
from clawbrain import Brain

brain = Brain()

# Store encrypted secret
brain.remember(
    agent_id="assistant",
    memory_type="secret",
    content="sk-1234567890abcdef",
    key="openai_api_key"
)

# Retrieve automatically decrypts
secrets = brain.recall(agent_id="assistant", memory_type="secret")
api_key = secrets[0].content  # Decrypted automatically
```

### 2. ✅ Insecure Installation Method (SUPPLY CHAIN RISK)

**Problem:**
- Primary installation method was `curl | bash` from remote URL
- No verification of code before execution
- High supply chain attack risk

**Solution:**
- Reordered documentation to recommend secure manual installation first
- Added security warnings to `curl | bash` method
- Added interactive confirmation prompt to remote-install.sh
- Display commit hash and author information for transparency
- Updated documentation with security notices

**Files Modified:**
- `README.md`
- `SKILL.md`
- `remote-install.sh`

**Changes:**
1. Prioritized manual git clone in installation instructions
2. Added ⚠️ security warnings about supply chain risks
3. Added interactive confirmation before remote script execution
4. Display git commit information for verification
5. Recommend manual method for production environments

**Recommended Installation:**
```bash
# Secure manual method (recommended)
cd ~/.openclaw/skills
git clone https://github.com/clawcolab/clawbrain.git
cd clawbrain
./install.sh
```

### 3. ✅ Dependencies and Package Management

**Problem:**
- Encryption dependency not documented in package manifest
- No clear indication of optional vs required dependencies

**Solution:**
- Added optional dependencies to `pyproject.toml`
- Documented encryption requirements in README and SKILL docs

**Files Modified:**
- `pyproject.toml`

**Changes:**
```toml
[project.optional-dependencies]
encryption = ["cryptography>=41.0.0"]
embeddings = ["sentence-transformers>=2.0.0"]
postgres = ["psycopg2-binary>=2.9.0"]
redis = ["redis>=4.0.0"]
all = [
    "cryptography>=41.0.0",
    "sentence-transformers>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "redis>=4.0.0"
]
```

## Installation with Encryption Support

```bash
# Install with encryption support
pip install git+https://github.com/clawcolab/clawbrain.git#egg=clawbrain[encryption]

# Install all optional dependencies
pip install git+https://github.com/clawcolab/clawbrain.git#egg=clawbrain[all]
```

## Encryption Key Management

### Auto-generated Keys
- Keys are automatically generated if `BRAIN_ENCRYPTION_KEY` is not set
- Stored at `.brain_key` (SQLite) or `~/.config/clawbrain/.brain_key`
- File permissions automatically set to 0600 (owner read/write only)

### Custom Keys
```bash
# Generate a key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set as environment variable
export BRAIN_ENCRYPTION_KEY="your-generated-key-here"
```

### Important Notes
- **Backup your encryption key!** Lost keys = lost encrypted data
- Encryption keys are specific to the installation
- Moving the database requires moving the encryption key
- Key rotation is not currently supported

## Backward Compatibility

- Existing unencrypted memories remain unencrypted
- New secrets automatically use encryption
- No breaking changes to existing API
- Graceful degradation if cryptography library not installed

## Security Best Practices

1. **Always install cryptography library for production use:**
   ```bash
   pip install cryptography
   ```

2. **Set a custom encryption key for production:**
   ```bash
   export BRAIN_ENCRYPTION_KEY="your-secure-key"
   ```

3. **Use manual installation for production environments**

4. **Backup encryption keys separately from database**

5. **Use PostgreSQL for production (better security features)**

6. **Restrict file permissions on database and key files**

## Testing

To verify encryption is working:

```python
from clawbrain import Brain

brain = Brain()

# Store a secret
brain.remember(
    agent_id="test",
    memory_type="secret",
    content="test-secret-value",
    key="test_key"
)

# Verify it's encrypted in the database
# (content should be base64-encoded ciphertext)

# Retrieve and verify decryption works
secrets = brain.recall(agent_id="test", memory_type="secret")
assert secrets[0].content == "test-secret-value"
assert secrets[0].content_encrypted == True
print("✅ Encryption working correctly")
```

## Migration Guide

For existing installations with unencrypted secrets:

### Automatic Migration on Startup (Default)

When ClawBrain initializes and generates a **new** encryption key (first-time encryption setup), it automatically:

1. Detects any existing unencrypted secrets in the database
2. Encrypts them using the newly generated key
3. Updates the records with encrypted content

This happens transparently during `Brain()` initialization - no manual intervention required for agent-driven installations.

```python
# Automatic migration happens here when key is first generated
brain = Brain()  
# Logs: "Found N unencrypted secrets - auto-migrating..."
# Logs: "Auto-migration complete: N secrets encrypted"
```

### CLI Migration (Manual Control)

Use the CLI command to check or migrate unencrypted secrets:

```bash
# Check what would be migrated (dry run)
clawbrain migrate-secrets --dry-run

# Migrate all unencrypted secrets
clawbrain migrate-secrets
```

The `clawbrain setup` command will also detect and notify you about unencrypted secrets.

### Programmatic Migration

If you need to migrate programmatically:

```python
from clawbrain import Brain

brain = Brain()

# Check for unencrypted secrets
unencrypted = brain.get_unencrypted_secrets()
print(f"Found {len(unencrypted)} unencrypted secrets")

# Migrate them (dry_run=False to actually migrate)
result = brain.migrate_secrets(dry_run=False)
print(f"Migrated: {result['migrated']}, Failed: {result['failed']}")
```

### Manual Migration (Legacy)

If you need manual control:

```python
from clawbrain import Brain

brain = Brain()

# 1. Retrieve old unencrypted secret
old_secrets = brain.recall(agent_id="assistant", memory_type="api_key")

# 2. Re-store with encryption
for secret in old_secrets:
    brain.remember(
        agent_id="assistant",
        memory_type="secret",  # Changed to "secret"
        content=secret.content,
        key=secret.key
    )

# 3. Delete old unencrypted version (optional)
# Implement deletion if needed
```

## Version History

- **v0.1.6**: Original version with security vulnerabilities
- **v0.1.7**: Security fixes and PyPI packaging
  - Added encryption support for secrets
  - Updated installation to use pip (PyPI)
  - Added auto-migration for existing unencrypted secrets
  - Added `clawbrain` CLI with setup, key management, and migration commands
  - Added `get_unencrypted_secrets()` and `migrate_secrets()` API methods

## References

- [Cryptography Library](https://cryptography.io/)
- [Fernet Symmetric Encryption](https://cryptography.io/en/latest/fernet/)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
