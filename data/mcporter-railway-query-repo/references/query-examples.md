# mcporter 火车票查询示例

## 基础查询命令

### 1. 查询车票
```bash
mcporter call 12306.get-tickets \
  date="2026-02-14" \
  fromStation="SHH" \
  toStation="KYH" \
  trainFilterFlags="GD" \
  sortFlag="startTime" \
  format="text" \
  --config ~/.mcporter/mcporter.json
```

### 2. 查询下午班次（12:00-18:00）
```bash
mcporter call 12306.get-tickets \
  date="2026-02-14" \
  fromStation="SHH" \
  toStation="KYH" \
  trainFilterFlags="GD" \
  earliestStartTime=12 \
  latestStartTime=18 \
  sortFlag="startTime" \
  --config ~/.mcporter/mcporter.json
```

### 3. 查询指定车次详情
```bash
mcporter call 12306.get-train-route-stations \
  trainCode="G7134" \
  departDate="2026-02-14" \
  format="text" \
  --config ~/.mcporter/mcporter.json
```

## 查询参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| date | 日期 (YYYY-MM-DD) | "2026-02-14" |
| fromStation | 出发站代码 | "SHH" |
| toStation | 到达站代码 | "KYH" |
| trainFilterFlags | 车次类型过滤 | "G"=高铁, "D"=动车, "GD"=高铁+动车 |
| earliestStartTime | 最早出发时间 (0-24) | 12 |
| latestStartTime | 最晚出发时间 (0-24) | 18 |
| sortFlag | 排序方式 | "startTime" / "arriveTime" / "duration" |
| sortReverse | 是否倒序 | true / false |
| limitedNum | 限制返回数量 | 10 |
| format | 输出格式 | "text" / "json" / "csv" |

## 常用查询场景

### 场景1: 上海虹桥到杭州东 下午高铁
```bash
./scripts/query-afternoon.sh 2026-02-18 AOH HZH
```

### 场景2: 上海到江阴 全天班次
```bash
./scripts/query-tickets.sh 2026-02-14 SHH KYH
```

### 场景3: 获取车站代码
```bash
./scripts/get-station-code.sh "上海虹桥"
```

## 配置说明

mcporter 配置文件 `~/.mcporter/mcporter.json`：

```json
{
  "mcpServers": {
    "12306": {
      "type": "sse",
      "url": "http://127.0.0.1:8080/sse",
      "name": "12306 高铁动车查询",
      "description": "查询高铁（G开头）和动车（D开头）余票",
      "enabled": true
    }
  }
}
```