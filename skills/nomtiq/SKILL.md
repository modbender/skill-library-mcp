---
name: nomtiq
description: "Nomtiq — finds restaurants worth going to. No rankings, no ads. Remembers your taste, knows your budget. 小饭票：找餐厅、推荐餐厅、吃什么、附近好吃的。"
version: "0.4.5"
author: oak lee
cover: cover.jpg
env:
  - AMAP_KEY
  - SERPER_API_KEY
  - MOLTBOOK_API_KEY
triggers:
  - "找餐厅"
  - "吃什么"
  - "推荐个地方吃饭"
  - "附近有什么好吃的"
  - "今晚吃什么"
  - "小饭票"
  - "find restaurant"
  - "where to eat"
  - "restaurant recommendation"
tags: [restaurant, food, recommendation, global, 美食, 找餐厅, 口味画像]
commands:
  - "找餐厅 [地点/场景] — 推荐 2+1 家餐厅"
  - "吃什么 — 根据当前场景推荐"
  - "记录 [餐厅名] — 记录用餐体验，更新口味画像"
  - "口味画像 — 查看当前偏好分析"
  - "find restaurant [location] — global search (Google/Yelp/Reddit)"
scripts:
  - scripts/search_router.py
  - scripts/search_all.py
  - scripts/search_global.py
  - scripts/profile.py
  - scripts/scene.py
  - scripts/moltbook.py
  - scripts/onboard.py
metadata:
  openclaw:
    emoji: "🎫"
    requires:
      bins: ["python3"]
      skills: ["search-hub"]
      env:
        - AMAP_KEY
        - SERPER_API_KEY
        - MOLTBOOK_API_KEY
    install:
      - id: python3
        kind: system
        bins: ["python3"]
        label: "Python 3 (system)"
    external_calls:
      - url: https://restapi.amap.com
        auth: query
        env: AMAP_KEY
        required: true
        purpose: "高德地图周边餐厅搜索"
      - url: https://google.serper.dev
        auth: bearer
        env: SERPER_API_KEY
        required: false
        purpose: "小红书/大众点评交叉验证搜索（search-hub 统一调用）"
      - url: https://www.moltbook.com/api/v1
        auth: bearer
        env: MOLTBOOK_API_KEY
        required: false
        purpose: "Anonymous restaurant review sharing (opt-in, max 2/day)"
        env: MOLTBOOK_API_KEY
        required: false
        purpose: "Anonymous restaurant review sharing (opt-in, max 2/day)"
---

# Nomtiq 小饭票 🎫

**一顿饭就是一段时光。**

---

小饭票从一个习惯开始——

我们写代码，开会，赶 deadline。一天结束，想找个地方好好吃顿饭，陪陪重要的人。但找餐厅这件事，比想象中难。

我的好朋友常常在亮马河一带请我吃饭。不去网红店，不刷榜单。就是找一家有意思的本地馆子，两个人坐下来，聊聊最近在做什么，聊聊工作和生活，偶尔抬头看天。

找餐厅其实不容易。一切都需要合适——但什么是合适呢？社交媒体的推荐太虚假，榜单里全是广告，大众点评其实不知道你喜欢什么，它只知道什么是流行的。

**所以我写了小饭票。没有排行榜。**

它记得你的口味，知道你去过哪里，了解你的预算和区域。它不给你推广告，只给你值得去的地方。用得越久，越懂你。

> 合适，就是我们一起花的时间。

---

## 🔒 隐藏菜单

小饭票有一个隐藏菜单模式，专为重要的时光设计。不追求准确，是时光里两个人的小冒险。

**一顿好饭，一段记得的时光。**

---
---

# Nomtiq 🎫

**A meal is a moment.**

---

It started with a habit.

We write code, sit in meetings, chase deadlines. At the end of the day, you want to find a good place to eat — and actually be present with the people who matter.

A friend of mine would take me to dinner along Liangma River — not the trending spots, not the ranked lists. Just a local place worth sitting in. Two people, a table, time to talk about what's been going on.

Everything has to fit. But what does *fit* mean? Social media recommendations are noise. Rankings are ads. Dianping knows what's popular — it doesn't know what you like.

**So I built Nomtiq. No rankings.**

It remembers your taste. Knows where you've been, what you liked, what you didn't. The longer you use it, the better it knows you.

> The right fit isn't a rating. It's the time we spend together.

---

## 🔒 Hidden Menu

There's a hidden menu — designed for moments that matter. Not about precision. A small adventure for two.

**A good meal. A moment worth remembering.**

---

> 技术文档见 AGENT_GUIDE.md
