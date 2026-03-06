# Safety Checklist for Copilot Skills

## Pre-Flight Checks (Before Running)

### ✅ Configuration Review
- [ ] Verified provider versions are correct and tested
- [ ] Checked `EXCLUDE_REPOS` includes templates/test repos
- [ ] Confirmed `DEFAULT_BRANCH` matches org standard (master/main)
- [ ] Validated `REPO_PATTERN` matches intended repositories
- [ ] Reviewed `CREATE_PR` setting (false for direct commit, true for PR workflow)

### ✅ Environment Checks
- [ ] Git credentials configured and valid
- [ ] Sufficient GitHub API rate limit available
- [ ] Terraform installed and matches min version
- [ ] Working directory is clean (no uncommitted changes)
- [ ] Running from correct directory location

### ✅ Access Verification
- [ ] Have write access to target repositories
- [ ] GitHub token has required permissions (repo, workflow)
- [ ] Can create releases in target repos
- [ ] Can push to default branch (or create PRs)

### ✅ Test First
- [ ] Tested on ONE repository first
- [ ] Reviewed changes made by test run
- [ ] Validated test changes (terraform validate, terraform plan)
- [ ] Confirmed workflows pass after test
- [ ] Rolled back test if needed

## During Execution

### ⚠️ Monitor Progress
- [ ] Watch for unexpected errors or warnings
- [ ] Verify repositories being processed match expectations
- [ ] Check that excluded repos are actually skipped
- [ ] Monitor GitHub Actions status (if workflow changes made)
- [ ] Validate no sensitive data in commits

### ⚠️ If Something Goes Wrong
1. **Stop immediately**: Ctrl+C or stop the script
2. **Assess damage**: How many repos affected?
3. **Document issue**: What happened, which repos, what changes?
4. **Rollback if needed**: See rollback procedures below
5. **Fix and test**: Correct issue, test on one repo, resume

## Post-Execution Verification

### ✅ Validate Changes
- [ ] All target repositories updated
- [ ] No unintended repositories modified
- [ ] Excluded repositories actually excluded
- [ ] Commits have proper format and messages
- [ ] Tags/releases created correctly
- [ ] CHANGELOGs updated properly

### ✅ Test Changes
- [ ] Run `terraform validate` on sample modules
- [ ] Run `terraform plan` on sample examples
- [ ] Check GitHub Actions all passing (green checks)
- [ ] Verify no broken links or references
- [ ] Test example deployments if critical

### ✅ Documentation
- [ ] Update internal docs with what was done
- [ ] Note any issues encountered
- [ ] Record any repos that needed manual fixes
- [ ] Update version tracking spreadsheet (if used)

## Rollback Procedures

### If Changes Need to be Reverted

#### Scenario 1: Changes Pushed but Not Released
```bash
# For each affected repository
cd <repo-name>

# Option A: Revert the commit
git revert HEAD
git push origin $DEFAULT_BRANCH

# Option B: Hard reset (if no one else pulled)
git reset --hard HEAD~1
git push --force-with-lease origin $DEFAULT_BRANCH
```

#### Scenario 2: Releases Created
```bash
# Delete the tag locally
git tag -d v1.2.3

# Delete the tag remotely
git push origin :refs/tags/v1.2.3

# Delete the release on GitHub (use gh CLI or web UI)
gh release delete v1.2.3 --yes

# Then revert commits as above
```

#### Scenario 3: Partial Failure (Some Repos Updated)
```bash
# 1. List successfully updated repos
git log --all --oneline --grep="upgrade:"

# 2. For each successful repo, decide:
#    - Keep changes (if they're fine)
#    - Revert (if problematic)
#    - Manual fix (if needs adjustment)

# 3. For failed repos:
#    - Fix the issue
#    - Re-run script on just those repos
#    - Or update manually
```

## Emergency Contacts

### When to Escalate
- [ ] Breaking changes discovered after release
- [ ] Multiple workflows failing across repos
- [ ] Customers reporting issues with modules
- [ ] Security vulnerability introduced
- [ ] Mass revert needed across many repos

### Who to Contact
1. **DevOps Lead**: [Name/Contact]
2. **Platform Team**: [Channel/Email]
3. **Security Team**: [Contact if security issue]

## Best Practices (Reminder)

### Always
- ✅ Test on single repo first
- ✅ Run during low-traffic hours
- ✅ Have rollback plan ready
- ✅ Keep changes small and atomic
- ✅ Commit messages with context

### Never
- ❌ Run on Friday afternoon
- ❌ Skip testing phase
- ❌ Update all repos without review
- ❌ Ignore failing validations
- ❌ Commit secrets or credentials

## Risk Matrix

| Action | Risk Level | Mitigation |
|--------|-----------|------------|
| Provider upgrade (minor) | 🟢 Low | Test one repo, automated rollback |
| Provider upgrade (major) | 🟡 Medium | Test thoroughly, staged rollout |
| Workflow changes | 🟢 Low | Validate syntax first |
| Release creation | 🟢 Low | Can delete/recreate easily |
| Breaking changes | 🔴 High | Require manual review + approval |
| Direct to production | 🔴 High | Always use staging/test first |

## Audit Trail

Keep a log of all bulk operations:

```bash
# Create operations log
echo "$(date): Upgraded AWS provider to 5.80.0 across 170 repos" >> operations-log.txt
echo "  Operator: $(whoami)" >> operations-log.txt  
echo "  Config: aws.config" >> operations-log.txt
echo "  Status: SUCCESS" >> operations-log.txt
echo "---" >> operations-log.txt
```

## Sign-off

Before running major operations, get approval:

- [ ] Changes reviewed by: __________________
- [ ] Approved by: __________________
- [ ] Scheduled time: __________________
- [ ] Rollback plan confirmed: __________________

---

**Remember**: These skills are powerful. With great power comes great responsibility! 🕷️
