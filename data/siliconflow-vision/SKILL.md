---
name: siliconflow-vision
description: |
  图片识别与分析工具。使用视觉大模型识别图片内容，输出详细客观的识别结果供主模型分析。当用户发图片时，主模型必须直接调用此 skill，然后基于识别结果进行分析和回答。支持 SiliconFlow（默认）、OpenAI、Anthropic 等多服务商。
---

# 图片识别与分析 Skill

## 工作流程

**用户发图片 → 主模型直接调用 skill → skill 识别图片 → skill 输出详细结果 → 主模型分析+网络搜索 → 给出准确回答**

## 核心原则（重要）

### 主模型必须遵守：

1. **必须调用 skill**：用户发图片时，主模型必须调用此 skill
2. **禁止直接回答**：不要用 OpenClaw 的 `image` 工具，不要跳过 skill
3. **skill 只识别**：skill 只做客观识别，不做分析解读
4. **主模型负责思考**：分析、联想、回答由主模型完成

### 正确流程：

```
用户: [图片] 这个 meme 笑点在哪？

主模型: python scripts/analyze_image.py meme.jpg
       ↓
Skill 输出: 详细识别结果（文字+元素）
       ↓
主模型: 基于识别结果进行分析
       - 如果需要背景知识 → 网络搜索
       - 如果需要验证 → 网络搜索
       ↓
主模型回答: 结合事实的准确解析
```

### 错误示范：

❌ 直接调用 `image` 工具回答
❌ 跳过 skill 自己猜测
❌ skill 做过多分析解读
❌ 不验证信息就回答

## 使用方式

### 脚本调用

```bash
# 基本用法（推荐）
python scripts/analyze_image.py /path/to/image.jpg

# 指定自定义问题
python scripts/analyze_image.py image.jpg -q "只提取文字"

# 智能模式（更精准，适合复杂图片）
python scripts/analyze_image.py meme.png -m smart

# 简短输出
python scripts/analyze_image.py screenshot.png -s

# 指定服务商
python scripts/analyze_image.py photo.jpg --provider openai
```

## 脚本参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `image` | 图片路径或 URL | `/path/to/image.jpg` |
| `-q, --question` | 自定义问题 | `-q "提取所有文字"` |
| `-m, --model` | 模型选择 | `-m smart` |
| `-s, --short` | 简短模式 | `-s` |
| `--provider` | 指定服务商 | `--provider openai` |
| `-c, --compress` | 压缩图片 | `-c` |

## 支持的服务商

| 服务商 | 默认模型 | 特点 | 配置键 |
|--------|----------|------|--------|
| **SiliconFlow** | deepseek-ai/deepseek-vl2 | 默认，快速稳定 | `siliconflow_api_key` |
| **OpenAI** | gpt-4o | 通用强大 | `openai_api_key` |
| **Anthropic** | claude-sonnet-4 | 推理能力强 | `anthropic_api_key` |

## 模型选择

| 模式 | 模型 | 速度 | 适用场景 |
|------|------|------|----------|
| **fast** | deepseek-ai/deepseek-vl2 | ~5秒 | 默认，详细识别日常图片 |
| **smart** | Qwen/Qwen2.5-VL-72B-Instruct | ~2分钟 | 复杂图片、图表、需要精准分析 |
| **balanced** | deepseek-ai/deepseek-vl 待测试 | 2-turbo |平衡速度与精度 |

## 配置说明

**文件**: `config/default.json`

```json
{
  "provider": "siliconflow",
  "api_key": "sk-xxx",
  "model": "fast"
}
```

**也可通过环境变量**:
- `SILICONFLOW_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

## Skill 输出格式（优化版）

当识别图片时，skill 会输出：

```
1. 图片类型：截图/表情包/聊天记录等
2. 清晰文字：完整提取所有文字
3. 画面元素：列出所有视觉元素
4. 整体布局：图片结构
5. 风格氛围：简约/搞笑/暗黑等
6. 其他细节：值得注意的元素
```

**重要原则**：
- 只做客观识别，不做分析解读
- 只做简单描述，不过度思考
- 文字必须完整准确
- 让主模型负责思考分析

## 错误处理

| 错误 | 解决方案 |
|------|----------|
| API key 失效 | 检查配置或环境变量 |
| 图片不存在 | 检查路径是否正确 |
| 超时 | 切换到 fast 模式重试 |
| 服务商不支持 | 切换到其他服务商 |

## 支持的图片类型

- 📸 **截图**：代码错误、聊天记录、网页
- 🎭 **表情包/Meme**：搞笑图片、网络梗图
- 📄 **文档**：表格、合同、发票、名片
- 📊 **图表**：数据可视化、流程图
- 🖼️ **照片**：风景、产品、人物

## 优化历史

**2026-02-04 优化**：
- ✅ 修改默认提示词为详细识别模式
- ✅ 要求完整提取所有清晰文字
- ✅ 要求描述画面元素和布局
- ✅ 明确禁止 skill 做分析解读
- ✅ 强调主模型负责思考分析
- ✅ 强制主模型使用 skill（禁止用 image 工具）

**2026-02-06 整合**：
- ✅ 合并 image-understand 功能
- ✅ 支持多服务商（SiliconFlow、OpenAI、Anthropic）
- ✅ 支持多种图片格式
- ✅ 支持图片 URL 和本地路径
