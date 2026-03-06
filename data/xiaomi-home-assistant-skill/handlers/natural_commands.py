#!/usr/bin/env python3
"""
OpenClaw Smart Home Natural Language Command Handler
Handles natural language commands for smart home control
"""

import json
import requests

class SmartHomeHandler:
    def __init__(self):
        # Load HA config
        # Use relative path - config.json should be in the same directory as this skill
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        self.ha_url = self.config['homeassistant']['url']
        self.token = self.config['homeassistant']['token']
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def execute_service(self, domain, service, entity_id, **kwargs):
        """Execute HA service"""
        url = f"{self.ha_url}/api/services/{domain}/{service}"
        data = {"entity_id": entity_id}
        data.update(kwargs)
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error executing service: {e}")
            return False
    
    def get_entity_state(self, entity_id):
        """Get entity state from HA"""
        url = f"{self.ha_url}/api/states/{entity_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting state: {e}")
            return None

# Natural language command mappings
COMMAND_MAPPINGS = {
    # Lighting
    "开灯": {"domain": "switch", "service": "turn_on", "entities": ["switch.zimi_dhkg02_35af_left_switch_service"]},
    "关灯": {"domain": "switch", "service": "turn_off", "entities": ["switch.zimi_dhkg02_35af_left_switch_service"]},
    "客厅灯": {"domain": "switch", "service": "toggle", "entities": ["switch.zimi_dhkg02_35af_left_switch_service"]},
    "卧室灯": {"domain": "switch", "service": "toggle", "entities": ["switch.zimi_dhkg02_16f1_left_switch_service"]},
    "阅读灯": {"domain": "switch", "service": "toggle", "entities": ["switch.zimi_dhkg01_2569_switch"]},
    
    # Curtains
    "开窗帘": {"domain": "cover", "service": "open_cover", "entities": ["cover.lumi_hmcn01_ea25_curtain"]},
    "关窗帘": {"domain": "cover", "service": "close_cover", "entities": ["cover.lumi_hmcn01_ea25_curtain"]},
    
    # Environment
    "客厅温度": {"sensor": "sensor.miaomiaoce_t2_06b8_temperature"},
    "客厅湿度": {"sensor": "sensor.miaomiaoce_t2_06b8_relative_humidity"},
    "卧室温度": {"sensor": "sensor.miaomiaoce_t2_245b_temperature"},
    "卧室湿度": {"sensor": "sensor.miaomiaoce_t2_245b_relative_humidity"},
}