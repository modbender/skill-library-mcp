# IssueFinder Tool Wrapper 使用说明

## 概述

`issuefinder-tool-wrapper.py` 是对原始 `issuefinder-tool.py` 的包装脚本，用于自动管理日志输出路径，无需修改原始工具脚本。

## 功能特性

- ✅ **自动路径管理**：使用 `ISSUEFINDER_LOGS_PATH` 环境变量管理日志路径
- ✅ **日期分组**：自动按 `年/月/日` 创建目录结构
- ✅ **保持兼容**：完全兼容原始工具的所有参数和功能
- ✅ **灵活覆盖**：仍可通过 `--output` 参数指定自定义路径

## 环境变量

### ISSUEFINDER_LOGS_PATH

指定日志输出的基础路径。

**默认值**：`~/issuefinder_mcp_log`

**设置方法**：

```bash
# 临时设置（当前会话）
export ISSUEFINDER_LOGS_PATH="/your/custom/path"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export ISSUEFINDER_LOGS_PATH="/your/custom/path"' >> ~/.bashrc
source ~/.bashrc
```

## 目录结构

包装脚本会自动创建以下目录结构：

```
$ISSUEFINDER_LOGS_PATH/
├── 2026/
│   ├── 02/
│   │   ├── 26/
│   │   │   ├── VIN_HLX33B124P1767770/        # 云端下载日志
│   │   │   │   ├── lastlog
│   │   │   │   ├── minidump
│   │   │   │   └── ...
│   │   │   ├── vehicle_logs.zip/             # 本地处理日志
│   │   │   │   ├── parsed_lastlog.txt
│   │   │   │   └── ...
│   │   │   └── ...
│   │   └── 28/
│   └── ...
└── ...
```

## 使用方法

### 方法 1: 使用便捷命令 `iflog`

最简单的方式，推荐使用：

```bash
# 添加到 PATH（一次性设置）
export PATH="$PATH:/home/lixiang/git/bug-bye-bye-agent/.siada-cli/skills/issuefinder-tool/scripts"

# 或添加别名到 ~/.bashrc 或 ~/.zshrc
alias iflog='/home/lixiang/git/bug-bye-bye-agent/.siada-cli/skills/issuefinder-tool/scripts/iflog'

# 使用示例
iflog --direct-download --vin HLX33B124P1767770 --happen-time "2025-10-27 18:43"
iflog -u /path/to/lastlog_file
iflog --issuefinder --vin HLX33B124P1767770 --happen-time "2025-10-27 18:43"
```

### 方法 2: 直接调用包装脚本

```bash
python3 .siada-cli/skills/issuefinder-tool/scripts/issuefinder-tool-wrapper.py [参数]
```

### 方法 3: 直接调用原始工具（手动指定路径）

```bash
python3 .siada-cli/skills/issuefinder-tool/scripts/issuefinder-tool.py --output ~/issuefinder_mcp_log/2026/02/28 [其他参数]
```

## 使用示例

### 示例 1: 云端下载日志（自动按日期分组）

```bash
# 使用包装脚本，自动输出到 ~/issuefinder_mcp_log/2026/02/28/VIN_HLX33B124P1767770/
iflog --direct-download \
  --vin HLX33B124P1767770 \
  --happen-time "2025-10-27 18:43"

# 输出位置：$ISSUEFINDER_LOGS_PATH/2026/02/28/VIN_HLX33B124P1767770/
```

### 示例 2: 本地日志处理（自动按日期分组）

```bash
# 处理本地日志文件，自动输出到日期目录
iflog -u /path/to/vehicle_logs.zip

# 输出位置：$ISSUEFINDER_LOGS_PATH/2026/02/28/vehicle_logs.zip/
```

### 示例 3: IssueFinder 分析（自动按日期分组）

```bash
# 自动分析并下载日志
iflog --issuefinder \
  --vin HLX33B124P1767770 \
  --happen-time "2025-10-27 18:43"

# 输出位置：$ISSUEFINDER_LOGS_PATH/2026/02/28/VIN_HLX33B124P1767770/
```

### 示例 4: 覆盖默认路径（使用 --output）

```bash
# 即使使用包装脚本，仍可手动指定输出路径
iflog -u /path/to/logs.zip --output /custom/path

# 输出位置：/custom/path/logs.zip/
```

## 与原始工具的区别

| 特性 | 原始工具 | 包装脚本 |
|------|---------|---------|
| 默认输出路径 | `./results` | `$ISSUEFINDER_LOGS_PATH/YYYY/MM/DD/` |
| 日期分组 | ❌ 不支持 | ✅ 自动创建 |
| 环境变量支持 | ❌ 不支持 | ✅ 支持 ISSUEFINDER_LOGS_PATH |
| 参数兼容性 | - | ✅ 100% 兼容 |
| 手动指定路径 | ✅ 支持 | ✅ 支持（覆盖默认） |

## 工作原理

包装脚本的工作流程：

1. **读取环境变量**：获取 `ISSUEFINDER_LOGS_PATH`（默认 `~/issuefinder_mcp_log`）
2. **创建日期目录**：自动创建 `年/月/日` 目录结构
3. **传递参数**：如果没有指定 `--output`，自动添加 `--output <日期目录>`
4. **调用原始工具**：使用修改后的参数调用 `issuefinder-tool.py`
5. **透传结果**：将原始工具的输出和退出码透传回用户

## 推荐的 Shell 配置

将以下内容添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
# IssueFinder 日志工具配置
export ISSUEFINDER_LOGS_PATH="$HOME/issuefinder_mcp_log"
alias iflog='python3 /home/lixiang/git/bug-bye-bye-agent/.siada-cli/skills/issuefinder-tool/scripts/issuefinder-tool-wrapper.py'

# 或使用便捷脚本
alias iflog='/home/lixiang/git/bug-bye-bye-agent/.siada-cli/skills/issuefinder-tool/scripts/iflog'
```

重新加载配置：

```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

## 故障排查

### 问题 1: 找不到原始工具脚本

**错误信息**：`错误: 找不到原始工具脚本`

**解决方法**：确保 `issuefinder-tool.py` 与包装脚本在同一目录

### 问题 2: 权限错误

**错误信息**：`Permission denied`

**解决方法**：
```bash
chmod +x .siada-cli/skills/issuefinder-tool/scripts/issuefinder-tool-wrapper.py
chmod +x .siada-cli/skills/issuefinder-tool/scripts/iflog
```

### 问题 3: 环境变量未生效

**解决方法**：确认环境变量已设置
```bash
echo $ISSUEFINDER_LOGS_PATH
```

如果为空，重新设置并 source 配置文件。

## 维护和更新

- ✅ **原始工具更新**：包装脚本无需修改，自动使用最新版本
- ✅ **云端同步**：原始 `issuefinder-tool.py` 可从云端同步更新
- ✅ **独立维护**：包装脚本与原始工具独立，互不影响

## 文件说明

```
.siada-cli/skills/issuefinder-tool/scripts/
├── issuefinder-tool.py           # 原始工具（从云端同步，不要修改）
├── issuefinder-tool-wrapper.py   # 包装脚本（本地维护）
├── iflog                          # 便捷命令脚本
└── WRAPPER_USAGE.md               # 本文档
```

---

**创建日期**：2026-02-28  
**维护者**：本地项目
