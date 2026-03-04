---
name: meihua-yishu
description: Traditional Chinese "Mei Hua Yi Shu" (Plum Blossom Divination) based on specific time calculation (Hour/Minute). Use when the user specifically asks for Plum Blossom Divination or provides hour/minute for calculation.
---

# 梅花易数 (Mei Hua Yi Shu) 🌸

基于时间（时、分）的精细起卦工具。

## 算法逻辑 (Logic)
1. **上卦**：小时 % 8 (余数为 0 则取 8)
2. **下卦**：分钟 % 8 (余数为 0 则取 8)
3. **动爻**：(小时 + 分钟) % 6 (余数为 0 则取 6)

## 使用方法 (Usage)
直接调用脚本获取起卦结果：
`node /root/clawd/skills/meihua-yishu/scripts/meihua.js [YYYY-MM-DD HH:MM]`

## 卦象解析建议
- **本卦**：当前的处境与状态。
- **互卦**：事情发展的中间过程与隐藏因素。
- **变卦**：事情的最终结果。
- **错卦**：从反面（立场）观察。
- **综卦**：换位思考（反转）观察。
- **动爻**：变动的关键点，参考周易爻辞。
