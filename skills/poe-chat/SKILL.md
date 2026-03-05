---
name: poe-chat
description: 使用 @gemini/@gpt/@claude 等触发词调用 Poe 模型（含 Gemini/GPT/claude/kimi/Deepseek等主流模型），自动选择 model_id 并说明使用了哪一个，支持文件上传。
---

# Poe Chat Skill

## 适用场景
- 用户输入包含 `@gemini`、`@gpt` 等 @触发词，希望用 Poe 上的具体模型回答问题。
- 需要自动匹配最合适的具体模型名称（例如 gemini-3-flash）。
- 支持把本地文件上传给模型分析。

## 使用方式

### 1) 安装依赖（只需一次）
```bash
pip install -r scripts/requirements.txt
```

如系统没有 `python` 命令，请改用 `python3` 执行下列命令。

### 2) 设置 Poe API Key（如未设置）
```bash
export POE_API_KEY="your_api_key"
```

也可以在调用时通过 `--api-key` 传入（优先生效）。

### 3) 查看可用模型（独立脚本）
```bash
python scripts/list_models.py
```

默认会在当前目录生成精简版 `models.json`（仅包含 `id`），并作为本地缓存（缓存时间 1 小时，基于文件修改时间）。

也可指定输出文件名：
```bash
python scripts/list_models.py --out models.json
```

如需查看完整模型信息（如 description 等），使用 `--full`：
```bash
python scripts/list_models.py --full --out models-full.json
```

### 4) 根据模型列表选择模型 ID

从 `models.json` 中选择要使用的模型 ID：
- 重点字段是 `data[].id`（这就是 `model_id`）
- 可结合 `data[].description` 判断用途和能力

示例（手动选择）：
```json
{
  "data": [
    {"id": "gemini-3-pro", "description": "..."},
    {"id": "claude-opus-4.6", "description": "..."}
  ]
}
```

当用户输入 `@gemini ...` 时，选择包含 `Gemini` 的模型，并遵循以下优先级：
1. **默认优先非 Pro**（例如优先 `gemini-3-flash` 而不是 `gemini-3-pro`）
2. **优先最新版本号**（例如 2.5 优于 2.0）
3. **只有用户明确要求 Pro/Ultra 时才选 Pro/Ultra**（例如用户输入 `@gemini-pro` 或明确说“用Pro”）

### 5) 调用脚本（直接传入模型 ID）
```bash
python scripts/poe_client.py \
  --message "请解释量子计算" \
  --model-id "gemini-3-flash" \
  --api-key "your_api_key" \
  --file "/path/to/document.pdf"
```

**说明**：
- `--message` 必填，内容中包含 `@xxx` 触发词即可（如 @gemini、@gpt）。
- `--file` 可选，可重复多次上传多个文件。

## 行为准则
1. **解析触发词**：从用户消息中提取第一个 `@xxx` 触发词。
2. **模型选择**：根据 `models.json` 里的 `data[].id` 手动选择最相关的具体模型。
3. **模型列表**：通过 `list_models.py` 获取模型列表，内存缓存 1 小时（不持久化）。
4. **API Key**：若环境变量 `POE_API_KEY` 未设置，`poe_client.py` 会提示用户输入。
5. **文件上传**：如提供 `--file`，`poe_client.py` 使用 `fastapi-poe` 上传并附加到请求。
6. **响应输出**：回答正文前必须标注 **具体模型名**（例如 `Model used: gemini-3-flash`）。

## 输出格式
```
Model used: <具体模型名>

<模型回答内容>
```

如存在模型返回的附件，列出附件信息（名称、类型、URL）。
