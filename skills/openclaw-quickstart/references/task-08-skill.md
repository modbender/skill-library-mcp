# 任务 8：安装一个新 Skill

## 目标
从 ClawHub 社区找到一个有用的 Skill，安装并成功使用它。

## 为什么重要
Skill 是 OpenClaw 的扩展系统。社区里有大量现成的 Skill，安装后 AI 就获得了新能力。学会用 ClawHub，相当于解锁了 OpenClaw 的完整生态。

## 动手步骤

### 第一步：让 AI 帮你找 Skill

> "帮我从 ClawHub 找一个有用的 Skill 并安装"

或者你有特定需求：

> "ClawHub 上有没有处理 PDF 的 Skill？"

> "帮我找一个能发邮件的 Skill"

### 第二步：AI 会做什么

1. 搜索 ClawHub：`clawhub search <关键词>`
2. 展示搜索结果，推荐适合的 Skill
3. 安装你选择的 Skill：`clawhub install <skill-name>`
4. 确认安装成功

### 第三步：使用刚安装的 Skill

安装后直接使用，AI 会自动识别并调用。

### 示例对话

```
你：帮我从 ClawHub 找一个有用的 Skill 安装
AI：我来搜索一下...

找到以下 Skill：
1. pdf-reader - 读取和分析 PDF 文件
2. gmail-helper - Gmail 邮件管理
3. notion-sync - 同步到 Notion

推荐安装 pdf-reader，你有 PDF 处理需求吗？

你：好的，安装它
AI：正在安装 pdf-reader...
✅ 安装成功！现在你可以说「帮我读取这个 PDF」来使用它了。
```

### 手动安装方式

如果你知道 Skill 名字，也可以直接说：

> "安装 ClawHub 上的 pdf-reader skill"

AI 会执行：
```bash
clawhub install pdf-reader
```

## ✅ 完成标志
`~/.openclaw/skills/` 目录中存在新安装的 Skill 文件夹。
