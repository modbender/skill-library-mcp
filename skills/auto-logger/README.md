# Auto Logger - 使用指南

## 🚀 快速开始

### 1. 手动记录
```powershell
# 记录某件事
.\scripts\auto-logger.ps1 -Action "manual"
```

### 2. 会话结束自动记录
```powershell
# 在会话结束时调用
.\scripts\auto-logger.ps1 -Action "session_end" -Summary "会话摘要内容"
```

### 3. 每日整理（定时任务）
```powershell
# 每天晚上 23:00 执行
.\scripts\auto-logger.ps1 -Action "daily_review"
```

---

## ⏰ 设置定时任务

### Windows 任务计划程序

1. 打开「任务计划程序」
2. 创建基本任务
3. 设置触发器（如每天 23:00）
4. 操作：启动程序
   - 程序：`powershell.exe`
   - 参数：`-ExecutionPolicy Bypass -File "C:\Users\24267\.openclaw\workspace\scripts\auto-logger.ps1" -Action "daily_review"`
   - 起始于：`C:\Users\24267\.openclaw\workspace`

### OpenClaw Cron（如果支持）

```bash
# 每小时记录
openclaw cron add --name "hourly-log" --cron "0 * * * *" --command "powershell -ExecutionPolicy Bypass -File scripts\auto-logger.ps1 -Action session_end"

# 每日整理（23:00）
openclaw cron add --name "daily-review" --cron "0 23 * * *" --command "powershell -ExecutionPolicy Bypass -File scripts\auto-logger.ps1 -Action daily_review"
```

---

## 📁 文件结构

```
workspace/
├── memory/
│   ├── 2026-03-01.md       # 每日记忆文件
│   └── ...
├── MEMORY.md                # 长期记忆
├── scripts/
│   └── auto-logger.ps1     # 自动记录脚本
└── skills/
    └── auto-logger/
        └── SKILL.md        # 技能说明
```

---

## 📝 记录模板

### 每日记忆文件格式

```markdown
# YYYY-MM-DD 记忆

## 📋 今日概要
- 会话数：X
- 重要事件：Y
- 完成任务：Z

## 🗣️ 对话记录
### HH:MM - 事件名称
- 内容详情

## ✅ 完成任务
- [x] 任务 1
- [x] 任务 2

## 📝 重要决策
- 决策内容

## 🔧 配置变更
- 新增/修改的文件

## 🏷️ 标签
#标签 1 #标签 2
```

---

## 🎯 自动记录触发条件

### 自动触发
- [ ] 会话结束时
- [ ] 检测到"记住"、"保存"等关键词
- [ ] 定时任务（每小时/每天）

### 手动触发
- [ ] 用户明确说"记录一下"
- [ ] 运行手动记录命令

---

## 🔐 安全注意事项

### 不记录的内容
- ❌ 密码原文（只记录"已设置密码"）
- ❌ 敏感个人信息（身份证号、银行卡等）
- ❌ 私密对话内容

### 建议
- ✅ 敏感配置使用环境变量
- ✅ 授权码等只保存在本地文件
- ✅ 定期检查和清理记忆文件

---

## 🛠️ 故障排除

### 问题：脚本无法执行
**解决：**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题：memory 目录不存在
**解决：**
```powershell
New-Item -ItemType Directory -Force -Path "C:\Users\24267\.openclaw\workspace\memory"
```

### 问题：文件编码问题
**解决：** 确保使用 UTF-8 编码保存文件

---

**创建日期：** 2026-03-01  
**用户：** 白凤  
**版本：** 1.0
