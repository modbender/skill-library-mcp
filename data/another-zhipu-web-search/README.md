# 智谱 Web Search Skill

使用智谱 AI 的 Web Search API 进行网络搜索的 Claude Code Skill。

## 功能特性

- 支持多种搜索引擎（智谱基础版/高阶版、搜狗、夸克）
- 智能搜索意图识别
- 可配置结果数量、时间范围、域名筛选等
- 结构化输出（标题、URL、摘要、网站名、图标等）

## 安装

### 1. 获取 API Key

访问 [智谱 BigModel 开放平台](https://bigmodel.cn/usercenter/apikeys) 获取您的 API Key。

### 2. 配置 API Key

```bash
export ZHIPUAI_API_KEY="your-api-key-here"
```

**重要**: 请使用环境变量方式配置 API Key，不要将密钥硬编码在脚本或配置文件中。

### 3. 在 Claude Code 中使用

将以下内容复制到您的项目根目录：
- `.claude/settings.json`（权限配置）
- `SKILL.md`（Skill 定义）
- `search_util.py`（搜索工具）
- `requirements.txt`（Python 依赖）

或者直接在 OpenClaw 安装后使用。

## 使用方法

### 在 Claude Code 中

当您需要搜索网络信息时，直接告诉 Claude，它会自动调用此 Skill。

### 命令行方式

```bash
# 基本搜索
python search_util.py "搜索内容"

# 更多选项
python search_util.py "人工智能最新发展" \
  --engine pro \
  --count 15 \
  --recency week \
  --content-size high

# 查看帮助
python search_util.py --help
```

## 搜索引擎选项

| 选项 | 说明 |
|-----|------|
| `pro` | 智谱高阶版（推荐） |
| `std` | 智谱基础版 |
| `sogou` | 搜狗搜索 |
| `quark` | 夸克搜索 |

## 时间筛选选项

| 选项 | 说明 |
|-----|------|
| `day` | 一天内 |
| `week` | 一周内 |
| `month` | 一个月内 |
| `year` | 一年内 |
| `all` | 不限（默认） |

## 目录结构

```
.
├── SKILL.md              # Skill 定义
├── search_util.py         # 搜索工具
├── README.md              # 使用说明
├── requirements.txt       # Python 依赖
└── .claude/
    └── settings.json      # 权限配置
```

## 更多信息

- [智谱 Web Search API 文档](https://bigmodel.cn/dev/api/search-tool/web-search)
- [产品价格](https://www.bigmodel.cn/pricing)

## 许可证

本项目仅供学习和分享使用。
