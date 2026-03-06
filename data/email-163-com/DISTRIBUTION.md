# 📦 email-163-com 技能发布指南

**版本**: 1.0.0  
**创建日期**: 2026-02-19

---

## ⚠️ GitHub 访问问题

ClawHub 使用 GitHub 账号登录，但在中国大陆可能无法访问。以下是解决方案：

---

## 🔧 解决方案

### 方案 A: 使用网络工具（推荐）⭐

如果你能访问 GitHub，这是最简单的方式：

```bash
# 1. 登录 ClawHub
clawhub login

# 2. 发布技能
cd ~/.openclaw/workspace/skills
clawhub publish ./email-163-com \
  --slug email-163-com \
  --name "email-163-com" \
  --version 1.0.0 \
  --changelog "初始版本 - 163 邮箱完整邮件管理工具"

# 3. 验证发布
clawhub search email-163-com
```

---

### 方案 B: 本地安装（无需 ClawHub）⭐⭐ 推荐中国大陆用户

用户可以直接从本地安装技能，无需通过 ClawHub：

#### 方法 1: 复制技能文件夹

```bash
# 发送技能文件夹给用户
# 用户复制到 ~/.openclaw/workspace/skills/ 即可

# 或者创建压缩包
cd ~/.openclaw/workspace/skills/
tar -czf email-163-com.tar.gz email-163-com/

# 发送文件：email-163-com.tar.gz
# 用户解压到 ~/.openclaw/workspace/skills/
```

#### 方法 2: 使用安装脚本

创建自动安装脚本：

```bash
# 用户运行：
curl -L https://your-server.com/email-163-com/install.sh | bash

# 或从本地运行：
bash ~/.openclaw/workspace/skills/email-163-com/install.sh
```

---

### 方案 C: 使用国内镜像（如果可用）

检查是否有国内 ClawHub 镜像：

```bash
# 设置国内镜像（如果有）
export CLAWHUB_REGISTRY=https://clawhub.cn
clawhub publish ./email-163-com --slug email-163-com
```

---

### 方案 D: 通过邮件分享技能

使用我们已经配置好的邮件功能：

```bash
# 1. 打包技能
cd ~/.openclaw/workspace/skills/
tar -czf email-163-com.tar.gz email-163-com/

# 2. 通过邮件发送
python3 ~/.config/himalaya/send-attachment.py \
  --to friend@example.com \
  --subject "email-163-com 技能包" \
  --body "请查收 email-163-com 技能包，解压到 ~/.openclaw/workspace/skills/ 即可使用" \
  --attach email-163-com.tar.gz
```

---

## 📦 本地安装说明（给用户）

### 安装步骤

1. **获取技能文件**
   - 从邮件下载 `email-163-com.tar.gz`
   - 或从其他渠道获取

2. **解压到技能目录**
   ```bash
   tar -xzf email-163-com.tar.gz -C ~/.openclaw/workspace/skills/
   ```

3. **验证安装**
   ```bash
   ~/.openclaw/workspace/skills/email-163-com/email-163-com --help
   ```

4. **配置邮箱**
   ```bash
   # 配置文件已预配置
   # 如需修改：nano ~/.config/email-163-com/config.json
   ```

5. **开始使用**
   ```bash
   # 读取邮件
   email-163-com read --count 5
   
   # 发送邮件
   email-163-com send --to x@example.com --subject "Hi" --body "Hello!"
   ```

---

## 🚀 快速分享脚本

创建分享脚本：

```bash
#!/bin/bash
# share-email-skill.sh

SKILL_DIR="$HOME/.openclaw/workspace/skills/email-163-com"
OUTPUT_DIR="$HOME/Desktop"

echo "📦 打包 email-163-com 技能..."
cd "$HOME/.openclaw/workspace/skills/"
tar -czf "$OUTPUT_DIR/email-163-com.tar.gz" email-163-com/

echo "✅ 打包完成！"
echo "📁 文件位置：$OUTPUT_DIR/email-163-com.tar.gz"
echo ""
echo "📧 通过邮件发送:"
echo "python3 ~/.config/himalaya/send-attachment.py \\
  --to friend@example.com \\
  --subject 'email-163-com 技能包' \\
  --attach $OUTPUT_DIR/email-163-com.tar.gz"
```

---

## 📋 技能信息（用于分享）

### 技能名称
email-163-com

### 版本
1.0.0

### 描述
163 邮箱完整邮件管理工具 - 发送/接收/搜索/管理邮件

### 功能
- ✅ 发送邮件（支持 HTML/纯文本）
- ✅ 发送附件（支持多附件）
- ✅ 读取邮件（IMAP ID 认证）
- ✅ 文件夹管理
- ✅ 邮件搜索
- ✅ 附件下载

### 系统要求
- Python 3.6+
- OpenClaw
- 163 邮箱账号

### 安装大小
~50KB（压缩后）

### 测试状态
✅ 10/10 测试通过

---

## 📞 推荐方案（中国大陆用户）

**最佳方案**: 本地安装 + 邮件分享

### 优势
- ✅ 无需访问 GitHub
- ✅ 无需 ClawHub 账号
- ✅ 快速分享
- ✅ 完全离线可用
- ✅ 使用我们已经配置好的邮件系统

### 流程
1. 打包技能文件
2. 通过 163 邮箱发送给需要的人
3. 对方解压到技能目录
4. 立即使用

---

## 📝 分享邮件模板

```
主题：📦 email-163-com 技能包 - 163 邮箱管理工具

你好！

这是 email-163-com 技能包，一个完整的 163 邮箱管理工具。

【功能】
- 发送邮件（支持附件）
- 接收邮件
- 搜索邮件
- 文件夹管理
- 附件下载

【安装】
1. 下载附件：email-163-com.tar.gz
2. 解压到：~/.openclaw/workspace/skills/
3. 运行测试：~/.openclaw/workspace/skills/email-163-com/email-163-com --help

【配置】
配置文件：~/.config/email-163-com/config.json
（已预配置你的邮箱信息）

【使用示例】
# 读取邮件
email-163-com read --count 5

# 发送邮件
email-163-com send --to x@example.com --subject "Hi" --body "Hello!"

# 发送附件
email-163-com send --to x@example.com --attach file.pdf

如有问题，随时联系！

-- 
Sent from OpenClaw
```

---

## 🎯 下一步

### 如果你想分享技能：

```bash
# 1. 打包
cd ~/.openclaw/workspace/skills/
tar -czf ~/Desktop/email-163-com.tar.gz email-163-com/

# 2. 通过邮件发送（使用我们的邮件技能）
python3 ~/.config/himalaya/send-attachment.py \
  --to friend@example.com \
  --subject "📦 email-163-com 技能包" \
  --body "请查收附件中的技能包" \
  --attach ~/Desktop/email-163-com.tar.gz
```

### 如果只是想自己使用：

技能已经安装好了，可以直接使用！
```bash
email-163-com read --count 5
```

---

**推荐**: 使用本地安装方案，无需依赖 GitHub 或 ClawHub！✅
