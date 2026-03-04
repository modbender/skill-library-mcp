---
name: esp-idf-helper
description: Help develop, build, flash, and debug ESP32/ESP8266 firmware using Espressif ESP-IDF on Linux/WSL. Use when the user asks about ESP-IDF project setup, configuring targets, menuconfig, building, flashing via esptool/idf.py, serial monitor, partition tables, sdkconfig, troubleshooting build/flash/monitor errors, or automating common idf.py workflows from the command line.
---

# esp-idf-helper

## Goal
Provide a repeatable, command-line-first workflow for ESP-IDF development on Linux/WSL: configure → build → flash → monitor → debug/troubleshoot.

## Quick start (typical loop)

### Method 1: Activate ESP-IDF first (Recommended)
```bash
# 1) Source the ESP-IDF environment (once per terminal session)
cd /path/to/esp-idf
. ./export.sh

# 1.1) Enable ccache to speed up compilation (recommended)
export IDF_CCACHE_ENABLE=1

# 2) Go to your project and build
cd /path/to/your/project
idf.py set-target <target>    # Set target chip (once per project)
idf.py build                 # Compile
idf.py -p <PORT> -b <BAUD> flash  # Flash to device (optional)
```

### Common commands
- `idf.py set-target <target>` — Set chip target: esp32, esp32s2, esp32s3, esp32c3, esp32p4
- `idf.py menuconfig` — Configure project settings (**must run in a new terminal window**)
- `idf.py build` — Build the project
- `idf.py update-dependencies` — Update project component dependencies
- `idf.py partition-table` — Build partition table and print partition entries
- `idf.py partition-table-flash` — Flash partition table to device
- `idf.py storage-flash` — Flash storage filesystem partition
- `idf.py size` — Show firmware size information
- `idf.py -p <PORT> -b <BAUD> flash` — Flash firmware (default baud: 1152000)
- `idf.py -p <PORT> monitor` — Open serial monitor
- `idf.py -p <PORT> -b <BAUD> monitor` — Open serial monitor with specific baud (e.g. 1152000)
- `idf.py -p <PORT> -b <BAUD> flash monitor` — Flash then monitor
- `bash {baseDir}/scripts/monitor_auto_attach.sh --project <PROJECT_DIR> --idf <IDF_DIR> --port <PORT> --baud <BAUD>` — Auto attach serial (usbipd) and retry monitor on open failure
- `bash {baseDir}/scripts/flash_with_progress.sh --project <PROJECT_DIR> --idf <IDF_DIR> --port <PORT> --mode <MODE>` — Flash with real-time progress output (supports auto usbipd attach retry, error summary, and second retry)

#### flash_with_progress 使用示例

```bash
# 普通烧录整个固件（带进度）
bash {baseDir}/scripts/flash_with_progress.sh \
  --project <PROJECT_DIR> \
  --idf <IDF_DIR> \
  --port <PORT> \
  --mode flash

# 加密烧录 app（带进度）
bash {baseDir}/scripts/flash_with_progress.sh \
  --project <PROJECT_DIR> \
  --idf <IDF_DIR> \
  --port <PORT> \
  --mode encrypted-app-flash

# 仅烧录分区表（带进度）
bash {baseDir}/scripts/flash_with_progress.sh \
  --project <PROJECT_DIR> \
  --idf <IDF_DIR> \
  --port <PORT> \
  --mode partition-table-flash

# 仅烧录文件系统分区（storage，带进度）
bash {baseDir}/scripts/flash_with_progress.sh \
  --project <PROJECT_DIR> \
  --idf <IDF_DIR> \
  --port <PORT> \
  --mode storage-flash

# 指定波特率并关闭自动串口映射重试
bash {baseDir}/scripts/flash_with_progress.sh \
  --project <PROJECT_DIR> \
  --idf <IDF_DIR> \
  --port <PORT> \
  --baud 460800 \
  --mode flash \
  --no-auto-attach

# 串口异常时自动二次重试（默认 retries=2，也可手动指定）
bash {baseDir}/scripts/flash_with_progress.sh \
  --project <PROJECT_DIR> \
  --idf <IDF_DIR> \
  --port <PORT> \
  --mode encrypted-app-flash \
  --retries 2
```
- `idf.py fullclean` — Clean build directory

### 在新窗口打开 monitor（Windows + WSL2）

推荐用脚本方式，避免 PowerShell/cmd 引号和 UNC 路径问题。

### 在新窗口打开 menuconfig（必须）

`menuconfig` 是 TUI 交互界面，必须在新窗口打开（不要在非交互后台中运行）。

1) 在 WSL 直接运行（你已在独立终端时）：

```bash
bash {baseDir}/scripts/run_menuconfig.sh \
  --project <PROJECT_DIR> \
  --idf <IDF_DIR>
```

2) 从 Windows PowerShell 拉起新窗口运行：

```powershell
Start-Process powershell -ArgumentList '-NoExit','-Command','wsl.exe -d <DISTRO> --cd / -- bash {baseDir}/scripts/run_menuconfig.sh --project <PROJECT_DIR> --idf <IDF_DIR>'
```

### 打开串口失败时自动映射并重试

当 `idf.py monitor` 因串口打开失败（端口不存在/被占用）报错时，可自动执行 usbipd 串口映射脚本并重试一次：

```bash
bash {baseDir}/scripts/monitor_auto_attach.sh \
  --project <PROJECT_DIR> \
  --idf <IDF_DIR> \
  --port <PORT> \
  --baud <BAUD> \
  --keyword "ESP32"
```


