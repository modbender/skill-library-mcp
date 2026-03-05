# 🦙 Ollama Updater - 带断点续传的 Ollama 安装工具

**版本**: 1.0.0  
**创建日期**: 2026-02-20  
**适用系统**: Linux, macOS

---

## 🎯 解决的问题

官方 Ollama 安装脚本在网络不稳定时下载会中断，需要从头开始下载：

```bash
# 官方脚本 - 下载中断后需要重新开始
$ curl -fsSL https://ollama.com/install.sh | sh
>>> Downloading ollama-linux-amd64.tar.zst
###################### 31.1%
curl: (92) HTTP/2 stream 1 was not closed cleanly: PROTOCOL_ERROR
tar: Unexpected EOF in archive  # ❌ 下载失败，前功尽弃
```

**ollama-updater** 通过断点续传功能解决这个问题：

```bash
# ollama-updater - 下载中断后可以继续
$ ollama-updater
>>> Downloading (attempt 1/3)...
###################### 31.1%
curl: (92) ...  # 网络错误
>>> Download interrupted. Partial file saved, will resume...
>>> Waiting 5 seconds before retry...
>>> Downloading (attempt 2/3)...
########################### 100.0%  # ✅ 从断点继续，成功完成
```

---

## ✨ 主要功能

### 1. 断点续传

使用 `curl -C -` 参数实现断点续传：

```bash
# 第一次下载（中断）
$ ollama-updater
>>> Downloading...
###################### 31.1%
# 网络中断...

# 重新运行（从 31.1% 继续）
$ ollama-updater
>>> Downloading (attempt 2/3)...
###################### 31.1% → 100.0%  # ✅ 继续下载
```

### 2. 自动重试

下载失败自动重试 3 次，每次间隔 5 秒：

```
Attempt 1/3: Failed (网络错误)
Waiting 5 seconds...
Attempt 2/3: Failed (连接超时)
Waiting 5 seconds...
Attempt 3/3: Success! ✅
```

### 3. 进度显示

实时显示下载进度和速度：

```
>>> Downloading ollama-linux-amd64.tar.zst
  256.00 MiB / 350.00 MiB [━━━━━━━━━━━━━━━━━━━━━━━━━━━╸━━━━] 73.14% 12.50 MiB/s
```

### 4. 完整功能

保留官方脚本所有功能：

- ✅ GPU 自动检测（NVIDIA/AMD）
- ✅ systemd 服务配置
- ✅ 多架构支持（x86_64, aarch64）
- ✅ macOS 支持
- ✅ WSL2 支持

---

## 🚀 快速开始

### 方法 1: 使用 OpenClaw（推荐）

```bash
# 安装技能
openclaw skills install ollama-updater

# 运行
ollama-updater
```

### 方法 2: 直接运行脚本

```bash
# 下载脚本
curl -fsSL https://raw.githubusercontent.com/openclaw/skills/main/ollama-updater/ollama-install.sh -o ollama-install.sh

# 添加执行权限
chmod +x ollama-install.sh

# 运行
sudo ./ollama-install.sh
```

### 方法 3: 使用 ClawHub

```bash
# 安装
clawhub install ollama-updater

# 运行
ollama-updater
```

---

## 📋 使用说明

### 基本用法

```bash
# 安装/更新到最新版本
ollama-updater
```

### 指定版本

```bash
# 安装特定版本
OLLAMA_VERSION=0.5.7 ollama-updater
```

### 手动运行

```bash
# 使用 sudo 运行
sudo bash /path/to/ollama-install.sh
```

---

## 🔧 故障排查

### 问题 1: 下载总是中断

**症状**:
```
curl: (92) HTTP/2 stream 1 was not closed cleanly: PROTOCOL_ERROR
```

**解决**:
1. 多次运行脚本，会自动从断点续传
2. 检查网络连接
3. 使用有线网络代替 WiFi

### 问题 2: 提示 zstd 错误

**症状**:
```
This version requires zstd for extraction. Please install zstd
```

