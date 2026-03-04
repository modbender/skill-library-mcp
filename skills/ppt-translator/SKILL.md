---
name: ppt-translator
description: Translate PowerPoint files to any language while preserving layout. Uses a render-and-verify agent loop (LibreOffice + Vision) to guarantee no text overflow. Activate when user wants to translate a PPT/PPTX file.
---

# 🎯 PPT Translator

保持排版翻译 PPT，支持任意语言对。

## 核心原理

**Agent Loop（渲染验证）：**
1. 提取 PPT 文字 + 样式
2. LLM 翻译（保证准确）
3. 写回 PPT（python-pptx）
4. LibreOffice 渲染成真实 PNG
5. Vision 模型检测文字溢出
6. 有溢出 → 缩字号 15% → 回步骤 3
7. 通过 → 输出最终 PPTX

## 依赖

- `python-pptx`（pip）
- `libreoffice`（yum/apt）

## 使用方法

```bash
python3 scripts/translate.py \
  --input /path/to/file.pptx \
  --output /path/to/output.pptx \
  --translations '{"原文": "translation", ...}' \
  --max-iter 5
```

## Agent 调用流程

1. 用户发送 PPTX 文件
2. Agent 提取所有文字 → 翻译（自己翻译或调用 LLM）
3. 调用 `scripts/translate.py` 执行渲染验证循环
4. 循环完成后将输出 PPTX 发回用户

## 输出

- 最终 PPTX 文件（可编辑）
- 渲染验证 PNG（可选，用于确认）
- 迭代日志（几轮收敛、最终字号缩放比）

## 注意事项

- LibreOffice 首次启动较慢（~5s），之后正常
- 字号缩放是全局的（所有 shape 等比缩），未来可优化为 per-shape
- 不支持 .ppt（老格式），仅支持 .pptx
