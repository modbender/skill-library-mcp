---
name: CoPAW 银登公告与结果爬取 Skill
description: 这是一个用于 CoPAW (Copilot Automation Workflow) 的标准
  Skill，支持自动爬取银登网不良贷款转让公告及转让结果，并利用大模型（LLM）提取关键数据。
---

# CoPAW 银登公告与结果爬取 Skill

这是一个用于 CoPAW (Copilot Automation Workflow) 的标准 Skill，支持自动爬取银登网不良贷款转让公告及转让结果，并利用大模型（LLM）提取关键数据。

## 目录结构
```
yindeng_skill/
├── skill.py             # 标准 Skill 接口 (Agent/Tool Use)
├── skill.json           # Skill 元数据定义
├── main.py              # CLI 入口脚本
├── crawler.py           # 核心爬虫逻辑
├── ocr_utils.py         # OCR 与数据汇总工具
├── requirements.txt     # 依赖清单
└── SKILL.md             # 说明文档
```

## Agent 集成 (CoPaw / Tool Use)

本 Skill 提供了标准的 Python 函数接口和 JSON Schema 定义，可供 AI Agent 直接调用。

### Python 接口
```python
from skill import run_yindeng_crawler

# 爬取并分析
result = run_yindeng_crawler(source="result", analyze=True)
print(result)
```

### Skill 定义 (skill.json)
包含完整的工具描述和参数定义，符合 OpenAI/Anthropics Tool Schema 标准。

## 功能特性
1. **多任务支持**：可同时爬取“转让公告”和“转让结果公告”。
2. **自动爬取**：根据日期（自动计算或指定）爬取银登网公告并下载 PDF。
3. **智能分析**：支持多模型（DeepSeek、千问、硅基流动等）提取 PDF 中的关键金融数据。
4. **数据导出**：
   - 爬取记录 Excel
   - 债权转让证明信息汇总（仅结果公告，含 OCR 数据）
   - LLM 分析结果报表 (`analysis_result.xlsx`)

## 部署与使用

### 1. 安装依赖
在运行环境或 Docker 容器中安装 Python 依赖（需提前安装 Tesseract-OCR 和 Poppler）：
```bash
pip install -r requirements.txt
```

### 2. 环境变量配置 (LLM)
设置以下环境变量以启用 LLM 分析功能。本 Skill 支持多种 LLM 提供商。

#### 通用配置
- `LLM_API_KEY`: **(必须)** 您的 API Key。
- `LLM_PROVIDER`: (可选) 指定服务商，如 `deepseek`, `siliconflow`, `qwen`。默认为 `deepseek`。
- `LLM_API_BASE`: (可选) API 基础地址。
- `LLM_MODEL`: (可选) 模型名称。

#### 常用服务商配置示例

**DeepSeek (默认)**
```bash
export LLM_API_KEY="sk-..."
export LLM_PROVIDER="deepseek"
# 默认 BASE: https://api.deepseek.com/v1
# 默认 MODEL: deepseek-chat
```

**硅基流动 (SiliconFlow)**
```bash
export LLM_API_KEY="sk-..."
export LLM_PROVIDER="siliconflow"
# 默认 BASE: https://api.siliconflow.cn/v1
# 默认 MODEL: deepseek-ai/DeepSeek-V3
```

**通义千问 (DashScope/Aliyun)**
```bash
export LLM_API_KEY="sk-..."
export LLM_PROVIDER="qwen"
# 默认 BASE: https://dashscope.aliyuncs.com/compatible-mode/v1
# 默认 MODEL: qwen-plus
```

### 3. 调用方式

**默认运行（爬取公告 + 结果）：**
```bash
python main.py
```

**仅爬取转让结果：**
```bash
python main.py --source result
```

**爬取并启用 LLM 分析：**
```bash
python main.py --analyze
```

**指定日期运行：**
```bash
python main.py 2026-03-03
```

## 输出结果
- **转让公告**: `YYYY-MM-DD银登公告/`
- **转让结果**: `YYYY-MM-DD银登公告结果/`
  - `*债权转让证明信息汇总.xlsx`: 包含 OCR 识别后的结构化数据。
  - `analysis_result.xlsx`: 包含 LLM 提取的深度分析数据。

## 退出码说明
- `0`: 成功且有新数据。
- `2`: 成功但**暂无更新**（所有任务均无新增数据）。
- `1`: 运行出错。
