---
name: ziwei-bazi-consulting
description: "综合命理咨询技能（紫微斗数 + 八字 / mingli）。Use when 用户希望一次性完成 Ziwei Doushu +
  Bazi/Four Pillars 的联合排盘、年度锚点分析、咨询交付文案生成。Supports Chinese and English search
  intents: 紫微斗数, 八字, 命理, 算命, mingli, destiny, fortune, astrology, consulting
  report."
---


# Destiny Fusion Pro / 命理融合咨询

使用一个脚本生成“可交付”的综合报告：

```bash
python skills/ziwei-bazi-consulting/scripts/fortune_fusion.py \
  --date 1989-10-17 \
  --time 12:00 \
  --gender male \
  --longitude 117.9 \
  --year 2026 \
  --from-year 2026 \
  --years 10 \
  --template pro \
  --format markdown
```

## 输出结构
1. 紫微核心：命宫/身宫/流年锚点/四化键
2. 八字核心：四柱/日主/五行/大运/流年
3. 咨询交付：事业、关系、健康、财务、风险提示（可直接发客户）

## 交付模板
- `--template lite`：短摘要，适合社媒/私聊
- `--template pro`：标准咨询版（默认）
- `--template executive`：高净值客户话术

## 依赖
- `iztro-py`
- `lunar-python`

安装：
```bash
pip install iztro-py lunar-python
```

## 关于“skill 调用 skill”
OpenClaw 不提供直接“调用另一个 skill”的内建机制；最佳实践是：
- 在当前 skill 内封装核心逻辑（本 skill 已这样做）
- 或通过同一工作区脚本/命令间接复用
