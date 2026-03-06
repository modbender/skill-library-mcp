# Apktool 使用指南

📖 **详细使用说明和命令参考**

---

## 🎯 命令概览

Apktool 有两个主要操作模式：

| 命令 | 简写 | 功能 |
|------|------|------|
| `decode` | `d` | 反编译 APK 文件 |
| `build` | `b` | 重新编译 APK |
| `install-framework` | `if` | 安装框架文件 |
| `empty-framework-dir` | `efd` | 清空框架目录 |

---

## 📥 反编译 APK (decode)

### 基本语法

```bash
apktool d [选项] <file.apk> [输出目录]
```

### 常用选项

| 选项 | 说明 |
|------|------|
| `-o <dir>` | 指定输出目录 |
| `-f` | 强制覆盖已存在的目录 |
| `-s` | 只解码 resources.arsc，不解码 dex 文件 |
| `-d` | 解码时包含调试信息 |
| `-k` | 保留原始签名文件 |
| `-m` | 仅分析模式，不生成文件 |
| `-r` | 不使用资源解码（快速模式） |
| `--no-src` | 不反编译源代码 |
| `--only-main-classes` | 仅反编译主 classes.dex |

### 使用示例

#### 示例 1：基本反编译

```bash
apktool d myapp.apk
# 输出到 myapp/ 目录
```

#### 示例 2：指定输出目录

```bash
apktool d myapp.apk -o output_folder
# 输出到 output_folder/ 目录
```

#### 示例 3：强制覆盖

```bash
apktool d myapp.apk -f
# 如果 output_folder 已存在则覆盖
```

#### 示例 4：快速分析（不生成文件）

```bash
apktool d myapp.apk -m
# 仅生成 apktool.yml 和 AndroidManifest.xml
```

#### 示例 5：不解码 dex 文件

```bash
apktool d myapp.apk -s
# 保留 classes.dex 不反编译，仅解码资源
```

#### 示例 6：仅反编译资源

```bash
apktool d myapp.apk --no-src
# 不解码代码，仅解码资源文件
```

---

## 📤 重新编译 APK (build)

### 基本语法

```bash
apktool b [选项] <文件夹> [输出 APK]
```

### 常用选项

| 选项 | 说明 |
|------|------|
| `-o <file>` | 指定输出 APK 路径 |
| `-f` | 强制覆盖已存在的 APK |
| `-c` | 使用压缩资源 |
| `-d` | 包含调试信息 |
| `-a` | 使用 aapt2（替代 aapt） |
| `--force-manifest` | 强制重新编译 AndroidManifest.xml |

### 使用示例

#### 示例 1：基本编译

```bash
apktool b myapp/
# 输出到 myapp/dist/myapp.apk
```

#### 示例 2：指定输出路径

```bash
apktool b myapp/ -o modified.apk
# 输出到 modified.apk
```

#### 示例 3：强制覆盖

```bash
apktool b myapp/ -o modified.apk -f
# 如果 modified.apk 已存在则覆盖
```

#### 示例 4：使用 aapt2

```bash
apktool b myapp/ -a -o modified.apk
# 使用 aapt2 构建资源（支持新特性）
```

---

## 🔧 框架管理 (Framework)

### 安装框架文件

```bash
# 从设备提取并安装框架
adb pull /system/framework/framework-res.apk
apktool if framework-res.apk

# 输出：
# I: Installing framework files...
# I: Framework installed to ~/.local/share/apktool/framework/1.apk
```

### 查看已安装框架

```bash
ls -la ~/.local/share/apktool/framework/
```

### 清空框架目录

```bash
apktool efd
# 或
apktool empty-framework-dir
```

---

## 📊 输出文件结构

### 反编译后的目录结构

```
myapp/
├── AndroidManifest.xml       # 清单文件（已解码）
├── apktool.yml               # Apktool 配置信息
├── apktool.id
├── res/                      # 资源文件
│   ├── drawable/            # 图片资源
│   ├── layout/              # 布局文件
│   ├── values/              # 字符串、颜色等
│   └── ...
├── smali/                    # 反编译的代码（smali 格式）
│   └── com/
│       └── example/
│           └── app/
│               └── MainActivity.smali
├── smali_classes2/          # 多 dex 文件的额外代码
├── assets/                   # 原始资源文件
├── lib/                      # 原生库（.so 文件）
├── unknown/                  # 无法识别的文件
└── original/                 # 原始文件的备份
```

### apktool.yml 文件格式

