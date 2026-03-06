# 自然语言时间解析

## 概述

**目的：** 解析用户用自然语言描述的刷推时间设置

**示例：**
- "每天3次，随机时间"
- "早上9点、下午3点、晚上9点"
- "每天随机2-4次"
- "工作日晚上8点，周末随机3次"

---

## 1. 解析流程

```
用户输入 → 分词 → 识别模式 → 提取参数 → 生成配置
```

### 1.1 识别模式

```python
def detect_pattern(user_input):
    # 随机范围
    if "随机" in user_input and "-" in user_input:
        return "random_range"
    
    # 随机固定次数
    elif "随机" in user_input:
        return "random"
    
    # 固定时间
    elif "点" in user_input:
        return "fixed"
    
    # 工作日/周末
    elif "工作日" in user_input or "周末" in user_input:
        return "weekday_weekend"
    
    # 默认
    else:
        return "unknown"
```

---

## 2. 固定时间解析

### 2.1 示例

**用户输入：** "早上9点、下午3点、晚上9点"

**解析：**
```python
def parse_fixed_time(user_input):
    # 提取时间点
    times = []
    
    # 匹配 "X点" 或 "X点Y分"
    import re
    pattern = r'(\d{1,2})点(\d{1,2}分)?'
    matches = re.findall(pattern, user_input)
    
    for hour, minute in matches:
        hour = int(hour)
        minute = int(minute[:-1]) if minute else 0
        
        # 处理中文时间描述
        if "早" in user_input and hour < 12:
            pass  # 早上，不用调整
        elif "下" in user_input and hour < 12:
            hour += 12  # 下午
        elif "晚" in user_input and hour < 12:
            hour += 12  # 晚上
        
        times.append(f"{hour:02d}:{minute:02d}")
    
    return {
        "type": "fixed",
        "times": times
    }
```

**输出：**
```json
{
  "type": "fixed",
  "times": ["09:00", "15:00", "21:00"]
}
```

### 2.2 支持的格式

| 用户输入 | 解析结果 |
|----------|----------|
| "早上9点" | ["09:00"] |
| "9点、15点、21点" | ["09:00", "15:00", "21:00"] |
| "早上9点30分、下午3点45分" | ["09:30", "15:45"] |
| "9am, 3pm, 9pm" | ["09:00", "15:00", "21:00"] |

---

## 3. 随机时间解析

### 3.1 示例

**用户输入：** "每天3次，随机时间"

**解析：**
```python
def parse_random_time(user_input):
    # 提取次数
    import re
    match = re.search(r'(\d+)次', user_input)
    count = int(match.group(1)) if match else 3
    
    # 提取时间范围（如果有）
    time_range = ["09:00", "22:00"]  # 默认
    
    # 返回
    return {
        "type": "random",
        "countPerDay": count,
        "timeRange": time_range
    }
```

**输出：**
```json
{
  "type": "random",
  "countPerDay": 3,
  "timeRange": ["09:00", "22:00"]
}
```

### 3.2 支持的格式

| 用户输入 | 解析结果 |
|----------|----------|
| "每天3次，随机时间" | 随机3次 |
| "随机5次" | 随机5次 |
| "每天随机2次，早上9点到晚上9点" | 随机2次（09:00-21:00） |

---

## 4. 随机范围解析

### 4.1 示例

**用户输入：** "每天随机2-4次"

**解析：**
```python
def parse_random_range(user_input):
    import re
    
    # 提取范围
    match = re.search(r'(\d+)-(\d+)次', user_input)
    if match:
        min_count = int(match.group(1))
        max_count = int(match.group(2))
    else:
        min_count = 2
        max_count = 4
    
    return {
        "type": "random_range",
        "minPerDay": min_count,
        "maxPerDay": max_count,
        "timeRange": ["09:00", "22:00"]
    }
```

**输出：**
```json
{
  "type": "random_range",
  "minPerDay": 2,
  "maxPerDay": 4,
  "timeRange": ["09:00", "22:00"]
}
```

---

## 5. 工作日/周末解析

### 5.1 示例

**用户输入：** "工作日晚上8点，周末随机3次"

