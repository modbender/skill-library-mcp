# Package Hygiene Guide

## Excluding Non-Text and System Files

This guide ensures your OpenClaw Twitter package is clean and professional.

## Files to ALWAYS Exclude

### 1. macOS System Files
```
.DS_Store           # Folder metadata
.DS_Store?          # Backup
._*                 # Resource forks
.Spotlight-V100     # Spotlight index
.Trashes            # Trash metadata
```

**Why exclude:** These are macOS-specific metadata files that:
- Leak information about your file system structure
- Cause confusion on other operating systems
- Add unnecessary bloat
- May contain sensitive path information

### 2. Windows System Files
```
Thumbs.db           # Thumbnail cache
Desktop.ini         # Folder customization
$RECYCLE.BIN/       # Recycle bin
```

### 3. Linux System Files
```
*~                  # Backup files
.directory          # KDE folder metadata
```

### 4. Sensitive Files (CRITICAL)
```
.env                # Environment variables
*.key               # API keys
*.pem               # Private keys
credentials.json    # Credentials
secrets.json        # Secrets
config.local.*      # Local configuration
```

**NEVER commit these files - they may contain:**
- AISA_API_KEY
- Twitter passwords
- Proxy credentials
- Database passwords
- API secrets

## Cleaning Your Package

### Before Distribution

```bash
# 1. Remove all .DS_Store files recursively
find . -name ".DS_Store" -type f -delete

# 2. Remove all macOS resource forks
find . -name "._*" -type f -delete

# 3. Remove Windows thumbnail cache
find . -name "Thumbs.db" -type f -delete

# 4. Remove backup files
find . -name "*~" -type f -delete

# 5. Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# 6. Verify no credentials are present
grep -r "AISA_API_KEY.*=.*sk-" . 2>/dev/null
grep -r "password.*=.*[^{]" . 2>/dev/null
```

### Automated Cleanup Script

Save as `cleanup.sh`:

```bash
#!/bin/bash
# OpenClaw Twitter - Package Cleanup Script

echo "🧹 Cleaning package..."

# System files
echo "Removing macOS system files..."
find . -name ".DS_Store" -type f -delete
find . -name "._*" -type f -delete
find . -name ".Spotlight-V100" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".Trashes" -type d -exec rm -rf {} + 2>/dev/null

echo "Removing Windows system files..."
find . -name "Thumbs.db" -type f -delete
find . -name "Desktop.ini" -type f -delete

echo "Removing Linux backup files..."
find . -name "*~" -type f -delete

# Python artifacts
echo "Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete

# Temporary files
echo "Removing temporary files..."
find . -name "*.tmp" -type f -delete
find . -name "*.temp" -type f -delete
find . -name "*.log" -type f -delete

# Verify
echo "✅ Cleanup complete!"
echo ""
echo "📊 Remaining files:"
find . -type f | wc -l
echo ""
echo "⚠️  Checking for potential secrets..."
if grep -r "sk-[a-zA-Z0-9]" . 2>/dev/null | grep -v ".git" | grep -v "cleanup.sh"; then
    echo "❌ WARNING: Potential API keys found! Review above."
else
    echo "✅ No obvious API keys found"
fi
```

Make it executable:
```bash
chmod +x cleanup.sh
```

## Git Configuration

### Essential .gitignore

Your `.gitignore` file should include:

```gitignore
# System files
.DS_Store
._*
Thumbs.db
Desktop.ini

# Secrets (CRITICAL)
.env
*.key
*.pem
credentials.json
secrets.json

# Python
__pycache__/
*.pyc
venv/

# IDEs
.vscode/
.idea/

# Temporary
*.log
*.tmp
```

### Global Git Ignore (Recommended)

Set up once per machine:

```bash
# Create global gitignore
cat > ~/.gitignore_global << EOF
# macOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
Desktop.ini

# IDEs
.vscode/
.idea/
*.swp
EOF

# Configure git to use it
git config --global core.excludesfile ~/.gitignore_global
```

## Pre-Distribution Checklist

Before releasing your package:

- [ ] Run cleanup script
- [ ] Verify .gitignore is present and complete
- [ ] Check for .DS_Store files: `find . -name ".DS_Store"`
- [ ] Check for credentials: `grep -r "sk-" . | grep -v ".git"`
- [ ] Check for hardcoded passwords: `grep -ri "password.*=.*[^{]" .`
- [ ] Review all files: `find . -type f | grep -v ".git"`
- [ ] Test on clean clone: `git clone <repo> test && cd test`
- [ ] Verify package size: `du -sh .`
- [ ] Check file count: `find . -type f | wc -l`

