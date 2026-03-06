# 🧪 Testing Checklist for ClawHub Release

## Pre-Release Testing

### 1. Fresh Install Test (Critical!)

**Goal:** Verify a new user can install without errors.

**Steps:**
```bash
# Simulate fresh user by removing all config
rm -f .env config.json bookmarks.json
rm -rf ../../life/resources/bookmarks/*

# Run setup
npm run setup

# Follow prompts with test credentials
# Enter test projects
# Complete setup

# Verify files created
ls -la .env config.json

# Verify permissions
ls -l .env  # Should show -rw------- (600)
```

**Expected:**
- ✅ Setup completes without errors
- ✅ `.env` created with 600 permissions
- ✅ `config.json` created with user's projects
- ✅ Helpful, clear prompts throughout

---

### 2. Dependency Check Test

**Goal:** Setup wizard correctly identifies missing dependencies.

**Steps:**
```bash
# Test without bird installed (if possible)
npm run setup
# Should warn about missing bird and offer install command

# Test without pm2
npm run setup
# Should note pm2 is optional for daemon mode
```

**Expected:**
- ✅ Warns about missing required deps (bird)
- ✅ Notes optional deps (pm2) are optional
- ✅ Provides install commands
- ✅ Allows continuing if user accepts risk

---

### 3. Credential Validation Test

**Goal:** Setup wizard catches invalid credentials.

**Steps:**
```bash
npm run setup

# When prompted for auth_token, enter: "test"
# When prompted for ct0, enter: "test"
```

**Expected:**
- ✅ Rejects credentials that are too short
- ✅ Offers to retry
- ✅ Provides helpful error messages

---

### 4. Dry Run Test

**Goal:** Test mode works without making changes.

**Steps:**
```bash
npm test
```

**Expected:**
- ✅ Shows what would be processed
- ✅ Doesn't create bookmarks.json
- ✅ Doesn't modify state
- ✅ No errors

---

### 5. Single Run Test

**Goal:** Process bookmarks once successfully.

**Steps:**
```bash
npm start
```

**Expected:**
- ✅ Fetches bookmarks successfully
- ✅ Creates `bookmarks.json` state file
- ✅ Analyzes at least one bookmark (if you have any)
- ✅ Saves results to `../../life/resources/bookmarks/`
- ✅ Valid JSON output files

**Verify output:**
```bash
ls -la ../../life/resources/bookmarks/
cat ../../life/resources/bookmarks/bookmark-*.json | jq .
```

---

### 6. Daemon Mode Test

**Goal:** PM2 daemon starts and runs.

**Steps:**
```bash
# Start daemon
npm run daemon

# Check status
pm2 status bookmark-intelligence

# View logs
pm2 logs bookmark-intelligence --lines 50

# Stop
pm2 stop bookmark-intelligence

# Restart
pm2 restart bookmark-intelligence

# Delete
pm2 delete bookmark-intelligence
```

**Expected:**
- ✅ Daemon starts without errors
- ✅ Shows as "online" in pm2 status
- ✅ Logs show periodic checks
- ✅ All pm2 commands work

---

### 7. Uninstall Test

**Goal:** Clean uninstall works correctly.

**Steps:**
```bash
# With daemon running
npm run daemon

# Run uninstall
npm run uninstall

# Choose to keep bookmarks
# Choose Y to confirm
```

**Expected:**
- ✅ Stops PM2 daemon
- ✅ Removes `.env`
- ✅ Removes `config.json`
- ✅ Removes `bookmarks.json`
- ✅ Asks about keeping analyzed bookmarks
- ✅ Respects user choice
- ✅ Shows summary of what was removed

**Verify:**
```bash
ls -la .env config.json bookmarks.json  # Should not exist
pm2 status  # bookmark-intelligence should not be listed
```

---

### 8. Re-install Test

**Goal:** Can install again after uninstalling.

**Steps:**
```bash
# After uninstall test
npm run setup
# Complete setup again
npm start
```

**Expected:**
- ✅ Setup works normally
- ✅ Doesn't have leftover state from previous install
- ✅ Works as if fresh install

---

### 9. Documentation Test

**Goal:** All documentation is accurate and helpful.

**Steps:**
1. Read through SKILL.md as a new user
2. Follow Quick Start section exactly
3. Verify all command examples work
4. Check all file paths exist
5. Verify troubleshooting solutions work

