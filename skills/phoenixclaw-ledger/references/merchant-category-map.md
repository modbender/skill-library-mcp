# Merchant to Category Mapping

This document defines the rules for automatically categorizing transactions based on merchant names and contextual signals.

## Category Hierarchy

### Primary Categories

| Category ID | Display Name | Icon | Description |
|-------------|--------------|------|-------------|
| `food` | Food & Dining | 🍜 | Restaurants, groceries, delivery |
| `transport` | Transportation | 🚗 | Rides, fuel, public transit |
| `shopping` | Shopping | 🛒 | Retail, online purchases |
| `entertainment` | Entertainment | 🎬 | Movies, games, events |
| `utilities` | Bills & Utilities | 📱 | Phone, internet, electricity |
| `housing` | Housing | 🏠 | Rent, property fees |
| `health` | Health | 💊 | Medical, pharmacy, fitness |
| `education` | Education | 📚 | Courses, books, training |
| `personal` | Personal Care | 💈 | Haircuts, beauty, clothing |
| `subscription` | Subscriptions | 🔄 | Digital services, memberships |
| `transfer` | Transfers | 💸 | P2P, bank transfers |
| `income` | Income | 💰 | Salary, reimbursements |
| `other` | Other | 📦 | Uncategorized |

### Subcategories (Optional)

```yaml
food:
  - restaurant
  - delivery
  - groceries
  - coffee
  - snacks

transport:
  - rideshare
  - public
  - fuel
  - parking
  - flights

shopping:
  - electronics
  - clothing
  - home
  - gifts
```

## Merchant Pattern Matching

### High-Confidence Mappings

These merchants are mapped with high certainty:

#### Food & Dining
```yaml
food:
  exact_match:
    - "Starbucks"
    - "星巴克"
    - "McDonald's"
    - "麦当劳"
    - "KFC"
    - "肯德基"
    - "Luckin Coffee"
    - "瑞幸咖啡"
    - "海底捞"
    - "Haidilao"
    
  contains:
    - "餐厅"
    - "饭店"
    - "Restaurant"
    - "Cafe"
    - "咖啡"
    - "奶茶"
    - "烘焙"
    - "Bakery"
    - "Pizza"
    - "外卖"
    
  platforms:
    - "美团"
    - "Meituan"
    - "饿了么"
    - "Ele.me"
    - "DoorDash"
    - "Uber Eats"
```

#### Transportation
```yaml
transport:
  exact_match:
    - "滴滴出行"
    - "DiDi"
    - "Uber"
    - "Lyft"
    - "高德打车"
    - "花小猪"
    - "12306"
    - "中国铁路"
    
  contains:
    - "出租"
    - "Taxi"
    - "地铁"
    - "Metro"
    - "公交"
    - "Bus"
    - "加油"
    - "Gas"
    - "Fuel"
    - "停车"
    - "Parking"
    - "航空"
    - "Airlines"
```

#### Shopping
```yaml
shopping:
  platforms:
    - "淘宝"
    - "Taobao"
    - "天猫"
    - "Tmall"
    - "京东"
    - "JD.com"
    - "拼多多"
    - "Pinduoduo"
    - "Amazon"
    - "亚马逊"
    
  contains:
    - "超市"
    - "Supermarket"
    - "便利店"
    - "Convenience"
    - "商城"
    - "Mall"
    - "Store"
```

#### Entertainment
```yaml
entertainment:
  exact_match:
    - "猫眼电影"
    - "淘票票"
    - "大麦"
    
  contains:
    - "电影"
    - "Cinema"
    - "KTV"
    - "游戏"
    - "Game"
    - "票务"
    - "Tickets"
```

#### Subscriptions
```yaml
subscription:
  exact_match:
    - "Netflix"
    - "Spotify"
    - "Apple"
    - "iCloud"
    - "Google One"
    - "ChatGPT"
    - "OpenAI"
    - "GitHub"
    - "腾讯视频"
    - "爱奇艺"
    - "优酷"
    - "网易云音乐"
    - "QQ音乐"
    
  contains:
    - "会员"
    - "Membership"
    - "订阅"
    - "Subscription"
    - "月费"
    - "年费"
    - "Premium"
    - "Plus"
    - "Pro"
```

## Matching Algorithm

### Priority Order

1. **User Custom Rules** (highest priority)
2. **Exact Match** on merchant name
3. **Platform Match** for known services
4. **Contains Match** for keywords
5. **AI Inference** based on context
6. **Default to `other`** if no match

### Matching Process

```python
def categorize(merchant: str, context: str) -> Category:
    # 1. Check user custom rules
    if match := user_rules.match(merchant):
        return match
    
    # 2. Exact match
    if match := exact_mappings.get(normalize(merchant)):
        return match
    
    # 3. Platform match
    for platform, category in platform_mappings.items():
        if platform in merchant:
            return category
    
    # 4. Contains match
    for keyword, category in keyword_mappings.items():
        if keyword in merchant.lower():
            return category
    
    # 5. AI inference
    if context:
        return ai_infer_category(merchant, context)
    
    # 6. Default
    return Category.OTHER
```

## User Custom Rules

Users can define custom mappings in their config:

```yaml
# ~/.phoenixclaw/config.yaml
plugins:
  phoenixclaw-ledger:
    custom_categories:
      "公司食堂": food
      "Company Cafeteria": food
      "物业费": housing
      "Property Fee": housing
      "健身房月卡": health
      "Gym Membership": health
```

### Rule Format

```yaml
custom_categories:
  "[Merchant Name]": [category_id]
  
# With regex support
custom_patterns:
  - pattern: ".*健身.*"
    category: health
  - pattern: ".*Gym.*"
    category: health
```

## Ambiguous Cases

### Context-Dependent Categorization

Some merchants require context:

| Merchant | Possible Categories | Resolution |
|----------|---------------------|------------|
| Amazon | shopping, subscription | Check amount pattern |
| 美团 | food, entertainment | Check specific service |
| Apple | electronics, subscription | Check amount (small = sub) |

### Amount-Based Hints

| Amount Pattern | Likely Category |
|----------------|-----------------|
| < $5 regular | food (coffee, snacks) |
| ~$10-15 monthly | subscription |
| Round numbers | transfers |

## Category Statistics

Track category usage for personalization:

```yaml
category_stats:
  food:
    count: 45
    total: 3500.00
    average: 77.78
    last_used: 2026-02-02
  transport:
    count: 12
    total: 580.00
    average: 48.33
    last_used: 2026-02-01
```

Use statistics for:
- Suggesting likely categories for ambiguous merchants
- Detecting unusual spending patterns
- Generating insights

---