1) 在 WSL 创建启动脚本：

```bash
cat >/tmp/run_monitor.sh <<'EOF'
#!/usr/bin/env bash
set -e
cd /path/to/your/project
source /path/to/esp-idf/export.sh
exec idf.py -p <PORT> -b 1152000 monitor
EOF
chmod +x /tmp/run_monitor.sh
```

2) 在 Windows PowerShell 新开窗口执行：

```powershell
Start-Process cmd.exe -WorkingDirectory C:\ -ArgumentList '/k','wsl.exe -d <DISTRO> -- bash /tmp/run_monitor.sh'
```

说明：
- 使用 `cmd.exe -WorkingDirectory C:\` 可以避免 `\\wsl.localhost\...` UNC 路径导致工作目录掉到 `C:\Windows`。
- 退出 monitor：`Ctrl+]`。

## Workflow decision tree
- If the user has **no project yet** → create from example/template; confirm target chip and IDF version.
- If **build fails** → collect the *first* error lines; identify missing deps/toolchain/cmake/python packages; confirm IDF env.
- If **flash fails** → confirm PORT permissions/WSL USB passthrough, baud rate, boot mode, correct chip target.
- If **monitor is gibberish** → wrong baud (monitor uses app baud), wrong serial adapter settings, or wrong console encoding.
- If **boot loop / panic** → request panic backtrace; decode with `addr2line` (or `idf.py monitor` built-in) and check partition/sdkconfig.
- If **`[Errno 11] Could not exclusively lock port <PORT>`** → serial port is occupied by another process; force release it with:
  ```bash
  sudo fuser -k <PORT>
  ```

## What to ask the user for (minimal)
1) Chip target: e.g. `esp32`, `esp32s2`, `esp32s3`, `esp32c3`, `esp32p4`.
2) ESP-IDF version + how it’s installed/activated (IDF Tools installer vs git clone; `IDF_PATH` / `ESPIDF_ROOT`).
3) Project path + whether it’s an ESP-IDF project (has `CMakeLists.txt`, `main/`, `sdkconfig`).
4) Serial port path: use `<PORT>` (e.g. `/dev/ttyUSB0`, `/dev/ttyACM*`, or WSL mapped `/dev/ttyS*`).
5) Exact failing command + the *first* error block in output.

## 串口设备获取（Windows + WSL2）

先在 Windows PowerShell 找到串口号，再在 WSL2 里映射 USB 设备。

### 安装 usbipd-win（Windows，推荐）

在 **管理员模式** PowerShell 中执行：

```powershell
winget install dorssel.usbipd-win
```

然后查看并映射设备：

```powershell
# Windows PowerShell：查看 USB 设备与 BUSID
usbipd list

# 将设备挂载到 WSL（每次重新插拔 USB 后都要重新执行）
usbipd attach --wsl --busid=<BUSID>
```

### 串口自动映射（推荐）

可直接使用脚本自动选择并挂载串口设备（优先选择 Connected 区域中的 serial 设备，且优先 STATE=Shared）：

```bash
bash {baseDir}/scripts/usbipd_attach_serial.sh
```

常用参数：

```bash
# 指定 BUSID
bash {baseDir}/scripts/usbipd_attach_serial.sh --busid <BUSID>

# 指定发行版
bash {baseDir}/scripts/usbipd_attach_serial.sh --distro <DISTRO>

# 按关键词筛选设备（如 ESP32 / COMxx / CP210x）
bash {baseDir}/scripts/usbipd_attach_serial.sh --keyword "ESP32"

# 仅预览，不执行
bash {baseDir}/scripts/usbipd_attach_serial.sh --dry-run
```

说明：
- 每次 USB 设备重新插拔后，`BUSID` 可能变化，需要重新 `usbipd list` 或重新运行自动映射脚本。
- 重新插拔 USB 后，通常都要再执行一次 `usbipd attach --wsl --busid=<BUSID>`（脚本会自动执行）。
- 在 WSL2 内可用 `ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null` 确认串口节点。

### 首次需要手动加载内核模块（WSL 2.3.11+）

在较新的 WSL 版本中，内核采用模块化设计，`vhci_hcd`（虚拟主机控制器接口）驱动可能不会自动加载。

在 WSL 终端执行：

```bash
sudo modprobe vhci_hcd
```

## New Feature: Create ESP-IDF Projects
- **Description**: Create a new ESP-IDF project or create a project from an example in the ESP Component Registry.
- **Usage**:
  ```bash
  idf.py create-project <project_name> <project_path>
  idf.py create-project-from-example <example_name> <project_path>
  ```

## Flash Encryption Support (加密烧录)

直接使用 `idf.py` 执行加密/非加密应用烧录：

```bash
# 加密烧录整个固件 (bootloader + partition table + app)
idf.py -p <PORT> encrypted-flash

# 加密烧录 app 分区
idf.py -p <PORT> encrypted-app-flash

# 非加密烧录 app 分区
idf.py -p <PORT> app-flash

# 非加密烧录整个固件 (bootloader + partition table + app)
idf.py -p <PORT> flash
```


## Bundled resources
### references/
- `references/esp-idf-cli.md` — concise command patterns + what to paste back when reporting errors.
- `references/idf-py-help.txt` — captured `idf.py --help` output for quick lookup/search.

To refresh the help text for your installed ESP-IDF version, run:
- `scripts/capture_idf_help.sh`

### assets/
Not used by default.