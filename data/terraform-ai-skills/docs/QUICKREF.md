# Quick Reference Card

## 🚀 Most Common Commands

### Next Time You Need Maintenance:

**Option 1 - Quick Prompt (Recommended):**
```
@copilot follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```

**Option 2 - Just Say This:**
```
Do full maintenance on all terraform modules using the skills in terraform-ai-skills/
```

**Option 3 - Manual Steps:**
```bash
# 1. Upgrade providers
./terraform-ai-skills/scripts/batch-provider-upgrade.sh

# 2. Validate everything
./terraform-ai-skills/scripts/validate-all.sh

# 3. Create releases
./terraform-ai-skills/scripts/create-releases.sh
```

---

## 📝 Prompts Cheat Sheet

| Prompt File | Use When | Time |
|------------|----------|------|
| `1-provider-upgrade.prompt` | Update provider versions only | 10 min |
| `2-workflow-standardization.prompt` | Fix GitHub Actions | 15 min |
| `3-release-creation.prompt` | Create releases & changelogs | 10 min |
| `4-full-maintenance.prompt` | **Do everything** ⭐ | 45 min |

---

## 🔧 Configuration (One-Time Setup)

Edit `config/global.config`:

```bash
# For AWS modules:
PROVIDER_NAME="aws"
PROVIDER_MIN_VERSION="5.0.0"

# For Azure modules:
PROVIDER_NAME="azurerm"
PROVIDER_MIN_VERSION="3.50.0"

# For GCP modules:
PROVIDER_NAME="google"
PROVIDER_MIN_VERSION="5.0.0"

# Your org:
ORG_NAME="your-org-name"
```

---

## 💡 Pro Tips

### Tip 1: Use Full Maintenance
Always start with prompt #4 - it does everything you need!

### Tip 2: For Other Orgs
Just update `config/global.config` - that's it!

### Tip 3: Quick Test
Test on one repo first:
```
@copilot upgrade provider in terraform-aws-vpc only using terraform-ai-skills/prompts/1-provider-upgrade.prompt
```

### Tip 4: Check Status First
Before starting:
```
@copilot audit all repos following terraform-ai-skills/ patterns - list current versions, open PRs, and workflow status
```

---

## ✅ What Gets Done Automatically

When you use `4-full-maintenance.prompt`:

- ✅ Provider upgraded to latest
- ✅ All examples updated
- ✅ GitHub Actions standardized
- ✅ All workflows passing (green checks)
- ✅ CHANGELOGs updated with emojis
- ✅ Releases created on GitHub
- ✅ Everything validated
- ✅ Summary report generated

---

## 🎯 Real World Examples

### Scenario 1: Monthly Maintenance
```
@copilot follow terraform-ai-skills/prompts/4-full-maintenance.prompt
```
**Done in 45 minutes!**

### Scenario 2: Just Update Provider
```
@copilot follow terraform-ai-skills/prompts/1-provider-upgrade.prompt
```
**Done in 10 minutes!**

### Scenario 3: Fix Failing Actions
```
@copilot follow terraform-ai-skills/prompts/2-workflow-standardization.prompt
```
**Done in 15 minutes!**

---

## 📊 Expected Results

After running full maintenance:
- **15 repos**: All updated ✅
- **35+ examples**: All validated ✅
- **Workflows**: 100% green 🟢
- **Releases**: All created with proper changelogs ✅
- **Time saved**: ~5 hours → 45 minutes! 🎉

---

## 🆘 Help

**Can't find config?**
→ Check: `terraform-ai-skills/config/global.config`

**Variables not working?**
→ Say: "Use config from terraform-ai-skills/config/global.config"

**Want to see what will change?**
→ Add: "Show me what will change first, don't apply yet"

---

## 📚 More Info

- Full documentation: `terraform-ai-skills/USAGE.md`
- All prompts: `terraform-ai-skills/prompts/`
- All scripts: `terraform-ai-skills/scripts/`
