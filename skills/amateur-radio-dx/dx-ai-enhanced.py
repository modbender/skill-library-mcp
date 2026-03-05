#!/usr/bin/env python3
"""
AI-Enhanced DX Monitor
Adds propagation prediction and DXCC filtering to ham-radio-dx
"""

import json
import sys
import os
import subprocess
from datetime import datetime
import math

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'dx-ai-config.json')

def load_config():
    """Load user configuration"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Config file not found: {CONFIG_FILE}")
        print("Run: python3 dx-ai-enhanced.py setup")
        sys.exit(1)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate great circle distance in km"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def grid_to_latlon(grid):
    """Convert Maidenhead grid to lat/lon (center of grid square)"""
    if len(grid) < 4:
        return None, None
    
    grid = grid.upper()
    lon = (ord(grid[0]) - ord('A')) * 20 - 180
    lat = (ord(grid[1]) - ord('A')) * 10 - 90
    lon += (ord(grid[2]) - ord('0')) * 2
    lat += (ord(grid[3]) - ord('0')) * 1
    lon += 1  # Center of square
    lat += 0.5
    
    return lat, lon

def get_solar_data():
    """Fetch current solar conditions (placeholder - would use real API)"""
    # TODO: Integrate with real solar data API
    # For now, return moderate conditions
    return {
        "sfi": 150,  # Solar Flux Index
        "a_index": 10,
        "k_index": 2,
        "ssn": 100,  # Sunspot number
        "condition": "fair"
    }

def predict_propagation(distance_km, band, mode, solar_data):
    """
    Predict propagation workability score (0.0-1.0)
    
    This is a simplified model. In production, would use:
    - ML model trained on historical QSO data
    - Real-time ionospheric data
    - Path loss calculations
    - Mode-specific considerations
    """
    
    # Band characteristics (rough optimal distance ranges in km)
    band_ranges = {
        "160m": (0, 800),
        "80m": (0, 1500),
        "40m": (0, 3000),
        "30m": (500, 5000),
        "20m": (1000, 8000),
        "17m": (1000, 10000),
        "15m": (1500, 12000),
        "12m": (1500, 12000),
        "10m": (2000, 15000),
        "6m": (0, 3000)
    }
    
    # Get band optimal range
    if band not in band_ranges:
        return 0.3  # Unknown band, moderate score
    
    min_dist, max_dist = band_ranges[band]
    
    # Calculate distance factor
    if distance_km < min_dist:
        distance_factor = distance_km / min_dist if min_dist > 0 else 0.5
    elif distance_km > max_dist:
        distance_factor = max(0.2, 1.0 - ((distance_km - max_dist) / max_dist))
    else:
        distance_factor = 0.9  # Sweet spot
    
    # Solar condition factor
    sfi = solar_data.get("sfi", 100)
    if band in ["10m", "12m", "15m"]:
        # Higher bands need better solar conditions
        solar_factor = min(1.0, sfi / 150)
    elif band in ["20m", "17m", "30m"]:
        solar_factor = 0.9  # Mid bands work in most conditions
    else:
        # Lower bands less dependent on solar
        solar_factor = 0.8
    
    # Mode factor (digital modes work better in poor conditions)
    mode_factor = {
        "FT8": 1.0,
        "FT4": 1.0,
        "CW": 0.9,
        "SSB": 0.7,
        "RTTY": 0.85
    }.get(mode, 0.8)
    
    # Combined score
    score = distance_factor * solar_factor * mode_factor
    
    return min(1.0, max(0.0, score))

def score_dx_spot(spot, config):
    """Score a DX spot based on workability and desirability"""
    
    # Parse spot data
    # Expected format: freq, dx_call, spotter, time, comment
    parts = spot.strip().split()
    if len(parts) < 3:
        return None
    
    try:
        freq = float(parts[0])
        dx_call = parts[1]
        
        # Determine band from frequency
        band = frequency_to_band(freq)
        if not band:
            return None
        
        # Extract prefix/DXCC entity (simplified)
        prefix = extract_prefix(dx_call)
        
        # Check if needed
        needed = prefix in config['needed_dxcc']
        already_worked = prefix in config.get('worked_dxcc', [])
        
        # Rarity score (0-1)
        if prefix in ['VP8', 'VK0', '3Y0', 'FT5', 'P5', 'BS7']:
            rarity = 1.0  # Most wanted
        elif prefix in ['ZL', 'VK', 'ZS', '9G', 'S9']:
            rarity = 0.8  # Rare
        elif needed:
            rarity = 0.6  # Needed but not super rare
        else:
            rarity = 0.3  # Common
        
        # Get solar data
        solar_data = get_solar_data()
        
        # Estimate DX location (would use callsign database in production)
        # For now, rough estimates based on prefix
        dx_locations = {
            "VP8": (-51.7963, -59.5236),  # Falklands
            "ZL": (-41.2865, 174.7762),    # New Zealand
            "VK": (-25.2744, 133.7751),    # Australia
            "ZS": (-30.5595, 22.9375),     # South Africa
            "P5": (40.3399, 127.5101),     # North Korea
        }
        
        # Try to get DX lat/lon
        dx_lat, dx_lon = dx_locations.get(prefix, (0, 0))
        
        # Calculate distance
        my_lat = config['operator']['qth']['latitude']
        my_lon = config['operator']['qth']['longitude']
        distance_km = calculate_distance(my_lat, my_lon, dx_lat, dx_lon)
        
        # Guess mode from frequency/comment (would parse properly in production)
        mode = "CW"  # Default
        if ".074" in str(freq) or "FT8" in spot:
            mode = "FT8"
        elif ".076" in str(freq) or "FT4" in spot:
            mode = "FT4"
        elif freq > 14.100 or freq < 14.070:
            mode = "SSB"
        
        # Predict propagation
        workability = predict_propagation(distance_km, band, mode, solar_data)
        
        # Bonus for needed DXCC
        needed_bonus = 0.3 if needed and not already_worked else 0.0
        
        # Combined score
        total_score = (rarity * 0.4) + (workability * 0.5) + needed_bonus
        
        return {
            "spot": spot,
            "dx_call": dx_call,
            "prefix": prefix,
            "freq": freq,
            "band": band,
            "mode": mode,
            "distance_km": int(distance_km),
            "needed": needed,
            "already_worked": already_worked,
            "rarity": rarity,
            "workability": workability,
            "score": total_score,
            "solar": solar_data
        }
        
    except Exception as e:
        print(f"Error scoring spot: {e}")
        return None

def frequency_to_band(freq_khz):
    """Convert frequency to band"""
    freq_mhz = freq_khz / 1000.0
    
    if 1.8 <= freq_mhz <= 2.0:
        return "160m"
    elif 3.5 <= freq_mhz <= 4.0:
        return "80m"
    elif 7.0 <= freq_mhz <= 7.3:
        return "40m"
    elif 10.1 <= freq_mhz <= 10.15:
        return "30m"
    elif 14.0 <= freq_mhz <= 14.35:
        return "20m"
    elif 18.068 <= freq_mhz <= 18.168:
        return "17m"
    elif 21.0 <= freq_mhz <= 21.45:
        return "15m"
    elif 24.89 <= freq_mhz <= 24.99:
        return "12m"
    elif 28.0 <= freq_mhz <= 29.7:
        return "10m"
    else:
        return None

def extract_prefix(callsign):
    """Extract DXCC prefix from callsign (simplified)"""
    # Remove /P, /M, /QRP, etc.
    call = callsign.split('/')[0]
    
    # Common special prefixes
    special = {
        "VP8": "VP8",
        "VK0": "VK0",
        "3Y0": "3Y0",
        "FT5": "FT5",
        "P5": "P5",
        "BS7": "BS7",
    }
    
    for prefix in special:
        if call.startswith(prefix):
            return prefix
    
    # Standard 2-letter prefixes
    if len(call) >= 2:
        two_letter = call[:2]
        if two_letter in ["ZL", "VK", "ZS", "9G", "S9", "K1", "W5", "EA", "DL", "G3"]:
            return two_letter
    
    # Single letter prefixes
    if len(call) >= 1:
        return call[0]
    
    return "??"

def watch_with_ai(config):
    """Watch DX spots with AI filtering and scoring"""
    
    print("🤖 AI-Enhanced DX Monitor")
    print("=" * 60)
    print(f"📍 QTH: {config['operator']['qth']['location']} ({config['operator']['qth']['grid']})")
    print(f"📡 Station: {config['operator']['station']['power']}W")
    print(f"🎯 Needed DXCC: {', '.join(config['needed_dxcc'][:5])}...")
    print(f"⚡ Min Workability: {config['preferences']['min_workability_score']*100:.0f}%")
    print("=" * 60)
    print()
    
    # Get raw spots from original dx-monitor.py
    script_dir = os.path.dirname(__file__)
    dx_monitor = os.path.join(script_dir, 'dx-monitor.py')
    
    try:
        result = subprocess.run(
            ['python3', dx_monitor, 'watch', '--new-only'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Error running dx-monitor.py: {result.stderr}")
            return
        
        # Parse and score spots
        spots = []
        for line in result.stdout.split('\n'):
            if line.strip() and not line.startswith('📡') and not line.startswith(' '):
                scored = score_dx_spot(line, config)
                if scored:
                    spots.append(scored)
        
        # Filter by minimum workability
        min_score = config['preferences']['min_workability_score']
        filtered_spots = [s for s in spots if s['workability'] >= min_score]
        
        # Sort by total score (descending)
        filtered_spots.sort(key=lambda x: x['score'], reverse=True)
        
        # Display results
        if not filtered_spots:
            print("📭 No workable DX spots match your criteria right now")
            print()
            print("💡 Tips:")
            print("  - Try lowering min_workability_score in dx-ai-config.json")
            print("  - Check back in 15-30 minutes")
            print("  - Best DX often at sunrise/sunset")
            return
        
        print(f"✨ Found {len(filtered_spots)} workable DX spots!")
        print()
        
        # Solar conditions
        solar = filtered_spots[0]['solar']
        print(f"☀️  Solar: SFI={solar['sfi']} A={solar['a_index']} K={solar['k_index']} ({solar['condition']})")
        print()
        
        # Top spots
        print("🎯 Top Workable DX (sorted by score):")
        print()
        print(f"{'Score':<6} {'Call':<12} {'Band':<6} {'Mode':<6} {'Dist':<8} {'Work%':<6} {'Status'}")
        print("-" * 70)
        
        for spot in filtered_spots[:15]:  # Top 15
            score_bar = "█" * int(spot['score'] * 10)
            work_pct = int(spot['workability'] * 100)
            
            status_icons = []
            if spot['needed']:
                status_icons.append("🔥")
            if spot['already_worked']:
                status_icons.append("✓")
            if work_pct >= 80:
                status_icons.append("📡")
            
            status = " ".join(status_icons)
            
            print(f"{spot['score']:.2f}   {spot['dx_call']:<12} {spot['band']:<6} {spot['mode']:<6} "
                  f"{spot['distance_km']:>5}km {work_pct:>3}%  {status}")
        
        print()
        print("Legend: 🔥 = Needed  ✓ = Already worked  📡 = Excellent propagation")
        print()
        
        # Alert for high-priority spots
        alert_threshold = config['preferences'].get('alert_threshold', 0.7)
        high_priority = [s for s in filtered_spots if s['score'] >= alert_threshold]
        
        if high_priority:
            print("🚨 HIGH PRIORITY ALERTS:")
            for spot in high_priority[:3]:
                print(f"   📻 {spot['dx_call']} on {spot['band']} {spot['mode']} - "
                      f"{int(spot['workability']*100)}% workable, "
                      f"{spot['distance_km']}km - " 
                      f"{'NEEDED!' if spot['needed'] else 'Rare DX'}")
            print()
        
    except subprocess.TimeoutExpired:
        print("⏱️  Timeout connecting to DX cluster")
    except Exception as e:
        print(f"❌ Error: {e}")

def setup():
    """Interactive setup for config file"""
    print("🎯 Ham Radio AI-Enhanced DX Monitor - Setup")
    print("=" * 60)
    print()
    
    callsign = input("Your callsign: ").upper()
    grid = input("Your grid square (e.g., EM12): ").upper()
    power = int(input("TX power (watts): "))
    
    print()
    print("Needed DXCC entities (comma-separated prefixes):")
    print("Example: VP8,VK0,3Y0,ZL,VK,ZS,P5,BS7")
    needed_input = input("Needed: ")
    needed_dxcc = [x.strip() for x in needed_input.split(',')]
    
    # Convert grid to lat/lon
    lat, lon = grid_to_latlon(grid)
    
    config = {
        "operator": {
            "callsign": callsign,
            "qth": {
                "grid": grid,
                "latitude": lat,
                "longitude": lon,
                "location": "Auto-detected"
            },
            "station": {
                "power": power,
                "antenna": "user-configured",
                "modes": ["FT8", "FT4", "CW", "SSB"]
            }
        },
        "preferences": {
            "priority_modes": ["FT8", "FT4"],
            "priority_bands": ["20m", "17m", "15m"],
            "min_workability_score": 0.5,
            "alert_threshold": 0.7
        },
        "needed_dxcc": needed_dxcc,
        "worked_dxcc": []
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print()
    print(f"✅ Configuration saved to {CONFIG_FILE}")
    print()
    print("Run: python3 dx-ai-enhanced.py watch")
    print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 dx-ai-enhanced.py [watch|setup]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "setup":
        setup()
    elif command == "watch":
        config = load_config()
        watch_with_ai(config)
    else:
        print(f"Unknown command: {command}")
        print("Usage: python3 dx-ai-enhanced.py [watch|setup]")
        sys.exit(1)

if __name__ == "__main__":
    main()
