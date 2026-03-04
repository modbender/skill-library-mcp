# Weather Open-Meteo Skill - 使用说明

## 快速开始

### 1. 基本使用

```powershell
# 进入技能目录
cd ~/.openclaw/workspace/skills/weather-openmeteo

# 查看帮助
.\weather-en.ps1 -City Shanghai
```

### 2. 支持的城市

- Shanghai (上海)
- Beijing (北京)
- Guangzhou (广州)
- Shenzhen (深圳)
- Chengdu (成都)

### 3. 输出示例

```
=== Current Weather - Shanghai ===
Time: 2026-03-03T17:45
Temperature: 8.7C
Wind speed: 12.0 km/h
Wind direction: 16 degrees
Weather: Overcast
```

## 脚本说明

### weather-en.ps1 (英文版)
- 使用英文显示天气信息
- 适合国际用户
- 完整的天气代码描述

### weather-cn.ps1 (中文版)
- 使用拼音显示天气信息
- 避免中文字符编码问题
- 适合中文用户

### weather-simple.ps1 (简化版)
- 基础功能
- 适合学习和修改

## API 说明

### 当前天气 API
```
https://api.open-meteo.com/v1/forecast?
  latitude=31.2304&
  longitude=121.4737&
  current_weather=true&
  timezone=Asia/Shanghai
```

### 7天预报 API
```
https://api.open-meteo.com/v1/forecast?
  latitude=31.2304&
  longitude=121.4737&
  daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum&
  timezone=Asia/Shanghai
```

## 天气代码对照表

| 代码 | 英文描述 | 中文描述 |
|------|----------|----------|
| 0 | Clear sky | 晴天 |
| 1 | Mainly clear | 主要晴朗 |
| 2 | Partly cloudy | 部分多云 |
| 3 | Overcast | 多云 |
| 45 | Fog | 雾 |
| 48 | Depositing rime fog | 雾凇 |
| 51-55 | Drizzle | 雨 |
| 61-65 | Rain | 雨 |
| 71-77 | Snow | 雪 |
| 80-86 | Rain showers | 雨 |
| 95-99 | Thunderstorm | 雷暴 |

## 故障排除

### 1. 脚本执行错误
```powershell
# 设置执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 网络连接问题
- 确保可以访问 open-meteo.com
- 检查防火墙设置

### 3. 城市不支持
编辑 `$cityCoords` 哈希表添加新城市：
```powershell
"CityName" = @{ latitude = 纬度; longitude = 经度; timezone = "Asia/Shanghai" }
```

## 扩展功能

### 添加新城市
1. 查找城市坐标：https://www.latlong.net/
2. 编辑脚本中的 `$cityCoords` 哈希表
3. 添加新的城市条目

### 自定义输出格式
修改脚本中的 `Write-Host` 语句来自定义输出格式

### 添加更多天气信息
Open-Meteo API 支持更多参数：
- `hourly=temperature_2m` - 每小时温度
- `daily=precipitation_probability_max` - 降水概率
- `current=relative_humidity_2m` - 相对湿度

## 许可证

MIT License - 免费使用，自由修改