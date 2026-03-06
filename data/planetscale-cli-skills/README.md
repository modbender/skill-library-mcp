# 🌐 PlanetScale CLI Skills

Comprehensive `pscale` command reference and automation workflows for managing PlanetScale databases via terminal.

[![ClawHub](https://img.shields.io/badge/ClawHub-planetscale--cli--skills-blue)](https://clawhub.com/skills/planetscale-cli-skills)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 What This Skill Provides

- **8 sub-skills** covering all major `pscale` commands
- **3 automation scripts** for common workflows (create branch, deploy schema, sync)
- **Decision trees** for common questions (branch vs deploy request, tokens vs passwords)
- **Troubleshooting sections** for self-service problem solving
- **Complete command reference** in each sub-skill's `references/` directory
- **Token-efficient workflows** (~90-95% reduction for repetitive operations)

## 📦 Installation

### Via ClawHub

```bash
clawhub install planetscale-cli-skills
```

### Via Git

```bash
git clone https://github.com/vince-winkintel/planetscale-cli-skills.git
```

## 🚀 Quick Start

### Prerequisites

Install the PlanetScale CLI:

```bash
# macOS
brew install planetscale/tap/pscale

# Linux
wget https://github.com/planetscale/cli/releases/latest/download/pscale_X.X.X_linux_amd64.tar.gz
tar -xzf pscale_*.tar.gz
sudo mv pscale /usr/local/bin/

# Windows
scoop bucket add pscale https://github.com/planetscale/scoop-bucket.git
scoop install pscale
```

### Authenticate

```bash
# Interactive login
pscale auth login

# Or use service tokens for CI/CD
export PLANETSCALE_SERVICE_TOKEN_ID=<token-id>
export PLANETSCALE_SERVICE_TOKEN=<token>
```

### Create Your First Branch

```bash
# Using automation script
./scripts/create-branch-for-mr.sh \
  --database my-database \
  --branch feature-branch

# Or manually
pscale branch create my-database feature-branch --from main
```

## 🧩 Sub-Skills

| Skill | Use When | Common Commands |
|-------|----------|----------------|
| **pscale-auth** | Login, logout, authentication | `pscale auth login/logout` |
| **pscale-branch** | Create, diff, promote branches | `pscale branch create/list/diff` |
| **pscale-deploy-request** | Deploy schema changes safely | `pscale deploy-request create/deploy` |
| **pscale-database** | Manage databases, open shells | `pscale database list`, `pscale shell` |
| **pscale-backup** | Create and restore backups | `pscale backup create/list` |
| **pscale-password** | Connection passwords | `pscale password create/list` |
| **pscale-org** | Switch organizations | `pscale org list/switch` |
| **pscale-service-token** | CI/CD authentication | `pscale service-token create` |

## 🛠️ Automation Scripts

All scripts in `scripts/` directory execute without loading into context (~90% token savings).

### create-branch-for-mr.sh

Create PlanetScale branch matching your MR or PR:

```bash
./scripts/create-branch-for-mr.sh \
  --database my-database \
  --branch feature-schema-migration
```

### deploy-schema-change.sh

Complete schema deployment workflow:

```bash
./scripts/deploy-schema-change.sh \
  --database my-database \
  --branch feature-schema-v2 \
  --deploy
```

### sync-branch-with-main.sh

Refresh development branch with main:

```bash
./scripts/sync-branch-with-main.sh \
  --database my-db \
  --branch feature-branch
```

## 🌊 Common Workflows

### Schema Migration (Safe Production Deployment)

```bash
# 1. Create branch
pscale branch create my-db feature-schema --from main

# 2. Make schema changes
pscale shell my-db feature-schema
-- ALTER TABLE users ADD COLUMN last_login DATETIME;

# 3. View diff
pscale branch diff my-db feature-schema

# 4. Create deploy request
pscale deploy-request create my-db feature-schema

# 5. Deploy
pscale deploy-request deploy my-db 1
```

### CI/CD Integration (GitHub Actions)

```yaml
deploy-schema:
  steps:
    - name: Create branch
      run: |
        ./scripts/create-branch-for-mr.sh \
          --database ${{ secrets.DATABASE }} \
          --branch ${{ github.ref_name }}
    
    - name: Apply schema
      run: |
        pscale shell ${{ secrets.DATABASE }} ${{ github.ref_name }} < migrations.sql
    
    - name: Deploy
      run: |
        ./scripts/deploy-schema-change.sh \
          --database ${{ secrets.DATABASE }} \
          --branch ${{ github.ref_name }} \
          --deploy
```

### Drizzle ORM Integration

```bash
# 1. Edit your schema file
vim schema.sql

# 2. Create PlanetScale branch and apply changes
./scripts/create-branch-for-mr.sh --database my-database --branch $(git branch --show-current)
pscale shell my-database $(git branch --show-current) < schema.sql

# 3. Deploy
./scripts/deploy-schema-change.sh --database my-database --branch $(git branch --show-current) --deploy

# 4. Pull schema back to Drizzle
pnpm drizzle-kit introspect
```

## 🎓 Decision Trees

### Branch vs Deploy Request?

```
What's your goal?
├─ Experimenting → Create branch
├─ Testing changes → Create branch
├─ Ready for production → Create deploy request
└─ Review before prod → Deploy request (safe, reviewable)
```

### Service Token vs Password?

```
Use case?
├─ CI/CD pipeline → Service token (rotatable, scoped)
├─ Local development → Password (temporary)
├─ Production app → Service token
└─ One-off admin → Password
```

### Direct Promotion vs Deploy Request?

```
⚠️ Always use deploy requests for production
```

## 📊 Token Efficiency

| Operation | Manual (7 steps) | Script (1 command) | Savings |
|-----------|-----------------|-------------------|---------|
| Schema migration | ~3000 tokens | ~150 tokens | **95%** |
| Branch creation | ~500 tokens | ~50 tokens | **90%** |
| Deploy request | ~800 tokens | ~80 tokens | **90%** |

## 🔗 Related Skills

- **drizzle-kit** - ORM schema management
- **gitlab-cli-skills** - GitLab MR integration
- **github** - GitHub PR and CI/CD

## 📚 Resources

- [PlanetScale CLI Docs](https://planetscale.com/docs/reference/planetscale-cli)
- [PlanetScale GitHub](https://github.com/planetscale/cli)
- [ClawHub Page](https://clawhub.com/skills/planetscale-cli-skills)

## 🤝 Contributing

Contributions welcome! Please:
1. Follow existing skill structure patterns
2. Include decision trees and troubleshooting
3. Add scripts to `scripts/` directory
4. Update README.md and relevant SKILL.md files

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built for [OpenClaw](https://openclaw.ai) AI agents
- Optimized using [skill-creator](https://clawhub.com/skills/skill-creator) patterns
- Inspired by [gitlab-cli-skills](https://github.com/vince-winkintel/gitlab-cli-skills)