## Archive Creation (Clean)

### Create Clean ZIP

```bash
# Option 1: Using git (cleanest)
git archive --format=zip --output=openclaw-twitter-v1.1.0.zip HEAD

# Option 2: Explicit file inclusion
zip -r openclaw-twitter-v1.1.0.zip \
  README.md \
  SKILL.md \
  SECURITY.md \
  scripts/twitter_client.py \
  .gitignore \
  -x "*.DS_Store" "._*" "__pycache__/*" "*.pyc"
```

### Create Clean Tarball

```bash
# Using git
git archive --format=tar.gz --output=openclaw-twitter-v1.1.0.tar.gz HEAD

# Manual with exclusions
tar czf openclaw-twitter-v1.1.0.tar.gz \
  --exclude=".DS_Store" \
  --exclude="._*" \
  --exclude="__pycache__" \
  --exclude="*.pyc" \
  --exclude=".env" \
  .
```

## Verification

### After Creating Archive

```bash
# Extract to temp location
mkdir temp-verify
unzip openclaw-twitter-v1.1.0.zip -d temp-verify

# Check for system files
find temp-verify -name ".DS_Store"  # Should return nothing
find temp-verify -name "._*"        # Should return nothing

# Check for credentials
grep -r "sk-[a-zA-Z0-9]" temp-verify  # Should return nothing

# Review all files
find temp-verify -type f

# Clean up
rm -rf temp-verify
```

## Common Mistakes

### ❌ Don't Do This

```bash
# Including everything
zip -r package.zip .  # ❌ Includes system files!

# Committing environment files
git add .env  # ❌ Never!

# Leaving debug files
git add debug.log  # ❌ Clean first
```

### ✅ Do This Instead

```bash
# Use git archive
git archive HEAD -o package.zip  # ✅ Clean

# Use .gitignore
echo ".env" >> .gitignore  # ✅ Prevent accidents

# Clean before commit
./cleanup.sh && git add .  # ✅ Clean first
```

## Automation

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Prevent committing system files

if git diff --cached --name-only | grep -q "\.DS_Store$"; then
    echo "❌ Error: Attempting to commit .DS_Store file"
    echo "Run: find . -name '.DS_Store' -delete"
    exit 1
fi

if git diff --cached --name-only | grep -q "\.env$"; then
    echo "❌ Error: Attempting to commit .env file"
    exit 1
fi

echo "✅ Pre-commit checks passed"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Package Hygiene

on: [push, pull_request]

jobs:
  check-hygiene:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Check for system files
        run: |
          if find . -name ".DS_Store" | grep .; then
            echo "❌ .DS_Store files found"
            exit 1
          fi
          
      - name: Check for credentials
        run: |
          if grep -r "sk-[a-zA-Z0-9]" . | grep -v ".github"; then
            echo "❌ Potential credentials found"
            exit 1
          fi
          
      - name: Verify .gitignore exists
        run: |
          if [ ! -f .gitignore ]; then
            echo "❌ .gitignore missing"
            exit 1
          fi
```

## File Size Guidelines

### Reasonable Package Sizes

- **Minimal:** < 100 KB (just code + docs)
- **Standard:** 100-500 KB (code + docs + examples)
- **Large:** 500 KB - 2 MB (includes assets)
- **Too Large:** > 2 MB (check for bloat)

### Check Your Size

```bash
# Total size
du -sh .

# Size by type
find . -name "*.py" -exec du -ch {} + | tail -1
find . -name "*.md" -exec du -ch {} + | tail -1

# Largest files
find . -type f -exec du -h {} + | sort -rh | head -20
```

## Quick Reference Commands

```bash
# Clean macOS files
find . -name ".DS_Store" -delete

# Clean Windows files
find . -name "Thumbs.db" -delete

# Clean Python cache
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Check for secrets
grep -r "sk-" . | grep -v ".git"

# Create clean archive
git archive HEAD -o package.zip

# Verify archive
unzip -l package.zip | grep -i "ds_store"  # Should be empty
```

## Summary

**Golden Rules:**
1. ✅ Always use `.gitignore`
2. ✅ Run cleanup before distribution
3. ✅ Use `git archive` for releases
4. ✅ Never commit credentials
5. ✅ Verify archives before publishing

**Result:** Professional, clean packages that respect users and platforms.

---

For questions about package hygiene, see the community guidelines or open an issue.
