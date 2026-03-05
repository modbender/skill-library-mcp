---
id: openclaw-iflow-doctor
name: OpenClaw iFlow Doctor
version: 1.1.0
description: AI-powered auto-repair system for OpenClaw with iflow integration. Automatically diagnose and fix crashes, config errors, model issues. Falls back to iflow-helper when needed.
changelog: |
  ## [1.1.0] - 2026-03-01
  ### Bug Fixes
  - Fix: watchdog.py --daemon not working (daemon thread exits with main)
  - Fix: Tilde (~) path expansion in config files
  - Fix: Desktop directory not found on servers
  - Add: systemd service for auto-start on boot
  - Add: install-systemd.sh script for easy installation
  
  ### Improvements
  - Use absolute paths throughout the codebase
  - Cross-platform support (Linux/Windows/macOS)
  - Better error handling and logging
  
  ### Compatibility
  - OpenClaw: 2026.2.x+
  - Python: 3.8+
  - OS: Linux (systemd), Windows, macOS
metadata: 
  {
    "openclaw": {
      "requires": {
        "bins": ["python3", "openclaw"],
        "skills": ["iflow-helper"]
      },
      "optional": {
        "skills": ["iflow-helper"],
        "description": "for complex repairs requiring manual intervention"
      },
      "triggers": ["error", "startup_failure", "health_check"]
    }
  }
---

# OpenClaw Self-Healing V2 - 智能自我修复系统

> **自动诊断和修复 OpenClaw 崩溃、配置错误、模型问题。当自动修复失败时，无缝调用 iflow-helper 协助。**

## 核心能力

### ✅ 自动修复能力

1. **智能问题分类** - 自动识别 8 种问题类型
2. **案例库匹配** - 10+ 预置常见问题和解决方案
3. **历史记录复用** - 自动应用成功的历史修复方案
4. **配置自动检查** - 启动前自动验证配置有效性
5. **进程监控** - 崩溃后自动重启并修复

### 🔗 与 iflow-helper 集成

**自动调用链**:
```
OpenClaw 错误 → Self-Healing 尝试修复
    ├─ 成功 → 记录并恢复
    └─ 失败 → 自动调用 iflow-helper → iflow CLI 协助
```

**触发方式**:
- **自动**: 错误发生时自动触发
- **手动**: `openclaw heal "错误描述"`
- **检查**: `openclaw skills run openclaw-iflow-doctor --check`

## 问题类型覆盖

| 类型 | 自动修复 | 需 iflow 协助 |
|------|----------|---------------|
| memory (记忆损坏) | ✓ 重置索引 | 复杂数据恢复 |
| gateway (网关崩溃) | ✓ 重启服务 | 配置损坏修复 |
| config (配置错误) | ✓ 自动修正 | 手动配置指导 |
| network (网络问题) | ✓ 检查连接 | 代理设置指导 |
| api (API 额度/密钥) | ✗ 额度检查 | 充值/更新密钥 |
| agent (Agent 冲突) | ✓ 重新加载 | 复杂配置调整 |
| permission (权限错误) | ✓ 修复权限 | 系统权限指导 |
| install (安装损坏) | ✗ 备份重装 | 完整重装指导 |

## 安装

### 前提条件

- **Python**: 3.8+
- **OpenClaw**: 已安装并配置
- **可选**: iflow-helper (用于复杂修复)

### 安装步骤

```bash
# 方式 1: 从 GitHub 安装
openclaw skills install https://github.com/kosei-echo/openclaw-iflow-doctor

# 方式 2: 本地安装
cd ~/.openclaw/skills/
git clone https://github.com/kosei-echo/openclaw-iflow-doctor.git
openclaw skills enable openclaw-iflow-doctor
```

### 启用自动修复

```bash
# 启用自动模式（推荐）
openclaw skills config openclaw-iflow-doctor --set auto_heal=true

# 启用监控模式
openclaw skills run openclaw-iflow-doctor --watchdog
```

## 使用方法

### 1. 全自动模式（推荐）

启用后无需干预，自动处理所有错误：

```bash
# 启用自动修复
openclaw skills enable openclaw-iflow-doctor --auto

# 后续所有错误自动处理
# 简单问题自动修复
# 复杂问题生成 BAT 文件并提示调用 iflow
```

