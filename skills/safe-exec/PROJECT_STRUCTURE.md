# SafeExec Project Structure

清晰的目录结构说明。

## 📁 目录结构

```
safe-exec/
├── README.md                    # 📘 主要文档（快速开始）
├── README-detail.md             # 📖 详细文档（完整指南）
├── README_EN.md                 # 📘 英文主文档
├── CHANGELOG.md                 # 📝 版本变更日志
├── LICENSE                      # ⚖️ MIT 许可证
├── SKILL.md                     # 🔧 ClawdHub skill 描述
│
├── scripts/                     # 💻 核心脚本
│   ├── safe-exec.sh            # 主执行脚本
│   ├── safe-exec-approve.sh    # 批准请求
│   ├── safe-exec-reject.sh     # 拒绝请求
│   ├── safe-exec-list.sh       # 列出待处理请求
│   ├── safe-exec-check-pending.sh  # 检查待处理
│   └── safe-exec-ai-wrapper.sh     # AI 集成包装器
│
├── monitoring/                  # 📊 监控系统
│   ├── check-github-issues.sh      # GitHub issue 检查器
│   ├── check-openclaw-comments.sh  # OpenClaw comment 检查器
│   ├── unified-monitor.sh          # 统一监控协调器
│   ├── unified-monitor-status.sh   # 监控状态查看
│   ├── issue-monitor-status.sh     # Issue 监控状态
│   └── run-issue-check.sh          # Issue 检查运行器
│
├── tests/                       # 🧪 测试脚本
│   ├── test.sh                 # 主测试脚本
│   ├── test-safeexec.sh        # SafeExec 测试
│   ├── test-regression.sh      # 回归测试
│   └── test-context-aware.sh   # 上下文感知测试
│
├── tools/                       # 🔧 工具脚本
│   ├── safe-exec-add-rule.sh   # 规则添加工具
│   ├── publish-to-github.sh    # GitHub 发布工具
│   ├── push-to-github.sh       # Git 推送工具
│   └── release.sh              # 发布脚本
│
├── docs/                        # 📚 详细文档
│   ├── BLOG.md                 # 博客（中文）
│   ├── BLOG_EN.md              # Blog（英文）
│   ├── CONTRIBUTING.md         # 贡献指南
│   ├── PUBLISHING_GUIDE.md      # 发布指南
│   ├── FIX_REPORT_v0.1.3.md    # 修复报告 v0.1.3
│   ├── FIX_REPORT_v0.2.3.md    # 修复报告 v0.2.3
│   ├── GITHUB_ISSUE_MONITOR.md # GitHub 监控文档
│   ├── GITHUB_RELEASE_v0.2.0.md # GitHub 发布 v0.2.0
│   ├── GLOBAL_SWITCH_GUIDE.md  # 全局开关指南
│   ├── PROJECT_REPORT.md       # 项目报告
│   ├── RELEASE_v0.2.0.md       # 发布说明 v0.2.0
│   ├── RELEASE_v0.2.4.md       # 发布说明 v0.2.4
│   ├── RELEASE_NOTES.md        # 发布笔记
│   └── USAGE.md                # 使用说明
│
├── templates/                   # 📄 模板文件
│   └── (template files)
│
└── .github/                     # 🐙 GitHub 配置
    └── workflows/              # GitHub Actions
        └── (workflow files)
```

## 📂 目录说明

### 根目录

主要入口文档和配置文件：
- **README.md** - 快速开始，核心功能介绍
- **README-detail.md** - 完整使用指南
- **CHANGELOG.md** - 版本历史
- **SKILL.md** - ClawdHub skill 描述

### scripts/（核心脚本）

SafeExec 的核心实现，包含所有主要功能脚本。

### monitoring/（监控系统）

GitHub issues 和 OpenClaw comments 的自动监控。

### tests/（测试）

所有测试脚本，确保功能正常。

### tools/（工具）

辅助工具，如规则管理、发布工具等。

### docs/（详细文档）

各种专题文档、博客文章、技术报告等。

---

**最后更新:** 2026-02-01
