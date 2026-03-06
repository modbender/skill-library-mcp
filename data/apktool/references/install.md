# Apktool 安装指南

📦 **完整安装步骤和配置说明**

---

## 🎯 概述

Apktool 是一个用于反向工程 Android APK 文件的工具。它需要 Java 运行时环境。

### 系统要求

- Java 8 或更高版本
- 50MB 可用磁盘空间
- Linux / macOS / Windows

---

## 📋 安装方法

### 方法一：包管理器安装（推荐 ⭐）

#### Debian/Ubuntu

```bash
# 安装 Java（如未安装）
sudo apt-get update
sudo apt-get install -y openjdk-11-jdk

# 安装 Apktool
sudo apt-get install -y apktool

# 验证安装
apktool --version
```

#### Arch Linux

```bash
sudo pacman -S apktool
```

#### macOS (Homebrew)

```bash
# 安装 Java
brew install openjdk

# 安装 Apktool
brew install apktool

# 验证安装
apktool --version
```

---

### 方法二：手动安装（最新稳定版）

#### 步骤 1：下载 Apktool

```bash
# 创建安装目录
sudo mkdir -p /opt/apktool
cd /opt/apktool

# 下载最新版本的 wrapper 脚本和 jar 文件
# 从官方 GitHub releases 获取
sudo wget -O apktool.jar https://github.com/iBotPeaches/Apktool/releases/download/v3.0.1/apktool_3.0.1.jar
sudo wget -O apktool https://github.com/iBotPeaches/Apktool/releases/download/v3.0.1/apktool_3.0.1
```

#### 步骤 2：设置执行权限

```bash
sudo chmod +x /opt/apktool/apktool
```

#### 步骤 3：创建符号链接

```bash
# 添加到系统路径
sudo ln -sf /opt/apktool/apktool /usr/local/bin/apktool

# 验证
which apktool
apktool --version
```

---

### 方法三：使用脚本自动安装

```bash
#!/bin/bash
# install-apktool.sh

set -e

INSTALL_DIR="/opt/apktool"
APKTOOL_VERSION="3.0.1"

echo "🔧 开始安装 Apktool ${APKTOOL_VERSION}..."

# 检查 Java
if ! command -v java &> /dev/null; then
    echo "❌ Java 未安装，请先安装 Java"
    exit 1
fi

# 创建目录
sudo mkdir -p ${INSTALL_DIR}
cd ${INSTALL_DIR}

# 下载文件
echo "📥 下载 Apktool..."
sudo wget -q --show-progress -O apktool.jar \
    https://github.com/iBotPeaches/Apktool/releases/download/v${APKTOOL_VERSION}/apktool_${APKTOOL_VERSION}.jar
sudo wget -q --show-progress -O apktool \
    https://github.com/iBotPeaches/Apktool/releases/download/v${APKTOOL_VERSION}/apktool_${APKTOOL_VERSION}

# 设置权限
sudo chmod +x apktool

# 创建链接
sudo ln -sf ${INSTALL_DIR}/apktool /usr/local/bin/apktool

echo "✅ Apktool 安装完成！"
apktool --version
```

保存为 `install-apktool.sh`，然后运行：

```bash
chmod +x install-apktool.sh
sudo ./install-apktool.sh
```

---

## 🔍 验证安装

### 检查版本

```bash
apktool --version
```

预期输出：`3.0.1`（或安装的版本）

### 测试基本功能

```bash
# 创建一个测试目录
mkdir -p /tmp/apktool-test

# 查看帮助
apktool --help

# 应该显示使用说明
```

---

## ⚙️ 配置（可选）

### 设置框架目录

Apktool 需要框架文件来解码某些 APK：

```bash
# 查看框架目录
apktool --framework

# 默认框架目录：~/.local/share/apktool/framework
```

### 设置 Java 内存限制

对于大型 APK，可能需要增加 Java 堆内存：

```bash
# 编辑 wrapper 脚本（如果手动安装）
sudo nano /opt/apktool/apktool

# 找到 java 命令行，添加内存参数：
java -Xmx1024M -jar /opt/apktool/apktool.jar "$@"
```

---

## 🐛 常见问题

### 问题 1：`command not found: apktool`

**原因**: Apktool 未添加到 PATH

**解决方案**:

```bash
# 检查安装位置
which apktool

# 如果返回空，创建符号链接
sudo ln -sf /opt/apktool/apktool /usr/local/bin/apktool
```

### 问题 2：`Error: Unable to access jarfile`

**原因**: jar 文件路径不正确或权限问题

**解决方案**:

```bash
# 检查 jar 文件是否存在
ls -la /opt/apktool/apktool.jar

# 重新下载
sudo wget -O /opt/apktool/apktool.jar \
    https://github.com/iBotPeaches/Apktool/releases/download/v3.0.1/apktool_3.0.1.jar
```

### 问题 3：Java 版本不兼容

**原因**: 需要 Java 8 或更高版本

**解决方案**:

```bash
# 检查 Java 版本
java -version

# 如版本过低，升级 Java
sudo apt-get install -y openjdk-11-jdk  # Debian/Ubuntu
brew install openjdk                    # macOS
```

### 问题 4：反编译失败 "Unsupported class file major version"

**原因**: Java 版本与 APK 编译版本不匹配

**解决方案**:

```bash
# 尝试使用不同 Java 版本
sudo update-alternatives --config java

# 或使用更高版本 Java
sudo apt-get install -y openjdk-17-jdk
```

---

## 📚 相关资源

- **官方网站**: https://apktool.org
- **GitHub**: https://github.com/iBotPeaches/Apktool
- **文档**: https://apktool.org/docs
- **Issue 追踪**: https://github.com/iBotPeaches/Apktool/issues

---

## 🔗 下一步

安装完成后，返回 [`../SKILL.md`](../SKILL.md) 查看使用指南。

---

**最后更新**: 2026-02-28
