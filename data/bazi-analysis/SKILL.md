---
name: bazi-analysis
description: 八字排盘专业版技能。Use when 用户要按出生日期时间做四柱（年/月/日/时）排盘，查看日主、十神、藏干、纳音、旬空、命宫/身宫/胎元、起运与大运、近年流年，并输出 markdown/json 结构化报告与用神忌神建议。
---

# Bazi Analysis Skill

使用 `scripts/bazi_chart.py` 生成八字增强盘。

## 输入
- 出生日期：`YYYY-MM-DD`
- 出生时间：`HH:MM`
- 性别：`male/female/男/女`

## 运行

```bash
python skills/bazi-analysis/scripts/bazi_chart.py \
  --date 1989-10-17 \
  --time 12:00 \
  --gender male \
  --format markdown
```

可选参数：
- `--from-year 2026 --years 10` 生成近年流年干支
- `--sect 1|2` 切换流派参数（默认 2）

结构化输出：

```bash
python skills/bazi-analysis/scripts/bazi_chart.py \
  --date 1989-10-17 \
  --time 12:00 \
  --gender male \
  --format json
```

## 输出要求
1. 先给排盘事实（四柱、日主）
2. 再给五行分布（木火土金水）
3. 最后给解释与建议（趋势语言，不做绝对断言）

## 依赖
- `lunar_python`
- 安装：`pip install lunar-python`

更多说明见 `references/notes.md`。
