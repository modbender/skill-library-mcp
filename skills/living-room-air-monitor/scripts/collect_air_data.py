#!/usr/bin/env python3
"""
Collect air quality data from living room sensor and store in SQLite database.
Run via cron every 4 hours: 0 0,4,8,12,16,20 * * *
"""

import sqlite3
import sys
import os
from datetime import datetime
import json
import urllib.request
import urllib.error
import ssl

# Database path (in skill data folder)
DB_PATH = os.path.expanduser("~/.openclaw/workspace/skills/living-room-air-monitor/data/air_quality.db")

# Dirigera hub settings
HUB_IP = "192.168.1.100"
TOKEN_FILE = os.path.expanduser("~/.openclaw/workspace/.dirigera_token")

def get_token():
    """Read token from file."""
    try:
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Token file not found: {TOKEN_FILE}")
        return None

def fetch_air_data():
    """Fetch air quality data from Dirigera hub."""
    token = get_token()
    if not token:
        return None
    
    url = f"https://{HUB_IP}:8443/v1/devices"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create SSL context that ignores certificate verification
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            devices = json.loads(response.read().decode('utf-8'))
            
            # Find the air quality sensor in living room
            for device in devices:
                if device.get('deviceType') == 'environmentSensor':
                    attributes = device.get('attributes', {})
                    room = device.get('room', {}).get('name', 'Unknown')
                    
                    if room.lower() == 'living room':
                        return {
                            'temperature': attributes.get('currentTemperature'),
                            'humidity': attributes.get('currentRH'),
                            'pm25': attributes.get('currentPM25'),
                            'co2': attributes.get('currentCO2'),
                            'datetime': datetime.now().isoformat()
                        }
            
            print("No air quality sensor found in living room")
            return None
            
    except urllib.error.URLError as e:
        print(f"Network error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def init_database():
    """Initialize the database with required table."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS air_quality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL UNIQUE,
            temperature REAL,
            humidity REAL,
            pm25 REAL,
            co2 REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_datetime ON air_quality(datetime)
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def save_reading(data):
    """Save a reading to the database. Skip if any value is None."""
    if data is None:
        print("No data to save (fetch failed)")
        return False
    
    # Check if any required value is None
    if (data.get('temperature') is None or 
        data.get('humidity') is None or 
        data.get('pm25') is None or 
        data.get('co2') is None):
        print("Incomplete data, skipping save")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO air_quality (datetime, temperature, humidity, pm25, co2)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['datetime'],
            data['temperature'],
            data['humidity'],
            data['pm25'],
            data['co2']
        ))
        conn.commit()
        print(f"Saved reading for {data['datetime']}")
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main entry point."""
    # Initialize database if needed
    init_database()
    
    # Fetch data from sensor
    print("Fetching air quality data...")
    data = fetch_air_data()
    
    # Save to database (only if all values present)
    if data:
        success = save_reading(data)
        if success:
            print(f"Temperature: {data['temperature']}°C")
            print(f"Humidity: {data['humidity']}%")
            print(f"PM2.5: {data['pm25']} µg/m³")
            print(f"CO2: {data['co2']} ppm")
        else:
            print("Failed to save reading")
            sys.exit(1)
    else:
        print("Failed to fetch data from sensor")
        sys.exit(1)

if __name__ == "__main__":
    main()
