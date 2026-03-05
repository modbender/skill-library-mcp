# 安全配置流程 (Safe Config Workflow)

## 用途

安全修改 OpenClaw 配置文件，自动执行检查、修复、验证、学习反馈流程。

## 触发条件

当用户要求：
- 修改配置
- 更改 Gateway 设置
- 调整渠道配置
- 修改模型/会话/认证配置
- 任何涉及 `~/.openclaw/openclaw.json` 的操作

## 核心原则

1. **先查文档** — https://docs.openclaw.ai/zh-CN
2. **先参考 config-validator** — 修改前查阅 schema 和有效值
3. **先确认** — 向用户确认修改内容和影响
4. **不猜测** — 没文档依据就不做
5. **要学习** — doctor --fix 后记录教训
6. **要过滤** — doctor 输出由 AI 过滤，用户只看关键信息

## 反馈策略（两种结合）

| 问题类型 | 处理方式 | 示例 |
|---|---|---|
| **小问题**（拼写错误、格式问题） | 自己学习 + 记录 | 不麻烦用户，记录到 MEMORY.md |
| **重要配置**（影响功能、渠道、认证） | 反馈用户 + 学习 | 让用户知情，避免再次犯错 |
| **反复出现的错误** | 反馈 + 记录 + 总结 | 形成知识库，永久避免 |

## 执行流程

### 标准流程（99% 情况）

```bash
# 步骤 0: 查阅 config-validator（修改前参考）
# 确认字段存在和有效值
# 查看配置示例

# 步骤 1: 修改配置（先向用户确认）
# 确认模板：
# 📋 配置修改确认
# 修改内容：XXX
# 原因：XXX
# 影响：XXX
# 风险：低/中/高
# 文档依据：https://docs.openclaw.ai/zh-CN/XXX
# 是否继续？是/否

# 步骤 2: 检查 + 自动修复
openclaw doctor --fix
# AI 内部过滤关键信息：
# openclaw doctor --fix 2>&1 | grep -E "Doctor changes|Normalized|Config overwrite|Backup|Invalid"

# 步骤 3: 对比备份（必须执行！）
diff ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
# AI 解读 diff，向用户说明修改内容

# 步骤 4: 记录教训（重要！）
# 把学到的正确配置值记录到 MEMORY.md

# 步骤 5: 等待热重载
sleep 3
# 3 秒是合理的：热重载是进程内重启（SIGUSR1），官方设计为快速应用

# 步骤 6: 验证 Gateway 状态
openclaw gateway status
# 确认 Gateway 正常运行
```

### 排障流程（如果 Gateway 启动失败）

```bash
# Gateway 失败 ≠ 机器人瘫痪！
# 诊断命令仍然可用，因为它们是检查文件系统，不依赖 Gateway RPC

# 步骤 1: 查看日志，了解失败原因
openclaw logs --follow
# 查看错误信息，例如：
#   - Config validation failed: XXX
#   - Port 18789 already in use
#   - Invalid token format

# 步骤 2: 根据日志手动修复配置
nano ~/.openclaw/openclaw.json
# 针对性修复发现的问题

# 步骤 3: 再次尝试启动
openclaw gateway restart

# 步骤 4: 再次验证
openclaw gateway status
```

## 输出格式

### 修改前确认

```
📋 配置修改确认

修改内容：XXX
原因：XXX
影响：XXX
风险：低/中/高
文档依据：https://docs.openclaw.ai/zh-CN/XXX

是否继续？是/否
```

### doctor --fix 后反馈

**AI 向用户反馈的格式（必须遵守）：**

```
✅ 配置检查完成

【修复内容】
- 字段：channels.telegram.streaming
- 原值："invalid_test_value"（无效）
- 新值："off"（有效）

【备份位置】
~/.openclaw/openclaw.json.bak

【其他警告】（与配置无关，可选处理）
- Node 版本警告：系统 Node 16.5.0，建议升级到 22+
- 会话记录缺失：1/2 sessions 缺少 transcript
```

**小问题（不麻烦用户）：**
```
✅ 配置检查完成

doctor 输出：无问题 / 修复了 XXX（小问题，已自动修复）

已记录到：MEMORY.md
```

**重要配置（反馈用户）：**
```
✅ 配置检查完成

【修复内容】
- 字段：XXX
- 原值："XXX"（无效）
- 新值："XXX"（有效）

【学到的知识】
- 正确值：XXX
- 含义：XXX
- 文档：https://docs.openclaw.ai/zh-CN/XXX

⚠️ 注意：XXX（影响说明）

已记录到：MEMORY.md
```

### 验证结果

```
✅ Gateway 状态正常

Runtime: running
RPC probe: ok
```

### 失败排障

```
❌ Gateway 启动失败

错误日志：
XXX（从 logs --follow 获取）

已手动修复：XXX
正在重启 Gateway...

✅ Gateway 已恢复正常
```

## doctor --fix 输出解读规则（AI 必须遵守）

### AI 职责：过滤并总结关键信息

**AI 应该执行的过滤（内部处理，用户不需要看）：**
```bash
openclaw doctor --fix 2>&1 | grep -E "Doctor changes|Normalized|Config overwrite|Backup|Invalid"
```

**AI 向用户反馈时明确分类：**
- **修复项** — Doctor changes、Normalized、Config overwrite
- **警告项** — Node 版本、会话记录、Skills 状态等

**AI 必须执行的操作：**
1. 过滤 doctor 输出，提取关键修复信息
2. 对比备份文件，解读 diff
3. 向用户反馈修复内容（字段、原值、新值）
4. 记录教训到 MEMORY.md
5. 等待 3 秒后验证 Gateway 状态

## 安全规则

1. **修改前必须查文档** — https://docs.openclaw.ai/zh-CN
2. **修改前必须向用户确认** — 即使是你要求的
3. **绝不猜测字段值** — 没文档依据就不做
4. **修复后必须学习** — 记录到 MEMORY.md
5. **Gateway 失败仍可排障** — 诊断命令不依赖 Gateway
6. **输出必须过滤** — 用户只看关键信息，杂项由 AI 处理

## 已知局限

| 局限 | 说明 | 应对方案 |
|---|---|---|
| doctor 检测不出端口无效 | 端口号格式正确但值无效时 | 手动验证关键配置 |
| Gateway 有保护机制 | 无效配置时自动回滚默认值 | 修复后验证配置已生效 |
| Gateway 重启输出不清晰 | 只显示"missing tool result" | 查看 logs --follow 确认 |

## 相关文档

- 官方配置文档：https://docs.openclaw.ai/zh-CN/gateway/configuration
- 官方 doctor 文档：https://docs.openclaw.ai/zh-CN/cli/doctor
- 官方 Gateway 手册：https://docs.openclaw.ai/zh-CN/gateway/index.md
- 官方故障排除：https://docs.openclaw.ai/zh-CN/gateway/troubleshooting
- 官方 FAQ：https://docs.openclaw.ai/zh-CN/help/faq.md

## 版本历史

- v1.0 (2026-02-26) — 初始版本，包含完整流程和反馈策略
- v1.1 (2026-02-26) — 更新测试验证后的流程，添加输出过滤规则和已知局限
