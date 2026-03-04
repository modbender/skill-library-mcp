#!/usr/bin/env python3
"""中国节假日检查 - 用于 cron 任务前置检查"""
import sys
import subprocess

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
    import datetime
    from datetime import date
    
    current_year = date.today().year
    version = get_installed_version()
    
    if not version:
        return {'status': 'not_installed', 'message': 'chinesecalendar 包未安装'}
    
    try:
        import chinese_calendar
        test_date = date(current_year, 1, 1)
        chinese_calendar.is_holiday(test_date)
        return {'status': 'ok', 'version': version, 'year': current_year}
    except Exception:
        return {'status': 'outdated', 'version': version, 'year': current_year}

def check_today():
    """检查今天是否为工作日"""
    from datetime import date
    from datetime import datetime
    
    try:
        import chinese_calendar
    except ImportError:
        return {'error': 'chinese_calendar 未安装', 'should_remind': False}
    
    target_date = date.today()
    is_holiday = chinese_calendar.is_holiday(target_date)
    is_workday = chinese_calendar.is_workday(target_date)
    
    if is_holiday:
        return {
            'date': str(target_date),
            'type': 'holiday',
            'should_remind': False,
            'message': f'{target_date} 是法定节假日，不提醒'
        }
    elif is_workday:
        return {
            'date': str(target_date),
            'type': 'workday',
            'should_remind': True,
            'message': f'{target_date} 是工作日，需要提醒'
        }
    else:
        return {
            'date': str(target_date),
            'type': 'weekend',
            'should_remind': False,
            'message': f'{target_date} 是周末，不提醒'
        }

if __name__ == '__main__':
    import json
    
    # 先检查包状态
    freshness = check_package_freshness()
    
    if freshness['status'] != 'ok':
        # 包有问题，输出错误并退出（不发送提醒）
        print(json.dumps(freshness, ensure_ascii=False))
        sys.exit(1)
    
    # 检查今天
    result = check_today()
    print(json.dumps(result, ensure_ascii=False))
    
    if result.get('should_remind'):
        sys.exit(0)  # 需要提醒
    else:
        sys.exit(2)  # 不需要提醒
