#!/usr/bin/env python3
"""
Environment monitoring and context awareness for smart home
"""

import json
import requests
from datetime import datetime

class EnvironmentMonitor:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
    def get_current_environment(self):
        """Get current temperature, humidity, and device states"""
        ha_url = self.config['homeassistant']['url']
        token = self.config['homeassistant']['token']
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Get living room temperature
        temp_response = requests.get(
            f"{ha_url}/api/states/sensor.miaomiaoce_t2_06b8_temperature",
            headers=headers
        )
        
        # Get living room humidity  
        humidity_response = requests.get(
            f"{ha_url}/api/states/sensor.miaomiaoce_t2_06b8_relative_humidity",
            headers=headers
        )
        
        environment = {
            'timestamp': datetime.now().isoformat(),
            'living_room': {
                'temperature': temp_response.json()['state'] if temp_response.status_code == 200 else 'unknown',
                'humidity': humidity_response.json()['state'] if humidity_response.status_code == 200 else 'unknown'
            }
        }
        
        return environment
        
    def is_comfortable(self):
        """Check if current environment is comfortable"""
        env = self.get_current_environment()
        temp = float(env['living_room']['temperature'])
        humidity = float(env['living_room']['humidity'])
        
        # Comfortable range: 22-26°C, 40-60% humidity
        temp_comfortable = 22 <= temp <= 26
        humidity_comfortable = 40 <= humidity <= 60
        
        return temp_comfortable and humidity_comfortable
        
if __name__ == "__main__":
    monitor = EnvironmentMonitor()
    print(json.dumps(monitor.get_current_environment(), indent=2))