### 2. 手动诊断

```bash
# 诊断特定问题
openclaw heal "Gateway service crashed"

# 或完整命令
openclaw skills run openclaw-iflow-doctor --diagnose "错误描述"
```

### 3. 配置检查

```bash
# 启动前检查配置
openclaw skills run openclaw-iflow-doctor --check-config

# 输出示例:
# ✓ Config file exists
# ✓ JSON syntax valid
# ✓ Required fields present
# ✓ Model connectivity OK
```

### 4. 查看统计

```bash
openclaw skills run openclaw-iflow-doctor --stats

# 输出:
# Total cases: 10
# Total records: 25
# Auto-fixed: 18
# Iflow-assisted: 7
# Success rate: 92%
```

## 修复流程

### 流程 1: 自动修复成功

```
[系统] OpenClaw gateway crashed
[系统] Self-Healing triggered
[系统] Analyzing: Gateway crash detected
[系统] Searching case library... Match found: CASE-002
[系统] Applying solution: Restart gateway service
[系统] ✓ Gateway restarted successfully
[系统] Report: openclaw修复报告_20240227.txt
[系统] Record saved to memory
```

**用户操作**: 查看报告，无需干预

### 流程 2: 自动修复失败 → 调用 iflow

```
[系统] OpenClaw config error
[系统] Self-Healing triggered
[系统] Analyzing: Complex config corruption
[系统] Searching case library... No match
[系统] Searching records... No previous fix
[系统] ✗ Cannot auto-fix
[系统] Generated: openclaw诊断书_20240227.txt
[系统] Generated: 重新安装openclaw.bat
[系统] Generated: 打开iFlow寻求帮助.bat
[系统] 
[系统] 💡 Suggestion: Double-click BAT files on desktop
[系统]    Or run: openclaw skills run iflow-helper
```

**用户操作**: 
1. 双击"打开iFlow寻求帮助.bat"
2. 在 iflow 中描述问题
3. iflow 协助完成修复
4. 修复记录自动同步

### 流程 3: 启动配置检查

```bash
openclaw gateway start
[系统] Config check running...
[系统] ⚠ Missing field: models.default
[系统] Attempting auto-fix...
[系统] ✓ Fixed: Set default model to deepseek-chat
[系统] Starting gateway...
[系统] ✓ Gateway started
```

## 配置文件

### 技能配置

位置: `~/.openclaw/skills/openclaw-iflow-doctor/config.json`

```json
{
  "version": "2.0.0",
  "auto_heal": true,
  "enable_bat_generation": true,
  "enable_iflow_integration": true,
  "similarity_threshold": 0.7,
  "max_bat_files": 2,
  "iflow_helper_skill": "iflow-helper",
  "language": "auto"
}
```

### 配置项说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| auto_heal | true | 是否自动尝试修复 |
| enable_bat_generation | true | 无法修复时是否生成 BAT |
| enable_iflow_integration | true | 是否启用 iflow-helper 调用 |
| similarity_threshold | 0.7 | 案例匹配相似度阈值 |
| max_bat_files | 2 | 最多生成 BAT 文件数 |
| language | auto | 报告语言（auto/zh/en） |

## 案例库

### 预置案例 (10个)

1. **CASE-001**: Memory Search Function Broken
   - 症状: 记忆搜索失败，身份识别损坏
   - 自动修复: ✓ 重置记忆索引
   
2. **CASE-002**: Gateway Service Not Starting
   - 症状: 网关无法启动或崩溃
   - 自动修复: ✓ 重启服务
   
3. **CASE-003**: API Rate Limit Exceeded
   - 症状: API 额度超限，429 错误
   - 自动修复: ✗ 需手动充值/iflow 协助
   
4. **CASE-004**: Agent Spawn Failed
   - 症状: Agent 调用失败
   - 自动修复: ✓ 重新加载
   
5. **CASE-005**: Channel Configuration Error
   - 症状: Channel 配置错误
   - 自动修复: ✓ 重置配置
   
6. **CASE-006**: Model Provider Connection Failed
   - 症状: 模型连接失败
   - 自动修复: ✓ 切换到备用模型
   
7. **CASE-007**: Configuration File Corrupted
   - 症状: 配置文件损坏
   - 自动修复: ✓ 从备份恢复
   
