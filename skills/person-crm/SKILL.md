---
name: personal-crm
description: Personal relationship manager powered by Feishu/Lark Bitable. Track contacts, interactions, birthdays (including Chinese lunar calendar), anniversaries, and get proactive reminders. Never forget a birthday again.
metadata: {"openclaw": {"requires": {"config": ["feishu.enabled"]}, "emoji": "💝", "homepage": "https://github.com/anthropics/personal-crm-skill"}}
---

# Personal CRM — 人际关系记忆助手

> 帮你记住身边每个人的故事。生日、喜好、上次聊了什么、下次该联系谁。

## Configuration

This skill stores data in a Feishu/Lark Bitable. Configure your table IDs in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "personal-crm": {
        "enabled": true,
        "config": {
          "app_token": "YOUR_BITABLE_APP_TOKEN",
          "contacts_table_id": "YOUR_CONTACTS_TABLE_ID",
          "interactions_table_id": "YOUR_INTERACTIONS_TABLE_ID"
        }
      }
    }
  }
}
```

You can set this up manually (see `SETUP.md`) or use the auto-setup command below.

**Reading config:** Read the user's config from `skills.entries.personal-crm.config` to get `app_token`, `contacts_table_id`, and `interactions_table_id`. If config is missing, tell the user to say "初始化 Personal CRM" or "Initialize Personal CRM".

## 自动建表（Auto Setup）

当用户说"初始化 Personal CRM"、"Initialize Personal CRM"或"设置 CRM"时，执行以下步骤：

### Step 1: 创建 Bitable
```
feishu_bitable_create_app(name="Personal CRM")
```
记录返回的 app_token。

### Step 2: 在默认表上创建联系人表字段
Bitable 创建时会自带一张默认表。先用 `feishu_bitable_get_meta` 获取默认表的 table_id，然后依次创建字段：

```
feishu_bitable_create_field(app_token, table_id, "关系", 3, property={"options": [{"name":"家人"},{"name":"女朋友"},{"name":"朋友"},{"name":"同事"},{"name":"领导"},{"name":"客户"},{"name":"合作伙伴"},{"name":"导师"},{"name":"其他"}]})
feishu_bitable_create_field(app_token, table_id, "手机", 13)
feishu_bitable_create_field(app_token, table_id, "微信", 1)
feishu_bitable_create_field(app_token, table_id, "邮箱", 1)
feishu_bitable_create_field(app_token, table_id, "城市", 1)
feishu_bitable_create_field(app_token, table_id, "公司", 1)
feishu_bitable_create_field(app_token, table_id, "职位", 1)
feishu_bitable_create_field(app_token, table_id, "生日", 5, property={"auto_fill":false,"date_formatter":"yyyy-MM-dd"})
feishu_bitable_create_field(app_token, table_id, "农历生日", 1)
feishu_bitable_create_field(app_token, table_id, "过农历生日", 7)
feishu_bitable_create_field(app_token, table_id, "纪念日", 5, property={"auto_fill":false,"date_formatter":"yyyy-MM-dd"})
feishu_bitable_create_field(app_token, table_id, "纪念日说明", 1)
feishu_bitable_create_field(app_token, table_id, "提醒提前天数", 2, property={"formatter":"0"})
feishu_bitable_create_field(app_token, table_id, "爱好", 4)
feishu_bitable_create_field(app_token, table_id, "标签", 4)
feishu_bitable_create_field(app_token, table_id, "备注", 1)
feishu_bitable_create_field(app_token, table_id, "最后联系", 5, property={"auto_fill":false,"date_formatter":"yyyy-MM-dd"})
feishu_bitable_create_field(app_token, table_id, "联系频率", 3, property={"options": [{"name":"每周"},{"name":"每月"},{"name":"每季度"},{"name":"偶尔"}]})
```

### Step 3: 创建互动记录表
目前 feishu_bitable 工具不支持直接创建新表，需要用户在飞书中手动添加第二张表。告诉用户：

> 联系人表已自动创建完成！请在飞书中打开这个多维表格，手动添加第二张表命名为"互动记录"，然后告诉我表的 table_id，我来自动创建所有字段。

当用户提供了互动记录表的 table_id 后，创建字段：
```
feishu_bitable_create_field(app_token, table_id, "联系人", 1)
feishu_bitable_create_field(app_token, table_id, "日期", 5, property={"auto_fill":false,"date_formatter":"yyyy-MM-dd"})
feishu_bitable_create_field(app_token, table_id, "类型", 3, property={"options": [{"name":"见面"},{"name":"通话"},{"name":"消息"},{"name":"会议"},{"name":"吃饭"},{"name":"邮件"}]})
feishu_bitable_create_field(app_token, table_id, "要点", 1)
feishu_bitable_create_field(app_token, table_id, "后续", 1)
feishu_bitable_create_field(app_token, table_id, "氛围", 3, property={"options": [{"name":"开心"},{"name":"平淡"},{"name":"深入"},{"name":"紧张"},{"name":"感动"},{"name":"尴尬"}]})
feishu_bitable_create_field(app_token, table_id, "费用", 2, property={"formatter":"0.0"})
```

### Step 4: 告诉用户配置信息
建表完成后，输出配置信息让用户添加到 `~/.openclaw/openclaw.json`，包含生成的 app_token、contacts_table_id 和 interactions_table_id。

## 激活条件
用户提到以下任何内容时激活：
- 认识了新朋友/新联系人
- 记录互动/见面/通话/吃饭
- 查询某人信息
- 谁很久没联系了
- 更新某人的信息
- 生日/纪念日相关
- 转述与某人的对话或经历（如"今天和小王吃饭，他说..."）
- 提到某人的新信息（如"小李换工作了"、"阿花下个月结婚"）
- 问"最近和谁见过面"、"上次见XX是什么时候"

## 核心理念
这不是冷冰冰的销售工具，而是帮用户做一个更有温度的人。
- 用户随口说的信息要主动捕捉并记录，不需要用户说"帮我记一下"
- 记录的是故事和细节，不是干巴巴的会议纪要
- 主动提醒生日和重要日期，不要等用户问

## 数据库字段

### 联系人表 (contacts_table_id)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| Personal CRM | Text | 主字段，填姓名 |
| 关系 | SingleSelect | 家人/女朋友/朋友/同事/领导/客户/合作伙伴/导师/其他 |
| 手机 | Phone | |
| 微信 | Text | |
| 邮箱 | Text | |
| 城市 | Text | |
| 公司 | Text | |
| 职位 | Text | |
| 生日 | DateTime | timestamp_ms，公历生日 |
| 农历生日 | Text | 如"1997年九月十三"，用于过农历生日的人 |
| 过农历生日 | Checkbox | 打勾=过农历生日，提醒时需转换当年公历 |
| 纪念日 | DateTime | timestamp_ms，恋爱纪念日、友谊纪念日等 |
| 纪念日说明 | Text | 这个纪念日是什么，如"恋爱纪念日" |
| 提醒提前天数 | Number | 生日/纪念日提前几天提醒，默认3天 |
| 爱好 | MultiSelect | 可自由新增 |
| 标签 | MultiSelect | 可自由新增 |
| 备注 | Text | 口味偏好、习惯、雷区、性格特点等 |
| 最后联系 | DateTime | timestamp_ms，每次记录互动时自动更新 |
| 联系频率 | SingleSelect | 每周/每月/每季度/偶尔 |
| 创建时间 | CreatedTime | 自动 |

### 互动记录表 (interactions_table_id)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 多行文本 | Text | 主字段，填事件简述（如"和小王深圳湾散步"） |
| 联系人 | Text | 填姓名 |
| 日期 | DateTime | timestamp_ms |
| 类型 | SingleSelect | 见面/通话/消息/会议/吃饭/邮件 |
| 要点 | Text | 聊了什么、发生了什么故事、对方分享的细节 |
| 后续 | Text | 需要跟进的事 |
| 氛围 | SingleSelect | 开心/平淡/深入/紧张/感动/尴尬 |
| 费用 | Number | 花销金额 |

## 操作指南

### 1. 添加联系人
从用户的自然语言中提取信息，调用：
```
feishu_bitable_create_record(
  app_token=<config.app_token>,
  table_id=<config.contacts_table_id>,
  fields={
    "Personal CRM": "姓名",
    "关系": "朋友",
    "城市": "深圳",
    ...只填用户提供的信息
  }
)
```

注意：
- DateTime 字段用 timestamp_ms（毫秒时间戳）
- MultiSelect 用数组
- 只填用户提供的信息，不要编造
- 创建后简洁确认，列出关键信息
- 如果用户提到生日，同时设置"提醒提前天数"默认为 3
- ⚠️ update_record 时只传需要更新的字段，不要传 null 值，避免清空已有数据

### 2. 记录互动
创建互动记录 + 更新联系人的"最后联系"日期：

步骤：
1. 先 list_records 联系人表，找到对应联系人的 record_id
2. create_record 到互动记录表
3. update_record 更新联系人的"最后联系"字段为当前时间

**智能捕捉：** 当用户随口转述与某人的经历时（如"今天和小王吃饭，他说他要结婚了"），应该：
- 自动创建互动记录（类型：吃饭，要点：他说要结婚了）
- 同时更新小王的备注（追加"计划结婚"等关键信息）
- 不需要用户明确说"帮我记录"

**要点写法：** 记录故事和细节，不是干巴巴的摘要。
- ❌ "讨论了工作情况"
- ✅ "他最近从腾讯跳到了字节，做大模型方向，说压力很大但很兴奋"

### 3. 查询联系人
调用 list_records 获取联系人列表，在结果中筛选匹配的记录。
展示格式：
```
💝 王明
├ 关系：朋友 | 公司：字节跳动 | 职位：算法工程师
├ 城市：深圳 | 微信：wangming
├ 生日：1995-03-15 | 纪念日：—
├ 爱好：摄影、旅游 | 标签：AI行业、大学同学
├ 最后联系：2026-02-20 | 联系频率：每月
└ 备注：不吃香菜，最近跳槽到字节做大模型
```

如果有互动记录，追加最近 3 条：
```
📅 最近互动：
├ 2026-02-20 吃饭 — 聊了跳槽的事，他很兴奋 [开心]
├ 2026-01-15 消息 — 问我借了本《深度学习》
└ 2025-12-31 见面 — 跨年聚会，一起倒数
```

### 4. 生日和纪念日提醒（定时任务）
每天检查所有联系人的生日和纪念日字段：

**检查逻辑：**
1. list_records 获取所有联系人
2. 如果"过农历生日"为 true：读取"农历生日"字段，转换为当年公历日期再比较
3. 如果"过农历生日"为 false/空：读取"生日"字段（公历），只比较月和日
4. 纪念日只看月和日
5. N = 提醒提前天数，默认3

**提醒格式：**
```
🎂 生日提醒
├ 明天：小美（女朋友）生日！[农历九月十三]
└ 根据备注和爱好给出简短送礼建议

