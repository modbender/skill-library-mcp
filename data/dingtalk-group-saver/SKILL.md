---
name: DingTalk Group Saver
description: 当收到钉钉群消息且被@时： 1. 自动提取群 ID (conversationId) 2. 自动提取群名字 3. 双写存储：
---

# DingTalk Group Saver

**版本**: 2.0.0  
**描述**: 当在钉钉群里被@时，自动保存群 ID 和群名字到 memory 中（双写持久化）

---

## 🎯 功能

当收到钉钉群消息且被@时：
1. 自动提取群 ID (conversationId)
2. 自动提取群名字
3. **双写存储**：
   - JSON 文件：`memory/dingtalk-groups.json`（结构化数据）
   - Markdown 文件：`MEMORY.md`（长期记忆，所有 Session 可读）

---

## 📁 文件结构

```
~/.openclaw/workspace/skills/dingtalk-group-saver/
├── SKILL.md              # 本文件
└── index.js              # 实现代码
```

---

## 💾 数据存储

### 1. JSON 文件（结构化）
**位置**：`~/.openclaw/workspace/memory/dingtalk-groups.json`

```json
{
  "groups": [
    {
      "conversationId": "cid/xxx==",
      "groupName": "测试群",
      "firstSeenAt": "2026-02-26T14:00:00+08:00",
      "lastActiveAt": "2026-02-26T14:00:00+08:00",
      "mentionCount": 1
    }
  ]
}
```

### 2. MEMORY.md（长期记忆）
**位置**：`~/.openclaw/workspace/MEMORY.md`

自动更新 `### 钉钉群列表（推送渠道）` 章节，包含：
- 群名称
- 群 ID
- 用途描述

**优势**：
- ✅ 所有 Session 启动时自动加载
- ✅ 人类可读，便于手动编辑
- ✅ 与系统配置、主人画像等长期记忆在一起

---

## 🔧 使用方式

**无需手动调用！** 自动触发：

1. 在钉钉群里@小牛马
2. 机器人回复消息
3. 自动保存群信息到：
   - `memory/dingtalk-groups.json`
   - `MEMORY.md`

---

## 📋 查看已保存的群

```bash
# 查看 JSON 数据
cat ~/.openclaw/workspace/memory/dingtalk-groups.json

# 查看 MEMORY.md 中的群列表
grep -A 10 "钉钉群列表" ~/.openclaw/workspace/MEMORY.md
```

---

## 🎯 使用场景

| 场景 | 说明 |
|------|------|
| 新群@机器人 | 自动记录群信息 |
| 发送群消息 | 从 MEMORY.md 查找群 ID |
| 群管理 | 维护已知群列表 |
| Session 切换 | 新 Session 自动继承群信息 |

---

## ⚠️ 注意事项

- 只在被@时触发（避免记录所有群）
- 群名字可能为空（API 限制）
- 首次保存后，后续@会更新 `lastActiveAt` 和 `mentionCount`
- **MEMORY.md 中的表格会自动同步更新**

---

## 🔄 更新日志

- **v2.0.0** - 新增 MEMORY.md 双写，保证所有 Session 可读
- **v1.0.0** - 初始版本，仅保存到 JSON 文件

---

由 OpenClaw 技能系统自动加载 🐂🐎
