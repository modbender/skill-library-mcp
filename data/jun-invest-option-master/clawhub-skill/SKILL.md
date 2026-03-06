---
name: jun-invest-option-master-installer
description: Install/restore the jun-invest-option-master Agent App (repo-based) into an OpenClaw workspace.
---

# jun-invest-option-master-installer

薄安装器 skill（方案2）：能力本体在 GitHub repo（本目录的上层仓库）。

## 使用

```bash
# clone repo first

git clone <YOUR_GIT_URL> jun-invest-option-master
cd jun-invest-option-master
bash scripts/install.sh --workspace "$HOME/.openclaw/workspace"
```

## 发布

```bash
clawhub publish ./clawhub-skill --slug jun-invest-option-master-installer --name "jun-invest-option-master installer" --version 0.1.0 --changelog "initial"
```
