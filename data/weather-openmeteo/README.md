# Weather Open-Meteo Skill

一个基于 Open-Meteo API 的天气查询技能，专门针对 PowerShell 环境优化，无需 API 密钥。

## 特性

- ✅ **无需 API 密钥** - 完全免费使用
- ✅ **PowerShell 优化** - 在 PowerShell 环境中运行良好
- ✅ **中文支持** - 专为中文用户设计
- ✅ **7天预报** - 提供完整的天气预报
- ✅ **多城市支持** - 内置中国主要城市坐标
- ✅ **天气代码翻译** - 将天气代码转换为中文描述

## 安装

1. 将整个 `weather-openmeteo` 文件夹复制到 `~/.openclaw/workspace/skills/` 目录
2. 确保 PowerShell 可以执行脚本（如果需要）：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## 使用方法

### 基本用法

```powershell
# 进入技能目录
cd ~/.openclaw/workspace/skills/weather-openmeteo

# 查看帮助
.\weather.ps1 -Help

# 获取当前天气（默认上海）
.\weather.ps1

# 获取指定城市天气
.\weather.ps1 -City Beijing

# 获取7天预报
.\weather.ps1 -City Shanghai -Forecast

# 同时获取当前天气和预报
.\weather.ps1 -City Guangzhou -Current -Forecast
```

### 直接 API 调用

```powershell
# 当前天气
Invoke-WebRequest -Uri "https://api.open-meteo.com/v1/forecast?latitude=31.2304&longitude=121.4737&current_weather=true" -UseBasicParsing

# 7天预报
Invoke-WebRequest -Uri "https://api.open-meteo.com/v1/forecast?latitude=31.2304&longitude=121.4737&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia%2FShanghai" -UseBasicParsing
```

## 支持的城市

- 上海 (Shanghai)
- 北京 (Beijing)
- 广州 (Guangzhou)
- 深圳 (Shenzhen)
- 成都 (Chengdu)
- 杭州 (Hangzhou)
- 南京 (Nanjing)
- 武汉 (Wuhan)
- 西安 (Xian)
- 重庆 (Chongqing)

## 天气代码说明

| 代码 | 描述 |
|------|------|
| 0 | 晴天 |
| 1-3 | 多云 |
| 45-48 | 雾 |
| 51-55 | 雨 |
| 61-65 | 雨 |
| 71-77 | 雪 |
| 80-86 | 雨/雪 |
| 95-99 | 雷暴 |

## 输出示例

### 当前天气
```
=== 当前天气 - Shanghai ===
时间: 2026-03-03T06:15
温度: 10.5°C
风速: 12.7 km/h
风向: 8°
天气: 多云
```

### 7天预报
```
=== 7天天气预报 - Shanghai ===
03-03 (周二): 多云 | 最高: 10.5°C | 最低: 6.7°C | 降水: 0mm
03-04 (周三): 多云 | 最高: 11.2°C | 最低: 6.9°C | 降水: 0mm
03-05 (周四): 多云 | 最高: 14.1°C | 最低: 9.1°C | 降水: 0mm
...
```

## 技术细节

- **API**: Open-Meteo (https://open-meteo.com/)
- **数据更新频率**: 每15分钟
- **支持时区**: 亚洲/上海 (GMT+8)
- **坐标系统**: WGS84

## 故障排除

1. **脚本执行错误**: 确保 PowerShell 执行策略允许运行脚本
2. **网络连接问题**: 检查网络连接，确保可以访问 open-meteo.com
3. **城市不支持**: 如果需要添加新城市，请编辑 `weather.ps1` 中的 `$cityCoords` 哈希表

## 扩展功能

要添加新城市，编辑 `weather.ps1` 文件中的 `$cityCoords` 哈希表：

```powershell
"城市名" = @{ latitude = 纬度; longitude = 经度; timezone = "Asia/Shanghai" }
```

## 许可证

MIT License - 免费使用，自由修改