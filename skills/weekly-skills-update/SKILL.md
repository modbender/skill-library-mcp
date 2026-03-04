---
name: weekly-skills-update
description: 每周自动更新技能并推送摘要。当收到"执行技能每周更新"或"skills-weekly-update"触发时，运行 clawhub update --all 并更新 SKILLS_INDEX.md，最后推送摘要给用户。
---

# 每周技能自动更新

## 触发条件

当收到以下任一消息时激活：
- "执行技能每周更新"
- "skills-weekly-update"
- "运行技能更新脚本"

## 执行流程

### 1. 执行更新命令

```bash
cd ~/.openclaw/workspace
clawhub update --all 2>&1 | tee /tmp/skills-update-output.txt
```

### 2. 解析更新结果

统计：
- 更新成功的技能数量（✓ 标记）
- 已是最新的技能数量（up to date）
- 更新失败的数量（error/failed）

### 3. 更新 SKILLS_INDEX.md

如果技能有增减：
1. 重新扫描技能目录
2. 更新技能总数
3. 更新「最后更新」日期
4. 在更新日志中添加记录

### 4. 生成摘要并推送

摘要格式：

```
🌀 **技能每周更新摘要**

**更新时间**: YYYY-MM-DD HH:MM

**结果**:
- ✅ 更新成功：X 个
- ⏭️ 已是最新：Y 个
- ❌ 更新失败：Z 个

**更新详情**:
- skill-name-1: v1.0.0 → v1.0.1
- skill-name-2: v1.2.0 → v1.3.0

**SKILLS_INDEX.md**: 已更新/无需更新

---
*下次更新：下周日 09:00*
```

## 错误处理

- 如果 clawhub 命令不存在：提示用户安装 `npm i -g clawhub`
- 如果更新失败：记录错误并继续
- 如果网络问题：重试 2 次，间隔 30 秒

## 注意事项

- 更新前不备份（clawhub 自动处理）
- 推送摘要到当前会话（飞书/主会话）
- 更新日志保存到 `~/clawd/workspace/logs/skills-update-YYYYMMDD.md`
