# 📸 Router Skill 视觉功能指南

**版本：** 1.0.0  
**日期：** 2026-03-02  
**状态：** ✅ 已实现

---

## ✅ 你的模型有图像理解功能！

**支持图像的模型：**

| 提供商 | 模型 | 图像支持 | 成本 |
|--------|------|----------|------|
| **Anthropic** | Claude-3-Opus | ✅ 支持 | $0.015/次 |
| **Anthropic** | Claude-3-Sonnet | ✅ 支持 | $0.003/次 |
| **Anthropic** | Claude-3-Haiku | ✅ 支持 | $0.00025/次 |
| **OpenAI** | GPT-4o | ✅ 支持 | $0.005/次 |
| **OpenAI** | GPT-4 Turbo | ✅ 支持 | $0.01/次 |
| **阿里云** | qwen-vl-max | ✅ 支持 | ¥0.03/次 |
| **阿里云** | qwen-vl-plus | ✅ 支持 | ¥0.01/次 |

**不支持的模型：**
- ❌ qwen2.5 系列（本地）
- ❌ qwen3.5-plus（纯文本）
- ❌ qwen3-max（纯文本）
- ❌ kimi-k2.5（纯文本）

---

## 🚀 快速开始

### 步骤 1: 配置 API Key

**选择你的视觉提供商：**

#### 选项 A: Anthropic Claude-3（推荐 ⭐⭐⭐⭐⭐）

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**优点：**
- ✅ 最强视觉理解
- ✅ 支持中文
- ✅ 便宜（Haiku 模型）

---

#### 选项 B: OpenAI GPT-4o

```bash
export OPENAI_API_KEY="sk-..."
```

**优点：**
- ✅ 多模态最强
- ✅ 支持中文
- ✅ 速度快

---

#### 选项 C: 阿里云 qwen-vl

```bash
export DASHSCOPE_API_KEY="sk-..."
```

**优点：**
- ✅ 国内访问快
- ✅ 支持中文好
- ✅ 便宜

---

### 步骤 2: 使用视觉功能

#### 方法 1: Python 代码

```python
from src.vision import VisionRecognizer

# 初始化（自动检测 API Key）
vision = VisionRecognizer()

# 分析图片
result = vision.analyze_image("screenshot.png", "描述这张截图")
print(result['content'])

# OCR 文字提取
text = vision.extract_text("document.png")
print(text)

# 描述截图
desc = vision.describe_screenshot("app_screenshot.png")
print(desc)
```

---

#### 方法 2: 快捷函数

```python
from src.vision import recognize_image, extract_text_from_image

# 快速识别
description = recognize_image("image.png")

# 快速 OCR
text = extract_text_from_image("document.png")
```

---

#### 方法 3: 命令行

```bash
# 分析图片
python -c "from src.vision import recognize_image; print(recognize_image('image.png'))"

# OCR
python -c "from src.vision import extract_text_from_image; print(extract_text_from_image('document.png'))"
```

---

## 📋 使用场景

### 场景 1: ClawHub 提交截图分析

```python
from src.vision import VisionRecognizer

vision = VisionRecognizer()

# 分析配置向导截图
result = vision.describe_screenshot("docs/screenshots/config_wizard.png")

print("截图内容：")
print(result['content'])

# 生成截图说明
print("\n截图说明：")
print("图 1: 配置向导界面")
print(result['content'][:200] + "...")
```

**输出示例：**
```
截图内容：
这是一个配置向导界面，显示：
1. 环境检测结果
   - Ollama: 已安装，发现 2 个模型
   - 阿里云百炼：已配置
2. 推荐配置
   - 主路由：qwen2.5:14b-32k (本地)
   - 验证器：dashscope/qwen3.5-plus (云端)
...

截图说明：
图 1: 配置向导界面
显示环境检测结果和推荐配置。检测到 Ollama 已安装，阿里云百炼已配置。推荐主路由使用本地 qwen2.5:14b 模型...
```

---

### 场景 2: UI 元素识别

```python
from src.vision import VisionRecognizer

vision = VisionRecognizer()

# 分析 UI 元素
result = vision.analyze_ui_elements("app_ui.png")

print("UI 元素分析：")
print(result['content'])
```

---

### 场景 3: 文档 OCR

```python
from src.vision import VisionRecognizer

vision = VisionRecognizer()

# 提取文档文字
text = vision.extract_text("document.png")

print("提取的文字：")
print(text)
```

---

## 💰 成本估算

### Anthropic Claude-3

| 模型 | 成本/次 | 100 次 | 1000 次 |
|------|---------|--------|---------|
| **Haiku** | $0.00025 | $0.025 | $0.25 |
| **Sonnet** | $0.003 | $0.3 | $3 |
| **Opus** | $0.015 | $1.5 | $15 |

**推荐：** Haiku（最便宜，适合 OCR 和简单分析）

---

### OpenAI GPT-4o

