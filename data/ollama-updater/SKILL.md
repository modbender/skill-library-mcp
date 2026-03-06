---
name: ollama-updater
description: 带断点续传功能的 Ollama 安装/更新工具，解决网络不稳定导致的下载中断问题。
---

# ollama-updater

带断点续传功能的 Ollama 安装/更新工具，解决网络不稳定导致的下载中断问题。

## 功能

- ✅ **断点续传**: 使用 `curl -C -` 实现下载中断后继续下载
- ✅ **自动重试**: 下载失败自动重试 3 次
- ✅ **进度显示**: 实时显示下载进度
- ✅ **智能清理**: 自动清理旧版本
- ✅ **GPU 支持**: 自动检测并安装 NVIDIA/AMD GPU 驱动

## 安装

```bash
# 使用 OpenClaw
openclaw skills install ollama-updater

# 或使用 ClawHub
clawhub install ollama-updater
```

## 使用方法

### 基本用法

```bash
ollama-updater
```

### 指定版本

```bash
OLLAMA_VERSION=0.5.7 ollama-updater
```

### 手动运行

```bash
# 直接运行脚本
bash /path/to/ollama-updater/main.py

# 或使用 sudo
sudo bash /path/to/ollama-updater/main.py
```

## 断点续传原理

使用 curl 的 `-C -` 参数实现断点续传：

```bash
# 普通下载（中断后需要从头开始）
curl -O https://example.com/file.tar.gz

# 断点续传（中断后可以继续）
curl -C - -O https://example.com/file.tar.gz
```

如果下载中断，只需重新运行命令，curl 会自动从断点处继续下载。

## 故障排查

### 下载总是中断

**原因**: 网络不稳定或服务器限速

**解决**:
1. 多次运行脚本，会自动从断点续传
2. 使用国内镜像（如有）
3. 检查网络连接

### 提示 zstd 错误

**原因**: 需要 zstd 解压工具

**解决**:
```bash
# Debian/Ubuntu
sudo apt-get install zstd

# RHEL/CentOS/Fedora
sudo dnf install zstd

# Arch
sudo pacman -S zstd
```

### 权限错误

**原因**: 需要 sudo 权限

**解决**:
```bash
sudo ollama-updater
```

## 与官方脚本的区别

| 功能 | 官方脚本 | ollama-updater |
|------|---------|----------------|
| 断点续传 | ❌ | ✅ |
| 自动重试 | ❌ | ✅ (3 次) |
| 进度显示 | ✅ | ✅ |
| GPU 检测 | ✅ | ✅ |
| systemd 配置 | ✅ | ✅ |

## 技术细节

### 断点续传实现

```bash
download_file() {
    local url="$1"
    local output="$2"
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        retry_count=$((retry_count + 1))
        
        # 使用 -C - 实现断点续传
        if curl --fail --show-error --location --progress-bar -C - -o "$output" "$url"; then
            return 0
        fi
        
        if [ $retry_count -lt $max_retries ]; then
            sleep 5
        fi
    done
    
    error "Download failed after $max_retries attempts"
}
```

### 下载流程

1. 检查是否需要断点续传（已有部分文件）
2. 使用 `curl -C -` 继续下载
3. 下载失败自动重试（最多 3 次）
4. 下载成功后验证并解压

## 系统要求

- Linux (x86_64, aarch64)
- macOS (x86_64, aarch64)
- curl (必需)
- zstd (新版 Ollama 需要)
- sudo (系统级安装需要)

## 文件结构

```
ollama-updater/
├── main.py              # 主程序（包装官方脚本）
├── ollama-install.sh    # 改进的安装脚本
├── SKILL.md             # 技能说明
├── README.md            # 使用指南
└── package.json         # 包信息
```

## 版本历史

### v1.0.0 (2026-02-20)

- 初始版本
- 添加断点续传功能
- 添加自动重试机制
- 保留官方脚本所有功能

## 许可证

MIT License

## 支持

如有问题，请提交到：https://github.com/openclaw/skills/issues
