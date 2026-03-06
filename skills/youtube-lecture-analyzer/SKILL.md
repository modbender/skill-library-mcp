---
name: YouTube 讲座字幕分析器
description: 提取讲座核心结构、关键观点、证据与可执行行动，用于复盘/写作/教学。
---

# YouTube 讲座字幕分析器

提取讲座核心结构、关键观点、证据与可执行行动，用于复盘/写作/教学。

## 使用方式

```bash
# 基础用法
python scripts/analyze_lecture.py <YouTube视频ID或URL>

# 指定语言优先级
python scripts/analyze_lecture.py <YouTube视频ID或URL> "zh-cn,en"

# 仅获取摘要
python scripts/analyze_lecture.py <YouTube视频ID或URL> --summary-only
```

## 输出格式

### 强制规则
1. 只基于字幕，不要补充；不确定要标注【不确定】
2. 先去噪：合并重复观点、删除口头禅、修正口误
3. 每个关键结论附【原文短引文】10–30字
4. 区分：事实(Fact) / 观点(Claim) / 推断(Inference) / 建议(Recommendation)

### 输出结构
- A) 一句话总论（≤25字）
- B) 讲座结构地图（3–6段）
- C) 5个关键问题及回答
- D) 核心概念与关系
- E) 可执行提炼（行动清单）
- F) 亮点与反直觉
- G) 盲区与待验证
- 摘要（中文200字 + 英文200字）

## 依赖
- youtube-transcript-api
- HTTP 代理：127.0.0.1:26739