8. **CASE-008**: Multiple Agents Conflict
   - 症状: 多 Agent 冲突
   - 自动修复: ✓ 重新加载配置
   
9. **CASE-009**: Permission Denied Errors
   - 症状: 权限拒绝错误
   - 自动修复: ✓ 修复权限
   
10. **CASE-010**: Log File Too Large
    - 症状: 日志文件过大
    - 自动修复: ✓ 清理日志

## 与 iflow-helper 协同

### 调用关系

```yaml
# openclaw-iflow-doctor 触发配置
triggers:
  on_error:
    steps:
      - step: 1
        name: "Self heal attempt"
        action: "auto_repair"
        timeout: 30s
        
      - step: 2
        name: "Call iflow-helper"
        condition: "step_1.failed"
        skill: "iflow-helper"
        args:
          task: "diagnose_and_repair"
          context: "{{error_description}}"
          use_multimodal: true
```

### 数据流

```
┌─────────────────────────────────────────────────────────┐
│  OpenClaw Error                                          │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  Self-Healing Analysis                                   │
│  - Search cases.json (10 built-in cases)                │
│  - Search records.json (historical fixes)               │
└────────┬────────────────────────────────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌──────┐  ┌──────────────────────────────────────────┐
│ Auto │  │ Generate Report + BAT                     │
│ Fix  │  │ - 重新安装openclaw.bat                   │
│      │  │ - 打开iFlow寻求帮助.bat                   │
└──┬───┘  └──────────────┬───────────────────────────┘
   │                     │
   ▼                     ▼
┌──────┐  ┌──────────────────────────────────────────┐
│Record│  │ Call iflow-helper                         │
│Success│  │ - Activate iflow CLI                      │
└──────┘  │ - User describes problem                  │
          │ - iflow diagnoses                         │
          │ - iflow fixes                             │
          └──────────────┬───────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────────────────┐
          │ Sync to Memory                            │
          │ - Save to records.json                    │
          │ - Optional: sync to iflow memory          │
          │ - Update cases.json if reusable           │
          └──────────────────────────────────────────┘
```

## 故障排除

### 技能无法加载

```bash
# 检查 Python 版本
python3 --version  # 需要 3.8+

# 检查文件权限
ls -la ~/.openclaw/skills/openclaw-iflow-doctor/

# 重新安装
openclaw skills reinstall openclaw-iflow-doctor
```

### 自动修复不触发

```bash
# 检查配置
openclaw skills config openclaw-iflow-doctor --get auto_heal

# 手动触发测试
openclaw skills run openclaw-iflow-doctor --test-trigger
```

### iflow-helper 调用失败

```bash
# 检查 iflow-helper 是否安装
openclaw skills list | grep iflow-helper

# 手动安装
openclaw skills install iflow-helper

# 禁用 iflow 集成（纯本地模式）
openclaw skills config openclaw-iflow-doctor --set enable_iflow_integration=false
```

## 最佳实践

### 1. 启用自动修复

首次安装后启用自动模式：
```bash
openclaw skills config openclaw-iflow-doctor --set auto_heal=true
```

### 2. 定期查看统计

每周查看修复统计，了解系统稳定性：
```bash
openclaw skills run openclaw-iflow-doctor --stats
```

### 3. 积累案例

遇到新问题并成功修复后，添加到案例库：
```bash
openclaw skills run openclaw-iflow-doctor --add-case
```

### 4. 配合 iflow 使用

复杂问题不要硬抗，及时调用 iflow：
- 双击生成的 BAT 文件
- 或在终端运行 `openclaw skills run iflow-helper`

## 相关链接

- **iflow-helper**: `~/.openclaw/workspace/skills/iflow-helper/`
- **案例库**: `~/.openclaw/skills/openclaw-iflow-doctor/cases.json`
- **配置**: `~/.openclaw/skills/openclaw-iflow-doctor/config.json`

## 总结

OpenClaw Self-Healing V2 提供：

✅ **自动修复** - 80% 常见问题自动解决
✅ **智能降级** - 复杂问题无缝转交 iflow
✅ **记忆积累** - 修复经验自动沉淀
✅ **零配置** - 安装即用，开箱即用
✅ **双向集成** - 与 iflow-helper 完美配合

**建议**: 与 iflow-helper 一起安装，获得最佳体验！