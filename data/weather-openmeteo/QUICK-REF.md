# Weather Open-Meteo Skill - 快速参考

## 🚀 快速开始

```powershell
# 进入技能目录
cd ~/.openclaw/workspace/skills/weather-openmeteo

# 查询当前天气（英文）
.\weather-en.ps1 -City Shanghai

# 查询当前天气（中文）
.\weather-cn.ps1 -City Beijing
```

## 📋 常用命令

### 查询天气
```powershell
# 上海天气（英文）
.\weather-en.ps1 -City Shanghai

# 北京天气（中文）
.\weather-cn.ps1 -City Beijing

# 广州天气（英文）
.\weather-en.ps1 -City Guangzhou
```

### 测试技能
```powershell
# 运行完整测试
.\test-skill.ps1
```

## 🏙️ 支持城市

| 城市 | 英文名 | 代码 |
|------|--------|------|
| 上海 | Shanghai | Shanghai |
| 北京 | Beijing | Beijing |
| 广州 | Guangzhou | Guangzhou |
| 深圳 | Shenzhen | Shenzhen |
| 成都 | Chengdu | Chengdu |
| 杭州 | Hangzhou | Hangzhou |
| 南京 | Nanjing | Nanjing |
| 武汉 | Wuhan | Wuhan |
| 西安 | Xian | Xian |
| 重庆 | Chongqing | Chongqing |

## 🌤️ 天气代码

| 代码 | 描述 |
|------|------|
| 0 | 晴天 |
| 1-3 | 多云 |
| 45-48 | 雾 |
| 51-65 | 雨 |
| 71-77 | 雪 |
| 80-86 | 雨/雪 |
| 95-99 | 雷暴 |

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `weather-en.ps1` | 英文版本 |
| `weather-cn.ps1` | 中文版本（拼音） |
| `weather-simple.ps1` | 简化版本 |
| `test-skill.ps1` | 测试脚本 |
| `SKILL.md` | 技能描述 |
| `README.md` | 项目概述 |
| `USAGE.md` | 使用指南 |
| `CREATION.md` | 创建过程 |
| `SUMMARY.md` | 项目总结 |
| `QUICK-REF.md` | 快速参考 |

## 🔧 故障排除

### 脚本执行错误
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 网络问题
- 检查是否可以访问 open-meteo.com
- 检查防火墙设置

### 城市不支持
编辑 `weather-en.ps1` 或 `weather-cn.ps1` 中的 `$cityCoords` 哈希表

## 📊 输出示例

### 英文版本
```
=== Current Weather - Shanghai ===
Time: 2026-03-03T17:45
Temperature: 8.7C
Wind speed: 12.0 km/h
Wind direction: 16 degrees
Weather: Overcast
```

### 中文版本
```
=== Dang Qian Tian Qi - Beijing ===
Shi Jian: 2026-03-03T17:45
Wen Du: 9.9C
Feng Su: 10.2 km/h
Feng Xiang: 315 du
Tian Qi: Qing Tian
```

## 🔗 API 参考

### 当前天气
```
https://api.open-meteo.com/v1/forecast?
  latitude=31.2304&
  longitude=121.4737&
  current_weather=true&
  timezone=Asia/Shanghai
```

### 7天预报
```
https://api.open-meteo.com/v1/forecast?
  latitude=31.2304&
  longitude=121.4737&
  daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum&
  timezone=Asia/Shanghai
```

## 💡 提示

1. **首次使用**：先运行 `.\test-skill.ps1` 验证安装
2. **中文显示**：使用 `weather-cn.ps1` 避免编码问题
3. **添加城市**：编辑脚本中的 `$cityCoords` 哈希表
4. **API 限制**：Open-Meteo 免费但有请求限制

## 📚 更多信息

- 详细使用指南：`USAGE.md`
- 创建过程：`CREATION.md`
- 项目总结：`SUMMARY.md`
- 完整文档：`README.md`