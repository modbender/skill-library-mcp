#!/usr/bin/env python3
"""
安全的静默监控处理器 - 不写入任何文件，仅返回内存中的结果
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Any

class SafeMonitoringHandler:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.monitoring_config = self.config.get('monitoring', {})
        
        # 默认配置
        self.default_thresholds = {
            'pet_water_filter_min': 10,
            'pet_water_battery_min': 10,
            'humidity_max': 70,
            'humidity_min': 40
        }
        
        # 合并用户配置和默认配置
        self.thresholds = {**self.default_thresholds, **self.monitoring_config.get('thresholds', {})}
        
    def _load_config(self, config_path: str) -> Dict:
        """加载智能家居配置"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def get_device_states(self) -> Dict[str, Any]:
        """获取所有相关设备的当前状态"""
        ha_url = self.config['homeassistant']['url']
        token = self.config['homeassistant']['token']
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        device_states = {}
        
        try:
            # 获取加湿器状态
            humidifier_response = requests.get(
                f"{ha_url}/api/states/switch.zimi_dhkg02_35af_right_switch_service",
                headers=headers,
                timeout=10
            )
            if humidifier_response.status_code == 200:
                device_states['humidifier'] = humidifier_response.json()
            else:
                device_states['humidifier'] = {'state': 'unavailable'}
            
            # 获取宠物饮水机滤芯状态
            pet_filter_response = requests.get(
                f"{ha_url}/api/states/sensor.petoneer_fresh_600_filter_life",
                headers=headers,
                timeout=10
            )
            if pet_filter_response.status_code == 200:
                device_states['pet_water_filter'] = pet_filter_response.json()
            else:
                device_states['pet_water_filter'] = {'state': 'unknown'}
            
            # 获取宠物饮水机电池状态
            pet_battery_response = requests.get(
                f"{ha_url}/api/states/sensor.petoneer_fresh_600_battery",
                headers=headers,
                timeout=10
            )
            if pet_battery_response.status_code == 200:
                device_states['pet_water_battery'] = pet_battery_response.json()
            else:
                device_states['pet_water_battery'] = {'state': 'unknown'}
            
            # 获取卧室湿度
            bedroom_humidity_response = requests.get(
                f"{ha_url}/api/states/sensor.miaomiaoce_t2_06b8_relative_humidity",
                headers=headers,
                timeout=10
            )
            if bedroom_humidity_response.status_code == 200:
                device_states['bedroom_humidity'] = bedroom_humidity_response.json()
            else:
                device_states['bedroom_humidity'] = {'state': 'unknown'}
            
            # 获取门锁状态
            door_lock_response = requests.get(
                f"{ha_url}/api/states/lock.aqara_v3_lock",
                headers=headers,
                timeout=10
            )
            if door_lock_response.status_code == 200:
                device_states['door_lock'] = door_lock_response.json()
            else:
                device_states['door_lock'] = {'state': 'unavailable'}
                
        except requests.exceptions.RequestException as e:
            # 网络连接问题
            device_states['network_error'] = str(e)
            
        return device_states
    
    def check_for_anomalies(self, device_states: Dict[str, Any]) -> List[str]:
        """检查设备状态中的异常情况"""
        anomalies = []
        
        # 检查网络连接问题
        if 'network_error' in device_states:
            anomalies.append(f"网络连接问题: {device_states['network_error']}")
            return anomalies
        
        # 检查加湿器离线
        humidifier_state = device_states.get('humidifier', {}).get('state', 'unavailable')
        if humidifier_state == 'unavailable':
            anomalies.append("加湿器离线")
        
        # 检查宠物饮水机滤芯
        try:
            filter_state = device_states.get('pet_water_filter', {}).get('state', 'unknown')
            if filter_state != 'unknown':
                filter_percent = float(filter_state)
                if filter_percent <= self.thresholds['pet_water_filter_min']:
                    anomalies.append(f"宠物饮水机滤芯剩余{filter_percent}%，需要更换")
        except (ValueError, TypeError):
            pass
        
        # 检查宠物饮水机电池
        try:
            battery_state = device_states.get('pet_water_battery', {}).get('state', 'unknown')
            if battery_state != 'unknown':
                battery_percent = float(battery_state)
                if battery_percent <= self.thresholds['pet_water_battery_min']:
                    anomalies.append(f"宠物饮水机电池剩余{battery_percent}%，需要充电")
        except (ValueError, TypeError):
            pass
        
        # 检查卧室湿度
        try:
            humidity_state = device_states.get('bedroom_humidity', {}).get('state', 'unknown')
            if humidity_state != 'unknown':
                humidity_value = float(humidity_state)
                if humidity_value > self.thresholds['humidity_max']:
                    anomalies.append(f"卧室湿度过高({humidity_value}%)，建议通风")
                elif humidity_value < self.thresholds['humidity_min']:
                    anomalies.append(f"卧室湿度过低({humidity_value}%)，建议开启加湿器")
        except (ValueError, TypeError):
            pass
        
        # 检查门锁异常状态
        door_lock_state = device_states.get('door_lock', {}).get('state', 'unavailable')
        if door_lock_state == 'unavailable':
            anomalies.append("门锁离线")
        elif door_lock_state not in ['locked', 'unlocked']:
            anomalies.append(f"门锁状态异常: {door_lock_state}")
        
        return anomalies
    
    def perform_monitoring_check(self) -> str:
        """
        执行监控检查并返回结果
        不写入任何文件，仅返回字符串结果
        """
        device_states = self.get_device_states()
        anomalies = self.check_for_anomalies(device_states)
        
        if anomalies:
            message = "【智能家居异常告警】\n"
            message += "\n".join(anomalies)
            return message
        else:
            return "HEARTBEAT_OK"

if __name__ == "__main__":
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    handler = SafeMonitoringHandler(config_path)
    response = handler.perform_monitoring_check()
    print(response)