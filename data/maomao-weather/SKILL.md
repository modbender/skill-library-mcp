---
name: weather
description: 查询全球任何城市的当前天气情况。当用户询问天气、查询城市温度、了解气象状况时使用此技能。支持中文、英文、拼音输入，自动匹配最佳位置。默认查询北京。
argument-hint: "[城市名]"
allowed-tools: Bash
---

# 天气查询技能

查询指定城市的当前天气信息，包括温度、天气状况、风速、风向等。

## 快速使用

1. **执行天气查询**：
   ```bash
   printf '%s\n' "$ARGUMENTS" | python3 "scripts/weather.py"
   ```

2. **参数处理**：
   - 城市参数支持中文、英文、拼音
   - 自动过滤"天气"、"怎么样"等修饰词
   - 无参数时默认查询北京

3. **输出解析**：脚本返回格式化的天气信息，提取核心数据呈现给用户。

## 详细参考

- **城市支持与查询技巧**：见 [references/weather_details.md](references/weather_details.md)
- **故障排除指南**：见 [references/weather_details.md#故障排除](references/weather_details.md#故障排除)

## 示例用法

- `查询北京天气` → 自动触发，查询北京
- `/weather 上海` → 查询上海天气
- `纽约温度多少` → 查询纽约天气
- `London weather` → 查询伦敦天气

脚本自动处理城市名匹配和地理编码，优先匹配知名城市。