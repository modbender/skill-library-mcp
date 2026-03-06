# Safety Playbook

## High-Risk Operations

These operations require explicit confirmation:

### 💰 Financial (costs money)
- Domain purchase
- Domain renewal
- Certificate purchase/renewal

### 🔥 Destructive (irreversible or high-impact)
- DNS replace-all (wipes all records)
- DNS delete
- Domain cancellation
- Certificate revocation

## Confirmation Pattern

All high-risk scripts implement this pattern:

```bash
echo "⚠️  WARNING: [description of action and consequences]" >&2
echo "Details: [show payload or parameters]" >&2
read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted." >&2
  exit 1
fi
# ... proceed with operation
```

## Pre-Flight Checklist

Before executing high-risk operations:

### Domain Purchase
- [ ] Verified domain availability
- [ ] Validated purchase payload JSON
- [ ] Confirmed pricing and period
- [ ] Checked Good as Gold funding
- [ ] Reviewed contact information
- [ ] Confirmed consent agreements

### Domain Renewal
- [ ] Verified domain is eligible for renewal
- [ ] Confirmed renewal period
- [ ] Checked account balance

### DNS Replace-All
- [ ] Backed up current DNS records (`./scripts/gd-dns.sh get <domain>`)
- [ ] Reviewed replacement payload
- [ ] Tested in OTE environment first (if possible)
- [ ] Confirmed no critical services will break

### DNS Delete
- [ ] Verified record is not critical
- [ ] Confirmed no services depend on it
- [ ] Documented reason for deletion

### Certificate Revocation
- [ ] Confirmed certificate is no longer needed
- [ ] Reviewed impact on services
- [ ] Have replacement certificate ready (if needed)

## Testing Strategy

**Always test in OTE first:**

1. Set up OTE environment:
   ```bash
   export GODADDY_API_BASE_URL="https://api.ote-godaddy.com"
   export GODADDY_API_KEY="your-ote-key"
   export GODADDY_API_SECRET="your-ote-secret"
   ```

2. Run operation in OTE
3. Verify results
4. Switch to production:
   ```bash
   export GODADDY_API_BASE_URL="https://api.godaddy.com"
   export GODADDY_API_KEY="your-prod-key"
   export GODADDY_API_SECRET="your-prod-secret"
   ```

## Recovery Procedures

### Accidentally deleted DNS records
- Restore from backup (if taken)
- Contact GoDaddy support for historical data
- Reconfigure from documentation

### Purchased wrong domain
- Domain purchases are generally non-refundable
- Contact GoDaddy support immediately
- May be eligible for Good as Gold credit

### Broke DNS for live service
- Use GoDaddy web UI for emergency fix
- Update records via API once stabilized
- Document incident for post-mortem

## Best Practices

1. **Backup before changes**: Always export current state before modifications
2. **Test in OTE**: Use test environment for workflow validation
3. **One change at a time**: Don't batch unrelated operations
4. **Document changes**: Keep audit trail of what was changed and why
5. **Verify after change**: Confirm operation succeeded as expected
6. **Monitor impact**: Watch for downstream effects (email, web, etc.)
