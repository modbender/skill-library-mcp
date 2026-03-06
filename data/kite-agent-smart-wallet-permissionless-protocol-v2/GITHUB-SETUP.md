# 发布到 GitHub

## 手动创建仓库

1. 打开 https://github.com/new
2. 仓库名: `kite-agent-wallet`
3. 设为 Public
4. 不要勾选 README
5. 点击 Create repository

## 本地执行

```bash
cd ~/.openclaw/workspace/skills/kite-agent-smart-wallet-permissionless-protocol-v2

git init
git add .
git commit -m "v2.0.4 - Kite AI Agent Wallet Protocol"

git remote add origin https://github.com/YOUR_USERNAME/kite-agent-wallet.git
git push -u origin main
```

## 或者一键创建

```bash
# 安装 gh CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# 登录
gh auth login

# 创建并推送
gh repo create kite-agent-wallet --public --source=. --push
```