```yaml
version: 3.0.1
apkFileName: myapp.apk
isFrameworkApk: false
usesFramework:
  ids:
  - 1
sdkInfo:
  minSdkVersion: '21'
  targetSdkVersion: '30'
packageInfo:
  forcedPackageId: '127'
  renamesManifestPackage: null
versionInfo:
  versionCode: '10'
  versionName: '1.0.0'
sharedLibrary: false
doNotCompress:
- resources.arsc
- png
```

---

## 🛠️ 高级用法

### 多 DEX 文件处理

某些大型 APK 包含多个 dex 文件：

```bash
# 反编译所有 dex 文件
apktool d large_app.apk -o large_app

# 仅反编译主 dex 文件
apktool d large_app.apk --only-main-classes -o large_app_main
```

### 跳过资源解码

如果只关心代码：

```bash
apktool d myapp.apk -r -o myapp_code
# 资源文件保持编码状态，速度更快
```

### 保留原始签名

```bash
apktool d myapp.apk -k -o myapp_signed
# 保留原始签名文件（用于分析）
```

### 调试模式

```bash
apktool d myapp.apk -d -o myapp_debug
# 解码时包含调试信息
```

---

## 🔄 典型工作流

### 工作流 1：修改应用资源

```bash
# 1. 反编译
apktool d myapp.apk -o myapp_mod

# 2. 修改资源
cd myapp_mod/res/values/
# 编辑 strings.xml 等文件

# 3. 重新编译
apktool b myapp_mod -o myapp_modified.apk

# 4. 签名 APK（需要 apksigner）
apksigner sign --ks mykey.jks myapp_modified.apk

# 5. 安装到设备
adb install myapp_modified.apk
```

### 工作流 2：分析权限

```bash
# 1. 快速分析模式
apktool d suspicious.apk -m -o analysis

# 2. 查看权限
cat analysis/AndroidManifest.xml | grep -A 1 "uses-permission"

# 3. 查看网络配置
cat analysis/res/values/strings.xml | grep -i "http\|url\|api"
```

### 工作流 3：本地化翻译

```bash
# 1. 反编译
apktool d myapp.apk -o myapp_i18n

# 2. 翻译字符串
cd myapp_i18n/res/values/
cp strings.xml strings.xml.bak
# 编辑 strings.xml 进行翻译

# 3. 创建其他语言的资源目录
mkdir -p values-zh-rCN
cp values/strings.xml values-zh-rCN/strings.xml
# 翻译中文版本

# 4. 重新编译
apktool b myapp_i18n -o myapp_chinese.apk

# 5. 签名并安装
apksigner sign --ks mykey.jks myapp_chinese.apk
adb install myapp_chinese.apk
```

---

## 📝 Smali 基础

### Smali 文件结构

```smali
.class public Lcom/example/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"

# 字段
.field private myValue:I

# 直接方法
.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V
    return-void
.end method

# 虚方法
.method public onCreate(Landroid/os/Bundle;)V
    .locals 1
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    const/4 v0, 0x0
    return-void
.end method
```

### 常用 Smali 指令

| 指令 | 说明 |
|------|------|
| `const/4` | 设置 4 位常量 |
| `move-result` | 移动方法返回值 |
| `invoke-virtual` | 调用虚方法 |
| `invoke-direct` | 调用直接方法 |
| `return-void` | 返回空值 |
| `if-eq` | 条件跳转（相等） |
| `goto` | 无条件跳转 |

---

## ⚠️ 注意事项

### 签名验证

修改后的 APK 无法直接安装，需要重新签名：

```bash
# 使用 apksigner（Android SDK）
apksigner sign --ks mykey.jks modified.apk

# 使用 jarsigner（JDK）
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
    -keystore mykey.jks modified.apk alias_name
```

### 完整性校验

某些应用有完整性校验机制：

- **签名校验** - 应用会检查签名是否改变
- **校验和校验** - 检查 APK 哈希值
- **安全校验** - 使用 SafetyNet 等

### 法律风险

- 仅对您拥有权限的 APK 进行反向工程
- 不要分发修改后的商业应用
- 遵守当地法律法规

---

## 🔗 相关资源

- **Smali 语法**: https://github.com/JesusFreli/smali
- **AndroidManifest.xml 格式**: https://developer.android.com/guide/topics/manifest/manifest-intro
- **apksigner 工具**: https://developer.android.com/studio/command-line/apksigner

---

**最后更新**: 2026-02-28
