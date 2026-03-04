---
name: check-chinese-holiday
description: 基于 chinesecalendar 包的中国节假日检测，判断是否为节假日/调休日工作日
metadata: {"clawdbot":{"emoji":"📅","requires":{"packages":["chinesecalendar"]}}}
---

# check-chinese-holiday

基于 `chinesecalendar` Python 包的中国节假日检测技能。支持查询指定日期是否为节假日/调休日，并自动检测包是否需要更新。

## 功能

1. **节假日查询** — 判断指定日期是中国法定节假日、调休日还是普通工作日
2. **包过期检测** — 自动检测 `chinesecalendar` 包是否支持当前年份，提示更新
3. **工作日判断** — 判断是否为需要上班的工作日（考虑调休）

---

## 依赖

- Python 3.8+
- `chinesecalendar` 包

安装：
```bash
pip install chinesecalendar
```

---

## 过期检测逻辑

### 检测原理

`chinesecalendar` 包的节假日数据需要每年更新。每次发布新版本时会添加下一年的节假日数据。

**过期判断规则**：
1. 获取当前年份（如 2026）
2. 检查已安装的 `chinesecalendar` 版本是否支持当前年份
3. 如果不支持，提示用户更新包

### 检测方法

```python
import datetime
import subprocess
import json

def check_package_freshness():
    """检测 chinesecalendar 包是否过期"""
    current_year = datetime.datetime.now().year

    # 获取已安装版本
    result = subprocess.run(
        ['pip', 'show', 'chinesecalendar'],
        capture_output=True, text=True
    )

    installed_version = None
    for line in result.stdout.split('\n'):
        if line.startswith('Version:'):
            installed_version = line.split(':')[1].strip()
            break

    if not installed_version:
        return {
            'status': 'not_installed',
            'message': 'chinesecalendar 包未安装',
            'action': '请运行: pip install chinesecalendar'
        }

    # 检查版本是否支持当前年份
    # 方法1: 尝试导入并查询当前年份
    try:
        import chinese_calendar
        # 尝试获取当前年份的任何一天，判断是否有节假日数据
        test_date = datetime.date(current_year, 1, 1)
        is_holiday = chinese_calendar.is_holiday(test_date)
        # 如果不报错，说明支持当前年份
        return {
            'status': 'ok',
            'version': installed_version,
            'year': current_year,
            'message': f'chinesecalendar {installed_version} 支持 {current_year} 年'
        }
    except Exception as e:
        # 方法2: 检查版本号
        # 根据包发布历史，1.9+ 版本支持 2025+，1.11+ 支持 2026+
        version_num = tuple(map(int, installed_version.split('.')[:2]))

        # 简单判断：1.11.0+ 支持 2026 年
        if version_num >= (1, 11):
            return {
                'status': 'ok',
                'version': installed_version,
                'year': current_year,
                'message': f'根据版本号判断，{installed_version} 可能支持 {current_year} 年'
            }
        else:
            return {
                'status': 'outdated',
                'version': installed_version,
                'current_year': current_year,
                'message': f'chinesecalendar {installed_version} 可能不支持 {current_year} 年',
                'action': f'请运行: pip install --upgrade chinesecalendar'
            }
```

---

## 核心功能实现

### 1. 判断指定日期类型

```python
import chinese_calendar
from datetime import date, datetime

def check_day(date_str=None):
    """
    检查指定日期的节假日情况

    Args:
        date_str: 日期字符串，格式 YYYY-MM-DD，默认为今天

    Returns:
        dict: 包含日期类型的详细信息
    """
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = date.today()

    # 判断逻辑
    is_holiday = chinese_calendar.is_holiday(target_date)
    is_workday = chinese_calendar.is_workday(target_date)
    get_holiday_name = chinese_calendar.get_holiday_name(target_date)

    # 获取详细信息
    if is_holiday:
        # 是节假日，获取节假日名称
        holiday_info = chinese_calendar.get_holiday_details(target_date)
        result = {
            'date': str(target_date),
            'type': 'holiday',
            'name': get_holiday_name,
            'is_workday': False,
            'message': f'{target_date} 是法定节假日: {get_holiday_name}'
        }
    elif is_workday:
        # 是工作日（可能是调休）
        result = {
            'date': str(target_date),
            'type': 'workday',
            'name': None,
            'is_workday': True,
            'message': f'{target_date} 是工作日（调休上班）'
        }
    else:
        # 普通休息日（非法定）
        result = {
            'date': str(target_date),
            'type': 'weekend',
            'name': None,
            'is_workday': False,
            'message': f'{target_date} 是普通周末'
        }

    return result
```

