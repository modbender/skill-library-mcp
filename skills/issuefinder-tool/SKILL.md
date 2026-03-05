---
name: issuefinder-tool
description: 功能强大的车辆日志下载与解析工具，支持云端日志下载、本地日志处理、自动故障分析等功能
---

# issuefinder-tool

## 工具概述

`issuefinder-tool` 是一个专业的车辆日志分析工具，提供云端日志下载、本地日志解析、自动故障分析等功能。工具能够自动识别日志类型，支持多种日志格式，并可与 IssueFinder API 集成进行智能分析。

### 核心功能
- **车辆日志下载**：从云端下载指定 VIN 和时间的车辆日志
- **智能故障分析**：自动分析车辆重启原因和故障信息
- **本地日志处理**：支持多种日志格式的解析和转换
- **自动类型识别**：智能检测日志文件类型，自动选择合适的解析工具
- **归档文件支持**：自动解压 zip、tar.gz、7z 等压缩格式

---

## 🚀 推荐使用方式

为了更好地管理日志输出路径，**强烈推荐使用包装脚本** `iflog` 命令。

### 为什么使用包装脚本？

- ✅ **自动路径管理**：日志自动保存到 `ISSUEFINDER_LOGS_PATH` 环境变量指定的路径
- ✅ **日期分组**：自动按 `年/月/日` 创建目录结构，便于管理
- ✅ **完全兼容**：支持原始工具的所有参数和功能
- ✅ **独立维护**：不影响原始工具的云端同步更新

### 快速开始

```bash
# 1. 设置环境变量（已配置为 /home/lixiang/work/sdata/iss-log）
export ISSUEFINDER_LOGS_PATH="/home/lixiang/work/sdata/iss-log"

# 2. 设置命令别名（添加到 ~/.bashrc 或 ~/.zshrc）
alias iflog='/home/lixiang/.openclaw/skills/issuefinder-tool/scripts/iflog'

# 3. 重新加载配置
source ~/.bashrc  # 或 source ~/.zshrc

# 4. 使用 iflog 命令（自动按日期分组）
iflog --direct-download --vin HLX33B124P1767770 --happen-time "2025-10-27 18:43"
iflog -u /path/to/lastlog_file
iflog --issuefinder --vin HLX33B124P1767770 --happen-time "2025-10-27 18:43"
```

### 自动生成的目录结构

```
/home/lixiang/work/sdata/iss-log/
├── 2026/
│   ├── 02/
│   │   ├── 28/
│   │   │   ├── VIN_HLX33B124P1767770/    # 云端下载的日志
│   │   │   ├── vehicle_logs.zip/         # 本地处理的日志
│   │   │   └── ...
│   │   └── 26/
│   │       └── ...
```

**详细文档**：查看 [WRAPPER_USAGE.md](./WRAPPER_USAGE.md) 了解更多信息

---

## 工作模式

### 本地文件处理模式（默认）

上传并处理本地日志文件，支持自动类型识别。

**适用场景**：已有日志文件，需要解析或转换格式

**基础用法**（推荐使用 iflog 命令，自动管理输出路径）：
```bash
# 自动检测文件类型并处理（使用配置的路径）
iflog -u /path/to/lastlog_file

# 处理压缩包（自动解压）
iflog -u /path/to/logs.zip

# 手动指定工具类型
iflog -t lastlog_unpack -u /path/to/lastlog_file --verbose

# 或使用原始工具（需手动指定输出路径）
issuefinder-tool.py -u /path/to/lastlog_file --output /home/lixiang/work/sdata/iss-log/$(date +%Y/%m/%d)
```

---

### IssueFinder 分析模式

通过 IssueFinder API 自动分析车辆重启原因和故障信息。

**适用场景**：需要自动分析车辆故障原因

**基础用法**（推荐使用 iflog 命令）：
```bash
# 分析车辆重启原因（自动保存到配置路径）
iflog --issuefinder --vin HLX33B124P1767770 --happen-time "2025-10-27 18:43"

# 支持多种时间格式
iflog --issuefinder --vin HLX33B124P1767770 --happen-time "2025-10-27T18:43"
iflog --issuefinder --vin HLX33B124P1767770 --happen-time "2025/10/27 18:43:00"
```

**分析结果包含**：
- 重启原因（reboot reason）
- 最终分析结果（final result）
- 屏幕状态（screen status）
- 相关日志文件下载

---

