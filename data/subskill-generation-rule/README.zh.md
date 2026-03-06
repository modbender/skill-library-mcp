# subskill-generate-rule

用于约束技能迭代时的新文件落盘位置，保持主技能根目录整洁、可维护。

## 规则

1. 新生成的推荐结果/分析结果文件统一放到 `data/`。
2. 新生成的功能代码统一放到 `subskills/<feature>/`。
3. 每个新功能使用独立文件夹。
4. 需要说明用法时，在该功能目录下补充 `SKILL.md`。
5. 避免把一次性脚本和生成产物直接放在技能根目录。

## 推荐目录结构

```text
<skill>/
  SKILL.md
  config.json
  data/
  subskills/
    <feature-a>/
      SKILL.md
      *.py
    <feature-b>/
      SKILL.md
      *.py
```

## 示例

- 配置优化脚本：`subskills/config-optimization/optimize_from_aggressive.py`
- 每日推荐脚本：`subskills/daily-recommendation/generate_daily_recommendation.py`
- 推荐结果：`data/today_recommendation_2026-02-14.json`

## 适用场景

- 功能持续迭代，容易在根目录堆积临时脚本和产物。
- 需要“先优化配置，再生成推荐”的固定流程。
- 希望后续新增功能可按模块独立维护。
