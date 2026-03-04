---
name: chinese-calendar
description: "获取中国日历信息，包括节假日、调休安排、工作日判断。使用 timor.tech API，数据每年自动更新。Use when: 需要判断某天是否是工作日、查询节假日安排、了解调休情况。"
metadata: { "openclaw": { "emoji": "📅", "requires": { "bins": ["curl"] } } }
---

# Chinese Calendar Skill

获取中国日历信息，包括节假日、调休安排、工作日判断。

## When to Use

✅ **USE this skill when:**

- 判断某天是否是工作日（考虑调休）
- 查询节假日安排
- 了解调休补班情况
- 生成工作日历提醒

❌ **DON'T use this skill when:**

- 只需要普通日期计算 → use built-in date tools
- 需要农历信息 → use lunar calendar tools
- 需要其他国家节假日 → use international calendar APIs

## API Source

使用 **timor.tech** 提供的免费 API：
- 数据每年自动更新
- 包含国务院发布的节假日安排
- 包含调休、补班信息

## Commands

### 查询某天是否是工作日

```bash
# 查询今天
curl -s "https://timor.tech/api/holiday/info/$(date +%Y-%m-%d)"

# 查询指定日期
curl -s "https://timor.tech/api/holiday/info/2026-02-28"

# 查询明天
curl -s "https://timor.tech/api/holiday/info/$(date -d 'tomorrow' +%Y-%m-%d 2>/dev/null || date -v+1d +%Y-%m-%d)"
```

### 查询指定年份的所有节假日

```bash
# 查询2026年所有节假日
curl -s "https://timor.tech/api/holiday/year/2026/"
```

### 批量查询多个日期

```bash
# 查询本周所有日期or day in {0..6}; do
  date_str=$(date -d "$day days" +%Y-%m-%d 2>/dev/null || date -v+${day}d +%Y-%m-%d)
  curl -s "https://timor.tech/api/holiday/info/$date_str"
  echo ""
done
```

## Response Format

### 工作日/节假日信息

```json
{
  "code": 0,
  "type": {
    "type": 0,      // 0: 工作日, 1: 周末, 2: 节日, 3: 调休
    "name": "工作日",
    "week": 6       // 星期几 (1-7)
  },
  "holiday": {
    "holiday": false,     // 是否放假
    "name": null,         // 节日名称
    "wage": 1,            // 工资倍数 (1, 2, 3)
    "target": null,       // 对应哪个节日
    "after": false,       // 是否是节后补班
    "date": "2026-02-28", // 日期
    "rest": 1             // 休息天数
  }
}
```

### Type 类型说明

| type | 含义 |
|------|------|
| 0 | 工作日 |
| 1 | 周末 |
| 2 | 节日 |
| 3 | 调休 |

### Holiday 类型说明

| 场景 | holiday | after | 示例 |
|------|---------|-------|------|
| 正常工作日 | false | false | 周一到周五 |
| 正常周末 | true | false | 周六、周日 |
| 节假日 | true | false | 春节、国庆 |
| 调休补班 | false | true | 春节后补班 |

## Usage Examples

### 判断明天是否需要上班

```bash
response=$(curl -s "https://timor.tech/api/holiday/info/$(date -d 'tomorrow' +%Y-%m-%d)")
if echo "$response" | grep -q '"holiday":false'; then
  echo "明天是工作日，需要上班"
else
  echo "明天放假，不用上班"
fi
```

### 获取下周所有工作日

```bash
for day in {1..7}; do
  date_str=$(date -d "$day days" +%Y-%m-%d)
  response=$(curl -s "https://timor.tech/api/holiday/info/$date_str")
  if echo "$response" | grep -q '"holiday":false'; then
    echo "$date_str: 工作日"
  fi
done
```

### 查询节假日名称

```bash
curl -s "https://timor.tech/api/holiday/info/2026-02-17" | grep -o '"name":"[^"]*"'
```

## PowerShell Usage (Windows)

在 Windows PowerShell 中使用：

```powershell
# 查询今天
$response = Invoke-RestMethod -Uri "https://timor.tech/api/holiday/info/$(Get-Date -Format 'yyyy-MM-dd')"
$response.type.name
$response.holiday.holiday

# 查询明天
$tomorrow = (Get-Date).AddDays(1).ToString("yyyy-MM-dd")
$response = Invoke-RestMethod -Uri "https://timor.tech/api/holiday/info/$tomorrow"
$response
```

## Integration with OpenClaw

在 Agent 中使用此 skill：

1. 读取本 SKILL.md 了解 API 用法
2. 使用 web_fetch 或 exec 调用 API
3. 解析 JSON 响应
4. 根据结果生成提醒或调整计划

### Example Workflow

```
1. 获取明天的日期
2. 调用 timor.tech API 查询
3. 判断是否是工作日
4. 如果是工作日 → 正常发送下班提醒
5. 如果是假期 → 发送假期祝福，跳过下班提醒
```

## Notes

- API 免费使用，无需注册
- 数据每年由 timor.tech 维护更新
- 节假日安排以国务院发布为准
- 支持年份范围：当年及前后几年

## Related

- 农历查询：需配合其他农历 API
- 国际节假日：使用 date.nager.at API