### 云端日志下载模式

通过 IssueFinder API 下载云端日志文件。

**适用场景**：需要获取云端存储的车辆日志

**基础用法**（推荐使用 iflog 命令）：
```bash
# 下载指定 VIN 和时间的日志（自动保存到配置路径）
iflog --cloud-log \
  --vin HLX33B124P1767770 \
  --happen-time "2025-10-27 18:43" \
  --task-type 1731484362257596488

# 自定义任务类型
iflog --cloud-log \
  --vin HLX33B124P1767770 \
  --happen-time "2025-10-27 18:43" \
  --task-type YOUR_TASK_ID \
  --poll-interval 30
```

---

### 直接云端下载模式（推荐）

直接从云端存储下载日志，绕过 IssueFinder API，速度更快。

**适用场景**：仅需要下载日志文件，不需要分析

**基础用法**（推荐使用 iflog 命令，自动管理输出路径）：
```bash
# 下载 Klog 类型日志（自动保存到 /home/lixiang/work/sdata/iss-log/YYYY/MM/DD/）
iflog --direct-download \
  --vin HLX14B175S1996368 \
  --happen-time "2025-11-06 18:00"

# 下载特定类型的日志，指定时间范围
iflog --direct-download \
  --vin HLX14B175S1996368 \
  --happen-time "2025-11-06 18:00" \
  --log-type log_HUF_Klog \
  --time-range 120

# 从测试环境下载
iflog --direct-download \
  --vin HLX14B175S1996368 \
  --happen-time "2025-11-06 18:00" \
  --env testtwo
```

---

## 支持的日志解析工具

| 工具名称 | 适用文件类型 | 说明 |
|---------|------------|------|
| `lastlog_unpack` | lastlog 文件 | 解析系统 lastlog 日志 |
| `minidump_unpack` | minidump 文件 | 解析系统崩溃转储文件 |
| `clp_decompress` | *.clp, *.clp.zst | 解压 CLP 压缩格式日志 |
| `md_parser_slog` | md_qx_slog2.bin | 解析 modem SLOG 格式日志 |
| `xbllog_unpack` | xbllog 文件 | 解析 XBL bootloader 日志 |
| `logfs_unpack` | logfs 文件 | 解压 logfs 文件系统日志 |
| `ftrace_console_parser` | gvmbootlog, gvmlog | 解析 ftrace 控制台日志 |
| `archive_extractor` | .zip, .tar.gz, .7z | 解压归档文件 |

**自动识别**：工具会根据文件名自动选择合适的解析工具，也可以通过 `-t` 参数手动指定。

---

## 常用参数说明

### 云端下载相关参数

| 参数 | 说明 | 示例 |
|-----|------|------|
| `--vin` | 车辆 VIN 码（必需） | `HLX33B124P1767770` |
| `--happen-time` | 问题发生时间（必需） | `"2025-10-27 18:43"` |
| `--log-type` | 日志类型（默认：log_HUF_Klog） | `log_HUF_kernel` |
| `--time-range` | 时间范围，单位分钟（默认：±60） | `120` |
| `--env` | 环境选择（默认：prod） | `prod`, `testtwo`, `ontest` |
| `--task-type` | 任务类型/Flow ID | `1731484362257596488` |

### 本地处理相关参数

| 参数 | 说明 | 示例 |
|-----|------|------|
| `-u, --upload` | 要处理的文件路径 | `/path/to/log.bin` |
| `-t, --tool` | 指定工具类型（可选） | `lastlog_unpack` |

### 通用参数

| 参数 | 说明 | 默认值 |
|-----|------|--------|
| `--server` | IssueFinder 服务器地址 | `https://issuefinder-playground-init-dev.inner.chj.cloud` |
| `--output` | 输出目录 | `./results` |
| `--timeout` | 超时时间（秒） | `300` |
| `--poll-interval` | 轮询间隔（秒） | `30` |
| `--verbose` | 显示详细输出 | - |
| `--keep-env` | 保留云端环境（不自动清理） | - |
| `--skip-version-check` | 跳过版本检查 | - |

---

## 常用日志类型

### HUF（主机端）日志类型
- `log_HUF_Klog` - 主机 Kernel 日志（默认）
- `log_HUF_kernel` - 主机内核日志
- `log_HUF_8155_android` - 8155 芯片 Android 日志
- `log_HUF_mcu` - MCU 日志

