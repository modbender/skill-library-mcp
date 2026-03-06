---
name: realmrouter-switch
description: Zero-friction RealmRouter model manager for OpenClaw. Chat-first workflow for setting API key, guided model picking, switching with availability check, rollback, connectivity testing, and short rr commands on both Unix and Windows.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins:
        - openclaw
      env:
        - REALMROUTER_API_KEY
    primaryEnv: REALMROUTER_API_KEY
    emoji: "🔁"
    os:
      - darwin
      - linux
      - win32
  version: 2.1.0
---

# RealmRouter Switch

> Chat-first model switching for OpenClaw.  
> 面向 OpenClaw 的对话式模型切换工具。

## 操作逻辑

### 1. 对话模式（推荐）

安装 skill 后，你只需要直接说：
- “切换模型” → 我会列出可用模型，你回复编号或模型名
- “把 key 设为 xxx” → 我会验证并更新
- “测试连通性” → 我会检查当前配置是否正常
- “回滚到上一个备份” → 我会恢复最近的备份

**重要**：所有操作我都会自动帮你执行，包括重启 gateway。

### 2. 命令行模式

如果习惯命令行，可以用 `rr` 快捷命令：
- `rr show` - 查看当前状态
- `rr pick` - 列出编号模型列表
- `rr switch <model>` - 切换模型
- `rr key <key>` - 更新 API Key
- `rr test` - 测试连通性
- `rr rollback` - 回滚备份

---

## 安装指南

### macOS / Linux 安装

#### 步骤 1: 安装 skill
```bash
npx clawhub install realmrouter-switch --force
```

#### 步骤 2: 安装 rr 快捷命令（可选但推荐）
```bash
# 方式一：使用安装脚本
bash ~/.openclaw/workspace/skills/realmrouter-switch/scripts/install_rr.sh

# 方式二：手动添加到 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc  # 如果用 zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # 如果用 bash
source ~/.zshrc  # 或 source ~/.bashrc
```

#### 步骤 3: 验证安装
```bash
rr show
# 或直接用 Python 脚本
python3 ~/.openclaw/workspace/skills/realmrouter-switch/scripts/realm_manager.py show
```

---

### Windows 安装

#### 步骤 1: 安装 skill
```powershell
npx clawhub install realmrouter-switch --force
```

#### 步骤 2: 安装 rr 快捷命令
```powershell
# 以管理员权限运行 PowerShell，然后执行：
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\realmrouter-switch\scripts\install_rr.ps1"
```

#### 步骤 3: 重启终端
关闭当前 PowerShell 窗口，重新打开一个新的。

#### 步骤 4: 验证安装
```powershell
rr show
# 或直接调用脚本
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\realmrouter-switch\scripts\realm_manager.ps1" show
```

---

## 命令详解

### rr show
显示当前配置状态：
- RealmRouter provider 是否存在
- 当前默认模型
- API Key（已掩码）

### rr pick
列出编号模型列表，方便选择：
```
[1] claude-opus-4-6-thinking
[2] claude-sonnet-4.6
[3] gpt-5.3-codex
[4] gpt-5.2-codex
[5] qwen3-max
...
```

### rr switch <model>
切换默认模型。支持三种格式：
- **编号**: `rr switch 3` （先用 `rr pick` 查看编号）
- **别名**: `rr switch gpt53` （内置别名见下方）
- **完整 ID**: `rr switch gpt-5.3-codex`

**内置别名**：
| 别名 | 实际模型 |
|------|---------|
| `opus` | claude-opus-4-6-thinking |
| `sonnet` | claude-sonnet-4.6 |
| `gpt53` | gpt-5.3-codex |
| `gpt52` | gpt-5.2-codex |
| `qwen` | qwen3-max |
| `r1` | deepseek-ai/DeepSeek-R1 |
| `gemini` | gemini-3.1-pro-high |
| `glm5` | zai-org/GLM-5 |

### rr key <api-key>
更新 RealmRouter API Key，会自动验证有效性。

### rr test
测试当前配置的连通性，验证 Key 和模型是否可用。

### rr rollback
恢复最近的备份文件。

### rr menu (Windows)
进入交互菜单模式，适合不熟悉命令行的用户。

---

## 完整使用流程示例

### macOS / Linux
```bash
# 1. 安装
npx clawhub install realmrouter-switch --force
bash ~/.openclaw/workspace/skills/realmrouter-switch/scripts/install_rr.sh

# 2. 设置 Key
rr key sk-xxxxxxxxxxxxx

# 3. 查看可选模型
rr pick

# 4. 切换模型
rr switch 3
# 或
rr switch gpt53

# 5. 验证
rr test
rr show
```

### Windows
```powershell
# 1. 安装
npx clawhub install realmrouter-switch --force
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.openclaw\workspace\skills\realmrouter-switch\scripts\install_rr.ps1"

# 2. 重启终端

# 3. 设置 Key
rr key sk-xxxxxxxxxxxxx

# 4. 查看可选模型
rr pick

# 5. 切换模型
rr switch 3
# 或
rr switch gpt53

# 6. 验证
rr test
rr show
```

---

## 特性总结

- **安全**: 修改前自动备份到 `~/.openclaw/backups/`
- **验证**: Key 和模型都会验证可用性
- **便捷**: 支持编号、别名、完整 ID 三种方式
- **跨平台**: macOS / Linux / Windows 统一体验
- **对话优先**: 直接告诉我你要做什么，我来执行

---

## 故障排除

### `rr: command not found`
- macOS/Linux: 确保 `~/.local/bin` 在 PATH 中
- Windows: 确保已重启终端，且 `%USERPROFILE%\bin` 在 PATH 中

### `API key verification failed`
- 检查 Key 是否正确
- 检查网络是否能访问 `https://realmrouter.cn/v1`
- 使用 `-Force` 参数强制跳过验证

### 切换后模型没生效
- 确保重启了 gateway: `openclaw gateway restart`
- 或在命令中加 `-RestartGateway` 参数
