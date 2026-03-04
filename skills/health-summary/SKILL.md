---
name: health-summary
description: Generate daily/weekly/monthly health summaries with nutrition totals, target comparisons, and trends.
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires": { "scripts": ["scripts/health_summary.js"] },
      },
  }
---

# health-summary

日次・週次・月次の健康サマリーを生成する。

## Script

```bash
# 今日のサマリー
node scripts/health_summary.js today

# 特定日のサマリー
node scripts/health_summary.js today --date=2026-02-24

# 週間サマリー（直近7日）
node scripts/health_summary.js week

# 月次サマリー（当月）
node scripts/health_summary.js month
```

## 出力形式

JSON で以下を返す:
- `totals`: カロリー、P/C/F、食物繊維、糖質、ナトリウム、飽和脂肪、水分、運動時間
- `targets`: 目標値（config/health_targets.json から）
- `deltas`: 目標との差分
- `latest_weight`: 直近の体重
- `latest_sleep`: 直近の睡眠時間

## ユーザーへの返信フォーマット

サマリーを返す際は以下の形式:

```
📊 今日の健康サマリー (2026-02-24)

🍽 栄養: 1,500kcal / P 120g / C 180g / F 40g
  目標比: kcal -700 / P -45g / C -95g / F -15g

🥦 詳細栄養: Fiber 15g / Sugar 30g / Na 1,800mg / SatFat 10g

💧 水分: 1,500ml（目標: 2,000ml）
🏃 運動: 30分
⚖️ 体重: 70kg / 😴 睡眠: 7h
```

## 目標設定

目標値は `config/health_targets.json` から読み込む。デフォルト（lean_mass_gain モード）:
- kcal: 2,200 / P: 165g / C: 275g / F: 55g
- 水分: 2,000ml / 食物繊維: 25g / 糖質上限: 50g
- ナトリウム上限: 2,300mg / 飽和脂肪上限: 16g