**Expected:**
- ✅ No broken links
- ✅ All commands work as documented
- ✅ File paths are correct
- ✅ Examples match actual output
- ✅ Beginner-friendly language

---

### 10. Security Test

**Goal:** Credentials are protected.

**Steps:**
```bash
# After setup
ls -l .env  # Check permissions
cat .gitignore  # Verify .env is excluded
git status  # Verify .env not staged
```

**Expected:**
- ✅ `.env` has 600 permissions (owner only)
- ✅ `.env` in `.gitignore`
- ✅ Git doesn't track `.env`
- ✅ `config.json` NOT in .gitignore (it's safe to share)

---

### 11. Examples Accuracy Test

**Goal:** Example files reflect actual output.

**Steps:**
```bash
# Run the skill
npm start

# Compare actual output to examples
cat ../../life/resources/bookmarks/bookmark-*.json
cat examples/sample-analysis.json

# Compare structure
```

**Expected:**
- ✅ Example JSON structure matches actual output
- ✅ All fields in example exist in real output
- ✅ Example is realistic and helpful

---

### 12. Error Handling Test

**Goal:** Graceful failure on common errors.

**Test Cases:**

**A. Invalid credentials:**
```bash
# Edit .env with garbage
npm start
```
Expected: ✅ Clear error message, suggests fixing .env

**B. No internet:**
```bash
# Disconnect network
npm start
```
Expected: ✅ Doesn't crash, reports network error

**C. No bookmarks:**
```bash
# With account that has 0 bookmarks
npm start
```
Expected: ✅ Reports "No bookmarks found", exits gracefully

**D. Malformed config.json:**
```bash
echo "{invalid json" > config.json
npm start
```
Expected: ✅ Reports config error, doesn't crash mysteriously

---

### 13. Cross-Platform Test (If Possible)

**Platforms to test:**
- [ ] Linux
- [ ] macOS
- [ ] Windows (WSL)

**Steps:**
```bash
npm run setup
npm start
```

**Expected:**
- ✅ Works on all platforms
- ✅ File paths resolve correctly
- ✅ Permissions work correctly

---

### 14. Beginner User Simulation

**Goal:** Someone with zero coding experience can use it.

**Persona:** "I installed OpenClaw, saw this skill, want to try it"

**Steps:**
1. Follow SKILL.md Quick Start only
2. Don't read code
3. Only use documented commands

**Expected:**
- ✅ Can complete setup without confusion
- ✅ Understands what's happening at each step
- ✅ Gets working skill at the end
- ✅ Knows how to use it daily

---

## Pre-Publish Checklist

Before submitting to ClawHub:

- [ ] All tests above pass
- [ ] No Brian-specific data in repo
- [ ] `.env` deleted (not in repo)
- [ ] `config.json` deleted or only contains examples
- [ ] `bookmarks.json` deleted
- [ ] `life/resources/bookmarks/` cleaned
- [ ] `.gitignore` updated
- [ ] `package.json` scripts all work
- [ ] Documentation is complete and accurate
- [ ] Examples are realistic
- [ ] README.md is compelling
- [ ] SKILL.md is beginner-friendly
- [ ] No console.log debugging code
- [ ] Error messages are helpful
- [ ] Version number is set correctly

---

## Post-Install User Testing

After publishing to ClawHub, have 2-3 real users test:

**Feedback to collect:**
- How long did setup take?
- Did they get stuck anywhere?
- Were instructions clear?
- Did it work on first try?
- What would make it easier?

---

## Known Issues to Document

List any limitations or known issues here:
- [ ] Cookie expiration (users need to refresh periodically)
- [ ] Rate limiting (too many requests might get blocked)
- [ ] LLM analysis quality depends on OpenClaw model
- [ ] Standalone mode (without OpenClaw) has limited analysis

These should be in SKILL.md troubleshooting!

---

## Success Criteria

The skill is ready for ClawHub when:
- ✅ Fresh install works without ANY manual file editing
- ✅ A non-technical user can set it up in under 10 minutes
- ✅ All documented commands work
- ✅ Error messages are helpful, not cryptic
- ✅ Examples match reality
- ✅ Security is solid (credentials protected)
- ✅ Uninstall is clean
