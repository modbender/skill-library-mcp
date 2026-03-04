# Weather Checker 🌤️

一个简单的命令行天气查询工具，使用 Open-Meteo API 获取天气数据。

## 功能特性

- ✅ 查询任意城市的天气
- ✅ 支持今天、明天、后天等未来7天的预报
- ✅ 默认查询北京明天的天气
- ✅ 支持JSON和文本两种输出格式
- ✅ 内置中国主要城市坐标
- ✅ 自动地理编码（支持全球城市）

## 安装

### 快速安装

```bash
# 进入项目目录
cd /Users/tal/work/Project/WeatherChecker

# 运行安装脚本
chmod +x setup.sh
./setup.sh
```

### 手动安装

```bash
# 1. 安装依赖
pip3 install requests --user

# 2. 使脚本可执行
chmod +x weather_checker.py

# 3. 创建符号链接（选择一种方式）
# 方式A：系统级安装（需要sudo）
sudo ln -sf $(pwd)/weather_checker.py /usr/local/bin/weather-checker

# 方式B：用户级安装
mkdir -p ~/.local/bin
ln -sf $(pwd)/weather_checker.py ~/.local/bin/weather-checker
# 将 ~/.local/bin 添加到 PATH 环境变量
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # 或 ~/.zshrc
source ~/.bashrc
```

## 使用方法

### 基本用法

```bash
# 查询北京明天的天气（默认）
weather-checker

# 查询上海明天的天气
weather-checker -c shanghai

# 查询广州后天的天气
weather-checker -c guangzhou -d 2

# 查询今天天气
weather-checker -d 0
```

### 高级用法

```bash
# 使用简单格式输出
weather-checker -f simple

# 使用JSON格式输出
weather-checker -f json

# 查询英文城市名
weather-checker -c "new york"
weather-checker -c "london"
weather-checker -c "tokyo"

# 列出所有预定义城市
weather-checker -l

# 查询自定义城市（支持中文）
weather-checker -c "杭州"
weather-checker -c "武汉市"
```

### 输出示例

**漂亮格式（默认）:**
```
🌤️ 天气查询结果 🌤️

地点: 北京
日期: 2026-02-26
天气: 🌦️ 小雨
温度: 3.8°C ~ 8.3°C
降水量: 💧 0.8mm
降水概率: 🌤️ 20%
```

**简单格式:**
```
『北京 2026-02-26 🌦️小雨 3.8°C~8.3°C 💧0.8mm 🌤️20%』
```

**JSON格式:**
```json
{
  "date": "2026-02-26",
  "temperature_max": 8.3,
  "temperature_min": 3.8,
  "precipitation": 0.8,
  "precipitation_probability": 20,
  "weather_code": 61,
  "weather_description": "小雨",
  "weather_emoji": "🌦️",
  "location_name": "北京",
  "query_city": "beijing"
}
```

## 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--city` | `-c` | 城市名称（支持中文/拼音/英文） | `beijing` |
| `--days` | `-d` | 查询多少天后的天气（0-7） | `1` |
| `--format` | `-f` | 输出格式：`json`、`pretty` 或 `simple` | `pretty` |
| `--list-cities` | `-l` | 列出所有预定义城市 | - |

## 预定义城市

工具内置以下中国主要城市的坐标：

- `beijing` - 北京
- `shanghai` - 上海
- `guangzhou` - 广州
- `shenzhen` - 深圳
- `hangzhou` - 杭州
- `chengdu` - 成都
- `xian` - 西安
- `wuhan` - 武汉
- `nanjing` - 南京
- `chongqing` - 重庆

## 技术细节

### 使用的API
- **天气数据**: [Open-Meteo API](https://open-meteo.com/)
- **地理编码**: Open-Meteo 地理编码API

### 天气代码映射
工具使用WMO天气代码标准，部分常见代码：
- 0-3: 晴到多云
- 45-48: 雾
- 51-57: 毛毛雨/冻雨
- 61-67: 雨
- 71-77: 雪
- 80-86: 阵雨/阵雪
- 95-99: 雷暴

### 错误处理
- 网络超时：10秒超时
- 城市未找到：返回错误信息
- API错误：返回HTTP状态码和错误信息

## 项目结构

```
WeatherChecker/
├── weather_checker.py    # 主程序
├── setup.sh             # 安装脚本
├── README.md            # 说明文档
└── .gitignore           # Git忽略文件
```

## 开发

### 添加新城市
编辑 `weather_checker.py` 中的 `CITY_COORDINATES` 字典，添加新的城市坐标。

### 扩展功能
可以扩展的功能：
- 添加更多天气参数（风速、湿度等）
- 支持历史天气查询
- 添加图表输出
- 多城市批量查询

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 支持

如有问题，请：
1. 检查网络连接
2. 确认城市名称正确
3. 查看错误信息中的详细说明