| 模型 | 成本/次 | 100 次 | 1000 次 |
|------|---------|--------|---------|
| **GPT-4o** | $0.005 | $0.5 | $5 |
| **GPT-4 Turbo** | $0.01 | $1 | $10 |

---

### 阿里云 qwen-vl

| 模型 | 成本/次 | 100 次 | 1000 次 |
|------|---------|--------|---------|
| **qwen-vl-plus** | ¥0.01 | ¥1 | ¥10 |
| **qwen-vl-max** | ¥0.03 | ¥3 | ¥30 |

---

## 🎯 推荐配置

### 最佳性价比

**提供商：** Anthropic Claude-3-Haiku

**理由：**
- ✅ 最便宜（$0.00025/次）
- ✅ 速度快
- ✅ 支持中文
- ✅ 足够用于截图分析

**月成本估算：**
- 100 次/月：$0.025（约¥0.18）
- 1000 次/月：$0.25（约¥1.8）
- 10000 次/月：$2.5（约¥18）

---

### 最佳质量

**提供商：** OpenAI GPT-4o 或 Claude-3-Opus

**理由：**
- ✅ 最强理解能力
- ✅ 支持复杂分析
- ✅ 准确率高

**月成本估算：**
- 100 次/月：$0.5-1.5
- 1000 次/月：$5-15
- 10000 次/月：$50-150

---

### 国内访问

**提供商：** 阿里云 qwen-vl

**理由：**
- ✅ 国内访问快
- ✅ 中文支持好
- ✅ 无需翻墙

**月成本估算：**
- 100 次/月：¥1
- 1000 次/月：¥10
- 10000 次/月：¥100

---

## 📊 功能对比

| 功能 | Claude-3 | GPT-4o | qwen-vl |
|------|----------|--------|---------|
| **图像理解** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **OCR 精度** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **中文支持** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **成本** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **国内访问** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🔧 高级用法

### 批量处理

```python
from src.vision import VisionRecognizer
from pathlib import Path

vision = VisionRecognizer()

# 批量分析截图
screenshot_dir = Path("docs/screenshots")
results = {}

for img_file in screenshot_dir.glob("*.png"):
    result = vision.describe_screenshot(str(img_file))
    results[img_file.name] = result['content']

# 保存结果
import json
with open("screenshot_descriptions.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"分析了 {len(results)} 张截图")
```

---

### 自定义提示词

```python
from src.vision import VisionRecognizer

vision = VisionRecognizer()

# 针对 ClawHub 提交优化提示词
prompt = """
分析这张截图，生成 ClawHub 提交用的截图说明。

要求：
1. 描述界面内容
2. 说明功能用途
3. 突出亮点
4. 100 字以内
"""

result = vision.analyze_image("screenshot.png", prompt)
print(result['content'])
```

---

### 错误处理

```python
from src.vision import VisionRecognizer

vision = VisionRecognizer()

try:
    result = vision.analyze_image("image.png")
    if result.get('success'):
        print("分析成功：", result['content'])
    else:
        print("分析失败，请检查 API Key 和图片格式")
except Exception as e:
    print(f"错误：{e}")
```

---

## ❓ 常见问题

### Q: 支持哪些图片格式？

**A:** 
- ✅ PNG（推荐）
- ✅ JPEG/JPG
- ✅ WebP
- ✅ GIF（静态）

---

### Q: 图片大小有限制吗？

**A:**
- Claude-3: 最大 5MB
- GPT-4o: 最大 20MB
- qwen-vl: 最大 10MB

**推荐：** 使用 PNG 格式，控制在 1MB 以内

---

### Q: 分析速度慢吗？

**A:**
- Claude-3-Haiku: 1-2 秒
- GPT-4o: 2-3 秒
- qwen-vl: 2-4 秒

---

### Q: 需要额外付费吗？

**A:** 
是的，视觉功能使用第三方 API，需要付费。

**但很便宜：**
- 最便宜的 Claude-3-Haiku：$0.00025/次（约¥0.0018/次）
- 100 次截图分析：约¥0.18

---

### Q: 可以离线使用吗？

**A:** 
不可以，视觉功能需要调用云端 API。

**如需离线：**
- 安装 PaddleOCR（免费，本地运行）
- 但只能 OCR，不能理解图像内容

---

## 🎉 总结

### 你有图像理解能力！

**支持的模型：**
- ✅ Claude-3 系列（最推荐）
- ✅ GPT-4o / GPT-4 Turbo
- ✅ 阿里云 qwen-vl

**成本：**
- 最便宜：¥0.0018/次（Claude-3-Haiku）
- 月成本：¥1-50（根据使用量）

**使用：**
```python
from src.vision import VisionRecognizer
vision = VisionRecognizer()  # 自动检测 API Key
result = vision.describe_screenshot("screenshot.png")
print(result['content'])
```

---

**现在你可以用视觉功能分析截图了！** 📸

---

_Guide Generated: March 2, 2026 01:55 GMT+8_  
_Version: 1.0.0_  
_Status: Implemented_
