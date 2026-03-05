# 快速开始指南

5 分钟快速上手 CANN 代码审查技能。

## 🎯 前提条件

- ✅ OpenClaw 已安装并运行
- ✅ GitCode API Token 已配置（在 TOOLS.md 中）

## 📝 审查第一个 PR

### 方法 1：直接对话

```
审查这个 PR: https://gitcode.com/cann/runtime/merge_requests/628
```

### 方法 2：使用命令

```
cann review 628
```

## 📊 审查流程

技能会自动执行以下步骤：

```
1. 获取 PR 信息 ──────> API 调用
         │
         ▼
2. 获取代码变更 ──────> API 调用
         │
         ▼
3. 分析代码质量 ──────> 内存/安全/可读性
         │
         ▼
4. 生成审查报告 ──────> 结构化报告
         │
         ▼
5. 发布评论 ──────────> API 调用
         │
         ▼
6. 发布 LGTM (可选) ───> API 调用
```

## 📋 审查报告示例

```markdown
## 🤖 CANN 代码审查报告

**PR**: #628 - XPU接口文件归档修改
**严重性**: ✅ Low
**审查时间**: 2026-03-04 09:30

---

### 📊 审查结论

**✅ 建议合入**

- **严重性**: Low
- **代码质量**: 良好
- **内存安全**: ✅ 无风险
- **安全性**: ✅ 无漏洞
- **测试覆盖**: 部分
- **文档完整性**: 完整

代码质量良好，可以合入。

---

### 📋 修改概述

本次 PR 主要是接口文件的归档和整理。

- **修改文件**: 3个 (+16行, -0行)
- **核心变更**:
  - `rt_external_base.h`: 新增枚举定义
  - `rt_external_device.h`: 新增回调接口
  - `rt_common.cc`: 实现回调注册

---

### 💡 改进建议

1. **测试覆盖**: 建议补充单元测试
2. **错误处理**: 考虑添加参数校验

---

### ✅ 代码亮点

- 接口设计清晰，命名规范
- 注释完整，易于理解
```

## 🤖 自动审查模式

配置定时任务，自动审查新 PR：

### 使用 OpenClaw Cron

```yaml
# 配置 cron 任务
cron:
  action: add
  job:
    name: "cann-auto-review"
    schedule:
      kind: "cron"
      expr: "0 */2 * * *"  # 每 2 小时
    payload:
      kind: "agentTurn"
      message: "cann-review auto"
    sessionTarget: "isolated"
```

### 自动审查流程

```
每 2 小时 ────> 检查新 PR ────> 逐个审查 ────> 发送汇总
```

## 🔧 高级用法

### 使用辅助脚本

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/cann-review

# 获取 PR 信息
./gitcode-api.sh get-pr cann runtime 628

# 获取文件变更
./gitcode-api.sh get-files cann runtime 628 | python3 -m json.tool

# 发布测试评论
./gitcode-api.sh post-comment cann runtime 628 "测试评论"
```

### 自定义审查重点

```
审查 PR#628，重点关注内存安全
```

### 调整严重性阈值

在技能调用时指定：

```
审查 PR#628，阈值设为 low
```

## 🐛 故障排查

### 问题：API 返回 401

**解决**：
```bash
# 检查 Token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.gitcode.com/api/v5/user

# 如果失败，重新生成 Token
```

### 问题：找不到 PR

**解决**：
- 确认 PR 编号正确
- 确认有权限访问该项目

### 问题：无法评论

**解决**：
- 检查 PR 是否已合并
- 检查 Token 是否有 `write_repository` 权限

## 📚 下一步

- 📖 阅读 [完整文档](README.md)
- 📝 查看 [变更日志](CHANGELOG.md)
- 🔄 从 v2.x [迁移](MIGRATION.md)

## 💬 获取帮助

如有问题，请：
1. 查看 [常见问题](SKILL.md#常见问题)
2. 联系维护团队
