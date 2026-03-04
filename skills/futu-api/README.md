# 富途API数据技能

简单易用的富途牛牛数据获取工具，专注于股票行情数据和技术分析。

## 🎯 功能特点

- ✅ **纯数据获取**：无交易功能，零风险
- ✅ **完整行情**：实时报价、K线、逐笔成交
- ✅ **技术分析**：移动平均线、RSI、布林带
- ✅ **市场数据**：板块列表、资金流向
- ✅ **简单易用**：命令行工具，开箱即用

## 🚀 5分钟上手

### 1. 安装依赖
```bash
pip install futu-api pandas
```

### 2. 运行FutuOpenD
- 从富途官网下载FutuOpenD
- 安装并运行应用程序
- 登录富途账户

### 3. 基本使用
```bash
# 查询腾讯行情
python futu_api.py quote 00700 --market HK

# 获取5分钟K线
python futu_api.py kline 00700 --market HK --type 5m --count 50

# 计算技术指标
python futu_api.py indicators 00700 --market HK --type day --count 30
```

## 📊 常用命令

### 行情查询
```bash
# 港股
python futu_api.py quote 00700 --market HK    # 腾讯
python futu_api.py quote 00941 --market HK    # 移动
python futu_api.py quote 02598 --market HK    # 连连数字

# 美股
python futu_api.py quote AAPL --market US     # 苹果
python futu_api.py quote TSLA --market US     # 特斯拉
```

### K线分析
```bash
# 不同周期
python futu_api.py kline 00700 --type 1m      # 1分钟线
python futu_api.py kline 00700 --type 5m      # 5分钟线
python futu_api.py kline 00700 --type day     # 日线
python futu_api.py kline 00700 --type week    # 周线

# 输出格式
python futu_api.py kline 00700 --format json  # JSON格式
python futu_api.py kline 00700 --format table # 表格格式
```

### 技术指标
```bash
# 计算所有指标
python futu_api.py indicators 00700

# 使用更多历史数据
python futu_api.py indicators 00700 --count 100

# 不同周期计算
python futu_api.py indicators 00700 --type week
```

### 市场数据
```bash
# 查看板块
python futu_api.py plates --market HK

# 查看逐笔成交
python futu_api.py ticker 00700 --count 20
```

## 🎯 使用示例

### 简单监控
```bash
# 监控多只股票
for stock in 00700 00941 02598; do
    python futu_api.py quote $stock --market HK
done
```

### 技术分析判断
```python
from futu_api import FutuAPI

api = FutuAPI()
api.connect()

kline = api.get_kline('00700', 'HK', 'day', 30)
indicators = api.get_indicators(kline)

if indicators.get('rsi', 0) < 30:
    print("🟢 RSI超卖，关注反弹机会")
elif indicators.get('rsi', 0) > 70:
    print("🔴 RSI超买，注意回调风险")

api.disconnect()
```

## ⚙️ 配置说明

### 连接设置
默认连接：`127.0.0.1:11111`
如需修改：
```python
api = FutuAPI(host="127.0.0.1", port=11111)
```

### 环境检查
```bash
# 检查连接
telnet 127.0.0.1 11111

# 检查进程
ps aux | grep FutuOpenD
```

## 🔧 故障排除

### 连接问题
1. **确保FutuOpenD运行**：检查应用程序是否打开
2. **检查登录状态**：需要在FutuOpenD中登录账户
3. **检查网络**：确保本地连接正常

### 数据问题
1. **检查股票代码**：格式为 `00700` (港股) 或 `AAPL` (美股)
2. **检查市场类型**：港股用 `--market HK`，美股用 `--market US`
3. **检查订阅**：部分数据需要先订阅才能获取

### 性能问题
1. **减少数据量**：使用 `--count` 参数限制数据条数
2. **增加间隔**：避免连续高频查询
3. **使用缓存**：重复查询可考虑本地缓存

## 📁 文件说明

- `futu_api.py` - 主程序，核心数据获取功能
- `requirements.txt` - Python依赖包
- `SKILL.md` - OpenClaw技能文档
- `README.md` - 使用说明文档

## 📚 学习资源

- [富途开放平台](https://openapi.futunn.com/)
- [API文档](https://openapi.futunn.com/doc/)
- [Python量化分析](https://github.com/waditu/tushare)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**简单 · 实用 · 高效**  
专注于数据获取，让量化分析更简单