#!/usr/bin/env python3
"""
Smart Home Complex Scenarios Handler
Handles multi-step automation scenarios like "I'm home", "Good night", etc.
"""

import json
import requests
from datetime import datetime, time
import asyncio

class ScenarioHandler:
    def __init__(self):
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
    
    def scenario_im_home(self):
        """Execute 'I'm home' scenario"""
        actions = [
            # Turn on living room lights
            ("switch", "turn_on", "switch.zimi_dhkg02_35af_left_switch_service"),
            # Open curtains if it's daytime
            ("cover", "open_cover", "cover.lumi_hmcn01_ea25_curtain") if self.is_daytime() else None,
            # Play welcome message via TTS (placeholder)
            # Check environment comfort and adjust if needed
        ]
        
        results = []
        for action in actions:
            if action:
                success = self.execute_service(action[0], action[1], action[2])
                results.append(success)
        
        return all(results) if results else True
    
    def scenario_good_night(self):
        """Execute 'Good night' scenario"""
        actions = [
            # Turn off all lights
            ("switch", "turn_off", "switch.zimi_dhkg02_35af_left_switch_service"),
            ("switch", "turn_off", "switch.zimi_dhkg02_16f1_left_switch_service"),
            ("switch", "turn_off", "switch.zimi_dhkg01_2569_switch"),
            # Close curtains
            ("cover", "close_cover", "cover.lumi_hmcn01_ea25_curtain"),
            # Set security mode (placeholder)
        ]
        
        results = []
        for action in actions:
            success = self.execute_service(action[0], action[1], action[2])
            results.append(success)
        
        return all(results)
    
    def is_daytime(self):
        """Check if current time is daytime (6AM-8PM)"""
        now = datetime.now().time()
        return time(6, 0) <= now <= time(20, 0)
    
    def scenario_too_cold(self):
        """Handle 'too cold' scenario - check temp and suggest solutions"""
        # Get current temperature
        temp_response = requests.get(
            f"{self.ha_url}/api/states/sensor.miaomiaoce_t2_06b8_temperature",
            headers=self.headers
        )
        
        if temp_response.status_code == 200:
            temp = float(temp_response.json()['state'])
            if temp < 20:
                # Suggest turning on heating or adjusting environment
                return f"Current temperature is {temp}°C. Would you like me to turn on the heating or adjust the environment?"
        
        return "Unable to check temperature."
    
    def scenario_too_bright(self):
        """Handle 'too bright' scenario"""
        # Close curtains
        self.execute_service("cover", "close_cover", "cover.lumi_hmcn01_ea25_curtain")
        return "I've closed the curtains to reduce the brightness."

if __name__ == "__main__":
    handler = ScenarioHandler()
    # Test scenarios
    print("Testing 'I'm home' scenario...")
    print(handler.scenario_im_home())