# Privacy Checklist

Before using this skill, verify:

- [ ] No apiKey values in files
- [ ] No token values in files  
- [ ] No secret/password in files
- [ ] No personal emails
- [ ] No absolute user paths
- [ ] No internal service URLs

**Scan Command**:
```powershell
Get-ChildItem . -Recurse -File | Select-String -Pattern 'apiKey|token|secret|password' -CaseSensitive:$false
```
