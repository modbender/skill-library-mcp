---
name: Config Validator Skill（配置验证器）
description: 验证 OpenClaw 配置字段和值的有效性，提供完整的 schema 参考和有效值枚举。
---

# Config Validator Skill（配置验证器）

## 用途

验证 OpenClaw 配置字段和值的有效性，提供完整的 schema 参考和有效值枚举。

## 使用时机

### ✅ 推荐：修改配置前查阅（预防错误）

在**思考如何修改配置时**就先查阅本 Skill：
- 确认字段是否存在
- 确认有效值是什么
- 查看配置示例
- 避免写错配置

### ✅ 必须：修改配置后验证（兜底检查）

在**safe-config-workflow 中**自动调用验证：
- 验证配置是否正确
- doctor --fix 兜底修复

## 触发条件

当用户需要：
- 确认某个配置字段是否存在
- 查询某个字段的有效值
- 验证配置是否正确
- 查找配置示例
- **修改配置前参考**（推荐）

## 模块结构

本 Skill 按模块组织配置 schema：

| 文件 | 内容 |
|---|---|
| `schema-channels.md` | Channels 完整 schema（Telegram, WhatsApp, Discord, Slack...） |
| `schema-agents.md` | Agents 完整 schema（defaults, list, heartbeat, sandbox...） |
| `schema-gateway.md` | Gateway 完整 schema（port, bind, auth, reload...） |
| `schema-session.md` | Session 完整 schema（dmScope, identityLinks, reset...） |
| `schema-tools.md` | Tools 完整 schema（elevated, sandbox, allow/deny...） |
| `schema-models.md` | Models 完整 schema（providers, fallbacks, aliases...） |
| `quick-reference.md` | 常用字段快速参考（50 个核心字段） |

## 使用方法

### 1. 查询字段有效值

```
用户：telegram 的 streaming 字段有哪些有效值？
AI: 查阅 schema-channels.md → 返回有效值
```

### 2. 验证配置

```
用户：这个配置对吗？{ "channels": { "telegram": { "streaming": "on" } } }
AI: 查阅 schema-channels.md → 验证并反馈
```

### 3. 查找配置示例

```
用户：如何配置 Telegram 机器人？
AI: 查阅 schema-channels.md → 返回示例配置
```

## 验证规则

### 严格验证

- 字段必须存在于 schema 中
- 值必须是枚举中的有效值
- 类型必须匹配（string, number, boolean, object, array）

### 常见错误

| 错误类型 | 示例 | 正确值 |
|---|---|---|
| 无效枚举值 | `"streaming": "on"` | `"off" \| "partial" \| "block" \| "progress"` |
| 无效类型 | `"port": "18789"` | `"port": 18789` |
| 未知字段 | `"channels": { "wechat": {} }` | 不支持的渠道 |

## 与 Safe Config Workflow 的集成

本 Skill 被 `safe-config-workflow` 自动调用：

```
safe-config-workflow 修改配置
    ↓
自动调用 config-validator 验证字段
    ↓
验证通过 → 继续执行
验证失败 → 反馈错误并停止
```

## 官方文档来源

所有 schema 信息来自官方文档：
- https://docs.openclaw.ai/gateway/configuration-reference
- https://docs.openclaw.ai/zh-CN/gateway/configuration

## 更新机制

当官方文档更新时：
1. 重新读取官方 configuration-reference.md
2. 更新对应的 schema 模块文件
3. 更新 quick-reference.md（如有变化）
4. 在 SKILL.md 中记录版本历史

## 版本历史

- v1.0 (2026-02-26) — 初始版本，包含完整 schema 和模块分文件