💕 纪念日提醒
└ 3天后：和小美的恋爱纪念日（在一起2周年）
```

### 5. 关系维护提醒
检查"最后联系"和"联系频率"：
- 每周：超过 7 天未联系
- 每月：超过 30 天未联系
- 每季度：超过 90 天未联系
- 偶尔：超过 180 天未联系

```
⏰ 该联系了
├ 老王（朋友）— 45天未联系，约定每月 [超期15天]
└ 张总（客户）— 35天未联系，约定每月 [超期5天]
```

### 6. 更新联系人
1. list_records 找到联系人 record_id
2. update_record 更新指定字段
3. 如果是从对话中捕捉到的新信息，追加到备注而不是覆盖
4. ⚠️ 只传需要更新的字段，绝不传 null 值

### 7. 智能信息捕捉规则
当用户在对话中提到某人的新信息时，主动更新：

**触发词示例：**
- "XX换工作了" → 更新公司/职位
- "XX搬到上海了" → 更新城市
- "XX下个月结婚" → 追加到备注
- "XX的生日是3月15号" → 更新生日字段 + 设置提醒
- "今天和XX..." → 创建互动记录

**处理流程：**
1. 识别提到的人名
2. 在联系人表中查找匹配
3. 如果找到，更新相关字段或创建互动记录
4. 如果没找到，询问是否要添加为新联系人
5. 简洁确认已记录，不要长篇大论

## 交互风格
- 从自然语言中智能提取信息，不要逐字段询问
- 信息不完整时，一次性列出缺失的关键字段询问
- 创建/更新后简洁确认，不要重复所有字段
- 查询结果用结构化格式展示
- 记录互动时用有温度的语言，不是公文体
- 用户随口提到的信息也要捕捉，表现得像一个贴心的助手而不是数据库终端