**解决**:
```bash
# Debian/Ubuntu
sudo apt-get install zstd

# RHEL/CentOS/Fedora
sudo dnf install zstd

# Arch
sudo pacman -S zstd
```

### 问题 3: 权限错误

**症状**:
```
sudo: a terminal is required to read the password
```

**解决**:
```bash
# 先验证 sudo 权限
sudo -v

# 然后运行
sudo ollama-updater
```

### 问题 4: 下载速度慢

**解决**:
1. 使用国内镜像（如有）
2. 避开网络高峰期
3. 使用下载工具先下载到本地，然后手动安装

---

## 📊 与官方脚本对比

| 功能 | 官方脚本 | ollama-updater |
|------|---------|----------------|
| 断点续传 | ❌ | ✅ `curl -C -` |
| 自动重试 | ❌ | ✅ (3 次) |
| 进度显示 | ✅ | ✅ |
| GPU 检测 | ✅ | ✅ |
| systemd 配置 | ✅ | ✅ |
| macOS 支持 | ✅ | ✅ |
| WSL2 支持 | ✅ | ✅ |

---

## 🛠️ 技术细节

### 断点续传实现

```bash
download_file() {
    local url="$1"
    local output="$2"
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        retry_count=$((retry_count + 1))
        status "Downloading (attempt $retry_count/$max_retries)..."
        
        # 关键：使用 -C - 实现断点续传
        if curl --fail --show-error --location --progress-bar -C - -o "$output" "$url"; then
            return 0
        fi
        
        # 检查是否有部分文件
        if [ -f "$output" ] && [ -s "$output" ]; then
            status "Download interrupted. Partial file saved, will resume..."
        fi
        
        if [ $retry_count -lt $max_retries ]; then
            status "Waiting 5 seconds before retry..."
            sleep 5
        fi
    done
    
    error "Download failed after $max_retries attempts"
}
```

### 关键参数说明

| 参数 | 说明 |
|------|------|
| `-C -` | 断点续传（从上次中断处继续） |
| `--fail` | HTTP 错误时失败（不输出 HTML） |
| `--show-error` | 显示错误信息 |
| `--location` | 跟随重定向 |
| `--progress-bar` | 显示进度条 |

---

## 📦 文件结构

```
ollama-updater/
├── main.py              # OpenClaw 技能入口
├── ollama-install.sh    # 改进的安装脚本（17KB）
├── SKILL.md             # 技能说明
├── README.md            # 本文件
├── package.json         # 包信息
└── TEST-REPORT.md       # 测试报告
```

---

## 🧪 测试报告

### 测试环境

- **系统**: Ubuntu 24.04 LTS
- **架构**: x86_64
- **网络**: WiFi (不稳定)

### 测试结果

| 测试项 | 官方脚本 | ollama-updater |
|--------|---------|----------------|
| 正常网络 | ✅ 成功 | ✅ 成功 |
| 网络中断（30%） | ❌ 失败 | ✅ 续传成功 |
| 网络中断（70%） | ❌ 失败 | ✅ 续传成功 |
| 完全断网 | ❌ 失败 | ✅ 重试 3 次后失败 |
| 平均下载时间 | 2 分钟 | 2-5 分钟（含重试） |

### 结论

- ✅ 断点续传功能正常工作
- ✅ 自动重试机制有效
- ✅ 在网络不稳定环境下明显优于官方脚本

---

## 📝 更新日志

### v1.0.0 (2026-02-20)

- ✅ 初始版本
- ✅ 添加断点续传功能
- ✅ 添加自动重试机制（3 次）
- ✅ 保留官方脚本所有功能
- ✅ 添加详细文档

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

- **Bug 报告**: https://github.com/openclaw/skills/issues
- **功能建议**: https://github.com/openclaw/skills/discussions

---

## 📄 许可证

MIT License

---

## 🔗 相关链接

- **Ollama 官网**: https://ollama.com
- **官方安装脚本**: https://ollama.com/install.sh
- **ClawHub 页面**: https://clawhub.com/skills/ollama-updater
- **GitHub**: https://github.com/openclaw/skills/tree/main/ollama-updater

---

**祝你安装顺利！🦙**
