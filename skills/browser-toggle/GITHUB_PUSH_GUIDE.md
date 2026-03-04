# 🚀 GitHub 发布指南

## 📋 步骤 1：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称：`browser-toggle`
3. 描述：`OpenClaw Browser Toggle Skill - 一键启用/禁用内置浏览器`
4. 设为 **Public**（公开）
5. **不要** 初始化 README（我们已有代码）
6. 点击 **Create repository**

## 📋 步骤 2：推送代码到 GitHub

```bash
# 进入 Skill 目录
cd /home/ereala/.openclaw/workspace/skills/browser-toggle

# 添加 GitHub 远程仓库（替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/browser-toggle.git

# 推送到 GitHub
git push -u origin master
```

**如果提示需要认证：**
- 使用 GitHub Personal Access Token
- 或配置 SSH key

## 📋 步骤 3：创建 GitHub Release

1. 访问：https://github.com/YOUR_USERNAME/browser-toggle/releases/new
2. Tag version: `v1.0.0`
3. Target: `master`
4. Release title: `browser-toggle v1.0.0`
5. 描述：使用 `GITHUB_RELEASE.md` 的内容
6. 上传文件：
   - `dist/browser-toggle-v1.0.0.tar.gz`
   - `dist/browser-toggle-v1.0.0.tar.gz.sha256`
7. 点击 **Publish release**

## 📋 步骤 4：更新 README

在 GitHub 仓库的 README.md 中添加：

```markdown
# Browser Toggle Skill

[![Release](https://img.shields.io/github/release/your-username/browser-toggle.svg)](https://github.com/your-username/browser-toggle/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一键启用/禁用 OpenClaw 内置浏览器

## 🚀 快速安装

```bash
wget https://github.com/YOUR_USERNAME/browser-toggle/releases/download/v1.0.0/browser-toggle-v1.0.0.tar.gz
tar -xzf browser-toggle-v1.0.0.tar.gz
cd browser-toggle-v1.0.0
bash setup.sh
```

## 💡 使用

```bash
openclaw-browser --enable
openclaw gateway restart
```

## 📚 文档

- [安装指南](INSTALL.md)
- [使用指南](使用指南.md)
```

## 📋 步骤 5：验证发布

访问：
- 仓库主页：https://github.com/YOUR_USERNAME/browser-toggle
- Releases: https://github.com/YOUR_USERNAME/browser-toggle/releases

---

*完成！现在可以分享给其他人了！*
