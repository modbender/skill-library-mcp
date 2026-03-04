# PR Automation Guide

Complete automation for handling Pull Requests on a2a-shib-payments.

---

## ✅ What's Automated

### 1. 🎉 First-Time Contributor Welcome
**Trigger:** When someone opens their first PR

**What happens:**
- Automatic welcome message posted to PR
- Links to CONTRIBUTING.md and CODE_OF_CONDUCT.md
- Sets expectations for review timeline
- Encourages community participation

**Example:**
```
👋 Welcome and thank you for your first contribution to the A2A SHIB Payment System!

We're excited to have you in the community! 🎉

What happens next:
1. A maintainer will review your PR soon (usually within 24-48 hours)
2. We may request changes or ask questions
3. Once approved, your contribution will be merged!
```

---

### 2. 🏷️ Auto-Labeling
**Trigger:** On PR open, edit, or sync

**Labels applied based on files changed:**

| Label | Files |
|-------|-------|
| `documentation` | `*.md`, `docs/**/*` |
| `bug` | `test-*.js` (without .md files) |
| `enhancement` | Core files (escrow.js, reputation.js, etc.) |
| `dependencies` | package.json, package-lock.json |
| `security` | auth.js, rate-limiter.js, audit-logger.js |
| `tests` | test-*.js, __tests__/** |
| `github-actions` | .github/workflows/** |
| `good first issue` | Branch names: typo-*, docs-*, fix-typo-* |

**Config:** `.github/labeler.yml`

---

### 3. 👀 Auto-Request Reviews
**Trigger:** When PR is opened or marked ready for review

**What happens:**
- Automatically requests review from @marcus20232023
- Skips if PR is from owner (you)
- Uses CODEOWNERS file for specific files

**CODEOWNERS protections:**
- Security files (auth.js, rate-limiter.js, audit-logger.js)
- Core logic (index.js, escrow.js, payment-negotiation.js, reputation.js)
- GitHub workflows

---

### 4. 🔍 PR Analysis
**Trigger:** On PR open

**Analyzes:**
- Code changes without tests (warns)
- Security-related changes (flags for extra review)
- Documentation updates

**Adds checklist comment:**
```
## 🤖 PR Analysis

⚠️ Code changes detected without tests. Consider adding tests to test-*.js files.

**Checklist:**
- [ ] Tests included
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Follows code style

*Thank you for your contribution!*
```

---

### 5. 📢 Maintainer Notifications

**Two notification systems:**

#### A. GitHub Actions (Immediate)
- Runs on PR open
- Logs notification to console
- Available in Actions tab

#### B. Cron Monitor (Every 10 minutes)
- Checks for new PRs
- Sends detailed Telegram message
- Includes:
  - PR number and title
  - Author username
  - Files changed
  - Additions/deletions
  - Direct link
  - Suggested actions

**Example Telegram notification:**
```
🔔 GitHub Activity Alert

🎉 +1 new PR(s)! Total: 1
  PR #5: "Add USDC token support" by @contributor
  📊 Changes: 3 files, +127/-45
  🔗 https://github.com/marcus20232023/a2a-shib-payments/pull/5
  
  ✅ Suggested Actions:
  1. Review the code changes
  2. Check if tests are included
  3. Test locally if needed
  4. Approve or request changes
```

---

## 📁 Files

### GitHub Actions Workflows
- `.github/workflows/pr-automation.yml` - Main PR automation (welcome, label, analyze)
- `.github/workflows/pr-review-request.yml` - Auto-request reviews
- `.github/workflows/test.yml` - Run tests on PR
- `.github/workflows/release.yml` - Auto-release on tag

### Configuration
- `.github/labeler.yml` - Auto-labeling rules
- `.github/CODEOWNERS` - Review requirements
- `.github/ISSUE_TEMPLATE/*` - Issue templates
- `.github/PULL_REQUEST_TEMPLATE.md` - PR template

### Monitoring
- `monitor-github.sh` - Bash script for monitoring
- `.github-monitor-state.json` - State tracking
- Cron job: Every 10 minutes

---

## 🎯 Handling PRs - Quick Guide

### When You Get a Notification

1. **Check the Telegram alert** - Read summary
2. **Click the PR link** - Review changes on GitHub
3. **Look for auto-labels** - Understand scope
4. **Check the analysis comment** - See if tests are missing
5. **Review the code** - Read through changes
6. **Test locally** (if needed):
   ```bash
   gh pr checkout <number>
   npm test
   ```
7. **Provide feedback** or approve:
   ```bash
   # Request changes
   gh pr review <number> --request-changes -b "Please add tests"
   
   # Approve
   gh pr review <number> --approve -b "LGTM! Thanks!"
   
   # Merge
   gh pr merge <number> --squash
   ```

### Common PR Types

**Documentation fixes** (typos, clarifications):
- Usually safe to merge quickly
- Auto-labeled as `documentation` and `good first issue`
- Check for accuracy, merge if good

**Bug fixes**:
- Check if tests are included
- Test locally
- Verify it fixes the issue
- Merge after approval

**Feature enhancements**:
- Thorough review needed
- Tests required
- May need discussion
- Consider breaking changes

**Security changes**:
- Extra careful review
- Test thoroughly
- Consider security implications
- Might want second opinion

---

## 🔧 Customization

### Add More Labels

Edit `.github/labeler.yml`:
```yaml
performance:
  - changed-files:
    - any-glob-to-any-file:
      - 'escrow.js'
      - 'payment-negotiation.js'
```

### Change Welcome Message

Edit `.github/workflows/pr-automation.yml`:
```yaml
pr-message: |
  Your custom welcome message here
```

### Add More Reviewers

Edit `.github/CODEOWNERS`:
```
# Add co-maintainers
* @marcus20232023 @contributor2
```

---

## 📊 Monitoring Status

**Cron job:** Active  
**Check frequency:** Every 10 minutes  
**Next check:** See `cron list`  

**Manual check:**
```bash
cd /home/marc/projects/a2a-shib-payments
./monitor-github.sh
```

**View cron jobs:**
```bash
openclaw cron list
```

**Disable monitoring:**
```bash
openclaw cron remove <job-id>
```

---

## 🎉 Benefits

✅ **Never miss a PR** - Instant notifications  
✅ **Welcoming community** - Auto-greet new contributors  
✅ **Organized** - Auto-labeled PRs  
✅ **Quality** - Analysis warns about missing tests  
✅ **Efficient** - Suggested actions save time  
✅ **Professional** - Shows well-maintained project  

---

## 🔗 Related

- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [PROMOTION-TRACKER.md](PROMOTION-TRACKER.md) - Launch tracking
- [LAUNCH-CHECKLIST.md](LAUNCH-CHECKLIST.md) - Launch guide

---

**All automation is active and running!** 🚀
