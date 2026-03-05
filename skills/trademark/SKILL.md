---
name: jisu-trademark
description: 使用极速数据商标信息 API，支持商标关键词搜索和商标详情查询，获取商标名称、申请人、国际分类、公告期号和商标图片等信息。
metadata: { "openclaw": { "emoji": "®️", "requires": { "bins": ["python3"], "env": ["JISU_API_KEY"] }, "primaryEnv": "JISU_API_KEY" } }
---

# 极速数据商标信息（Jisu Trademark）

基于 [商标信息 API](https://www.jisuapi.com/api/trademark/) 的 OpenClaw 技能，支持：

- **商标搜索**（`/trademark/search`）：按关键字、申请号、申请人等搜索商标；
- **商标详情**（`/trademark/detail`）：按申请/注册号 + 国际分类查询商标完整信息。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/trademark/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/trademark/trademark.py`

## 使用方式

### 1. 商标搜索（/trademark/search）

```bash
python3 skills/trademark/trademark.py search '{"keyword":"手机","pagenum":1,"pagesize":10}'
```

请求 JSON 示例：

```json
{
  "keyword": "手机",
  "pagenum": 1,
  "pagesize": 10,
  "ismatch": 0,
  "type": 1,
  "classid": "0"
}
```

### 2. 商标详情（/trademark/detail）

```bash
python3 skills/trademark/trademark.py detail '{"regno":"4952050","classid":"42"}'
```

请求 JSON 示例：

```json
{
  "regno": "4952050",
  "classid": "42"
}
```

## 请求参数

### 商标搜索

| 字段名   | 类型   | 必填 | 说明                                                                 |
|----------|--------|------|----------------------------------------------------------------------|
| keyword  | string | 是   | 关键词                                                               |
| pagenum  | int    | 是   | 当前页，默认 1，最大 40                                              |
| pagesize | int    | 是   | 每页数量，默认 10，最大 100                                          |
| ismatch  | int    | 否   | 关键词是否完全匹配，默认 0                                           |
| type     | string | 否   | 关键词类型：1商标名，2注册号，3申请人，4商标名/注册号/申请人任一匹配，默认 1 |
| classid  | string | 否   | 国际分类，0 为全部，非 0 时限定在指定类别，多类别用分号分隔                 |

### 商标详情

| 字段名  | 类型   | 必填 | 说明       |
|---------|--------|------|------------|
| regno   | string | 是   | 申请/注册号 |
| classid | string | 是   | 国际分类     |

## 返回结果示例（节选）

### 商标搜索

```json
{
  "keyword": "手机",
  "pagenum": "1",
  "pagesize": "20",
  "list": [
    {
      "name": "手机工坊 SHOUJIDIY",
      "regno": "13145424",
      "classid": "14",
      "appdate": "2013-08-27",
      "firsttrialno": "1430",
      "firsttrialdate": "2014-11-06",
      "announceno": "1442",
      "announcedate": "2015-02-07",
      "pic": "http://api.jisuapi.com/trademark/upload/201807/31173651574910.jpg",
      "agent": "杭州龙华知识产权代理有限公司",
      "status": "注册申请完成",
      "registrant": "浙江富春江移动通信科技有限公司"
    }
  ],
  "total": "2764"
}
```

### 商标详情

```json
{
  "regno": "4952050",
  "classid": "42",
  "appdate": "2005-10-19",
  "firsttrialno": "1156",
  "firsttrialdate": "2009-02-20",
  "announceno": "1168",
  "announcedate": "2009-05-21",
  "startdate": "2009-05-21",
  "enddate": "2019-05-20",
  "iscommon": "0",
  "type": "一般",
  "pic": "http://api.jisuapi.com/trademark/upload/201807/29194006862201.jpg",
  "agent": "",
  "status": "",
  "name": "S",
  "registrant": "北京搜狗信息服务有限公司",
  "idcard": "",
  "address": "北京市海淀区中关村东路1号院9号楼搜狐网络大厦9层02房间",
  "productlist": [
    {
      "classid": "4220",
      "name": "计算机软件更新"
    }
  ],
  "processlist": [
    {
      "name": "商标注册申请中",
      "date": "2005-10-19"
    }
  ]
}
```

## 常见错误码

来源于 [官方商标文档](https://www.jisuapi.com/api/trademark/)：

| 代号 | 说明             |
|------|------------------|
| 201  | 关键词为空       |
| 202  | 注册号为空       |
| 203  | 分类 ID 为空     |
| 205  | 没有匹配的结果（扣次数） |
| 210  | 没有信息         |

系统错误码：

| 代号 | 说明                 |
|------|----------------------|
| 101  | APPKEY 为空或不存在  |
| 102  | APPKEY 已过期        |
| 103  | APPKEY 无请求权限    |
| 104  | 请求超过次数限制     |
| 105  | IP 被禁止            |

## 在 OpenClaw 中的推荐用法

1. 用户输入：「帮我查一下和‘手机工坊’相关的注册商标。」  
2. 代理构造 JSON：`{"keyword":"手机工坊","pagenum":1,"pagesize":10}` 并调用：  
   `python3 skills/trademark/trademark.py search '{"keyword":"手机工坊","pagenum":1,"pagesize":10}'`  
3. 从搜索结果中选取目标商标（根据名称、申请人、分类等），记下其 `regno` 和 `classid`，再调用 `detail` 子命令获取完整详情。  
4. 将商标状态、公告期号、分类和申请人等关键信息整理成自然语言说明给用户。  

