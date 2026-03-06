---
name: ziwei-doushu
description: 紫微斗数专业版排盘技能。Use when 用户要求紫微斗数排盘、校验命宫/身宫、查看十二宫主辅星、命宫三方四正、按年份提取大运/流年锚点与四化信息，并输出 markdown/json 报告（支持经度修正）。
---

# Ziwei Doushu Skill

使用 `scripts/ziwei_chart.py` 生成稳定、可复现的紫微斗数排盘结果。

## 1) 收集输入

始终先确认这四项：
- 出生日期：`YYYY-MM-DD`
- 出生时间：`HH:MM`（24 小时制）
- 性别：`male/female`（或 `男/女`）
- 出生地经度（可选）：例如上饶约 `117.9`

如果用户不提供经度：照常排盘，但在结论里标注“未做真太阳时修正”。

## 2) 运行排盘脚本

```bash
python skills/ziwei-doushu/scripts/ziwei_chart.py \
  --date 1989-10-17 \
  --time 12:00 \
  --gender male \
  --longitude 117.9 \
  --year 2026 \
  --format markdown
```

若需要结构化结果供后续自动化处理：

```bash
python skills/ziwei-doushu/scripts/ziwei_chart.py \
  --date 1989-10-17 \
  --time 12:00 \
  --gender male \
  --longitude 117.9 \
  --format json
```

## 3) 输出规范

优先输出三层：
1. **排盘事实**：命宫、身宫、五行局、十二宫主星
2. **技术备注**：是否做经度修正、修正分钟数、时辰索引
3. **解释性结论**：基于命盘结构给出可执行建议（事业/健康/关系）

避免“绝对化预言”措辞，使用概率与趋势语气。

## 4) 依赖与故障处理

- 依赖：`iztro-py`
- 安装：`pip install iztro-py`
- 常见问题：
  - `ModuleNotFoundError: iztro_py` → 安装依赖并重试
  - 时间边界（23:00~01:00）→ 明确提醒用户子时跨日敏感

## 5) 参考

需要解释“时辰索引”“经度修正”时，读取：
- `references/mapping.md`
