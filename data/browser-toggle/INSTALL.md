# 📦 OpenClaw Browser Toggle Skill - 安装指南

> 一键启用/禁用 OpenClaw 内置浏览器

---

## 🚀 快速安装

### 方法 1：从压缩包安装（推荐）

```bash
# 1. 下载 Skill 包
# 假设文件名为：browser-toggle-v1.0.0.tar.gz

# 2. 解压
tar -xzf browser-toggle-v1.0.0.tar.gz
cd browser-toggle

# 3. 运行安装脚本
bash setup.sh

# 完成！
```

### 方法 2：从 Git 仓库安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/browser-toggle-skill.git
cd browser-toggle-skill

# 2. 运行安装脚本
bash setup.sh
```

### 方法 3：手动安装

```bash
# 1. 创建 Skill 目录
mkdir -p ~/.openclaw/workspace/skills/browser-toggle

# 2. 复制文件
cp browser_toggle.py ~/.openclaw/workspace/skills/browser-toggle/
cp README.md ~/.openclaw/workspace/skills/browser-toggle/
cp SKILL.md ~/.openclaw/workspace/skills/browser-toggle/

# 3. 设置权限
chmod +x ~/.openclaw/workspace/skills/browser-toggle/browser_toggle.py
```

---

## 📋 安装后验证

```bash
# 查看状态
~/.openclaw/workspace/skills/browser-toggle/browser_toggle.py --status

# 或（如果创建了全局命令）
openclaw-browser --status
```

**预期输出：**
```
==================================================
OpenClaw 浏览器配置状态
==================================================
模式：Chrome 扩展
已启用：False
Profile: chrome
无头模式：True
==================================================
```

---

## 🎯 快速开始

### 启用内置浏览器

```bash
# 方法 1：使用全局命令
openclaw-browser --enable

# 方法 2：使用完整路径
~/.openclaw/workspace/skills/browser-toggle/browser_toggle.py --enable

# 重启 OpenClaw
openclaw gateway restart
```

### 禁用内置浏览器

```bash
openclaw-browser --disable
openclaw gateway restart
```

---

## 📁 文件结构

```
browser-toggle/
├── setup.sh              # 安装脚本
├── browser_toggle.py     # 主程序
├── README.md             # 项目说明
├── SKILL.md              # Skill 描述
├── 使用指南.md           # 详细使用文档
└── skill.conf            # 配置文件
```

---

## 🔧 系统要求

| 要求 | 说明 |
|------|------|
| OpenClaw | v2026.2.26+ |
| Python | 3.8+ |
| Chrome/Chromium | 已安装 |
| 操作系统 | Linux / macOS / Windows |

---

## ⚠️ 注意事项

1. **启用后需要重启 OpenClaw**
   ```bash
   openclaw gateway restart
   ```

2. **首次使用需要手动登录**
   - 让 AI 打开网站（如百度网盘）
   - 在 AI 打开的浏览器窗口中手动登录
   - 登录状态会保存

3. **切换模式需要重新登录**
   - 从 `chrome` 切换到 `openclaw` 需要重新登录网站

---

## 🐛 故障排除

### 问题 1：命令未找到

**解决：**
```bash
# 使用完整路径
~/.openclaw/workspace/skills/browser-toggle/browser_toggle.py --enable
```

### 问题 2：Chrome 未找到

**解决：**
```bash
# 安装 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y
```

### 问题 3：配置失败

**解决：**
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

# 查看文档
cat ~/.openclaw/workspace/skills/browser-toggle/README.md
cat ~/.openclaw/workspace/skills/browser-toggle/使用指南.md
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

## 📚 相关资源

- [OpenClaw 文档](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Skill 仓库](https://clawhub.com)

---

*版本：v1.0.0*  
*最后更新：2026-02-28*
