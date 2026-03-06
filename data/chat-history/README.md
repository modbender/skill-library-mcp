# Chat History - OpenClaw对话归档系统

**作者**: Tonyfenwick1982
**版本**: v1.0
**分类**: 生产力工具 / AI辅助
**平台**: OpenClaw
**许可证**: MIT

**联系方式**: tonyfenwick881412@gmail.com

---

## 📖 简介

Chat History是一个OpenClaw对话归档系统，帮助你自动归档和搜索对话记录。

### 核心特性

- ✅ **自动归档**：每天自动归档对话记录（可自定义时间）
- ✅ **增量归档**：只归档上次归档后的新消息，避免重复
- ✅ **多Channel支持**：自动识别并归档webui/imessage/telegram等所有channel
- ✅ **跨端查询**：无论在哪端，都能查询所有channel的对话
- ✅ **自然语言触发**：30+关键词，"我记不清了"、"找不到之前的对话"
- ✅ **评估记录管理**：列出/搜索评估，避免重复评估

---

## 🚀 快速开始

### 安装

**步骤1**：复制skill到OpenClaw skills目录
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/Tonyfenwick1982/chat-history.git
# 或手动复制chat-history文件夹
```

**步骤2**：进入skill目录并启动
```bash
cd ~/.openclaw/workspace/skills/chat-history
python3 main.py --start
```

系统会自动设置定时任务，每天23:59归档对话。

---

### 使用

#### 自然语言触发（最方便）

```
用户: 我想不起来了，之前说过关于视频的事
→ 自动搜索"视频"并显示结果

用户: 我之前评估过哪些skills
→ 自动列出评估记录
```

#### 命令使用

**基础命令**：
```
/chat_history             # 查看所有指令
/chat_history start       # 启动自动归档
/chat_history stop        # 停止自动归档
/chat_history status      # 查看归档状态
/chat_history timing      # 查看或设置归档时间
```

**搜索命令**：
```
/chat_history search "关键词"    # 搜索对话
/chat_history list               # 列出所有归档
/chat_history list webui         # 只列webui端
/chat_history 20260216          # 列出指定日期
```

---

## 📊 数据结构

```
~/.openclaw/workspace/conversation-archives/
├── 20260204-webui.txt           # 文件命名：YYYYMMDD-channel.txt
├── 20260204-imessage.txt
├── 20260205-webui.txt
├── ...
├── status.json                   # 归档状态
└── evaluations-index.json        # 评估记录索引
```

---

## 🛡️ 安全性

**安全承诺**：
- ✅ 无网络请求（纯本地操作）
- ✅ 无硬编码API keys
- ✅ 无上传数据到服务器
- ✅ 所有操作在本地工作目录内

**依赖项**：
- Python 3.x
- 所有依赖项为Python标准库（无第三方依赖）

---

## 📚 文档

- [Skill定义](SKILL.md) - OpenClaw Skill定义
- [安全性评估](SECURITY-UTILITY-ASSESSMENT.md) - 安全与实用性评估
- [测试指南](TEST-GUIDE.md) - 完整测试指南

---

## 📞 联系方式

- Author: Tonyfenwick1982
- GitHub: https://github.com/Tonyfenwick1982
- Email: tonyfenwick881412@gmail.com

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

## ⚠️ 免责声明

本工具仅用于管理和搜索用户自己的对话记录，不涉及任何隐私泄露或数据传输。所有数据存储在本地，安全可控。
