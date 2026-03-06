# CANN Runtime 代码审查技能

自动审查 GitCode 上的 CANN runtime 项目 PR，检查内存泄漏、安全漏洞和代码可读性。

## ✨ 特性

- 🔍 **全面代码审查**：内存泄漏、安全漏洞、代码可读性
- 🚀 **基于 API**：使用 GitCode API，无需浏览器自动化，稳定可靠
- 💬 **自动评论**：自动发布结构化审查报告
- ✅ **LGTM 支持**：低风险 PR 自动发布 `/lgtm`
- 🤖 **自动模式**：支持定时任务，自动审查新 PR

## 📦 安装

1. 确保 OpenClaw 已配置 GitCode API Token（已在 TOOLS.md 中配置）
2. 技能位于：`~/.openclaw/workspace/skills/cann-review/`

## 🚀 使用方法

### 手动审查单个 PR

直接提供 PR 链接：

```
审查这个 PR: https://gitcode.com/cann/runtime/merge_requests/628
```

或使用命令：

```
cann review PR#628
```

### 自动审查模式

配置定时任务，自动审查新 PR：

```yaml
# 在 OpenClaw 中配置 cron 任务
schedule: "0 */2 * * *"  # 每 2 小时执行一次
task: "cann-review auto"
```

## 🔧 API 辅助脚本

提供了 `gitcode-api.sh` 辅助脚本：

```bash
# 获取 PR 信息
./gitcode-api.sh get-pr cann runtime 628

# 获取 PR 文件变更
./gitcode-api.sh get-files cann runtime 628

# 发布评论
./gitcode-api.sh post-comment cann runtime 628 "LGTM!"

# 列出开放的 PR
./gitcode-api.sh list-prs cann runtime
```

## 📊 审查报告格式

审查报告包括：

- **审查结论**：严重性评估和建议
- **修改概述**：变更文件和核心变更
- **代码质量检查**：
  - 内存安全
  - 安全性
  - 可读性
  - 逻辑正确性
- **改进建议**：具体优化建议
- **代码亮点**：做得好的地方

## ⚙️ 配置

### API Token

在 `TOOLS.md` 中配置：

```markdown
### GitCode
- **Personal Access Token**: `your-token-here`
- **API Base URL**: `https://api.gitcode.com/api/v5`
```

### 审查阈值

可在技能中调整发布 LGTM 的阈值：

- `low`: 仅低风险发布 LGTM
- `medium`: 低和中低风险发布 LGTM（默认）
- `high`: 低、中、高风险都发布 LGTM（不推荐）

## 🐛 故障排查

### API 返回 401

检查 Token 是否有效：
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.gitcode.com/api/v5/user
```

### 无法评论已合并的 PR

这是正常行为，已合并的 PR 可能禁止新评论。

### API 频率限制

GitCode API 限制：50次/分钟，4000次/小时。如需大量审查，添加适当延迟。

## 📝 版本历史

### v3.0.0 (2026-03-04)
- 🎉 **重大更新**：全面改用 GitCode API
- 🚀 提高稳定性和可靠性
- 📝 简化操作流程

详细版本历史见 SKILL.md

## 📄 许可证

内部使用

## 🤝 贡献

如有问题或建议，请联系维护团队。
