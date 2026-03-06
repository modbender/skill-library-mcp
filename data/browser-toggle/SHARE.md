# 🎁 OpenClaw Browser Toggle Skill - 分享包

> 一键启用/禁用 OpenClaw 内置浏览器，无需手动修改配置文件

---

## 📦 发布信息

- **Skill 名称：** browser-toggle
- **版本：** v1.0.0
- **发布日期：** 2026-02-28
- **作者：** AI Assistant
- **大小：** 8.1 KB
- **SHA256：** `52e6793d41094b6495ce5a9ae165b9fa03947989d739290399a352e76d8b52c7`

---

## 🚀 快速安装

### 1. 下载 Skill 包

```bash
# 从 GitHub Releases 下载
wget https://github.com/your-username/browser-toggle/releases/download/v1.0.0/browser-toggle-v1.0.0.tar.gz

# 验证文件完整性
sha256sum browser-toggle-v1.0.0.tar.gz
# 应该输出：52e6793d41094b6495ce5a9ae165b9fa03947989d739290399a352e76d8b52c7
```

### 2. 解压并安装

```bash
# 解压
tar -xzf browser-toggle-v1.0.0.tar.gz
cd browser-toggle-v1.0.0

# 运行安装脚本
bash setup.sh
```

### 3. 验证安装

```bash
# 查看状态
openclaw-browser --status

# 或
~/.openclaw/workspace/skills/browser-toggle/browser_toggle.py --status
```

---

## 💡 使用示例

### 启用内置浏览器

```bash
# 启用（可视化模式）
openclaw-browser --enable
openclaw gateway restart

# 启用（无头模式）
openclaw-browser --enable --headless
openclaw gateway restart
```

### 禁用内置浏览器

```bash
openclaw-browser --disable
openclaw gateway restart
```

### 查看状态

```bash
openclaw-browser --status
```

---

## 📋 功能特性

- ✅ **一键切换** - 无需手动编辑配置文件
- ✅ **自动备份** - 修改前自动备份配置
- ✅ **失败恢复** - 配置失败可快速恢复
- ✅ **跨平台** - 支持 Linux/macOS/Windows
- ✅ **无头模式** - 支持后台运行
- ✅ **独立空间** - 不访问个人浏览器数据

---

## 🎯 使用场景

### 场景 1：访问需要登录的网站

```bash
# 1. 启用内置浏览器
openclaw-browser --enable
openclaw gateway restart

# 2. 让 AI 打开网站（如百度网盘）
# 3. 手动登录（在 AI 打开的浏览器窗口中）
# 4. 后续可以直接使用
```

### 场景 2：日常自动化

```bash
# 启用无头模式（后台运行）
openclaw-browser --enable --headless
openclaw gateway restart
```

### 场景 3：恢复默认

```bash
# 禁用内置浏览器
openclaw-browser --disable
openclaw gateway restart
```

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目说明 |
| [INSTALL.md](INSTALL.md) | 安装指南 |
| [使用指南.md](使用指南.md) | 详细使用文档 |
| [SKILL.md](SKILL.md) | Skill 描述 |
| [RELEASE.md](RELEASE.md) | 发布说明 |

---

## 🔧 系统要求

| 要求 | 说明 |
|------|------|
| OpenClaw | v2026.2.26+ |
| Python | 3.8+ |
| Chrome/Chromium | 已安装 |
| 操作系统 | Linux / macOS / Windows |

---

## 🐛 故障排除

### 问题 1：命令未找到

```bash
# 使用完整路径
~/.openclaw/workspace/skills/browser-toggle/browser_toggle.py --enable
```

### 问题 2：Chrome 未找到

```bash
# 安装 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y
```

### 问题 3：配置失败

```bash
# 从备份恢复
~/.openclaw/workspace/skills/browser-toggle/browser_toggle.py --restore ~/.openclaw/workspace/backups/xxx.json
```

---

## 📞 获取帮助

```bash
# 查看帮助
openclaw-browser --help

# 查看状态
openclaw-browser --status

# 查看日志
tail -f /tmp/openclaw/openclaw-*.log
```

---

## 📦 卸载

```bash
# 1. 禁用内置浏览器
openclaw-browser --disable
openclaw gateway restart

# 2. 删除 Skill
rm -rf ~/.openclaw/workspace/skills/browser-toggle

# 3. 删除全局命令（如果存在）
sudo rm -f /usr/local/bin/openclaw-browser
```

---

## 📄 许可证

MIT License

---

## 🔗 相关链接

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Skill Hub](https://clawhub.com)

---

## 📧 反馈与支持

- **问题反馈：** https://github.com/your-username/browser-toggle/issues
- **讨论区：** https://github.com/openclaw/openclaw/discussions

---

*版本：v1.0.0*  
*发布日期：2026-02-28*  
*维护者：AI Assistant*
