---
name: relation-keeper
description: |
  维护、记忆、提醒你的社交关系。用于：(1) 记录和累积人物肖像（性别、出生年/日、家庭地址、手机、一起做过的事等），
  (2) 记录未来的约会、纪念日、生日并设置分级提醒，(3) 归档过去共同经历（约会、吃饭、游玩等），
  以便后续查询某人时能回溯。
metadata:
  openclaw:
    slug: relation-keeper
    emoji: "👥"
    requires: {}
    install:
      - id: "setup-cron"
        kind: "run"
        label: "配置提醒扫描定时任务"
        command: "node scripts/install.js"
---

# 关系维护 Relation Keeper

维护你的社交关系网络：**肖像维护**、**未来提醒**、**过去归档**。

---

## 一、数据存储

数据存储在 `$RELATION_KEEPER_DATA` 指向的目录；未设置时使用当前 skill 目录下的 `data/` 文件夹。

### 1.1 人物肖像 `portraits.json`

```json
{
  "people": {
    "张三": {
      "name": "张三",
      "aliases": ["老张"],
      "gender": "男",
      "birthday": "03-15",
      "birthYear": 1990,
      "birthDate": "1990-03-15",
      "address": "北京市朝阳区xx路xx号",
      "phone": "+86 138****1234",
      "notes": "大学同学，做金融",
      "updatedAt": "2026-02-05T10:00:00Z",
      "facts": [
        { "key": "喜好", "value": "喜欢钓鱼", "source": "2026-01-20 聊天", "at": "2026-01-20" },
        { "key": "职位", "value": "某银行经理", "source": "2026-01-20", "at": "2026-01-20" }
      ]
    }
  }
}
```

- 每次用户提及某人及与其相关的事件、信息时，更新对应 portrait。
- **gender**：性别（男/女/其他）。
- **birthday**：`MM-DD` 格式，用于周年提醒。
- **birthYear**：出生年（数字），可选。
- **birthDate**：出生日期，可模糊，如 `"1990"`、`"1990-03"`、`"1990-03-15"`。
- **address**：家庭地址。
- `facts` 为键值对列表，可按 `key` 去重或追加（同一 key 保留最新一条）。

### 1.2 过去事件 `past_events.json`

```json
{
  "events": [
    {
      "id": "evt-001",
      "personIds": ["张三", "李四"],
      "type": "吃饭",
      "date": "2026-01-18",
      "summary": "和张三、李四在海底捞聚餐",
      "details": "讨论创业想法",
      "createdAt": "2026-02-05T10:00:00Z"
    }
  ]
}
```

- `type`：吃饭、约会、游玩、聚会、会议等。
- 查询某人时，可基于 `personIds` 过滤并返回相关 past_events。

### 1.3 未来事件 `future_events.json`

```json
{
  "events": [
    {
      "id": "fevt-001",
      "personIds": ["张三"],
      "type": "生日",
      "date": "2026-03-15",
      "time": null,
      "summary": "张三生日",
      "reminderRule": "birthday",
      "createdAt": "2026-02-05T10:00:00Z"
    },
    {
      "id": "fevt-002",
      "personIds": ["李四"],
      "type": "约会",
      "date": "2026-02-10",
      "time": "18:30",
      "summary": "和李四晚餐",
      "reminderRule": "appointment",
      "createdAt": "2026-02-05T10:00:00Z"
    }
  ]
}
```

- `reminderRule`：
  - `birthday`：生日/纪念日规则
  - `appointment`：约会规则

---

## 二、提醒规则：单一扫描任务

**不创建一次性提醒**，使用**一个每 15 分钟运行的 Cron** 调用 `scan.js` 扫描，如有需要提醒的内容则输出。

### 2.1 提醒规则

| 事件类型 | 提醒时机 |
|----------|----------|
| 生日 / 纪念日 | 7 天前、3 天前、当天（每年按 MM-DD 匹配） |
| 约会 | 事件前 2 小时、事件当刻 |

### 2.2 定时任务自动配置

安装本 skill 时，执行 `npm install` 会自动运行 `postinstall` 脚本，调用 `node scripts/install.js` 配置定时任务。用户无需手动执行 `openclaw cron add`。

若自动配置失败，可手动运行：
```bash
cd <skill 目录> && npm run install:cron
```

### 2.3 scan.js 行为

