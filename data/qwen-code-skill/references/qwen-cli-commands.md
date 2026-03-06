# Qwen CLI 命令参考

## 基本命令

### 状态检查
```bash
scripts/qwen-code.js status
```
检查 Node.js 版本、CLI 安装状态、认证状态、已配置模型和最近会话。

### 版本信息
```bash
scripts/qwen-code.js version
scripts/qwen-code.js -v
```

### 帮助
```bash
scripts/qwen-code.js help
scripts/qwen-code.js --help
scripts/qwen-code.js -h
```

## 任务执行

### 运行任务
```bash
scripts/qwen-code.js run "任务描述"
scripts/qwen-code.js run "创建 Python Flask API" -m qwen3-coder-plus
scripts/qwen-code.js run "重构这个函数" -y
```

**选项：**
- `-m, --model <model>` - 指定模型
- `-y, --yolo` - YOLO 模式（自动批准所有操作）
- `-s, --sandbox` - 沙盒模式
- `--approval-mode <mode>` - 审批模式 (plan|default|auto-edit|yolo)
- `-o, --output-format <format>` - 输出格式 (text|json|stream-json)
- `-d, --debug` - 调试模式
- `--continue` - 恢复当前项目的最近会话
- `--resume <id>` - 恢复指定会话 ID

## 代码审查

```bash
scripts/qwen-code.js review <文件路径>
scripts/qwen-code.js review src/app.ts
scripts/qwen-code.js review src/app.ts -m qwen3-coder-plus
```

审查内容：
- 潜在 bug
- 性能问题
- 代码风格问题
- 安全漏洞
- 改进建议

## Headless 模式

用于脚本化、自动化和 CI/CD 集成：

```bash
scripts/qwen-code.js headless "任务描述"
scripts/qwen-code.js headless "分析代码" -o json
scripts/qwen-code.js headless "生成 commit message" --continue
```

**管道操作示例：**
```bash
git diff | qwen -p "生成 commit message"
gh pr diff | qwen -p "审查此 PR"
cat logs/app.log | qwen -p "分析错误原因"
```

## Sub-Agent 管理

```bash
# 创建子代理
scripts/qwen-code.js agent spawn "代码审查员" 请审查这个模块

# 列出子代理
scripts/qwen-code.js agent list

# 其他 agent 命令
scripts/qwen-code.js agent <action> [args]
```

## Skills 管理

```bash
# 列出已安装 skills
scripts/qwen-code.js skill list

# 创建新 skill
scripts/qwen-code.js skill create "python-expert"

# 打开 skill 目录
scripts/qwen-code.js skill open <skill-name>
```

## MCP 服务器管理

```bash
# 列出 MCP 服务器
scripts/qwen-code.js mcp list

# 添加 MCP 服务器
scripts/qwen-code.js mcp add google-drive

# 其他 MCP 命令
scripts/qwen-code.js mcp <command> [args]
```

## 扩展管理

```bash
# 列出扩展
scripts/qwen-code.js extensions list

# 安装扩展
scripts/qwen-code.js extensions install <git-url>
```

## 可用模型

| 模型 | 用途 |
|------|------|
| qwen3.5-plus | 通用编程 |
| qwen3-coder-plus | 复杂代码任务 |
| qwen3-coder-next | 轻量代码生成 |
| qwen3-max | 最强能力 |

## 配置文件

- **配置目录：** `~/.qwen/`
- **配置文件：** `~/.qwen/settings.json`
- **会话数据：** `~/.qwen/projects/<cwd>/chats`

## 认证方式

### OAuth 认证（推荐）
```bash
qwen
# 按提示完成 OAuth 登录
```

### API Key 认证
在 `~/.qwen/settings.json` 中配置：
```json
{
  "env": {
    "BAILIAN_CODING_PLAN_API_KEY": "sk-xxx"
  }
}
```

## 自动化用例

```bash
# 代码审查自动化
git diff | qwen -p "生成 commit message"

# 日志分析
tail -f app.log | qwen -p "如果发现异常，通知我"

# PR 审查
gh pr diff | qwen -p "审查此 PR"

# OpenClaw 后台任务
bash workdir:~/project background:true yieldMs:30000 \
  command:"qwen -p '创建 API 服务'"
```

## VS Code 扩展

- 扩展市场：https://marketplace.visualstudio.com/items?itemName=qwenlm.qwen-code-vscode-ide-companion
