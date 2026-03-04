---
name: route-assistant
description: Intelligent route planning assistant with optimized display. Three-part output: transport options table, recommended schemes, and important reminders.
metadata:
  openclaw:
    emoji: 🗺️
    triggers:
      - 怎么去
      - 路线
      - 距离
      - 多远
      - 出行
      - 公交
      - 开车
      - 步行
      - 打车
      - 地址
      - 哪里
      - how to get
      - route
      - distance
      - transit
      - driving
---

# Route Assistant (route-assistant)

An intelligent travel route planning assistant with optimized three-part output structure using Amap (高德地图) API.

## Output Structure

### Part 1: 出行方式一览 (Transport Options Table)
Shows all available transport methods in table format:
| 出行方式 | 距离 | 耗时 | 明细 |
|---------|------|------|------|
| 🚗 驾车 | 22.6公里 | 33分钟 | 自驾前往 |
| 🚌 公交 | 22.4公里 | 45分钟 | 公共交通 |
| 🚕 打车 | 22.6公里 | 40分钟 | 出租车/网约车 |
| 🚶 步行 | 961米 | 10分钟 | 徒步 |

### Part 2: 推荐方案 (Recommended Schemes)
Sorted by travel time, filters infeasible options:
- Driving: Always shown
- Transit: Only if available
- Taxi: Only if distance > 1km
- Walking: Only if distance ≤ 3km

### Part 3: 重要提醒 (Important Reminders)
When train/flight info is provided:
- Shows departure/arrival times
- Calculates suggested departure time
- Warns if travel time conflicts with departure time

## Features

1. **Smart Recognition** - Automatically extracts origin and destination
2. **Three-Part Output** - Structured display for clarity
3. **Intelligent Filtering** - Filters infeasible options
4. **Time Conflict Detection** - Warns if can't make it on time

## Query Examples

- "从XX到XX怎么去?"
- "坐G106车从XX到XX"
- "天安门到故宫怎么走"

## Technical Details

- Uses Amap Geocoding API
- Uses Amap Direction API v5
- Duration estimated based on distance (v5 doesn't return duration)
- Smart filtering based on distance thresholds
