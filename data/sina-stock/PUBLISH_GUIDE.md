# 📤 Sina Stock Skill 发布指南

本指南将帮助你把 `sina-stock` skill 发布到 GitHub 和 ClawHub.ai。

---

## 📋 准备工作

### 1. 确认文件结构

确保项目包含以下文件：

```
sina-stock/
├── README.md          # GitHub 展示页面
├── SKILL.md           # 技能使用文档
├── _meta.json         # LobsterAI 元数据
├── clawhub.yaml       # ClawHub 发布配置
├── .gitignore         # Git 忽略文件
└── scripts/
    └── get_stock.py   # 主脚本
```

✅ 所有文件已创建完成！

---

## 🚀 发布到 GitHub

### 步骤 1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `sina-stock`
   - **Description**: `A 股实时行情 Skill for LobsterAI - 获取上证指数、深证成指等股票数据`
   - **Visibility**: Public（公开）
   - **不要** 初始化 README/.gitignore（我们已经有了）

3. 点击 "Create repository"

### 步骤 2: 推送代码到 GitHub

在仓库创建页面，复制你的仓库地址，然后运行：

```bash
cd C:/Users/86183/lobsterai/project/sina-stock

# 添加远程仓库（你的 GitHub 用户名：Sunnyfo）
git remote add origin https://github.com/Sunnyfo/sina-stock.git

# 验证远程仓库
git remote -v

# 推送到 GitHub
git push -u origin main
```

### 步骤 3: 完善 GitHub 页面

1. **添加 Topics**：
   - 在仓库页面点击 "Manage topics"
   - 添加：`lobsterai`, `skill`, `stock`, `finance`, `A 股`, `股票`, `新浪财经`

2. **关于区域**：
   - 点击 "Manage" 编辑关于信息
   - 设置 website: `https://clawhub.ai`（发布后）

---

## 🦞 发布到 ClawHub.ai

### 方式 1: 通过 ClawHub 网站（推荐）

1. 访问 https://clawhub.ai/skills/publish

2. 登录/注册账号

3. 填写发布信息：
   - **Name**: `sina-stock`
   - **Description**: `获取 A 股实时股票行情数据，无需 API Key`
   - **GitHub Repository**: `https://github.com/Sunnyfo/sina-stock`
   - **Version**: `1.0.0`
   - **Category**: `Finance`
   - **Tags**: `stock, finance, A 股，行情，股票`

4. 上传/配置文件：
   - 上传 `clawhub.yaml`（已创建）
   - 或直接在网页填写配置

5. 提交审核

### 方式 2: 通过 ClawHub CLI

```bash
# 安装 ClawHub CLI（如果未安装）
npm install -g @clawhub/cli

# 登录
clawhub login

# 发布
cd C:/Users/86183/lobsterai/project/sina-stock
clawhub publish
```

---

## ✅ 发布前检查清单

### 代码质量
- [x] 脚本可以正常运行
- [x] 错误处理完善
- [x] 代码注释清晰

### 文档完整性
- [x] README.md - 项目介绍
- [x] SKILL.md - 使用文档
- [x] clawhub.yaml - 发布配置
- [ ] 截图/演示（可选，但推荐）

### 配置正确性
- [x] _meta.json 配置正确
- [x] clawhub.yaml 填写完整
- [ ] GitHub 仓库地址已更新

---

## 📸 添加截图（推荐）

截图可以大幅提升审核通过率！

### 步骤：

1. 运行 skill 并截图：

```bash
python "C:/Users/86183/AppData/Roaming/LobsterAI/SKILLs/sina-stock/scripts/get_stock.py" sh000001 sz399001 sz399006
```

2. 创建 screenshots 目录：

```bash
mkdir screenshots
```

3. 保存截图到 `screenshots/` 目录

4. 更新 clawhub.yaml：

```yaml
submission:
  screenshots:
    - path: screenshots/demo1.png
      description: 大盘指数查询示例
```

---

## 🔍 审核流程

1. **提交**：通过网站或 CLI 提交
2. **自动检查**：ClawHub 检查配置和代码
3. **人工审核**：1-3 个工作日
4. **发布**：审核通过后上线

### 审核提示

✅ **确保**：
- 技能可以正常运行
- 文档清晰完整
- 不包含敏感信息
- 数据来源合法

❌ **避免**：
- 需要 API Key 但未说明
- 文档不完整
- 代码无法运行
- 侵犯第三方权益

---

## 📊 发布后

### 推广你的 Skill

1. **社交媒体**：
   - 在 Twitter/微博分享
   - 加入 LobsterAI 社区

2. **文档链接**：
   - 在 GitHub README 添加 ClawHub 链接
   - 在 ClawHub 页面链接到 GitHub

3. **收集反馈**：
   - 关注 GitHub Issues
   - 回复用户问题
   - 持续改进

---

## 🔗 相关链接

- [LobsterAI 官方文档](https://lobsterai.com/)
- [ClawHub 发布指南](https://clawhub.ai/docs/publish)
- [Skill 开发最佳实践](https://clawhub.ai/docs/best-practices)

---

## 💡 常见问题

**Q: 发布需要收费吗？**
A: ClawHub 基础发布是免费的。

**Q: 审核需要多长时间？**
A: 通常 1-3 个工作日。

**Q: 可以更新已发布的 Skill 吗？**
A: 可以，修改版本号后重新提交。

**Q: 如何删除已发布的 Skill？**
A: 在 ClawHub 后台管理或联系支持。

---

祝你发布顺利！🎉

如有问题，请查看：
- GitHub Issues: https://github.com/Sunnyfo/sina-stock/issues
- ClawHub 文档：https://clawhub.ai/docs