### HUR（其他）日志类型
- `log_HUR_Klog` - HUR Kernel 日志

**提示**：不同日志类型包含的文件数量和类型不同，根据实际需求选择合适的类型。

---

## 支持的时间格式

工具支持以下时间格式输入（会自动转换为标准格式）：

```bash
# ISO 格式
2025-10-27T18:43

# 空格分隔（需要引号）
"2025-10-27 18:43"
"2025-10-27 18:43:00"

# 斜杠分隔（需要引号）
"2025/10/27 18:43"
"2025/10/27 18:43:00"
```

---

## 使用示例

### 示例 1: 快速分析车辆故障

```bash
# 自动下载日志并分析重启原因
issuefinder-tool.py --issuefinder \
  --vin HLX33B124P1767770 \
  --happen-time "2025-10-27 18:43"
```

**输出**：
- 分析结果：重启原因、最终结论
- 下载的日志文件
- 保存位置：`./results/`

---

### 示例 2: 下载指定时间范围的所有日志

```bash
# 下载前后 2 小时的日志
issuefinder-tool.py --direct-download \
  --vin HLX14B175S1996368 \
  --happen-time "2025-11-06 18:00" \
  --time-range 120 \
  --output ./my_logs
```

---

### 示例 3: 处理本地压缩包中的日志

```bash
# 自动解压并识别处理所有日志文件
issuefinder-tool.py -u /path/to/vehicle_logs.zip --verbose

# 指定特定工具处理
issuefinder-tool.py -t lastlog_unpack -u /path/to/logs.tar.gz
```

---

### 示例 5: 批量处理多个文件

```bash
# 处理目录中的所有日志文件（通过脚本循环）
for file in /path/to/logs/*; do
  issuefinder-tool.py -u "$file" --output ./results/$(basename "$file")
done
```

---

## 高级功能

### 自动版本更新

工具会自动检查服务器版本并更新到最新版本：
- 更新文件保存在：`~/.issuefinder/issuefinder-tool.py`
- 可使用 `--skip-version-check` 跳过版本检查

### 环境管理

- **自动清理**：默认完成后自动删除云端环境
- **保留环境**：使用 `--keep-env` 参数保留环境供后续使用
- **环境 ID**：工具会输出环境 ID，可用于调试

---

## 故障排查

### 常见问题

**1. 找不到文件或无法识别类型**
```bash
# 使用 -t 参数手动指定工具类型
issuefinder-tool.py -t lastlog_unpack -u /path/to/file
```

**2. 云端下载失败**
```bash
# 使用 --verbose 查看详细错误信息
issuefinder-tool.py --direct-download --vin XXX --happen-time "..." --verbose
```

**3. 环境清理失败**
- 环境会在 1 小时不活动后自动清理
- 使用 `--keep-env` 可以保留环境供后续使用

**4. 连接超时**
```bash
# 增加超时时间
issuefinder-tool.py -u file --timeout 600
```

---

## 最佳实践

1. **使用直接下载模式**：如果只需要日志文件，使用 `--direct-download` 比 `--cloud-log` 更快
2. **合理设置时间范围**：默认 ±60 分钟通常足够，特殊情况可扩大到 ±120 分钟
3. **启用详细输出**：调试时使用 `--verbose` 查看详细信息
4. **指定输出目录**：使用 `--output` 将不同任务的日志分开存储
5. **批量处理**：结合 Shell 脚本实现批量下载和处理

---

## 相关资源

- **服务器地址**：`https://issuefinder-playground-init-dev.inner.chj.cloud`
- **工具位置**：`.siada-cli/skills/issuefinder-tool/scripts/`
  - `issuefinder-tool.py` - 原始工具（从云端同步）
  - `issuefinder-tool-wrapper.py` - 包装脚本（推荐）
  - `iflog` - 便捷命令（推荐）
- **默认输出目录**：
  - 原始工具：`./results/`
  - 包装脚本：`$ISSUEFINDER_LOGS_PATH/YYYY/MM/DD/` (已配置为 `/home/lixiang/work/sdata/iss-log/`)
- **更新位置**：`~/.issuefinder/issuefinder-tool.py`
- **包装脚本文档**：[WRAPPER_USAGE.md](./WRAPPER_USAGE.md)

---

## 获取帮助

```bash
# 查看完整帮助信息
issuefinder-tool.py -h

# 查看版本信息
issuefinder-tool.py --version
```

---

**最后更新**：2026-02-28  
