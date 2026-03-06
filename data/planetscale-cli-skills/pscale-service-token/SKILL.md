---
name: pscale-service-token
description: Create, list, and manage service tokens for CI/CD authentication. Use when setting up automated deployments, configuring CI/CD pipelines (GitHub Actions, GitLab CI, CircleCI, etc.), creating non-interactive authentication, or rotating CI/CD credentials. Preferred over passwords for production automation. Triggers on service token, CI/CD auth, automation token, pipeline authentication.
---

# pscale service-token

Create, list, and manage service tokens for CI/CD and automation.

## Common Commands

```bash
# Create service token
pscale service-token create --org <org>

# List service tokens
pscale service-token list --org <org>

# Delete service token
pscale service-token delete <token-id> --org <org>
```

## Workflows

### CI/CD Setup (GitHub Actions)

```bash
# 1. Create service token
pscale service-token create --org my-org

# Returns:
#   TOKEN_ID: xxxxx
#   TOKEN: yyyyy

# 2. Add to GitHub Secrets
#   PLANETSCALE_SERVICE_TOKEN_ID = xxxxx
#   PLANETSCALE_SERVICE_TOKEN = yyyyy

# 3. Use in workflow
# .github/workflows/deploy.yml
# env:
#   PLANETSCALE_SERVICE_TOKEN_ID: ${{ secrets.PLANETSCALE_SERVICE_TOKEN_ID }}
#   PLANETSCALE_SERVICE_TOKEN: ${{ secrets.PLANETSCALE_SERVICE_TOKEN }}
# run: |
#   pscale deploy-request deploy my-db my-branch
```

### CI/CD Pipeline Integration

```bash
# 1. Create service token
pscale service-token create --org my-org

# 2. Add to your CI/CD secrets/variables
#   PLANETSCALE_SERVICE_TOKEN_ID
#   PLANETSCALE_SERVICE_TOKEN

# 3. Use in your pipeline config (.github/workflows, .gitlab-ci.yml, etc.)
# deploy:
#   script:
#     - pscale deploy-request create $DATABASE $BRANCH_NAME
```

### Token Rotation

```bash
# 1. List existing tokens
pscale service-token list --org my-org

# 2. Create new token
pscale service-token create --org my-org

# 3. Update CI/CD secrets

# 4. Delete old token
pscale service-token delete <old-token-id> --org my-org
```

## Troubleshooting

### Token authentication fails

**Error:** `401 Unauthorized`

**Solutions:**
- Verify both TOKEN_ID and TOKEN are set correctly
- Check token hasn't been deleted: `pscale service-token list`
- Ensure token has required permissions
- Try creating new token (old may be expired)

### Token not showing in list

**Cause:** Tokens are organization-scoped

**Solution:**
```bash
# Ensure correct org
pscale org show

# List tokens for specific org
pscale service-token list --org <correct-org>
```

## Security Best Practices

1. **Rotate tokens regularly** (every 90 days recommended)
2. **Use separate tokens** for different CI/CD systems
3. **Delete unused tokens** immediately
4. **Never commit tokens** to version control
5. **Use secrets management** (GitHub Secrets, environment variables, vault systems)
6. **Limit token scope** if possible (coming in future PlanetScale updates)

## Related Skills

- **pscale-auth** - Interactive authentication (development)
- **pscale-deploy-request** - Automated deployments via tokens
- **gitlab-cli-skills** - GitLab CI integration
- **github** - GitHub Actions integration

## References

See `references/commands.md` for complete command reference.