- 读取 `portraits.json`（生日 MM-DD）与 `future_events.json`
- 生日/纪念日：按 MM-DD 每年匹配，检查当天、+3 天、+7 天
- 约会：检查当前时间是否落在「事件前 2h」或「事件当刻」窗口内
- 已发送的提醒记录在 `reminders_sent.json`，避免重复

### 2.4 添加未来事件时

仅需写入 `future_events.json`，**无需创建任何 Cron**。扫描任务会自动发现并提醒。

---

## 三、技能行为指南

### 3.1 何时触发本 skill

- 用户提及某人及与其相关的信息、事件。
- 用户说「记一下」「提醒我」「某人生日」「和某人约会」等。
- 用户问「我和张三之前做过什么」「张三喜欢什么」「下周有什么安排」等。

### 3.2 肖像维护

- 解析用户输入中的人名、事件、属性（年龄、手机、喜好等）。
- 更新 `portraits.json`：新建或合并到已有 portrait，追加 `facts`。
- 若事件属于「过去」，同时写入 `past_events.json`。

### 3.3 未来事件与提醒

- 解析日期、时间（支持自然语言，如「下周五晚上 6 点半」）。
- 确定 `reminderRule`：生日/纪念日用 `birthday`，具体时间约会用 `appointment`。
- 写入 `future_events.json` 即可，扫描任务每 15 分钟会自动发现并提醒。
- 向用户确认：「已记录，到时会提醒你。」

### 3.4 过去事件归档

- 用户描述「上周和谁吃饭」「昨天和谁约会」时，写入 `past_events.json`。
- 关联 `personIds`，便于按人查询。

### 3.5 查询

- 「张三的信息」→ 读取 `portraits.json` 中 `张三`，并可选汇总 `past_events` 中与之相关的事件。
- 「我和张三一起做过什么」→ 查询 `past_events` 中 `personIds` 包含张三的事件。
- 「近期有什么社交安排」→ 查询 `future_events.json` 未来 N 天内事件。

---

## 四、配置

在 shell 或 `~/.openclaw/.env` 中：

```bash
# 数据目录（可选，未设置时使用 skill/data/）
export RELATION_KEEPER_DATA="$HOME/.openclaw/relation-keeper"

# 时区（用于计算提醒时间）
export RELATION_KEEPER_TZ="Asia/Shanghai"

# 提醒发送渠道（可选）
# 配置则直接推送到该渠道，如: export RELATION_KEEPER_CHANNEL="telegram:YOUR_CHAT_ID"
# 未配置则推送到当前聊天（main session）
export RELATION_KEEPER_CHANNEL=""
```

---

## 五、自然语言触发示例

| 用户说 | 技能动作 |
|--------|----------|
| 张三生日 3 月 15 号，记一下 | 更新 portrait 生日，创建 future_event + birthday 提醒 |
| 下周五晚 6 点半和李四吃饭 | 创建 appointment，设置 2h 前 + 当刻提醒 |
| 上周和张三在海底捞吃过饭 | 写入 past_event，更新 portrait |
| 张三喜欢钓鱼 | 更新 portrait.facts |
| 张三的电话是 138xxxx1234 | 更新 portrait.phone |
| 张三是男的 / 张三性别 | 更新 portrait.gender |
| 张三 1990 年出生 | 更新 portrait.birthYear / birthDate |
| 张三住朝阳区xx路 | 更新 portrait.address |
| 我和张三做过什么 | 查 past_events，汇总输出 |
| 张三是谁 / 张三的信息 | 输出 portrait + 相关 past_events 摘要 |
| 近期有什么约会 / 生日 | 查 future_events 未来 7–14 天 |

---

## 六、脚本与工具

从 skill 根目录（`relation-keeper/`）运行，需 Node.js 16+：

```bash
# 人物肖像
node scripts/portrait.js get 张三
node scripts/portrait.js upsert 张三 --birthday 03-15 --gender 男 --birthYear 1990 --address "北京市朝阳区xx路" --fact-key 喜好 --fact-value 钓鱼

# 事件
node scripts/events.js future-add --persons 张三 --type 生日 --date 2026-03-15 --summary "张三生日" --rule birthday
node scripts/events.js past-add --persons "张三,李四" --type 吃饭 --date 2026-01-18 --summary "海底捞聚餐"

# 扫描提醒（通常由 Cron 每 15 分钟调用，也可手动执行测试）
node scripts/scan.js

# 配置定时任务（安装时自动执行，也可手动运行）
npm run install:cron
```
