# wechat-publisher

**一键发布 Markdown 到微信公众号草稿箱 🚀**

基于 [wenyan-cli](https://github.com/caol64/wenyan-cli) 封装的 OpenClaw skill。

---

## ✨ 功能特性

- 🚀 **一键发布** - Markdown 自动转换并推送到草稿箱
- 🎨 **多主题支持** - lapis、phycat、default 等精美主题
- 💻 **代码高亮** - 9 种代码高亮主题，Mac 风格代码块
- 🖼️ **图片自动处理** - 本地/网络图片自动上传到微信图床
- 🔒 **安全设计** - 凭证从 TOOLS.md 读取，不会泄露
- 📚 **完整文档** - 详细的使用说明和故障排查指南

---

## 🚀 快速开始

### 1. 安装 wenyan-cli

```bash
npm install -g @wenyan-md/cli
```

### 2. 克隆此仓库

```bash
git clone https://github.com/0731coderlee-sudo/wechat-publisher.git
cd wechat-publisher
```

### 3. 配置 API 凭证

在 OpenClaw workspace 的 `TOOLS.md` 中添加：

```markdown
## 🔐 WeChat Official Account (微信公众号)

**API Credentials:**
\`\`\`bash
export WECHAT_APP_ID=your_wechat_app_id
export WECHAT_APP_SECRET=your_wechat_app_secret
\`\`\`

**IP Whitelist:** 确保运行机器的 IP 已添加到公众号后台白名单

**后台地址:** https://mp.weixin.qq.com/
```

**如何获取凭证：**
1. 登录微信公众号后台：https://mp.weixin.qq.com/
2. 设置与开发 → 基本配置 → 开发者ID(AppID) 和 开发者密码(AppSecret)
3. 添加服务器 IP 到白名单：设置与开发 → 基本配置 → IP白名单

### 4. 发布测试文章

```bash
./scripts/publish.sh example.md
```

### 5. 查看草稿箱

前往微信公众号后台草稿箱查看：https://mp.weixin.qq.com/

---

## 📝 使用方法

### Markdown 格式要求

文件顶部**必须**包含 frontmatter（wenyan 强制要求）：

```markdown
---
title: 文章标题（必填！）
cover: ./assets/cover.jpg  # 封面图（必填！推荐 1080×864）
---

# 正文开始

你的内容...
```

**封面图推荐：**
- **相对路径**（推荐）：`./assets/cover.jpg`
- **绝对路径**：`/path/to/cover.jpg`
- **网络图片**：`https://example.com/cover.jpg`
- **尺寸建议**：1080×864（微信推荐比例）

### 发布命令

```bash
# 基本用法（使用默认主题）
./scripts/publish.sh article.md

# 指定主题和代码高亮
./scripts/publish.sh article.md lapis solarized-light

# 可用主题：lapis, phycat, default, orange, purple...
# 可用代码高亮：solarized-light, monokai, github, atom-one-dark...
```

---

## 🎨 主题预览

| 主题 | 风格 | 适合场景 |
|------|------|----------|
| **lapis** | 蓝色优雅 | 技术文章、教程 |
| **phycat** | 绿色清新 | 博客、随笔 |
| **default** | 经典简约 | 通用场景 |
| **orange** | 橙色活力 | 产品介绍 |
| **purple** | 紫色神秘 | 设计、创意 |

查看完整主题列表：[references/themes.md](references/themes.md)

---

## 🛠️ 故障排查

### 常见问题

**1. 错误：`Error: 未能找到文章封面`**
- **原因**：frontmatter 缺少 `cover` 字段
- **解决**：确保 frontmatter 包含 `title` 和 `cover`

**2. 错误：`Error: 45166 (IP地址不在白名单中)`**
- **原因**：运行机器的 IP 未添加到微信白名单
- **解决**：登录公众号后台添加 IP 到白名单

**3. 发布成功但看不到文章？**
- **原因**：文章在草稿箱，需要审核发布
- **解决**：草稿箱 → 选中文章 → 发布

**4. 图片上传失败？**
- **原因**：网络图片无法访问或格式不支持
- **解决**：使用本地图片或检查网络连接

查看完整故障排查指南：[references/troubleshooting.md](references/troubleshooting.md)

---

## 📂 项目结构

```
wechat-publisher/
├── SKILL.md                     # OpenClaw skill 完整文档
├── README.md                    # 本文件
├── example.md                   # 测试文章示例
├── .gitignore                   # Git 忽略文件
├── assets/
│   └── default-cover.jpg        # 默认封面（1080×864）
├── scripts/
│   ├── publish.sh               # 发布脚本（自动加载凭证）
│   └── setup.sh                 # 环境变量设置脚本
└── references/
    ├── themes.md                # 主题列表和使用说明
    └── troubleshooting.md       # 详细故障排查指南
```

---

## 🔧 高级用法

### 自定义主题

创建你自己的主题配置文件：

```bash
wenyan theme create my-theme
wenyan publish -f article.md -t my-theme
```

### 批量发布

```bash
for file in articles/*.md; do
    ./scripts/publish.sh "$file"
done
```

### 使用环境变量

```bash
export WECHAT_APP_ID=your_id
export WECHAT_APP_SECRET=your_secret
wenyan publish -f article.md
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发流程

1. Fork 此仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [wenyan-cli](https://github.com/caol64/wenyan-cli) - 优秀的微信公众号发布工具
- [OpenClaw](https://openclaw.ai) - 强大的 AI Agent 框架

---

## 📮 联系方式

- **GitHub**: [@0731coderlee-sudo](https://github.com/0731coderlee-sudo)
- **Issues**: [提交问题](https://github.com/0731coderlee-sudo/wechat-publisher/issues)

---

**如果这个 skill 对你有帮助，请给个 ⭐️ Star！**
