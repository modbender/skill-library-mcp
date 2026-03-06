# Nantong Local Life Skill (Amap Pro Version)

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-orange?style=flat-square)](https://www.openclaw.ai/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT) [![Data Source](https://img.shields.io/badge/Data-Amap_API-blue.svg?style=flat-square)](https://lbs.amap.com/)

This is a professional-grade OpenClaw skill that provides **real-time, data-driven, bilingual (Chinese/English)** recommendations for popular food, attractions, and entertainment in **Nantong, Jiangsu** (江苏南通).

It leverages the **Amap (高德地图) API** to provide up-to-date, high-quality information, making it one of the most accurate and comprehensive local guides available.

## ✨ Pro Features

- **Amap API Integration**: All data is sourced directly from the Amap API, ensuring recommendations are fresh, accurate, and reliable.
- **Bilingual Support**: Automatically detects the user's query language (Chinese or English) and responds in the same language. Defaults to Chinese.
- **Comprehensive & Ranked**: Covers over 10 distinct categories, with items ranked by real user ratings and popularity.
- **Rich Details**: Provides names, addresses, ratings, average cost, and phone numbers for most listings.

## How to Use

Once installed, you can activate the skill by asking your OpenClaw assistant questions in either Chinese or English:

**Chinese (中文):**
- "南通有什么好吃的？"
- "推荐一下南通的旅游景点和评分。"
- "南通晚上有什么好玩的？找几个评分高的KTV。"

**English:**
- "What are some good places to eat in Nantong?"
- "Can you recommend some tourist attractions in Nantong with ratings?"
- "What is there to do for fun at night in Nantong? Find some top-rated KTVs."

## Installation

### Via ClawHub CLI

```bash
# Install the skill (replace with your actual slug after publishing)
clawhub install your-username/nantong-local-life-amap-pro
```

## Knowledge Base Highlights

This skill's knowledge base is built from **over 1,000 POIs** retrieved from the Amap API in March 2026, covering:

| Category | Top-Rated Example (Bilingual) |
|---|---|
| **Top Restaurants** | 中天黄海大酒店 (Zhongtian Huanghai Hotel) - ⭐4.8 |
| **Hot Pot & BBQ** | 龙啸老火锅 (Longxiao Hot Pot) - ⭐4.7 |
| **Coffee & Desserts** | 星巴克 (Starbucks) - ⭐4.5 |
| **Attractions** | 中国工农红军第十四军纪念馆 (Red 14th Army Memorial) - ⭐4.8 |
| **Parks & Squares** | 南通森林野生动物园 (Nantong Forest Wildlife Zoo) - ⭐4.7 |
| **Shopping Malls** | 南通万象城 (Nantong Mixc) - ⭐4.9 |
| **Nightlife** | 魅KTV·AI辅唱 (Mei KTV) - ⭐4.8 |

## Contributing

Since this skill is data-driven by an external API, contributions should focus on:
- Improving the `SKILL.md` prompt templates.
- Adding new categories or search keywords to `fetch_poi.py`.
- Enhancing the data processing logic in `process_poi.py`.

## License

This project is licensed under the MIT License.
