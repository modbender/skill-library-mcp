# ClawHub 发布替代方案

## 问题分析

1. **浏览器登录失败**：出现 "Missing state" 错误
2. **GitHub Token 失败**：出现 "Unauthorized" 错误

这表明 ClawHub 使用的是自己的认证系统，而不是直接使用 GitHub token。

## 解决方案

### 方案 1：在 ClawHub 网站上获取 API Token

1. **访问 ClawHub 网站**
   
   打开：https://clawhub.ai

2. **使用 GitHub 登录**
   
   点击 "Sign in with GitHub"，授权 ClawHub 访问你的 GitHub 账号

3. **获取 API Token**
   
   登录后，访问：https://clawhub.ai/settings/tokens
   
   或者：
   - 点击右上角头像
   - 选择 "Settings"
   - 选择 "API Tokens"

4. **创建新 Token**
   
   - 点击 "Create Token"
   - 名称：`CLI Token`
   - 权限：选择 `publish` 和 `delete`（如果需要）
   - 点击 "Create"
   - **复制 token**（只显示一次！）

5. **使用 Token 登录 CLI**
   
   ```bash
   clawhub login --token YOUR_CLAWHUB_TOKEN
   ```
   
   注意：这次使用的是 ClawHub 的 token，不是 GitHub 的 token。

### 方案 2：直接在网站上发布

如果 CLI 一直有问题，可以直接在网站上传：

1. **访问 ClawHub**
   
   https://clawhub.ai

2. **登录**
   
   使用 GitHub 账号登录

3. **发布 Skill**
   
   - 点击 "Publish" 或 "Upload Skill"
   - 选择上传方式：
     - **上传文件夹**：选择 `brand-monitor-skill` 文件夹
     - **上传 ZIP**：先压缩文件夹，然后上传
     - **从 GitHub**：如果你的 skill 在 GitHub 上，可以直接导入

4. **填写信息**
   
   - **Slug**: `brand-monitor`
   - **Name**: `Brand Monitor for New Energy Vehicles`
   - **Version**: `1.1.0`
   - **Description**: `新能源汽车品牌舆情监控 - 自动搜索、分析国内平台的品牌提及情况`
   - **Tags**: `automotive`, `monitoring`, `chinese-platforms`, `new-energy-vehicle`
   - **License**: `MIT`

5. **提交**
   
   点击 "Publish" 完成发布

### 方案 3：等待浏览器回调完成

如果你刚才运行了 `clawhub login`，浏览器应该已经打开了。

**步骤：**

1. 在浏览器中完成授权
2. 等待浏览器显示 "Success" 或类似消息
3. **不要关闭浏览器**，等待 CLI 显示登录成功
4. 如果 CLI 超时，重新运行 `clawhub login`

**如果浏览器没有自动打开：**

手动访问 CLI 显示的 URL，例如：
```
https://clawhub.ai/cli/auth?redirect_uri=...
```

### 方案 4：使用 GitHub Actions 自动发布

创建 `.github/workflows/publish-clawhub.yml`：

```yaml
name: Publish to ClawHub

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install ClawHub CLI
        run: npm i -g clawhub
      
      - name: Publish to ClawHub
        env:
          CLAWHUB_TOKEN: ${{ secrets.CLAWHUB_TOKEN }}
        run: |
          cd brand-monitor-skill
          clawhub publish . \
            --slug brand-monitor \
            --name "Brand Monitor for New Energy Vehicles" \
            --version ${GITHUB_REF#refs/tags/v}
```

然后在 GitHub 仓库设置中添加 `CLAWHUB_TOKEN` secret。

## 推荐方案

**最简单的方式：方案 1**

1. 在 ClawHub 网站上登录
2. 获取 API Token
3. 使用 token 登录 CLI
4. 发布

**最快的方式：方案 2**

直接在网站上传，跳过 CLI。

## 当前状态

- ❌ 浏览器登录失败（Missing state）
- ❌ GitHub Token 失败（Unauthorized）
- ⏳ 需要从 ClawHub 网站获取正确的 API Token

## 下一步

1. 访问 https://clawhub.ai
2. 使用 GitHub 登录
3. 获取 API Token（Settings -> API Tokens）
4. 使用 ClawHub token 登录 CLI
5. 发布 skill

或者直接在网站上发布。

---

**注意：** ClawHub 的 API Token 和 GitHub 的 Personal Access Token 是不同的！你需要从 ClawHub 网站获取 token。
