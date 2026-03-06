# GitHub 免密码配置

**再也不用为 Git 操作和 GitHub API 调用输入密码！**

[![许可证](https://img.shields.io/badge/许可证-MIT-green.svg)](LICENSE)
[![平台](https://img.shields.io/badge/平台-macOS%20|%20Linux%20|%20Windows-blue.svg)]()

[English](README.md) | 简体中文

## 🎯 这个工具做什么

使用以下方式配置 **完全免密码的 GitHub 认证**：
1. **SSH 密钥** - 零密码 Git 操作（push/pull/clone）
2. **个人访问令牌** - 零密码仓库管理

**一次配置，终身便利！**

## ⚡ 快速开始

```bash
curl -fsSL https://raw.githubusercontent.com/happydog-intj/github-passwordless-setup/master/setup.sh | bash
```

## ✨ 配置前后对比

| 操作 | 配置前 | 配置后 |
|------|--------|--------|
| `git push` | ❌ 需要密码 | ✅ 即时完成 |
| `git clone` | ❌ 需要密码 | ✅ 即时完成 |
| `gh repo create` | ❌ 需要重新认证 | ✅ 即时完成 |
| Token 过期 | ❌ 中断工作流 | ✅ 永不过期* |

*使用"永不过期"令牌设置时

## 📋 你将获得什么

### SSH 密钥认证
- ✅ 无需密码推送代码
- ✅ 即时拉取更新
- ✅ 无缝克隆仓库
- ✅ 支持所有 Git 操作

### 带 PAT 的 GitHub CLI (gh)
- ✅ 创建仓库：`gh repo create`
- ✅ 管理问题：`gh issue create/list`
- ✅ 处理 PR：`gh pr create/merge`
- ✅ 所有 GitHub 操作

## 🚀 手动配置（5分钟）

### 第一部分：SSH 密钥（3分钟）

```bash
# 1. 生成密钥（如果还没有的话）
ssh-keygen -t ed25519 -C "your-email@example.com"

# 2. 复制公钥
cat ~/.ssh/id_ed25519.pub | pbcopy  # macOS
cat ~/.ssh/id_ed25519.pub           # Linux（手动复制）

# 3. 添加到 GitHub
# 访问：https://github.com/settings/ssh/new
# 粘贴密钥并保存

# 4. 测试
ssh -T git@github.com
```

### 第二部分：GitHub CLI 令牌（2分钟）

```bash
# 1. 创建令牌
# 访问：https://github.com/settings/tokens/new
# 权限范围：✅ repo（选择全部）
# 点击"Generate token"并复制

# 2. 安装 GitHub CLI
brew install gh  # macOS
# Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# 3. 配置令牌
gh auth login --with-token
# 粘贴你的令牌

# 4. 设置 SSH 协议
gh config set git_protocol ssh
```

## 🧪 验证配置

```bash
# 测试 SSH
ssh -T git@github.com
# 预期输出：Hi username! You've successfully authenticated...

# 测试 GitHub CLI
gh auth status
# 预期输出：✓ Logged in to github.com

# 测试完整工作流
gh repo create test-$(date +%s) --public && gh repo delete --yes $(gh repo list --limit 1 --json name --jq '.[0].name')
# 预期：无需密码即可创建和删除仓库
```

## 📖 文档

查看 [SKILL.md](./SKILL.md) 了解：
- 详细配置说明
- 故障排除指南
- 高级配置选项
- 安全最佳实践
- 多账号配置

## 🔒 安全性

- SSH 密钥使用 ED25519（最安全）
- 令牌可限制为最小权限
- 可使用密码短语保护
- 泄露后易于撤销

## 🌐 平台支持

- ✅ macOS 10.15+
- ✅ Linux（Ubuntu、Debian、Fedora、Arch 等）
- ✅ Windows（WSL2、Git Bash）

## 🛠️ 包含工具

- `setup.sh` - 自动化配置脚本
- `verify.sh` - 配置验证工具
- 完整文档

## 💡 使用场景

适合：
- OpenClaw 自动化工作流
- CI/CD 流水线
- 开发团队
- 厌倦输入密码的任何人

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests！

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE)

## 🔗 相关链接

- [OpenClaw](https://github.com/openclaw/openclaw)
- [ClawHub](https://clawhub.ai)
- [GitHub SSH 文档](https://docs.github.com/zh/authentication/connecting-to-github-with-ssh)

---

**用 ❤️ 为追求效率的开发者打造**
