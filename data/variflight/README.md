# Variflight Skill

飞常准 (Variflight) API 工具 - 支持 OpenClaw、Claude Code、Cursor 等所有 AI 客户端。

## 特性

- ✅ **零依赖** - 纯 Python 标准库，无需安装 MCP
- ✅ **多客户端支持** - OpenClaw、Claude Code、Cursor、GitHub Actions 等
- ✅ **灵活配置** - 环境变量、配置文件、命令行参数
- ✅ **完整功能** - 航班查询、火车票、天气、价格等

## 安装

```bash
# 克隆仓库
git clone https://github.com/variflight-ai/variflight-skill.git
cd variflight-skill

# 或使用特定目录
cp -r variflight-skill/scripts /path/to/your/project/
```

## 获取 API Key

访问 https://ai.variflight.com 获取 API Key。

## 配置

支持以下方式（按优先级排序）：

### 1. 命令行参数（最高优先级）

```bash
./scripts/flights.sh --api-key sk-xxxx PEK SHA 2025-02-15
```

### 2. 环境变量（推荐用于 CI/CD）

```bash
export VARIFLIGHT_API_KEY="sk-xxxxxxxxxxxxxxxx"
```

### 3. 配置文件

按以下顺序查找：
- `./.variflight.json`（项目级）
- `~/.variflight.json`（用户级）
- `~/.config/variflight/config.json`（XDG 标准）

配置格式：
```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxx"
}
```

快速设置：
```bash
cp .variflight.json.example ~/.variflight.json
# 编辑 ~/.variflight.json 填入你的 API key
```

## 使用

### 航班查询

```bash
# 按航线查询
./scripts/flights.sh PEK SHA 2025-02-15

# 按航班号查询
./scripts/flight.sh MU2157 2025-02-15

# 中转方案
./scripts/transfer.sh BJS SHA 2025-02-15

# 舒适度指数
./scripts/happiness.sh MU2157 2025-02-15

# 机场天气
./scripts/weather.sh PEK

# 机票价格
./scripts/price.sh HFE CAN 2025-02-15
```

### 火车票查询

```bash
./scripts/train.sh "上海" "合肥" 2025-02-15

# 查询火车站
./scripts/station.sh "北京西"
```

## 客户端集成

### OpenClaw (特别支持)

OpenClaw 会自动识别 skill 并加载 SKILL.md 中的说明。

**安装方式：**
```bash
# 通过 ClawHub 安装
openclaw skill install variflight

# 或手动安装到 workspace
cp -r variflight-skill ~/.openclaw/workspace/skills/variflight
```

**配置方式：**
```bash
# 方式1: OpenClaw 环境变量文件
echo 'VARIFLIGHT_API_KEY=sk-xxxx' > ~/.openclaw/workspace/.env.variflight

# 方式2: 通用配置文件 (推荐)
echo '{"api_key": "sk-xxxx"}' > ~/.variflight.json
```

**使用示例：**
```bash
# OpenClaw 会自动识别这些命令
./skills/variflight/scripts/flights.sh PEK SHA 2025-02-15
./skills/variflight/scripts/train.sh "上海" "合肥" 2025-02-15
```

### Claude Code

在 `.claude/settings.json` 中添加：
```json
{
  "env": {
    "VARIFLIGHT_API_KEY": "sk-xxxxxxxxxxxxxxxx"
  }
}
```

或使用配置文件：
```bash
echo '{"api_key": "sk-xxxx"}' > ~/.variflight.json
```

### Cursor

在 Cursor Settings → General → Environment Variables 中添加：
```
VARIFLIGHT_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### GitHub Actions

```yaml
- name: Query Flights
  env:
    VARIFLIGHT_API_KEY: ${{ secrets.VARIFLIGHT_API_KEY }}
  run: |
    ./scripts/flights.sh PEK SHA 2025-02-15
```

### Docker

```dockerfile
ENV VARIFLIGHT_API_KEY=sk-xxxxxxxxxxxxxxxx
COPY scripts/ /app/scripts/
```

## API Endpoints

| Endpoint | 描述 | 示例参数 |
|----------|------|----------|
| `flights` | 按航线查航班 | dep=PEK arr=SHA date=2025-02-15 |
| `flight` | 按航班号查询 | fnum=MU2157 date=2025-02-15 |
| `transfer` | 中转方案 | depcity=BJS arrcity=SHA depdate=2025-02-15 |
| `happiness` | 舒适度指数 | fnum=MU2157 date=2025-02-15 |
| `futureAirportWeather` | 机场天气 | code=PEK type=1 |
| `trainStanTicket` | 火车票 | cdep=上海 carr=合肥 date=2025-02-15 |
| `searchTrainStations` | 火车站 | query=北京西 |
| `getFlightPriceByCities` | 机票价格 | dep_city=HFE arr_city=CAN dep_date=2025-02-15 |

## 常见机场代码

| 城市 | 机场 | 代码 |
|------|------|------|
| 北京 | 首都机场 | PEK |
| 北京 | 大兴机场 | PKX |
| 上海 | 虹桥机场 | SHA |
| 上海 | 浦东机场 | PVG |
| 广州 | 白云机场 | CAN |
| 深圳 | 宝安机场 | SZX |
| 成都 | 双流机场 | CTU |
| 杭州 | 萧山机场 | HGH |
| 合肥 | 新桥机场 | HFE |
| 西安 | 咸阳机场 | XIY |

## 许可证

MIT

## 链接

- Variflight AI: https://ai.variflight.com
- ClawHub: https://clawhub.com
