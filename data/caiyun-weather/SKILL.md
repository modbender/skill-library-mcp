---
name: caiyun-weather
description: "通过彩云天气 API 查询天气数据 — 实时天气、逐小时/一周预报、历史天气和天气预警。当用户询问任何城市的天气、温度、空气质量、天气预报、降雨概率、历史天气或天气预警时使用此技能。需要设置 CAIYUN_WEATHER_API_TOKEN 环境变量。Use when: user asks about current weather, temperature, air quality, forecast, rain, historical weather, or alerts for any city."
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "bins": ["python3"],
            "env": ["CAIYUN_WEATHER_API_TOKEN"],
          },
        "primaryEnv": "CAIYUN_WEATHER_API_TOKEN",
      },
  }
---

# 彩云天气 (Caiyun Weather)

通过彩云天气 API 查询天气数据。支持直接使用城市名称（中文或英文），无需提供经纬度。

## 前置条件

使用前需设置环境变量：

```bash
export CAIYUN_WEATHER_API_TOKEN="你的API密钥"
```

免费申请 API 密钥：https://docs.caiyunapp.com/weather-api/

## 何时使用

✅ **使用此技能：**
- "北京现在天气怎么样？"
- "上海明天会下雨吗？"
- "深圳未来一周天气预报"
- "广州空气质量如何？"
- "杭州过去24小时的天气"
- "成都有没有天气预警？"
- "What's the weather in Beijing?"
- 用户询问任何城市的天气、温度、空气质量、预报或预警

❌ **不要使用此技能：**
- 气候趋势分析或长期历史数据
- 航空/航海专业气象（METAR、TAF）
- 用户未配置彩云天气 API Token

## 命令

使用 `--city` 加城市名称（中文或英文）。如需精确定位，可使用 `--lng` 和 `--lat`。

### 实时天气

```bash
python3 "{{skill_path}}/scripts/caiyun_weather.py" realtime --city "北京"
```

### 逐小时预报（72小时）

```bash
python3 "{{skill_path}}/scripts/caiyun_weather.py" hourly --city "上海"
```

### 一周预报（7天）

```bash
python3 "{{skill_path}}/scripts/caiyun_weather.py" weekly --city "深圳"
```

### 历史天气（过去24小时）

```bash
python3 "{{skill_path}}/scripts/caiyun_weather.py" history --city "杭州"
```

### 天气预警

```bash
python3 "{{skill_path}}/scripts/caiyun_weather.py" alerts --city "成都"
```

### 使用坐标（可选）

对于无法通过城市名识别的地点：

```bash
python3 "{{skill_path}}/scripts/caiyun_weather.py" realtime --lng 116.4074 --lat 39.9042
```

## 内置城市（即时查询）

北京、上海、广州、深圳、杭州、成都、武汉、南京、重庆、西安、天津、苏州、郑州、长沙、青岛、大连、厦门、昆明、贵阳、哈尔滨、沈阳、长春、福州、合肥、济南、南昌、石家庄、太原、呼和浩特、南宁、海口、三亚、拉萨、乌鲁木齐、兰州、西宁、银川、香港、澳门、台北、珠海、东莞、佛山、无锡、宁波、温州

英文名和其他全球城市通过在线地理编码自动解析。

## 说明

- 脚本仅使用 Python 标准库，无需 pip 安装
- 内置城市即时解析，其他城市通过 OpenStreetMap 地理编码
- API 对中国地区数据最为精准
- 有频率限制，请避免短时间内频繁请求