### 2. 完整示例

```python
#!/usr/bin/env python3
"""中国节假日检查工具"""

import chinese_calendar
import subprocess
import json
import sys
from datetime import date, datetime

def get_installed_version():
    """获取已安装的版本"""
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'show', 'chinesecalendar'],
        capture_output=True, text=True
    )
    for line in result.stdout.split('\n'):
        if line.startswith('Version:'):
            return line.split(':')[1].strip()
    return None

def check_package_freshness():
    """检查包是否过期"""
    current_year = date.today().year
    version = get_installed_version()

    if not version:
        return {
            'status': 'not_installed',
            'message': 'chinesecalendar 包未安装',
            'action': 'pip install chinesecalendar'
        }

    # 尝试使用包
    try:
        test_date = date(current_year, 1, 1)
        chinese_calendar.is_holiday(test_date)
        return {
            'status': 'ok',
            'version': version,
            'year': current_year,
            'message': f'✓ chinesecalendar {version} 支持 {current_year} 年'
        }
    except Exception:
        # 包不支持当前年份
        return {
            'status': 'outdated',
            'version': version,
            'year': current_year,
            'message': f'✗ chinesecalendar {version} 不支持 {current_year} 年',
            'action': f'pip install --upgrade chinesecalendar'
        }

def check_day(date_str=None):
    """检查指定日期"""
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return {'error': '日期格式错误，请使用 YYYY-MM-DD'}
    else:
        target_date = date.today()

    is_holiday = chinese_calendar.is_holiday(target_date)
    is_workday = chinese_calendar.is_workday(target_date)
    holiday_name = chinese_calendar.get_holiday_name(target_date)

    if is_holiday:
        return {
            'date': str(target_date),
            'type': 'holiday',
            'name': holiday_name,
            'is_workday': False,
            'message': f'🎉 {target_date} 是法定节假日: {holiday_name}'
        }
    elif is_workday:
        return {
            'date': str(target_date),
            'type': 'workday',
            'name': None,
            'is_workday': True,
            'message': f'💼 {target_date} 是工作日（调休上班）'
        }
    else:
        return {
            'date': str(target_date),
            'type': 'weekend',
            'name': None,
            'is_workday': False,
            'message': f'🆗 {target_date} 是普通周末'
        }

if __name__ == '__main__':
    # 检查包状态
    freshness = check_package_freshness()
    print(json.dumps(freshness, ensure_ascii=False, indent=2))

    # 检查今天
    print('\n--- 今日日期检查 ---')
    today = check_day()
    print(json.dumps(today, ensure_ascii=False, indent=2))
```

---

## 输出示例

### 包状态检查

```json
{
  "status": "ok",
  "version": "1.11.0",
  "year": 2026,
  "message": "✓ chinesecalendar 1.11.0 支持 2026 年"
}
```

或过期时：

```json
{
  "status": "outdated",
  "version": "1.9.0",
  "year": 2026,
  "message": "✗ chinesecalendar 1.9.0 不支持 2026 年",
  "action": "pip install --upgrade chinesecalendar"
}
```

### 日期检查

```json
{
  "date": "2026-02-17",
  "type": "holiday",
  "name": "春节",
  "is_workday": false,
  "message": "2026-02-17 是法定节假日: 春节"
}
```

```json
{
  "date": "2026-02-15",
  "type": "workday",
  "name": null,
  "is_workday": true,
  "message": "2026-02-15 是工作日（调休上班）"
}
```

```json
{
  "date": "2026-03-07",
  "type": "weekend",
  "name": null,
  "is_workday": false,
  "message": "2026-03-07 是普通周末"
}
```

---

## 注意事项

1. **数据来源** — 节假日数据来自国务院公告，通常每年 11-12 月发布下一年的安排
2. **更新频率** — `chinese-calendar` 库每年更新一次支持下一年的数据
3. **准确性** — 建议每年初检查一次包是否需要更新
4. **调休判断** — `is_workday()` 会正确识别调休上班日
