# Contributing to Copilot Skills

## For Internal Teams

These skills are designed to be extended and customized for your needs.

## Adding a New Skill

1. **Create a prompt file**: `prompts/N-skill-name.prompt`
2. **Create a script** (optional): `scripts/skill-name.sh`
3. **Update README**: Add to the skills list
4. **Test on one repo first**

### Prompt Template

```markdown
# Prompt: [Skill Name]

## Copilot Prompt:

\`\`\`
Please [describe the task]:

1. Step 1
2. Step 2
3. Step 3

Configuration from: config/[provider].config
\`\`\`

## Expected Outcome:
- Outcome 1
- Outcome 2

## Time Estimate: X minutes
```

## Customizing for Your Org

### Modifying Provider Versions

Edit the relevant config file:

```bash
# config/aws.config
PROVIDER_MIN_VERSION="5.90.0"  # Update to desired version
TERRAFORM_MIN_VERSION="1.11.0"  # Update if needed
```

### Changing Repository Patterns

```bash
# For different naming conventions
REPO_PATTERN="tf-module-*"           # Instead of terraform-aws-*
REPO_PATTERN="infra-modules-aws-*"   # Custom pattern
```

### Adding Custom Validation

Edit `scripts/validate-all.sh`:

```bash
# Add custom checks
echo "Running custom validation..."
./your-custom-validator.sh
```

### Modifying Workflows

Update `prompts/2-workflow-standardization.prompt` with your workflow requirements:

```yaml
# Add your required workflows
- .github/workflows/your-custom-workflow.yml
- .github/workflows/security-scan.yml
```

## Testing Changes

Always test on a single repository first:

```bash
# 1. Clone one test repo
cd /tmp
git clone https://github.com/clouddrove/terraform-aws-vpc.git
cd terraform-aws-vpc

# 2. Run your modified script
/path/to/terraform-ai-skills/scripts/your-script.sh

# 3. Verify changes
git diff

# 4. If good, rollout to all repos
```

## Best Practices

### 1. Always Use Version Control
- Commit skill changes to git
- Use branches for major modifications
- Tag stable versions

### 2. Document Everything
- Add comments to scripts
- Update USAGE.md with examples
- Keep QUICKREF.md current

### 3. Keep Skills Atomic
- One skill = one clear purpose
- Compose complex operations from simple skills
- Don't create monolithic prompts

### 4. Safe Defaults
- Set `CREATE_PR=false` initially
- Test with `NOTIFY_ON_COMPLETE=false`
- Use `EXCLUDE_REPOS` liberally

## Common Customizations

### 1. Add Pre-commit Hooks Support

```bash
# In upgrade script, add:
if [ -f ".pre-commit-config.yaml" ]; then
  pre-commit run --all-files
fi
```

### 2. Add Slack Notifications

```bash
# In config:
NOTIFY_ON_COMPLETE=true
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK"

# In scripts:
send_slack_notification() {
  curl -X POST $SLACK_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"$1\"}"
}
```

### 3. Add Cost Estimation

```bash
# Before changes:
infracost breakdown --path .

# After changes:
infracost diff --path .
```

### 4. Add Security Scanning

```bash
# Add to validation:
trivy config .
checkov -d .
tfsec .
```

## Skill Ideas

Here are more skills you might want to add:

1. **Security Audit**: Run security scanners on all modules
2. **Cost Optimization**: Analyze and suggest cost improvements
3. **Documentation Generator**: Auto-generate README files
4. **License Checker**: Ensure all modules have proper licenses
5. **Dependency Graph**: Generate module dependency maps
6. **Migration Helper**: Migrate from old patterns to new
7. **Breaking Change Detector**: Identify breaking changes
8. **Performance Analyzer**: Check module performance
9. **Compliance Checker**: Validate against company policies
10. **Auto-Tagging**: Ensure consistent resource tagging

## Sharing Skills

To share with other teams:

1. **Export the config template**:
   ```bash
   cp terraform-ai-skills/ /shared/location/
   ```

2. **Document org-specific settings**:
   - Create `ORG-SPECIFIC.md`
   - List any custom modifications
   - Note which scripts need tokens/credentials

3. **Remove sensitive data**:
   - Clear `SLACK_WEBHOOK_URL`
   - Remove any API tokens
   - Sanitize example outputs

## Getting Help

- Check existing skills for patterns
- Review script comments
- Test incrementally
- Ask in team chat if stuck

## Versioning Skills

We recommend semantic versioning:

```bash
# Tag releases
git tag -a v1.0.0 -m "Initial release"
git tag -a v1.1.0 -m "Added GCP support"
git tag -a v0.0.1 -m "Breaking: Changed config format"
```

## Rollback Procedure

If something goes wrong:

```bash
# 1. Identify affected repos
git log --oneline --all --decorate --graph

# 2. Revert specific commit
git revert <commit-sha>

# 3. Or reset to previous state
git reset --hard <previous-commit>

# 4. Force push (if needed and safe)
git push --force-with-lease
```

## Support

For questions or issues:
- Check the TROUBLESHOOTING section in USAGE.md
- Review closed issues in GitHub
- Contact DevOps team
- Update this guide with solutions!
