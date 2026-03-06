---
name: langextract-search
description: 集成智谱搜索、DuckDuckGo 搜索和多模型结构化提取的完整工作流。
license: Apache-2.0
---

# LangExtract Search Skill

集成智谱搜索 + DuckDuckGo 搜索 + 多模型结构化提取的完整工作流。

## 功能特性

- 🔍 **智谱 AI 搜索**: 使用智谱 zai-sdk 进行网络搜索
- 🌐 **DuckDuckGo 搜索**: 备用搜索引擎（支持多后端：Bing/Google/Brave 等）
- 📝 **多模型提取**: 支持 OpenAI 通用协议
- 🔄 **完整工作流**: 搜索 → 提取 → 保存，一键完成
- ⚙️ **灵活配置**: 支持时间过滤、地区设置、代理等高级参数

## 前置条件

1. Python 3.8+
2. **ddgs**（DuckDuckGo 搜索库）
3. **requests**（HTTP 请求库）
4. 可选：配置 langextract 处理模型

## 安装

```bash
pip install requests ddgs langextract
```

参考 `conf.json.example` 配置模型

### 首次使用交互选择

如果未在 `openclaw.json` 中配置 `baseUrl`，首次运行时会自动提示选择套餐类型，选择结果保存到项目 `conf.json` 文件中。

## 快速开始

```bash
cd scripts
python search.py "搜索关键词" --verbose
```

## 使用方法

### 基本用法

```bash
python search.py "搜索关键词"
```

### 验证输入输出（详细模式）

```bash
python search.py "搜索关键词" --verbose
```

### 保存完整 JSON

```bash
python search.py "搜索关键词" --save-json
```

### 自定义 DuckDuckGo 结果数量

```bash
python search.py "搜索关键词" --ddg-max-results 30
```

### 所有选项

```bash
python search.py --help
```

## 搜索配置

搜索参数通过 `conf.json` 配置。默认配置开箱即用，无需额外设置。

### 默认配置（自动应用）

| 搜索引擎   | 默认结果数 | 时间过滤 | 其他            |
| ---------- | ---------- | -------- | --------------- |
| 智谱搜索   | 15 条      | 不限     | search_pro 引擎 |
| DuckDuckGo | 20 条      | 不限     | 自动选择后端    |

### 自定义配置

当默认配置不满足需求时（如需要时间过滤、地区设置、代理等），请参阅 **[references/search-params.md](references/search-params.md)** 获取完整参数说明。

常见自定义场景：

- 搜索最近一周/一月的内容：设置 `timelimit: "week"` 或 `"month"`
- 限定搜索地区：设置 `region: "cn-zh"` 或 `"us-en"`
- 使用代理访问：设置 `proxy: "http://127.0.0.1:7890"`
- 切换搜索后端：设置 `backend: "google"` 或 `"bing,google"`

## 更多信息

工作流详细说明、输出文件格式和故障排除，请参阅 **[references/workflow-details.md](references/workflow-details.md)**。
