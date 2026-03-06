---
name: 星期五
slug: friday
version: 1.0.0
homepage: https://clawdhub.com/skills/friday
description: 专用编程代理 - 使用 opencode 进行代码编写、审查、重构和调试
changelog: 初始版本 - 专用编程代理，支持代码生成、审查和重构
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":["opencode"]},"os":["linux","darwin","win32"]}}
---

# 星期五 (Friday) - 专用编程代理

**定位：** 专注于代码编写、审查和重构的编程代理  
**核心工具：** opencode CLI  
**模型：** 支持多种编程优化模型

## 何时使用

- 编写新功能代码
- 代码审查和 PR 审核
- 重构现有代码
- Bug 修复和调试
- 单元测试编写
- 技术文档生成

## 快速启动

### 一键执行任务

```bash
# 在当前项目目录运行
opencode run "你的编程任务描述"

# 指定工作目录
opencode run --workdir /path/to/project "任务描述"
```

### 后台运行（长时间任务）

```bash
# 启动后台会话
opencode run --background "构建完整的 REST API"

# 监控进度
opencode status <session-id>

# 查看日志
opencode log <session-id>
```

### 交互式会话

```bash
# 启动交互式编程会话
opencode chat

# 或直接进入项目
cd /path/to/project && opencode chat
```

## 核心功能

### 1. 代码生成

```bash
# 生成新功能
opencode run "创建一个用户认证模块，支持 JWT 和 OAuth2"

# 生成测试
opencode run "为 user_service.py 编写单元测试，覆盖率 90%+"
```

### 2. 代码审查

```bash
# 审查 PR
opencode run "审查这个 PR 的代码质量、安全性和性能问题"

# 代码审计
opencode run "审计这个模块的安全漏洞和代码异味"
```

### 3. 重构

```bash
# 重构代码
opencode run "重构这个函数，提高可读性和性能"

# 类型转换
opencode run "将这个 JavaScript 文件转换为 TypeScript"
```

### 4. 调试

```bash
# 分析错误
opencode run "分析这个错误日志，找出根本原因并修复"

# 性能优化
opencode run "分析这段代码的性能瓶颈并优化"
```

## 工作模式

### 全自动模式 (适合可信任务)

```bash
opencode run --auto "任务描述"
```

### 交互式模式 (需要确认)

```bash
opencode run --interactive "任务描述"
```

### 只读模式 (仅分析，不修改)

```bash
opencode run --read-only "分析这个架构并提出改进建议"
```

## 最佳实践

### 1. 明确任务范围

❌ 模糊："改进这个代码"  
✅ 明确："重构这个函数，减少嵌套层级，添加错误处理"

### 2. 提供上下文

```bash
# 指定相关文件
opencode run --context "src/,tests/" "添加输入验证"

# 指定技术栈
opencode run --stack "python,fastapi,postgresql" "创建用户 API"
```

### 3. 分步执行复杂任务

```bash
# 第一步：分析
opencode run --read-only "分析当前架构"

# 第二步：规划
opencode run "基于分析结果，制定重构计划"

# 第三步：执行
opencode run --auto "执行重构计划第一步"
```

### 4. 验证结果

```bash
# 运行测试
opencode run "运行测试并修复失败用例"

# 代码检查
opencode run "运行 linter 并修复所有警告"
```

## 配置

### 模型选择

```bash
# 使用特定模型
opencode run --model "coder-model" "任务"

# 使用默认模型（在 ~/.opencode/config.toml 配置）
opencode run "任务"
```

### 常用配置项

在 `~/.opencode/config.toml` 中配置：

```toml
[default]
model = "coder-model"
auto_approve = false
max_iterations = 10

[profiles.python]
model = "python-expert"
lint_tool = "ruff"
test_runner = "pytest"

[profiles.javascript]
model = "js-expert"
lint_tool = "eslint"
test_runner = "vitest"
```

## 输出格式

### 代码变更

星期五会输出：
- 修改的文件列表
- 变更摘要
- 关键决策说明
- 潜在风险提示

### 审查报告

- 问题分类（安全/性能/风格）
- 严重程度
- 修复建议
- 代码示例

## 安全注意事项

⚠️ **重要规则：**

1. **不要在不信任的目录运行** - 星期五有文件系统访问权限
2. **审查自动变更** - 即使是 --auto 模式，也要 review 关键变更
3. **敏感信息** - 不要在提示中包含密钥、密码等敏感信息
4. **Git 提交** - 自动提交前确保变更正确

## 故障排除

### 常见问题

**问题：** 星期五卡住或无响应  
**解决：** 检查网络、模型 API 状态，或重启会话

**问题：** 变更不符合预期  
**解决：** 提供更详细的任务描述，或切换到交互模式

**问题：** 权限错误  
**解决：** 检查工作目录权限，或使用 sudo（谨慎）

## 相关技能

- `agentic-coding` - 合同驱动的代码开发流程
- `coding-agent` - 通用编程代理支持
- `github` - GitHub 集成和 PR 管理

## 反馈

- 有用吗？`clawdhub star friday`
- 保持更新：`clawdhub update friday`
- 报告问题：https://clawdhub.com/skills/friday

---

*星期五，你的编程伙伴。让代码写得更快、更好、更安心。*
