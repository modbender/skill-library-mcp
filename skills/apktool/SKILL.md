---
name: apktool
description: 反向工程 Android APK 文件的命令行工具
homepage: https://apktool.org
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["apktool", "java", "jadx"] },
        "install":
          [
            {
              "id": "apt",
              "kind": "apt",
              "package": "apktool",
              "label": "安装 Apktool (Debian/Ubuntu)",
              "platforms": ["linux-debian", "linux-ubuntu"],
            },
            {
              "id": "brew",
              "kind": "brew",
              "package": "apktool",
              "label": "安装 Apktool (macOS Homebrew)",
              "platforms": ["macos"],
            },
            {
              "id": "jadx",
              "kind": "manual",
              "package": "jadx",
              "label": "安装 JADX (Android dex 反编译器)",
              "script": "cd /tmp && curl -L -o jadx.zip https://github.com/skylot/jadx/releases/download/v1.5.0/jadx-1.5.0.zip && unzip -o jadx.zip && mkdir -p /opt/jadx && cp -r lib /opt/jadx/ && cp bin/jadx /opt/jadx/ && sed -i 's|APP_HOME=\".*\"|APP_HOME=\"/opt/jadx\"|g' /opt/jadx/jadx && ln -sf /opt/jadx/jadx /usr/local/bin/jadx",
            },
          ],
      },
  }
---

# Apktool 技能

🔧 **反向工程 Android APK 文件的命令行工具**

---

## 📦 依赖声明

### 必需二进制文件

- `apktool` - Android APK 反向工程工具
- `java` - Java 运行时（Apktool 基于 Java）

### 检查依赖

```bash
# 检查 apktool 是否已安装
which apktool
apktool --version

# 检查 Java 是否已安装
java -version
```

### 安装指引

如未安装，请阅读 [`references/install.md`](./references/install.md) 获取详细安装步骤。

---

## 🎯 核心功能

- **反编译（Disassemble）** - 将 APK 解码为近乎原始形式（smali 代码、资源文件）
- **编译（Assemble）** - 将修改后的代码和资源重新打包为 APK
- **分析（Analyze）** - 快速检查资源清单和配置文件，无需重建

---

## 🚀 快速开始

### 反编译 APK

```bash
# 基本反编译
apktool d app.apk

# 指定输出目录
apktool d app.apk -o output_folder

# 仅分析不生成文件（-m 模式）
apktool d app.apk -m
```

### 重新编译 APK

```bash
# 编译反编译后的文件夹
apktool b app_folder

# 指定输出 APK 路径
apktool b app_folder -o modified_app.apk
```

### 典型工作流

```bash
# 1. 反编译
apktool d target.apk -o target_decompiled

# 2. 修改资源或代码
# 编辑 target_decompiled/ 中的文件

# 3. 重新编译
apktool b target_decompiled -o target_modified.apk

# 4. 签名 APK（需要额外工具）
# apksigner 或 jarsigner
```

---

## 📚 详细文档

| 主题 | 文档 |
|------|------|
| 🔧 安装指南 | [`references/install.md`](./references/install.md) |
| 📖 完整用法 | [`references/usage.md`](./references/usage.md) |
| 🛠️ 常见问题 | [`references/troubleshooting.md`](./references/troubleshooting.md) |

---

## 🔐 安全提示

- **合法使用** - 仅对您拥有权限的 APK 进行反向工程
- **学习研究** - 适用于安全研究、应用分析、本地化翻译等合法用途
- **遵守法律** - 请勿用于侵犯版权或绕过软件保护

---

## 🤝 使用示例

### 示例 1：查看 APK 结构

```bash
# 快速分析 APK 结构（不生成文件）
apktool d app.apk -m

# 查看 AndroidManifest.xml
cat apktool.yml
```

### 示例 2：修改应用资源

```bash
# 反编译
apktool d myapp.apk

# 修改 res/values/strings.xml 进行本地化
# 编辑文件...

# 重新编译
apktool b myapp -o myapp_localized.apk
```

### 示例 3：分析权限配置

```bash
# 反编译并查看 AndroidManifest.xml
apktool d target.apk -m
cat target/AndroidManifest.xml | grep permission
```

---

## 💡 提示

- 反编译后的代码为 **smali** 格式（Android 的汇编语言）
- 如需 Java 源代码，可配合 **jadx** 工具使用
- 修改后的 APK 需要**重新签名**才能安装到设备
- 大型 APK 反编译可能需要数分钟

---

**版本**: 0.0.2  
**最后更新**: 2026-02-28
