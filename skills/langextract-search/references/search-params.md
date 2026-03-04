# 搜索参数配置详解

本文档详细说明 `conf.json` 中搜索相关的配置参数。当默认配置无法满足需求时，参考此文档进行自定义配置。

## 智谱 AI 搜索配置 (zhipu_search)

### 基础配置

| 参数 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| `enabled` | boolean | `true` | 否 | 是否启用智谱搜索 |
| `apiKey` | string | - | 是 | API Key（支持环境变量名或实际密钥） |

### 搜索引擎 (search_engine)

| 值 | 说明 | 特点 |
|----|------|------|
| `search_std` | 智谱基础版搜索引擎 | 支持全部参数 |
| `search_pro` | 智谱高阶版搜索引擎（默认） | 支持全部参数，效果更好 |
| `search_pro_sogou` | 搜狗搜索 | count 仅支持 10/20/30/40/50 |
| `search_pro_quark` | 夸克搜索 | 仅支持 timelimit、content_size |

### 结果数量 (count)

- **类型**: number
- **范围**: 1-50
- **默认值**: 15
- **说明**: 返回搜索结果的数量。数量越大，消耗的 token 越多。

### 时间过滤 (timelimit)

统一格式，自动映射到智谱原生格式：

| 配置值 | 智谱原生值 | 说明 |
|--------|-----------|------|
| `day` | `oneDay` | 一天内 |
| `week` | `oneWeek` | 一周内 |
| `month` | `oneMonth` | 一个月内 |
| `year` | `oneYear` | 一年内 |
| `null` | `noLimit` | 不限时间（默认） |

### 内容长度 (content_size)

| 值 | 说明 |
|----|------|
| `medium` | 返回摘要信息，满足基础推理需求 |
| `high` | 最大化上下文，信息量大，适合需要细节的场景（默认） |

### 域名过滤 (search_domain_filter)

- **类型**: string | null
- **默认值**: null
- **示例**: `"www.example.com"`
- **说明**: 限定搜索结果只来自指定域名，null 表示不限制

---

## DuckDuckGo 搜索配置 (duckduckgo_search)

### 基础配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | boolean | `true` | 是否启用 DuckDuckGo 搜索 |
| `maxResults` | number | `20` | 返回结果数量 |
| `timeout` | number | `10` | 请求超时（秒） |

### 地区代码 (region)

| 代码 | 地区 |
|------|------|
| `cn-zh` | 中国 |
| `us-en` | 美国 |
| `uk-en` | 英国 |
| `jp-jp` | 日本 |
| `kr-kr` | 韩国 |
| `de-de` | 德国 |
| `fr-fr` | 法国 |
| `ru-ru` | 俄罗斯 |
| `wt-wt` | 无地区限制（默认） |

### 安全搜索 (safesearch)

| 值 | 说明 |
|----|------|
| `on` | 严格过滤成人内容 |
| `moderate` | 适度过滤（默认） |
| `off` | 不过滤 |

### 时间过滤 (timelimit)

统一格式，自动映射到 DDGS 原生格式：

| 配置值 | DDGS 原生值 | 说明 |
|--------|------------|------|
| `day` | `d` | 一天内 |
| `week` | `w` | 一周内 |
| `month` | `m` | 一个月内 |
| `year` | `y` | 一年内 |
| `null` | `None` | 不限时间（默认） |

### 搜索后端 (backend)

| 值 | 说明 |
|----|------|
| `auto` | 自动选择最佳引擎（默认） |
| `bing` | 使用 Bing 搜索 |
| `google` | 使用 Google 搜索 |
| `duckduckgo` | 使用 DuckDuckGo 搜索 |
| `brave` | 使用 Brave 搜索 |
| `yandex` | 使用 Yandex 搜索 |
| `yahoo` | 使用 Yahoo 搜索 |
| `wikipedia` | 使用 Wikipedia |

可组合多个后端：`"bing,google,duckduckgo"`

### 代理设置 (proxy)

- **类型**: string | null
- **默认值**: null
- **示例**:
  - `"http://127.0.0.1:7890"` - HTTP 代理
  - `"socks5://127.0.0.1:1080"` - SOCKS5 代理
  - `"tb"` - Tor Browser（等同于 `socks5://127.0.0.1:9150`）

---

## DuckDuckGo 搜索运算符

在搜索查询中可以使用以下运算符：

| 运算符 | 示例 | 说明 |
|--------|------|------|
| 空格 | `cats dogs` | OR 搜索 |
| 引号 | `"cats and dogs"` | 精确匹配 |
| `-` | `cats -dogs` | 排除词 |
| `+` | `cats +dogs` | 强调词 |
| `filetype:` | `cats filetype:pdf` | 文件类型（pdf/doc/xls/ppt/html） |
| `site:` | `dogs site:example.com` | 指定站点 |
| `-site:` | `cats -site:example.com` | 排除站点 |
| `intitle:` | `intitle:dogs` | 标题包含 |
| `inurl:` | `inurl:cats` | URL 包含 |

---

## 配置示例

### 最小配置（使用默认值）

```json
{
  "zhipu_search": {
    "enabled": true,
    "apiKey": "YOUR_API_KEY"
  },
  "duckduckgo_search": {
    "enabled": true
  }
}
```

### 完整配置

```json
{
  "zhipu_search": {
    "enabled": true,
    "apiKey": "ZHIPU_SEARCH_API_KEY",
    "search_engine": "search_pro",
    "count": 15,
    "timelimit": null,
    "content_size": "high",
    "search_domain_filter": null
  },
  "duckduckgo_search": {
    "enabled": true,
    "maxResults": 20,
    "region": "wt-wt",
    "safesearch": "moderate",
    "timelimit": null,
    "backend": "auto",
    "proxy": null,
    "timeout": 10
  }
}
```

### 只搜索最近一周的中文结果

```json
{
  "zhipu_search": {
    "enabled": true,
    "apiKey": "YOUR_API_KEY",
    "timelimit": "week"
  },
  "duckduckgo_search": {
    "enabled": true,
    "region": "cn-zh",
    "timelimit": "week"
  }
}
```

### 使用代理访问

```json
{
  "duckduckgo_search": {
    "enabled": true,
    "proxy": "http://127.0.0.1:7890",
    "timeout": 30
  }
}
```
