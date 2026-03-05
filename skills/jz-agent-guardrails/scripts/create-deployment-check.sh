#!/bin/bash
# Create deployment verification system for a project
# Usage: bash create-deployment-check.sh /path/to/project

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/project"
    exit 1
fi

PROJECT_DIR="$1"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: $PROJECT_DIR does not exist"
    exit 1
fi

echo "🔧 Creating deployment verification system in $PROJECT_DIR"
echo ""

# 1. Create .deployment-check.sh template
cat > "$PROJECT_DIR/.deployment-check.sh" << 'EOF'
#!/bin/bash
# Project Deployment Verification Script
# Customize this to verify your specific integration points

set -e

echo "🔍 Deployment Verification"
echo "=========================="
echo ""

FAILED=0

# Test 1: Main output generation
echo "Test 1: Main output generated..."
# TODO: Add your test here
# Example: bash scripts/generate_report.sh > /dev/null 2>&1
# if [ -f /tmp/report.txt ]; then
#     echo "  ✅ Report generated"
# else
#     echo "  ❌ No report"
#     FAILED=1
# fi
echo "  ⚠️ Not implemented yet"

# Test 2: Output format
echo "Test 2: Output format..."
# TODO: Check output has required elements
# Example: grep -q "Required Field" /tmp/report.txt
echo "  ⚠️ Not implemented yet"

# Test 3: Integration points
echo "Test 3: Integration points..."
# TODO: Verify all entry points work
echo "  ⚠️ Not implemented yet"

echo ""
echo "=========================="
if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed (or not yet implemented)"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
EOF

chmod +x "$PROJECT_DIR/.deployment-check.sh"
echo "✅ Created .deployment-check.sh"

# 2. Create DEPLOYMENT-CHECKLIST.md template
cat > "$PROJECT_DIR/DEPLOYMENT-CHECKLIST.md" << 'EOF'
# Deployment Checklist

**Problem this solves:** Built new features but forgot to wire them into production.

---

## Pre-Deployment Checklist

Before marking any feature "done", verify:

### 1. Code Changes
- [ ] New code written/modified
- [ ] Tests pass (manual or automated)
- [ ] No hardcoded secrets (run `bash check-secrets.sh`)

### 2. Integration Points
- [ ] **Identify all entry points** (cron jobs, APIs, user commands)
- [ ] **Update all entry points** to use new code
- [ ] **Verify old code is replaced** (not running in parallel)

### 3. Configuration
- [ ] Config files updated (if needed)
- [ ] Environment variables set (if needed)
- [ ] Documentation updated

### 4. End-to-End Test
- [ ] **Run the actual production flow** (not just the function)
- [ ] **Verify user-facing output** (what they see, not logs)
- [ ] **Check all edge cases** (empty results, errors, etc.)

### 5. Monitoring
- [ ] Logs in place
- [ ] Error alerts configured
- [ ] Success metrics defined

---

## Post-Deployment Verification

Within 24h of deploying:

- [ ] **Monitor first real run** (cron, webhook, whatever)
- [ ] **Check user feedback** (did they receive expected output?)
- [ ] **Review logs** (any errors/warnings?)
- [ ] **Verify metrics** (is it working as expected?)

---

## Project-Specific Integration Points

<!-- Document your specific entry points here -->

Example:
### Feature: Hourly Reports
Entry points to check:
1. `scripts/send_hourly.sh` (cron job)
2. Heartbeat integration (message delivery)
3. Manual commands

Verification steps:
```bash
# Run the actual production flow
bash scripts/send_hourly.sh

# Check output file
cat /tmp/report.txt

# Verify user receives it
# (check messaging platform)
```

---

## Lessons Learned (Incident Log)

### [Date]: [Brief Description]

**Symptom:** 

**Root cause:** 

**Fix:** 

**Prevention (added to checklist):** 

---

**Remember:** A feature isn't "done" until users receive the intended benefit.
EOF

echo "✅ Created DEPLOYMENT-CHECKLIST.md"

# 3. Create git hook
mkdir -p "$PROJECT_DIR/.git-hooks"

cat > "$PROJECT_DIR/.git-hooks/pre-commit-deployment" << 'EOF'
#!/bin/bash
# Pre-commit hook for deployment verification
# Runs .deployment-check.sh if project files changed

# Customize this pattern to match your project files
FILE_PATTERN="." # Change to your pattern, e.g., "src/", "lib/", etc.

if git diff --cached --name-only | grep -q "$FILE_PATTERN"; then
    echo "🔍 Project files changed, running deployment verification..."
    
    if bash .deployment-check.sh; then
        echo "✅ Deployment checks passed"
        exit 0
    else
        echo ""
        echo "❌ Deployment verification failed!"
        echo "Fix the issues above or use --no-verify to skip (not recommended)"
        exit 1
    fi
fi

# No relevant changes, allow commit
exit 0
EOF

chmod +x "$PROJECT_DIR/.git-hooks/pre-commit-deployment"
echo "✅ Created git hook template"

# 4. Installation instructions
cat > "$PROJECT_DIR/.deployment-setup-instructions.txt" << 'EOF'
Deployment Verification Setup Complete!

Files created:
  .deployment-check.sh            - Automated verification script
  DEPLOYMENT-CHECKLIST.md         - Full deployment workflow
  .git-hooks/pre-commit-deployment - Git hook template

Next steps:

1. Customize .deployment-check.sh:
   - Add tests for your specific integration points
   - Verify output format, content, etc.
   
2. Install git hook:
   
   If this is a standalone repo:
   cp .git-hooks/pre-commit-deployment .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   
   If this is part of a larger repo:
   cd /path/to/parent-repo
   cp this/.git-hooks/pre-commit-deployment .git/hooks/pre-commit-yourproject
   # Then modify .git/hooks/pre-commit to call it

3. Document integration points in DEPLOYMENT-CHECKLIST.md

4. Run verification:
   bash .deployment-check.sh
   
5. Test git hook:
   # Make a change and commit - should trigger verification

Remember: A feature isn't done until end-to-end production flow is verified.
EOF

echo ""
echo "✅ Deployment verification system created!"
echo ""
cat "$PROJECT_DIR/.deployment-setup-instructions.txt"