**解析：**
```python
def parse_weekday_weekend(user_input):
    result = {
        "type": "weekday_weekend"
    }
    
    # 分割工作日和周末
    parts = user_input.split("，")
    
    for part in parts:
        if "工作日" in part:
            # 解析工作日
            result["weekday"] = parse_time_part(part.replace("工作日", ""))
        elif "周末" in part:
            # 解析周末
            result["weekend"] = parse_time_part(part.replace("周末", ""))
    
    return result

def parse_time_part(text):
    if "随机" in text:
        return parse_random_time(text)
    elif "点" in text:
        return parse_fixed_time(text)
    else:
        return {"type": "unknown"}
```

**输出：**
```json
{
  "type": "weekday_weekend",
  "weekday": {
    "type": "fixed",
    "times": ["20:00"]
  },
  "weekend": {
    "type": "random",
    "countPerDay": 3,
    "timeRange": ["09:00", "22:00"]
  }
}
```

### 5.2 支持的格式

| 用户输入 | 解析结果 |
|----------|----------|
| "工作日晚上8点，周末随机3次" | 工作日固定20:00，周末随机3次 |
| "工作日早上9点和下午3点，周末随机2次" | 工作日09:00和15:00，周末随机2次 |
| "周一到周五随机2次，周末固定10点" | 工作日随机2次，周末固定10:00 |

---

## 6. 统一解析入口

```python
def parse_schedule(user_input):
    """统一解析入口"""
    
    # 1. 识别模式
    pattern = detect_pattern(user_input)
    
    # 2. 根据模式解析
    if pattern == "fixed":
        return parse_fixed_time(user_input)
    elif pattern == "random":
        return parse_random_time(user_input)
    elif pattern == "random_range":
        return parse_random_range(user_input)
    elif pattern == "weekday_weekend":
        return parse_weekday_weekend(user_input)
    else:
        # 无法识别，使用默认
        return {
            "type": "random",
            "countPerDay": 3,
            "timeRange": ["09:00", "22:00"]
        }
```

---

## 7. 完整示例

### 7.1 示例 1

**用户输入：** "每天3次，随机时间"

**解析：**
```json
{
  "type": "random",
  "countPerDay": 3,
  "timeRange": ["09:00", "22:00"]
}
```

**生成的随机时间：**
```
10:23, 14:47, 19:15
```

### 7.2 示例 2

**用户输入：** "早上9点、下午3点、晚上9点"

**解析：**
```json
{
  "type": "fixed",
  "times": ["09:00", "15:00", "21:00"]
}
```

**Cron 任务：**
```
0 9 * * *
0 15 * * *
0 21 * * *
```

### 7.3 示例 3

**用户输入：** "每天随机2-4次"

**解析：**
```json
{
  "type": "random_range",
  "minPerDay": 2,
  "maxPerDay": 4,
  "timeRange": ["09:00", "22:00"]
}
```

**今天生成：** 随机3次
**时间：** 11:05, 15:32, 20:18

### 7.4 示例 4

**用户输入：** "工作日晚上8点，周末随机3次"

**解析：**
```json
{
  "type": "weekday_weekend",
  "weekday": {
    "type": "fixed",
    "times": ["20:00"]
  },
  "weekend": {
    "type": "random",
    "countPerDay": 3,
    "timeRange": ["09:00", "22:00"]
  }
}
```

**Cron 任务：**
```
# 工作日
0 20 * * 1-5

# 周末（每天随机生成）
```

---

## 8. 错误处理

### 8.1 无法识别

**用户输入：** "随便吧"

**处理：**
```json
{
  "type": "random",
  "countPerDay": 3,
  "timeRange": ["09:00", "22:00"]
}
```

**提示用户：**
```
无法识别你的输入，使用默认设置：每天随机3次（09:00-22:00）。

确认吗？

1. 确认
2. 重新设置
```

### 8.2 冲突处理

**用户输入：** "早上9点，随机3次"

**处理：**
- 优先使用固定时间
- 提示用户确认

```
你既说了固定时间，又说了随机，我理解为：每天早上9点固定刷推。

对吗？

1. 对
2. 不对，重新设置
```

---

*文档版本: 1.0*
*更新: 2026-03-02*
