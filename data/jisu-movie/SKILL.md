---
name: jisu-movie
description: 使用极速数据电影影讯 API 查询当前城市上映电影、电影放映的电影院、电影院放映的电影、电影详情、按城市获取电影院以及电影城市列表。
metadata: { "openclaw": { "emoji": "🎬", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

## 极速数据电影影讯（Jisu Movie）

基于 [电影影讯 API](https://www.jisuapi.com/api/movie/) 的 OpenClaw 技能，支持：

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/movie/

- **当前城市上映电影**（`/movie/on`）
- **电影放映的电影院**（`/movie/movietheater`）
- **电影院放映的电影**（`/movie/theatermovie`）
- **电影详情**（`/movie/detail`）
- **按城市获取电影院**（`/movie/theater`）
- **获取电影城市列表**（`/movie/city`）

非常适合在对话中回答「今天杭州有哪些上映的电影？」「附近哪家电影院在放某部电影？」「帮我查一下《盗梦空间》的详细信息」等问题。

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/movie/movie.py`

## 使用方式与请求参数

### 1. 当前城市上映电影（/movie/on）

```bash
python3 skills/movie/movie.py on '{"cityid":"382","city":"杭州","date":"2018-07-08"}'
```

请求 JSON 示例：

```json
{
  "cityid": "382",
  "city": "杭州",
  "date": "2018-07-08"
}
```

| 字段名 | 类型   | 必填 | 说明                         |
|--------|--------|------|------------------------------|
| cityid | int    | 否   | 城市 ID，和 `city` 任选其一 |
| city   | string | 否   | 城市名称，和 `cityid` 任选其一 |
| date   | string | 否   | 日期，默认当天（格式：YYYY-MM-DD） |

返回结果示例（结构与官网一致，截取部分字段）：

```json
{
  "city": "杭州",
  "cityid": "382",
  "date": "2018-07-08",
  "list": [
    {
      "movieid": "137363",
      "moviename": "我不是药神",
      "pic": "http://api.jisuapi.com/movie/upload/movie/14/137363.jpg"
    }
  ]
}
```

### 2. 电影放映的电影院（/movie/movietheater）

```bash
python3 skills/movie/movie.py movietheater '{"cityid":"382","city":"杭州","movieid":"137363","date":"2018-07-08"}'
```

请求 JSON 示例：

```json
{
  "cityid": "382",
  "city": "杭州",
  "movieid": "137363",
  "date": "2018-07-08"
}
```

| 字段名  | 类型     | 必填 | 说明                         |
|---------|----------|------|------------------------------|
| cityid  | string   | 否   | 城市 ID，和 `city` 任选其一 |
| city    | string   | 否   | 城市名称，和 `cityid` 任选其一 |
| movieid | string   | 是   | 电影 ID                      |
| date    | string   | 否   | 日期，默认当天（格式：YYYY-MM-DD） |

返回结果包含电影院列表，每项含 `theatername`、`address`、`issale`、`minprice`、`theaterid`、`lat`、`lng` 等字段。

### 3. 电影院放映的电影（/movie/theatermovie）

```bash
python3 skills/movie/movie.py theatermovie '{"theaterid":"2059","date":"2018-07-08"}'
```

请求 JSON 示例：

```json
{
  "theaterid": "2059",
  "date": "2018-07-08"
}
```

| 字段名    | 类型     | 必填 | 说明                         |
|-----------|----------|------|------------------------------|
| theaterid | string   | 是   | 电影院 ID                    |
| date      | string   | 否   | 日期，默认当天（格式：YYYY-MM-DD） |

返回结果中 `list` 为该影院当日影片列表，每个影片包含 `moviename`、`movieid`、`enname`、`director`、`actor`、`duration`、`class`、`year`，以及 `showlist` 场次列表（时间、语言、厅名、价格、购票链接等）。

### 4. 电影详情（/movie/detail）

```bash
python3 skills/movie/movie.py detail '{"movieid":"14","moviename":"盗梦空间"}'
```

请求 JSON 示例：

```json
{
  "movieid": "14",
  "moviename": "盗梦空间"
}
```

| 字段名    | 类型     | 必填 | 说明                              |
|-----------|----------|------|-----------------------------------|
| movieid   | string   | 否   | 电影 ID，和 `moviename` 任选其一 |
| moviename | string   | 否   | 电影名称，和 `movieid` 任选其一 |

返回结果示例（部分字段）：

```json
{
  "moviename": "盗梦空间",
  "movieid": "14",
  "enname": "Inception",
  "pic": "http://api.jisuapi.com/movie/upload/movie/1/14.jpg",
  "class": "动作 冒险 科幻",
  "year": "2010",
  "releasedate": "2010-09-01",
  "country": "美国",
  "director": "克里斯托弗·诺兰",
  "actor": "",
  "screenwriter": "克里斯托弗·诺兰",
  "publisher": "华纳兄弟影片公司",
  "summary": "",
  "screentype": "2D/IMAX",
  "duration": "148分钟"
}
```

### 5. 按城市获取电影院（/movie/theater）

```bash
python3 skills/movie/movie.py theater '{"cityid":"382","city":"杭州","keyword":"万达"}'
```

请求 JSON 示例：

```json
{
  "cityid": "382",
  "city": "杭州",
  "keyword": "万达"
}
```

| 字段名   | 类型     | 必填 | 说明                         |
|----------|----------|------|------------------------------|
| cityid   | string   | 否   | 城市 ID，和 `city` 任选其一 |
| city     | string   | 否   | 城市名称，和 `cityid` 任选其一 |
| keyword  | string   | 否   | 影院名称关键词，如“万达”         |

返回结果中 `list` 为影院列表，每项包含 `theaterid`、`theatername`、`tel`、`address`、`hours`、`seatnum`、`roomnum`、`logo`、`score`、`summary`、`lat`、`lng` 等字段。

### 6. 获取电影城市列表（/movie/city）

```bash
python3 skills/movie/movie.py city '{"parentid":"0"}'
```

请求 JSON 示例：

```json
{
  "parentid": "0"
}
```

| 字段名   | 类型     | 必填 | 说明                  |
|----------|----------|------|-----------------------|
| parentid | string   | 否   | 上级 ID，0 表示顶级省份 |

返回结果示例（部分）：

```json
[
  {
    "cityid": "1",
    "name": "北京",
    "parentid": "0",
    "parentname": "",
    "topname": "",
    "depth": "1"
  },
  {
    "cityid": "30",
    "name": "浙江",
    "parentid": "0",
    "parentname": "",
    "topname": "",
    "depth": "1"
  }
]
```

## 常见错误码

来自 [官方电影影讯文档](https://www.jisuapi.com/api/movie/) 的业务错误码：

| 代号 | 说明        |
|------|-------------|
| 201  | 城市和城市 ID 为空 |
| 202  | 城市不存在    |
| 203  | 影院 ID 为空  |
| 204  | 电影 ID 为空  |
| 205  | 电影 ID 不存在 |
| 206  | 电影院 ID 不存在 |
| 210  | 没有信息      |

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

1. 用户提出需求，例如：「帮我看看今天杭州有什么电影可以看，并找一场今晚 8 点左右的场次。」  
2. 代理先调用：`movie on` 获取当前城市上映电影列表，从中挑出热门影片供用户选择。  
3. 用户选定某部电影后，调用：`movie movietheater` 获取这部电影在附近城市的放映电影院及最低票价。  
4. 如需具体排片信息，再调用：`movie theatermovie` 查询某个电影院的当日场次列表，并根据 `starttime`、`price`、`hallname` 等字段为用户推荐合适场次和购票链接。  
5. 如用户只问某部电影的信息，可直接调用：`movie detail` 获取影片详细资料（导演、演员、片长、简介等），进行摘要回答。  

