# Pyzotero CLI Installation Guide

使用 Python 脚本方式调用 pyzotero 库的详细安装指南。

## 目录

1. [前提条件](#前提条件)
2. [安装方法](#安装方法)
3. [平台特定说明](#平台特定说明)
4. [配置访问模式](#配置访问模式)
5. [故障排除](#故障排除)
6. [卸载](#卸载)

---

## 前提条件

### 必需软件

- **Python 3.7+** - 用于运行 pyzotero 脚本
- **pip** 或 **pipx** - 用于安装包
- **Zotero 7+** - 用于本地 API 访问 (本地模式需要)

### 检查系统

检查 Python 3 是否已安装:
```bash
python3 --version
```

检查 pip 是否已安装:
```bash
pip3 --version
```

检查 pipx 是否已安装:
```bash
pipx --version
```

---

## 安装方法

### 方法一：pipx (推荐)

pipx 在隔离的虚拟环境中安装 Python 包。

#### 为什么推荐 pipx?

- **PEP 668 兼容**: 防止与系统 Python 包冲突
- **隔离环境**: 每个应用有自己的虚拟环境
- **干净卸载**: 易于移除，无副作用
- **安全性**: 减少系统级包冲突风险

#### 安装步骤

**1. 安装 pipx**

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install pipx -y
pipx ensurepath
```

**Arch Linux:**
```bash
sudo pacman -S pipx
pipx ensurepath
```

**Fedora:**
```bash
sudo dnf install pipx
pipx ensurepath
```

**macOS (Homebrew):**
```bash
brew install pipx
pipx ensurepath
```

**2. 安装 pyzotero**
```bash
pipx install pyzotero
```

**3. 验证安装**
```bash
python3 -c "from pyzotero import zotero; print('pyzotero 已安装')"
```

---

### 方法二：pip (通用)

#### 系统级安装 (需要 sudo)
```bash
sudo pip install pyzotero
```

#### 用户级安装 (推荐)
```bash
pip install --user pyzotero
export PATH="$HOME/.local/bin:$PATH"
```

将 PATH 导出添加到 `~/.bashrc` 或 `~/.zshrc`:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### 方法三：虚拟环境

适合开发或测试:

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 pyzotero
pip install pyzotero

# 验证
python3 -c "from pyzotero import zotero; print('OK')"
```

---

## 平台特定说明

### Debian 11+ / Ubuntu 23.04+ (PEP 668 系统)

这些系统实施了 PEP 668，禁止使用系统 pip 安装包。

**推荐方案:**
```bash
pipx install pyzotero
```

**备选方案:**
```bash
pip install --user pyzotero
export PATH="$HOME/.local/bin:$PATH"
```

### Arch Linux

```bash
# 使用 pipx (推荐)
pipx install pyzotero

# 或使用 pip
pip install --user pyzotero
```

### Fedora 34+

```bash
# 安装 pipx
sudo dnf install pipx
pipx ensurepath

# 安装 pyzotero
pipx install pyzotero
```

### macOS

```bash
# 使用 Homebrew 安装 pipx
brew install pipx
pipx ensurepath

# 安装 pyzotero
pipx install pyzotero
```

### Windows

```bash
# 使用 pip
pip install pyzotero

# 或下载 Zotero 桌面版后使用内置 Python
```

---

## 配置访问模式

### 模式一：本地模式 (默认，推荐)

适用于本地有 Zotero 7+ 安装的情况。

**配置步骤:**

1. **打开 Zotero 7+**

2. **启用本地 API:**
   - Windows/Linux: 编辑 > 首选项 > 高级
   - macOS: Zotero > 设置 > 高级

3. **勾选:** "允许此计算机上的其他应用程序与 Zotero 通信"

4. **重启 Zotero**

5. **设置环境变量 (可选，默认为 true):**
   ```bash
   export ZOTERO_LOCAL="true"
   ```

6. **测试连接:**
   ```bash
   cd /root/.openclaw/workspace/skills/pyzotero-cli
   python3 scripts/zotero_tool.py listcollections
   ```

**输出示例:**
```
✓ 已连接到本地 Zotero
共有 5 个集合:

1. 📁 未命名集合
   密钥：ABC123
```

---

### 模式二：在线模式

适用于远程访问或无 Zotero 安装的服务器。

**配置步骤:**

1. **获取 API 密钥:**
   - 访问 https://www.zotero.org/settings/keys
   - 点击 "Create new private key"
   - 授予读取权限 (Read access to library and files)
   - 复制密钥

2. **获取用户 ID:**
   - 访问 https://www.zotero.org/settings/keys
   - 在 "Your userID for use in API calls" 处找到

3. **设置环境变量:**
   ```bash
   export ZOTERO_LOCAL="false"
   export ZOTERO_USER_ID="your_user_id"
   export ZOTERO_API_KEY="your_api_key"
   ```

4. **永久设置 (可选):**
   ```bash
   echo 'export ZOTERO_LOCAL="false"' >> ~/.bashrc
   echo 'export ZOTERO_USER_ID="your_user_id"' >> ~/.bashrc
   echo 'export ZOTERO_API_KEY="your_api_key"' >> ~/.bashrc
   source ~/.bashrc
   ```

5. **测试连接:**
   ```bash
   python3 scripts/zotero_tool.py listcollections
   ```

---

## 故障排除

### 问题 1: 无法连接到本地 Zotero

**错误信息:**
```
✗ 无法连接到本地 Zotero: ...
```

**解决方案:**

1. 确保 Zotero 正在运行
2. 检查是否启用本地 API:
   - 设置 > 高级 > "允许此计算机上的其他应用程序与 Zotero 通信"
3. 重启 Zotero
4. 确认使用的是 Zotero 7 或更新版本

---

### 问题 2: 模块未找到

**错误信息:**
```
ModuleNotFoundError: No module named 'pyzotero'
```

**解决方案:**

```bash
# 使用 pipx 安装
pipx install pyzotero

# 或使用 pip
pip install --user pyzotero
```

---

### 问题 3: 权限错误 (PEP 668)

**错误信息:**
```
error: externally-managed-environment
```

**解决方案:**

使用 pipx 或 --user 标志:

```bash
# 推荐
pipx install pyzotero

# 备选
pip install --user pyzotero
```

---

### 问题 4: 在线模式认证失败

**错误信息:**
```
✗ 无法连接到 Zotero 在线 API: ...
```

**解决方案:**

1. 检查环境变量是否正确设置:
   ```bash
   echo $ZOTERO_LOCAL
   echo $ZOTERO_USER_ID
   echo $ZOTERO_API_KEY
   ```

2. 确认 API 密钥有效:
   - 访问 https://www.zotero.org/settings/keys
   - 检查密钥是否已过期或被撤销

3. 确认用户 ID 正确:
   - 用户 ID 是数字，不是用户名

---

### 问题 5: 命令执行无输出

**可能原因:**

1. Zotero 库为空
2. 搜索关键词无匹配结果

**解决方案:**

```bash
# 检查是否有项目
python3 scripts/zotero_tool.py listcollections

# 使用更宽泛的搜索词
python3 scripts/zotero_tool.py search -q "test" -l 5
```

---

## 卸载

### 使用 pipx 安装
```bash
pipx uninstall pyzotero
```

### 使用 pip 安装
```bash
pip uninstall pyzotero
```

### 删除技能 (可选)
```bash
rm -rf /root/.openclaw/workspace/skills/pyzotero-cli
```

---

## 验证安装

运行以下命令验证安装是否成功:

```bash
# 检查 pyzotero 库
python3 -c "from pyzotero import zotero; print('✓ pyzotero 库已安装')"

# 检查脚本
cd /root/.openclaw/workspace/skills/pyzotero-cli
python3 scripts/zotero_tool.py --help

# 测试连接 (本地模式)
python3 scripts/zotero_tool.py listcollections
```

---

## 下一步

安装完成后:

1. 📖 阅读 [QUICKSTART.md](QUICKSTART.md) 快速开始
2. 💡 查看 [EXAMPLES.md](EXAMPLES.md) 了解使用示例
3. 📚 参考 [SKILL.md](SKILL.md) 获取完整命令参考
4. 🔧 查看 [CHANGELOG_v2.md](CHANGELOG_v2.md) 了解 v2.0.0 更新内容

---

**更新日期:** 2026-02-23  
**版本:** 2.0.0
