#!/usr/bin/env python3
"""
自動記錄健康數據到 AX3 系統
支援體重、血糖等多種健康指標的自動識別與記錄
"""
import re
import sys
import subprocess
import json
from datetime import datetime

# AX3 習慣 ID 映射
HABIT_MAP = {
    'weight': 1,      # 體重
    'blood_sugar': 4, # 血糖
    'running': 2      # 跑步機
}

def extract_weight(text):
    """從文字中提取體重數值"""
    patterns = [
        r'體重[：:]*\s*(\d+\.?\d*)\s*(?:kg|公斤|KG)?',
        r'(\d+\.?\d*)\s*(?:kg|公斤|KG)',
        r'^(\d+\.?\d*)$'  # 純數字
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            # 合理範圍檢查（40-200 kg）
            if 40 <= value <= 200:
                return value
    return None

def extract_blood_sugar(text):
    """從文字中提取血糖數值"""
    patterns = [
        r'血糖[：:]*\s*(\d+)',
        r'(\d+)\s*mg/dL'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = int(match.group(1))
            # 合理範圍檢查（50-500 mg/dL）
            if 50 <= value <= 500:
                return value
    return None

def extract_running_time(text):
    """從文字中提取跑步時間（分鐘）"""
    patterns = [
        r'跑步[機]*[：:]*\s*(\d+)\s*分',
        r'跑步[機]*[：:]*\s*(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None

def record_to_ax3(habit_id, value):
    """呼叫 mcporter 記錄到 AX3"""
    try:
        cmd = [
            'mcporter',
            '--config', '/Users/klcintw/clawd/config/mcporter.json',
            'call', 'ax3-personal.record_habit',
            f'habitId={habit_id}',
            f'numberValue={value}'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_message(text):
    """處理訊息並自動記錄健康數據"""
    results = []
    
    # 檢查體重
    weight = extract_weight(text)
    if weight:
        result = record_to_ax3(HABIT_MAP['weight'], weight)
        if result.get('success'):
            results.append({
                'type': 'weight',
                'value': weight,
                'unit': 'kg',
                'record_id': result.get('recordId'),
                'message': f"✅ 體重 {weight} kg 已記錄"
            })
    
    # 檢查血糖
    blood_sugar = extract_blood_sugar(text)
    if blood_sugar:
        result = record_to_ax3(HABIT_MAP['blood_sugar'], blood_sugar)
        if result.get('success'):
            results.append({
                'type': 'blood_sugar',
                'value': blood_sugar,
                'unit': 'mg/dL',
                'record_id': result.get('recordId'),
                'message': f"✅ 血糖 {blood_sugar} mg/dL 已記錄"
            })
    
    # 檢查跑步時間
    running = extract_running_time(text)
    if running:
        result = record_to_ax3(HABIT_MAP['running'], running)
        if result.get('success'):
            results.append({
                'type': 'running',
                'value': running,
                'unit': 'min',
                'record_id': result.get('recordId'),
                'message': f"✅ 跑步機 {running} 分鐘已記錄"
            })
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 record_health_data.py '<message_text>'")
        sys.exit(1)
    
    message = sys.argv[1]
    results = process_message(message)
    
    if results:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        for r in results:
            print(r['message'])
    else:
        print(json.dumps({'detected': False, 'message': '未偵測到健康數據'}))

if __name__ == '__main__':
    main()
