# Weather-Open-Meteo 技能发布说明

## 技能概述

Weather-Open-Meteo 是一个专门针对 PowerShell 环境优化的天气查询技能，使用 Open-Meteo API 提供免费的天气服务。

## 主要特性

- ✅ **无需 API 密钥** - 完全免费使用 Open-Meteo API
- ✅ **PowerShell 优化** - 专门针对 PowerShell 环境优化
- ✅ **双语支持** - 英文和中文（拼音）版本
- ✅ **多城市支持** - 内置10个中国主要城市
- ✅ **完整文档** - 详细的使用说明和创建文档

## 安装方法

### 通过 ClawHub CLI 安装

```bash
# 搜索技能
clawhub search "weather openmeteo"

# 安装技能
clawhub install weather-openmeteo
```

### 手动安装

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills

# 克隆或复制技能文件
git clone <repository-url> weather-openmeteo
```

## 使用方法

### 基本命令

```powershell
# 进入技能目录
cd ~/.openclaw/workspace/skills/weather-openmeteo

# 英文版本
.\weather-en.ps1 -City Shanghai

# 中文版本
.\weather-cn.ps1 -City Beijing
```

### 支持的城市

- Shanghai (上海)
- Beijing (北京)
- Guangzhou (广州)
- Shenzhen (深圳)
- Chengdu (成都)
- Hangzhou (杭州)
- Nanjing (南京)
- Wuhan (武汉)
- Xian (西安)
- Chongqing (重庆)

## 文件结构

```
weather-openmeteo/
├── SKILL.md                 # 技能描述文件
├── README.md                # 项目概述
├── USAGE.md                 # 使用指南
├── QUICK-REF.md             # 快速参考
├── CREATION.md              # 创建过程
├── SUMMARY.md               # 项目总结
├── PROJECT-COMPLETE.md      # 完成总结
├── PUBLISH.md               # 发布说明
├── weather-en.ps1           # 英文版本脚本
├── weather-cn.ps1           # 中文版本脚本
├── weather-simple.ps1       # 简化版本脚本
├── test-skill.ps1           # 测试脚本
├── demo-en.ps1              # 演示脚本
├── example.ps1              # 使用示例
└── weather.ps1              # 完整脚本
```

## 技术细节

### API 端点

- **基础 URL**: `https://api.open-meteo.com/v1/forecast`
- **当前天气**: `?current_weather=true`
- **7天预报**: `?daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum`

### 坐标系统

- **坐标系**: WGS84
- **时区**: 亚洲/上海 (GMT+8)
- **更新频率**: 每15分钟

### 天气代码

- **范围**: 0-99
- **描述**: 中英文对照
- **覆盖**: 晴、云、雨、雪、雾、雷暴等

## 测试结果

所有测试都已通过：
- ✅ 脚本文件检查
- ✅ 英文版本测试
- ✅ 中文版本测试
- ✅ API 连接测试
- ✅ 文档完整性检查

## 版本信息

- **版本**: 1.0.0
- **创建时间**: 2026年3月3日
- **作者**: OpenClaw 用户
- **许可证**: MIT License

## 更新日志

### v1.0.0 (2026-03-03)
- 初始版本发布
- 支持10个中国主要城市
- 提供英文和中文版本
- 完整的文档体系

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License - 免费使用，自由修改