---
name: public-apis-skill-creator
description: 公共API/免费API SKILL生成器：从 public-apis/public-apis 自动检索免费 API，按功能推荐并给出最小可用调用示例（curl/Python/JS），并可自动生成自定义名称的 API skill。用户提到“公共API”“免费API”“public APIs”“找接口/找API”“生成API skill”时触发。
---

# public-apis-skill-creator

## 能力
- 按功能关键词搜索 public-apis 仓库里的免费 API
- 输出 API 的认证要求、HTTPS、CORS、文档链接
- 自动生成最小可用示例（curl / Python / JavaScript）
- 自动生成“公共API/免费API”对应的 skill 包（名称可自定义）
- 查看并打印 public-apis 全量 API 列表（支持 --top / --json）

## 用法

### 1) 按功能找 API
```bash
bash {baseDir}/scripts/search_api.sh "weather forecast"
```

### 2) 自动推荐 + 生成调用模板（一步到位）
```bash
bash {baseDir}/scripts/solve_task.sh "weather api"
# 指定用推荐列表第 2 个 API
bash {baseDir}/scripts/solve_task.sh "weather api" --pick 2
# 可选：尝试对选中 API 做一次 GET 探测
bash {baseDir}/scripts/solve_task.sh "weather api" --pick 2 --try
```

### 3) 自动生成对应 skill（支持自定义名称）
```bash
bash {baseDir}/scripts/solve_task.sh "weather api" \
  --pick 2 \
  --make-skill \
  --skill-name weather-api-skill
```
会在 `skills/<skill-name>/` 下生成可直接使用的 skill 骨架。

### 4) 手动生成调用模板
```bash
bash {baseDir}/scripts/gen_usage.sh \
  --name "Open-Meteo" \
  --url "https://api.open-meteo.com/v1/forecast?latitude=39.9&longitude=116.4&hourly=temperature_2m" \
  --auth "No"
```

### 5) 打印 public-apis 全部列表
```bash
bash {baseDir}/scripts/list_all_apis.sh
# 只看前 50 条
bash {baseDir}/scripts/list_all_apis.sh --top 50
# JSON 输出
bash {baseDir}/scripts/list_all_apis.sh --json
```

## 典型请求示例
- "帮我找免费天气 API 并给 Python 示例"
- "找一个免费汇率 API，要求 HTTPS 且无需 key"
- "我想做新闻聚合，推荐 3 个 API 并比较"
- "基于公共API生成一个新免费天气 skill，名称叫 weather-free"
