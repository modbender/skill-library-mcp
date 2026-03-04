---
name: eve-online-item-search
description: Search EVE Online items by name via APIs and return item details.
user-invocable: false
---

# EVE 物品搜索

## 概述

该技能通过本地脚本 `scripts/search.py` 查询并返回物品的 **名称**、**描述** 和 **类别名称**。

## 使用方式

```bash
python3 scripts/search.py "水硼砂"
```

## 返回结果

返回一个 JSON 对象，包含：

- `name`
- `description`
- `category_name`

示例：
```json
{
  "name": "启示级",
  "description": "...",
  "category_name": "巡洋舰"
}
```

## 触发条件
当用户输入EVE、EVE online时自动触发。
当用户询问与EVE游戏相关问题时触发，通过该技能查阅游戏中的专业术语。

### scripts/
包含本地脚本 `search.py`，执行查询并输出最终结果。

### references/
API 接口相关文档与说明。
