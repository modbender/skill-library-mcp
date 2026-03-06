# Safety & Rollback Reference

**Read this before running any bulk operations.**

## Pre-Flight Checklist

### Configuration
- [ ] `EXCLUDE_REPOS` includes templates, test repos, and repos you want to protect
- [ ] `DEFAULT_BRANCH` matches your org standard (`master` or `main`)
- [ ] `REPO_PATTERN` is specific enough — test with `gh repo list <ORG> | grep <PATTERN>`
- [ ] `CREATE_PR=true` if you want review gates before changes merge

### Environment
- [ ] Git credentials configured and valid
- [ ] GitHub token has `repo` + `workflow` permissions
- [ ] Terraform installed and matches minimum version
- [ ] Working directory is clean (`git status`)

### Test First (Non-Negotiable)
- [ ] Run on ONE non-critical repo first
- [ ] Review the changes (`git diff`)
- [ ] Run `terraform validate` and `terraform plan` on the test module
- [ ] Confirm GitHub Actions pass after changes
- [ ] Only then proceed to bulk operation

## During Execution

- Watch for unexpected errors — stop immediately with `Ctrl+C` if something looks wrong
- Verify repos being processed match your expectations
- Monitor that `EXCLUDE_REPOS` are actually being skipped

## Rollback Procedures

### Revert a commit
```bash
# Revert last commit in a specific repo
cd terraform-YOUR-MODULE
git revert HEAD --no-edit
git push origin master
```

### Revert multiple repos at once
```bash
# List all affected repos, then revert each
for repo in $(gh repo list YOUR-ORG --json name -q '.[].name' | grep 'terraform-aws-'); do
  cd $repo && git revert HEAD --no-edit && git push && cd ..
done
```

### Delete an incorrect release/tag
```bash
# Delete a GitHub release
gh release delete v1.2.3 --repo YOUR-ORG/terraform-aws-MODULE

# Delete the tag
git push origin --delete v1.2.3
git tag -d v1.2.3
```

### Revert a workflow file change
```bash
git show HEAD~1:.github/workflows/terraform.yml > .github/workflows/terraform.yml
git commit -m "revert: restore previous workflow"
git push
```

## Emergency Recovery

If bulk operations went wrong across many repos:

1. **Stop the operation** immediately
2. **Assess scope** — how many repos were affected?
3. **Check `git log`** on affected repos to see exactly what changed
4. **Use `DRY_RUN=true`** to preview what a revert would do
5. **Revert in reverse order** — releases first, then commits

```bash
# Preview what changed across all repos (dry run assessment)
gh repo list YOUR-ORG --json name -q '.[].name' | grep terraform-aws- | while read repo; do
  echo "=== $repo ===" && gh api repos/YOUR-ORG/$repo/commits?per_page=1 -q '.[0].commit.message'
done
```

## Safe Configuration Patterns

```bash
# Always start with dry run
DRY_RUN=true

# Use PRs for review before merging
CREATE_PR=true

# Protect critical repos
EXCLUDE_REPOS="terraform-aws-core terraform-aws-network terraform-aws-security"

# Validate everything
RUN_TERRAFORM_VALIDATE=true
RUN_TERRAFORM_FMT=true
RUN_TFLINT=true
RUN_TFSEC=true
```
