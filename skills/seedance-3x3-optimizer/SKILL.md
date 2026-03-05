---
name: seedance-3x3-optimizer
description: 将普通剧情文本重写成适配 Seedance 的“3x3 法则”视觉化脚本（对峙/爆发/终结或和谐/裂痕/决裂，共 9 段）。当用户说“按 3x3/33 法则优化剧情”“把这段故事改成更有画面感的 Seedance 文本”“做成可直接粘贴的视频生成脚本”时使用。
---

# Seedance 3x3 Optimizer

> 来源参考：<https://x.com/ponyodong/status/2021534195659816995>

## 快速流程

1. 判断剧情类型：`action`（动作冲突）或 `emotion`（情感冲突）。
2. 提取输入中的核心信息：角色、场景、冲突、关键动作、结局。
3. 运行脚本生成 9 段视觉化文本（每段 50-120 字）。
4. 返回结果时附上可选参数建议（风格、镜头节奏、颜色对比）。

## 使用脚本

```bash
python3 /home/ubuntu/.openclaw/workspace/skills/seedance-3x3-optimizer/scripts/optimize_story.py \
  --story "少年在宗门大比被羞辱，最终拔剑逆袭" \
  --mode action \
  --title "宗门逆袭" \
  --style "玄幻电影感"
```

输出默认为 Markdown，可直接粘贴到 Seedance。

如需 JSON：

```bash
python3 /home/ubuntu/.openclaw/workspace/skills/seedance-3x3-optimizer/scripts/optimize_story.py \
  --story "兄妹因理念不同最终分道扬镳" \
  --mode emotion \
  --json
```

## 结果要求（重写标准）

- 不写抽象判断词（如“很强”“很伤心”），改写为可见细节（眼神、呼吸、环境反应、光线变化、物体状态）。
- 每一段都要有至少一个“可拍到”的元素：
  - 镜头/距离（推近、远景、背影、特写）
  - 物理细节（碎石、雨雾、衣角、汗水、裂纹）
  - 光色对比（冷暖、明暗、金紫等）
- 九段形成完整曲线，不要九段都在同一情绪强度。

## 段落模板

- `action`：对峙(1-3) → 爆发(4-6) → 终结(7-9)
- `emotion`：和谐(1-3) → 裂痕(4-6) → 决裂(7-9)

更细模板见：`references/3x3-patterns.md`
