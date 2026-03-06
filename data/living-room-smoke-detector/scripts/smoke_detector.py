#!/usr/bin/env python3
"""
Living Room Smoke Detector
Simple smoke/fire detection using Dirigera air sensor.
Queries sensor every 5 minutes, broadcasts alert on Mac speaker if danger detected.
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import ssl
from datetime import datetime

# Paths
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

STATE_FILE = os.path.join(DATA_DIR, "detector_state.json")
ALERT_SOUND_PATH = os.path.join(DATA_DIR, "alert.mp3")
TOKEN_FILE = os.path.expanduser("~/.openclaw/workspace/.dirigera_token")

# Settings
HUB_IP = "192.168.1.100"
PM25_THRESHOLD = 250
CO2_THRESHOLD = 2000
ALERT_INTERVAL = 5  # seconds between alert plays

# Load or create state
def load_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {
        'latest_reading': None,
        'alert_active': False,
        'last_check': None
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

# Fetch current air data from Dirigera
def fetch_air_data():
    try:
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()
    except:
        print("❌ No token file")
        return None
    
    url = f"https://{HUB_IP}:8443/v1/devices"
    headers = {"Authorization": f"Bearer {token}"}
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            devices = json.loads(response.read().decode('utf-8'))
            
            for device in devices:
                if device.get('deviceType') == 'environmentSensor':
                    attrs = device.get('attributes', {})
                    room = device.get('room', {}).get('name', '')
                    
                    if room.lower() == 'living room':
                        return {
                            'pm25': attrs.get('currentPM25'),
                            'co2': attrs.get('currentCO2'),
                            'time': datetime.now().isoformat()
                        }
    except Exception as e:
        print(f"❌ Fetch error: {e}")
    
    return None

# Check if alert needed
def check_danger(reading):
    if not reading:
        return False
    pm25 = reading.get('pm25')
    co2 = reading.get('co2')
    
    if pm25 is None or co2 is None:
        return False
    
    return pm25 > PM25_THRESHOLD or co2 > CO2_THRESHOLD

# Play alert sound
def play_alert():
    try:
        subprocess.run(['afplay', ALERT_SOUND_PATH], timeout=15, check=True)
        return True
    except:
        return False

# Generate alert sound if missing
def ensure_alert_sound():
    if os.path.exists(ALERT_SOUND_PATH):
        return True
    
    print("Generating alert sound...")
    try:
        aiff = "/tmp/alert.aiff"
        subprocess.run(['say', '-v', 'Samantha', '-o', aiff, 
                       "Attention! Abnormal smoke level detected."], 
                      check=True, capture_output=True)
        subprocess.run(['ffmpeg', '-y', '-i', aiff, '-ar', '44100', 
                       '-ac', '2', '-b:a', '192k', ALERT_SOUND_PATH],
                      check=True, capture_output=True)
        os.remove(aiff)
        return True
    except:
        return False

# Main alert loop - plays continuously until air clears
def alert_loop(state):
    print("🚨 DANGER! Entering alert loop...")
    print("   Press Ctrl+C to stop manually")
    
    play_count = 0
    
    try:
        while True:
            play_count += 1
            print(f"   Alert #{play_count}", end=" ")
            
            if play_alert():
                print("✅")
            else:
                print("❌")
            
            time.sleep(ALERT_INTERVAL)
            
            # Check if air cleared
            reading = fetch_air_data()
            if reading:
                state['latest_reading'] = reading
                save_state(state)
                
                pm25 = reading.get('pm25', 0)
                co2 = reading.get('co2', 0)
                print(f"   Check: PM2.5={pm25}, CO2={co2}")
                
                if not check_danger(reading):
                    print("✅ Air cleared! Exiting alert loop.")
                    break
                    
    except KeyboardInterrupt:
        print("\n⚠️ Alert loop interrupted")
    
    return play_count

# Main function
def main():
    print("=" * 50)
    print("🔥 LIVING ROOM SMOKE DETECTOR")
    print("=" * 50)
    print(f"Thresholds: PM2.5 >{PM25_THRESHOLD}, CO2 >{CO2_THRESHOLD}")
    print()
    
    # Ensure alert sound exists
    if not ensure_alert_sound():
        print("❌ Failed to create alert sound")
        sys.exit(1)
    
    # Load state
    state = load_state()
    
    # Fetch current reading
    print("Checking sensor...")
    reading = fetch_air_data()
    
    if not reading:
        print("❌ Failed to read sensor")
        sys.exit(1)
    
    # Save latest reading
    state['latest_reading'] = reading
    pm25 = reading.get('pm25', 0)
    co2 = reading.get('co2', 0)
    
    print(f"Reading: PM2.5={pm25} µg/m³, CO2={co2} ppm")
    
    # Check for danger
    if check_danger(reading):
        state['alert_active'] = True
        save_state(state)
        
        # Run alert loop
        plays = alert_loop(state)
        print(f"Total alerts played: {plays}")
        
        # Clear alert
        state['alert_active'] = False
        print("📢 Alert cleared")
    else:
        print("✅ Air quality normal")
        state['alert_active'] = False
    
    # Save final state
    state['last_check'] = datetime.now().isoformat()
    save_state(state)
    print(f"Last check: {state['last_check']}")

if __name__ == "__main__":
    main()
