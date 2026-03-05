# Privacy Checklist

Before using this skill, verify:

- [ ] No apiKey values in files
- [ ] No token values in files
- [ ] No secret/password in files
- [ ] Redact tokens in output (show first 4 chars only)

**Scan Command**:
```powershell
Get-ChildItem . -Recurse -File | Select-String -Pattern 'apiKey|token|secret|password' -CaseSensitive:$false
```
