---
name: jisu-recipe
description: 使用极速数据菜谱大全 API 按关键词或分类检索菜谱，并支持查询菜谱分类和菜谱详情。
metadata: { "openclaw": { "emoji": "🍳", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

## 极速数据菜谱大全（Jisu Recipe）

基于 [菜谱大全 API](https://www.jisuapi.com/api/recipe/) 的 OpenClaw 技能，支持：

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/recipe/

- **菜谱搜索**（`/recipe/search`）
- **菜谱分类**（`/recipe/class`）
- **按分类检索**（`/recipe/byclass`）
- **根据 ID 查询详情**（`/recipe/detail`）

适合在对话中回答「帮我找几个白菜的家常菜做法」「给我推荐减肥菜谱」「这道菜怎么做、用什么材料」等问题。

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/recipe/recipe.py`

## 使用方式与请求参数

### 1. 菜谱搜索（/recipe/search）

按关键词搜索菜谱，可指定起始条数和数量，返回菜谱列表及每道菜的详细信息。

```bash
python3 skills/recipe/recipe.py search '{"keyword":"白菜","num":10,"start":0}'
```

请求 JSON 示例：

```json
{
  "keyword": "白菜",
  "num": 10,
  "start": 0
}
```

| 字段名  | 类型   | 必填 | 说明                 |
|---------|--------|------|----------------------|
| keyword | string | 是   | 关键词（UTF-8）      |
| num     | int    | 是   | 获取数量             |
| start   | int    | 是   | 起始条数，默认 0     |

返回结果示例（结构与官网一致，截取部分字段）：

```json
{
  "num": "10",
  "list": [
    {
      "id": "8",
      "classid": "2",
      "name": "醋溜白菜",
      "peoplenum": "1-2人",
      "preparetime": "10-20分钟",
      "cookingtime": "10-20分钟",
      "content": "……",
      "pic": "http://api.jisuapi.com/recipe/upload/20160719/115138_46688.jpg",
      "tag": "减肥,家常菜,排毒,补钙",
      "material": [
        {
          "mname": "油",
          "type": "0",
          "amount": "适量"
        },
        {
          "mname": "白菜",
          "type": "1",
          "amount": "380g"
        }
      ],
      "process": [
        {
          "pcontent": "准备食材。",
          "pic": "http://api.jisuapi.com/recipe/upload/20160719/162550_84583.jpg"
        }
      ]
    }
  ]
}
```

### 2. 菜谱分类（/recipe/class）

获取菜谱分类树（如功效、减肥、美容等大类以及其子类）。

```bash
python3 skills/recipe/recipe.py class
```

无需额外 JSON 参数。

返回结果示例（部分）：

```json
[
  {
    "classid": "1",
    "name": "功效",
    "parentid": "0",
    "list": [
      {
        "classid": "2",
        "name": "减肥",
        "parentid": "1"
      }
    ]
  }
]
```

### 3. 按分类检索菜谱（/recipe/byclass）

按分类 ID 检索菜谱，可用于先通过 `/recipe/class` 获取分类，再按指定二级分类拉取菜谱列表。

```bash
python3 skills/recipe/recipe.py byclass '{"classid":2,"start":0,"num":10}'
```

请求 JSON 示例：

```json
{
  "classid": 2,
  "start": 0,
  "num": 10
}
```

| 字段名  | 类型 | 必填 | 说明                 |
|---------|------|------|----------------------|
| classid | int  | 是   | 分类 ID（二级 ID）   |
| start   | int  | 是   | 起始条数，默认 0     |
| num     | int  | 是   | 获取数量             |

返回结构与 `/recipe/search` 相同，也是 `num` 和 `list` 列表。

### 4. 菜谱详情（/recipe/detail）

根据菜谱 ID 获取某道菜的完整做法（包括材料、步骤、图片等）。

```bash
python3 skills/recipe/recipe.py detail '{"id":5}'
```

请求 JSON 示例：

```json
{
  "id": 5
}
```

| 字段名 | 类型 | 必填 | 说明   |
|--------|------|------|--------|
| id     | int  | 是   | 菜谱 ID |

返回结果示例（部分字段）：

```json
{
  "id": "5",
  "classid": "2",
  "name": "翡翠彩蔬卷",
  "peoplenum": "1-2人",
  "preparetime": "10分钟内",
  "cookingtime": "10分钟内",
  "content": "……",
  "pic": "http://api.jisuapi.com/recipe/upload/20160719/115138_19423.jpg",
  "tag": "减肥,咸香,宴请,抗氧化,抗衰老,私房菜,聚会",
  "material": [
    {
      "mname": "大白菜",
      "type": "1",
      "amount": "3片"
    },
    {
      "mname": "菠菜",
      "type": "1",
      "amount": "30g"
    }
  ],
  "process": [
    {
      "pcontent": "彩椒，红萝卜切丝",
      "pic": "http://api.jisuapi.com/recipe/upload/20160719/162546_72503.jpg"
    }
  ]
}
```

## 常见错误码

来自 [官方菜谱文档](https://www.jisuapi.com/api/recipe/) 的业务错误码：

| 代号 | 说明       |
|------|------------|
| 201  | 关键词为空  |
| 202  | 分类 ID 为空 |
| 203  | 详情 ID 为空 |
| 205  | 没有信息     |

系统错误码：

| 代号 | 说明                     |
|------|--------------------------|
| 101  | APPKEY 为空或不存在     |
| 102  | APPKEY 已过期           |
| 103  | APPKEY 无请求此数据权限 |
| 104  | 请求超过次数限制         |
| 105  | IP 被禁止               |
| 106  | IP 请求超过限制         |
| 107  | 接口维护中               |
| 108  | 接口已停用               |

## 在 OpenClaw 中的推荐用法

1. 用户提问：「帮我找几个减肥的白菜菜谱。」  
2. 代理可以先调用：`python3 skills/recipe/recipe.py class` 获取 `功效` → `减肥` 的 `classid`，或者直接使用关键词搜索：  
   `python3 skills/recipe/recipe.py search '{"keyword":"减肥 白菜","num":10,"start":0}'`。  
3. 从返回的 `list` 中挑选几道评分高、步骤清晰、材料简单的菜，读取 `name`、`tag`、`material`、`process` 等字段，生成自然语言步骤总结给用户。  
4. 若用户对某一道菜很感兴趣，可通过其 `id` 再调用：`python3 skills/recipe/recipe.py detail '{"id":<菜谱ID>}'` 获取完整详情，用于精细化讲解或分步烹饪指导。  

