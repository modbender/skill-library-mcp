# 🔍 本地生活交叉验证工具

**用大众点评 × 小红书双平台交叉验证，找到真正靠谱的店。**

大众点评看评分和评论数，小红书看真实用户体验——两个平台都说好的店，踩雷概率极低。

---

## 功能

- 🍜 **餐厅验证** — 粤菜、火锅、日料、西餐……任意菜系
- 💆 **本地生活** — 按摩、美容、健身房、KTV、亲子
- 🏨 **酒店景点** — 民宿、酒店、景点门票
- 📊 **交叉匹配** — thefuzz 模糊匹配 + 多策略打分
- 🤖 **反检测** — 持久化会话 + 可见浏览器，稳定抓取

## 支持城市

深圳、广州、上海、北京、杭州、成都、武汉、南京、长沙、重庆、西安、苏州、天津、厦门、青岛等 28 个城市（可在 config.py 自行扩展）

---

## 快速开始

### 1. 一键安装

```bash
chmod +x setup.sh
./setup.sh
```

或手动安装：

```bash
pip3 install playwright thefuzz
python3 -m playwright install chromium
```

### 2. 登录平台（只需一次）

```bash
cd scripts
python3 session_manager.py dianping      # 登录大众点评
python3 session_manager.py xiaohongshu   # 登录小红书
# 或一次全部: python3 session_manager.py all
```

浏览器弹出后手动登录，登录成功后按回车。会话自动保存 7 天。

### 3. 开始使用

```bash
python3 crosscheck.py '深圳南山区' '粤菜'
python3 crosscheck.py '广州天河区' '早茶'
python3 crosscheck.py '上海静安区' '按摩'
python3 crosscheck.py '成都锦江区' '火锅'
```

---

## 输出示例

```
============================================================
🔍 本地生活交叉验证: 深圳福田区 - 火锅
============================================================

  🎯 两平台共同推荐 (2 家):

  1. 【冯校长老火锅(深圳福田店)】 7.2/10 👍 推荐
     大众点评: 5.0分 | 5959条评论 | ¥114
     小红书: 2.1⭐ (352赞) | 匹配度0.78
     一致性: 高 (0.82)

  2. 【八合里潮汕鲜牛肉火锅】 7.1/10 👍 推荐
     大众点评: 5.0分 | 8520条评论 | ¥123
     小红书: 1.8⭐ (180赞) | 匹配度0.72
     一致性: 高 (0.75)

  📍 仅大众点评 (8 家):
    1. 海底捞火锅(福田COCO Park店) — 5.0分 12000评 ¥120
    ...
```

---

## 项目结构

```
restaurant-crosscheck/
├── README.md
├── setup.sh                 # 一键安装
├── requirements.txt
├── .gitignore
└── scripts/
    ├── __init__.py
    ├── config.py            # 配置: 城市代码、选择器、评分权重
    ├── models.py            # 数据模型: DianpingRestaurant, XiaohongshuPost 等
    ├── session_manager.py   # 浏览器会话管理（登录/检查/重置）
    ├── fetch_dianping.py    # 大众点评抓取（sync Playwright）
    ├── fetch_xiaohongshu.py # 小红书抓取（sync Playwright）
    ├── match_restaurants.py # 跨平台模糊匹配 + 一致性评分
    └── crosscheck.py        # 主程序: 交叉验证入口
```

---

## 评分原理

```
大众点评                           小红书
  ↓                                 ↓
搜索「深圳南山区 粤菜」           搜索「深圳南山区 粤菜 推荐」
  ↓                                 ↓
提取: 店名/评分/评论数/人均/标签  提取: 笔记标题→店名/点赞/情感/关键词
  ↓                                 ↓
  └──────────┬──────────────────────┘
             ↓
     thefuzz 多策略模糊匹配（阈值 0.55）
     ├─ 精确比率 (ratio)
     ├─ 部分匹配 (partial_ratio)
     ├─ Token排序 (token_sort_ratio)
     └─ 包含关系 (containment)
             ↓
     综合评分 = 点评分×0.4 + 小红书互动×0.3 + 一致性×0.3
             ↓
     🔥强推(≥8) / 👍推荐(≥6) / 🤔可试(<6)
```

---

## 与 v1 的主要改进

| 问题 | v1 (原始) | v2 (当前) |
|------|-----------|-----------|
| async/sync 混用 | `'coroutine' object has no attribute 'goto'` | 全部统一为 sync Playwright |
| 城市代码 | 硬编码 0（默认上海） | 28 个城市自动匹配 |
| headless 被拦截 | 页面空白 | headless=False + 反检测参数 |
| 文件混乱 | 6 个 crosscheck 文件 | 1 个入口，模块化拆分 |
| 小红书提取 | 只能提取 1 家 | 多策略提取（括号、探店模式、后缀、分隔符） |
| 依赖 mock 数据 | crosscheck_simple.py 全是假数据 | 全部真实抓取 |

---

## 常见问题

**Q: 页面空白？**
A: 重新登录 `python3 session_manager.py all`

**Q: 海外无法访问？**
A: 需开国内 VPN

**Q: thefuzz 没装？**
A: 工具会自动回退到简单匹配，但建议安装: `pip3 install thefuzz`

**Q: 想加新城市？**
A: 编辑 `config.py` 的 `CITY_CODES`，打开 dianping.com 切换城市看 URL 里的代码

---

## 贡献

欢迎 PR！尤其是：
- 新增城市代码
- 优化小红书店名提取
- 支持更多平台（美团、抖音）
- 增加 headless 反检测

## License

MIT
