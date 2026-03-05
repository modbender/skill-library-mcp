---
name: jisu-astro
description: 使用极速数据星座运势 API 查询十二星座列表以及每日、每周、每月、每年星座运势。
metadata: { "openclaw": { "emoji": "✨", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

## 极速数据星座运势（Jisu Astro）

基于 [星座运势 API](https://www.jisuapi.com/api/astro/) 的 OpenClaw 技能，支持：

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/astro/

- **星座列表**（`/astro/all`）：获取 12 星座的 ID、名称、日期范围和图标。
- **星座运势查询**（`/astro/fortune`）：按星座 ID 和日期查询今日、明日、本周、本月、本年星座运势。

可用于对话中回答「我是什么座」「今天白羊座运势怎样」「帮我看看这个月的感情/工作运」等问题。

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/astro/astro.py`

## 使用方式与请求参数

### 1. 获取星座列表（/astro/all）

```bash
python3 skills/astro/astro.py all
```

返回结果示例（节选自 [官方文档](https://www.jisuapi.com/api/astro/)）：

```json
[
  {
    "astroid": "1",
    "astroname": "白羊座",
    "date": "3-21~4-19",
    "pic": "http://api.jisuapi.com/astro/static/images/baiyang.png"
  },
  {
    "astroid": "2",
    "astroname": "金牛座",
    "date": "4-20~5-20",
    "pic": "http://api.jisuapi.com/astro/static/images/jinniu.png"
  }
]
```

字段说明：

- `astroid`：星座 ID（1–12）
- `astroname`：星座名称（如 白羊座、金牛座）
- `date`：星座日期范围
- `pic`：星座图标地址

### 2. 星座运势查询（/astro/fortune）

```bash
python3 skills/astro/astro.py fortune '{"astroid":1,"date":"2016-01-19"}'
```

请求 JSON 示例：

```json
{
  "astroid": 1,
  "date": "2016-01-19"
}
```

| 字段名  | 类型 | 必填 | 说明                          |
|---------|------|------|-------------------------------|
| astroid | int  | 是   | 星座 ID（1–12）               |
| date    | string | 否 | 日期（`YYYY-MM-DD`），默认今天 |

返回结果示例（节选自 [官方文档](https://www.jisuapi.com/api/astro/)）：

```json
{
  "astroid": "1",
  "astroname": "白羊座",
  "year": {
    "date": "2016",
    "summary": "未来一年将是白羊座历经艰辛终于寻得新的突破的一年。",
    "money": "上半年收入还算稳定，但也不太会有意料之外的收入，需要花钱的地方倒是不少。",
    "career": "十月之前，都相对还是白羊座的蛰伏期。",
    "love": "与事业运类似，今年的桃花运也主要集中在下半年爆发。"
  },
  "week": {
    "date": "2016-01-17~01-23",
    "money": "偏财机会继续受重视。本职工作收入受压。",
    "career": "太阳本周转入朋友宫，对事业的执着感下调，会寻觅新的圈子。",
    "love": "一夜情几率高……",
    "health": "性能量高强，小心纵欲伤身。",
    "job": "方向有变，高新行业值得你更多关注。"
  },
  "today": {
    "date": "2016-01-19",
    "presummary": "你需要思考自身价值观是否符合当下环境。",
    "star": "处女座",
    "color": "黄色",
    "number": "5",
    "summary": "4",
    "money": "4",
    "career": "4",
    "love": "3",
    "health": "80%"
  },
  "tomorrow": {
    "date": "2016-01-20",
    "presummary": "今天你有些悲观哦。",
    "star": "巨蟹座",
    "color": "青绿色",
    "number": "4",
    "summary": "3",
    "money": "3",
    "career": "3",
    "love": "3",
    "health": "77%"
  },
  "month": {
    "date": "2016-1",
    "summary": "本月，事业对你而言是非常重要的。",
    "money": "火星入资源宫，热烈关注偏财。",
    "career": "木星上旬开启在工作宫的逆行……",
    "love": "心灵刹那的触动和性的爆发，高度吻合。"
  }
}
```

常见字段：

- 顶层：`astroid`, `astroname`
- `today` / `tomorrow`：`date`, `presummary`, `star`（贵人星座）, `color`, `number`, `summary`, `money`, `career`, `love`, `health`
- `week` / `month` / `year`：`date`, `summary`, `money`, `career`, `love`, 以及本周的 `job`、`health` 等。

脚本不会对内容做拆分或转换，而是原样返回 `result`，方便代理按需挑选段落进行摘要或重写。

## 常见错误码

来自 [官方星座运势文档](https://www.jisuapi.com/api/astro/) 的业务错误码：

| 代号 | 说明        |
|------|-------------|
| 201  | 日期不正确  |
| 202  | 星座 ID 不正确 |
| 203  | 没有信息    |

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

1. 用户提供生日或星座问题：「1995-04-10 是什么座？今天和本周运势如何？」  
2. 代理先调用：`astro all` 获取 12 星座的日期范围，基于生日确定用户星座对应的 `astroid`。  
3. 然后调用：`astro fortune '{"astroid":1,"date":"2025-03-02"}'` 获取白羊座的今日/本周/本月/本年运势。  
4. 从返回结构中选择合适粒度（例如今日 + 本周 + 本月），对 `summary`、`money`、`career`、`love`、`health` 等字段进行整理和摘要，用自然语言给出贴合用户问题的解读。  

