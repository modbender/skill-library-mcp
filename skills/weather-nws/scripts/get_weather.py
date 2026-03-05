#!/usr/bin/env python3
"""
Unified weather fetcher with US (NWS) priority and global fallback (wttr.in)
Provides consistent, actionable output format.
Phase 1: Hourly forecast, AirNow AQI, structured grid data for accumulations
Phase 2: Station observations (--current), enhanced alert formatting with priorities
Phase 3: Astronomical times (--astro), aviation TAFs (--taf), fire weather (--fire)
"""

import sys
import json
import urllib.request
import urllib.parse
import os
import re
from datetime import datetime, timedelta

try:
    from dateutil import parser as date_parser
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False
    date_parser = None

# Temporal query detection patterns (pre-compiled for reuse)
TEMPORAL_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [
    r'tonight at\s+\d+',
    r'tonight',
    r'this afternoon',
    r'tomorrow morning',
    r'tomorrow afternoon',
    r'tomorrow night',
    r'tomorrow at\s+\d+',
    r'tomorrow',
    r'\d+\s*(?:am|pm|AM|PM)',
    r'at\s+\d+',
    r'when will',
    r'how long until',
    r'stop raining',
    r'stop snowing',
    r'start raining',
    r'start snowing',
    r'\d+:\d+',
]]

# AQI category colors and health recommendations
AQI_CATEGORIES = {
    (0, 50): {"name": "Good", "emoji": "🟢", "color": "green",
              "recommendation": "Air quality is satisfactory. Enjoy your outdoor activities!"},
    (51, 100): {"name": "Moderate", "emoji": "🟡", "color": "yellow",
                "recommendation": "Sensitive groups should consider limiting prolonged outdoor exertion."},
    (101, 150): {"name": "Unhealthy for Sensitive Groups", "emoji": "🟠", "color": "orange",
                 "recommendation": "Children, elderly, and those with respiratory/heart conditions should limit outdoor activities."},
    (151, 200): {"name": "Unhealthy", "emoji": "🔴", "color": "red",
                 "recommendation": "Everyone should reduce prolonged outdoor exertion. Sensitive groups: avoid outdoor activities."},
    (201, 300): {"name": "Very Unhealthy", "emoji": "🟣", "color": "purple",
                 "recommendation": "Avoid outdoor activities. Everyone may experience health effects."},
    (301, 500): {"name": "Hazardous", "emoji": "🔵", "color": "maroon",
                 "recommendation": "Health alert: everyone may experience serious health effects. Stay indoors."},
}

# Alert severity/urgency/certainty weights for priority calculation
ALERT_SEVERITY_WEIGHTS = {
    "Extreme": 4,
    "Severe": 3,
    "Moderate": 2,
    "Minor": 1,
    "Unknown": 0,
}

ALERT_URGENCY_WEIGHTS = {
    "Immediate": 3,
    "Expected": 2,
    "Future": 1,
    "Unknown": 0,
}

ALERT_CERTAINTY_WEIGHTS = {
    "Observed": 3,
    "Likely": 2,
    "Possible": 1,
    "Unknown": 0,
}

ALERT_SEVERITY_STYLES = {
    "Extreme": {"emoji": "⚫", "tint": "bold", "badge": "EXTREME"},
    "Severe": {"emoji": "🔴", "tint": "red", "badge": "SEVERE"},
    "Moderate": {"emoji": "🟠", "tint": "orange", "badge": "MODERATE"},
    "Minor": {"emoji": "🟡", "tint": "yellow", "badge": "MINOR"},
    "Unknown": {"emoji": "⚪", "tint": "none", "badge": "UNKNOWN"},
}

ALERT_URGENCY_TAGS = {
    "Immediate": "⏰ Immediate",
    "Expected": "📅 Expected",
    "Future": "🔮 Future",
    "Unknown": "❓ Unknown",
}

ALERT_RESPONSE_ACTIONS = {
    "Shelter": "🏠 Shelter in place",
    "Evacuate": "🏃 Evacuate immediately",
    "Prepare": "🎒 Prepare now",
    "Monitor": "👀 Monitor conditions",
    "Execute": "⚡ Execute plan",
    "Avoid": "🚫 Avoid area",
    "None": "ℹ️ Stay informed",
}


def geocode_location(location):
    """Convert location string to lat/lon using Nominatim (OSM)"""
    try:
        # Remove temporal qualifiers for geocoding
        clean_location = strip_temporal_qualifiers(location)
        # 5-digit US zip codes are ambiguous — Nominatim may match international
        # postal codes first. Append ", USA" to force US resolution.
        if re.match(r'^\d{5}(-\d{4})?$', clean_location.strip()):
            clean_location = clean_location.strip() + ', USA'
        encoded = urllib.parse.quote(clean_location)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data and len(data) > 0:
                return float(data[0]['lat']), float(data[0]['lon']), data[0].get('display_name', location)
    except Exception as e:
        print(f"Geocoding error: {e}", file=sys.stderr)
    return None, None, location


def strip_temporal_qualifiers(text):
    """Remove temporal qualifiers from location for geocoding"""
    # Remove common temporal patterns
    patterns_to_remove = [
        r'\s+at\s+\d+.*?(?:am|pm)?',
        r'\s+tonight\s*$',
        r'\s+this afternoon\s*$',
        r'\s+tomorrow\s*(?:morning|afternoon|night)?\s*$',
        r'\s+when will.*$',
        r'\s+how long until.*$',
        r'\s+at\s+\d+:\d+.*$',
        r'\s+\d+\s*(?:am|pm)\s*$',
    ]
    result = text
    for pattern in patterns_to_remove:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    return result.strip()


def is_temporal_query(location):
    """Check if location string contains temporal query patterns"""
    for pattern in TEMPORAL_PATTERNS:
        if pattern.search(location):
            return True
    return False


def parse_target_time(location):
    """Parse target time from temporal query"""
    location_lower = location.lower()
    now = datetime.now()
    
    # Check for specific time patterns
    time_match = re.search(r'(\d+):?(\d*)?\s*(am|pm)?', location_lower)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        ampm = time_match.group(3)
        
        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
        
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target < now:
            target += timedelta(days=1)
        return target
    
    # Check for relative patterns
    if 'tomorrow' in location_lower:
        if 'morning' in location_lower:
            return (now + timedelta(days=1)).replace(hour=8, minute=0)
        elif 'afternoon' in location_lower:
            return (now + timedelta(days=1)).replace(hour=14, minute=0)
        elif 'night' in location_lower:
            return (now + timedelta(days=1)).replace(hour=20, minute=0)
        else:
            return (now + timedelta(days=1)).replace(hour=12, minute=0)
    
    if 'tonight' in location_lower:
        return now.replace(hour=20, minute=0) if now.hour < 20 else (now + timedelta(days=1)).replace(hour=20, minute=0)
    
    if 'this afternoon' in location_lower:
        target = now.replace(hour=15, minute=0)
        return target if target > now else None
    
    return now


def is_us_location(lat, lon):
    """Check if coordinates are roughly within US bounds (includes AK and HI)"""
    conus = 24 <= lat <= 49 and -125 <= lon <= -66
    alaska = 51 <= lat <= 72 and -180 <= lon <= -130
    hawaii = 18 <= lat <= 23 and -161 <= lon <= -154
    return conus or alaska or hawaii


def get_nws_gridpoint(lat, lon):
    """Get NWS gridpoint for lat/lon"""
    try:
        url = f"https://api.weather.gov/points/{lat},{lon}"
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data['properties']
    except Exception as e:
        print(f"NWS gridpoint error: {e}", file=sys.stderr)
    return None


def get_nws_forecast(gridpoint):
    """Get detailed 12-hour forecast from NWS"""
    try:
        forecast_url = gridpoint.get('forecast')
        if not forecast_url:
            return None
            
        req = urllib.request.Request(forecast_url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data['properties']
    except Exception as e:
        print(f"NWS forecast error: {e}", file=sys.stderr)
    return None


def get_nws_hourly_forecast(gridpoint):
    """Get hourly forecast from NWS (~156 periods, 7 days)"""
    try:
        # Extract office and grid coordinates
        forecast_url = gridpoint.get('forecast', '')
        if not forecast_url:
            return None
        
        # Construct hourly URL from forecast URL
        # forecast_url like: https://api.weather.gov/gridpoints/TOP/32,81/forecast
        base_url = forecast_url.rsplit('/forecast', 1)[0]
        hourly_url = f"{base_url}/forecast/hourly"
            
        req = urllib.request.Request(hourly_url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data['properties']
    except Exception as e:
        print(f"NWS hourly forecast error: {e}", file=sys.stderr)
    return None


def get_nws_grid_data(gridpoint):
    """Get structured grid data for accumulations"""
    try:
        forecast_url = gridpoint.get('forecast', '')
        if not forecast_url:
            return None
        
        # Construct grid data URL
        base_url = forecast_url.rsplit('/forecast', 1)[0]
            
        req = urllib.request.Request(base_url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('properties', {})
    except Exception as e:
        print(f"NWS grid data error: {e}", file=sys.stderr)
    return None


def get_nws_alerts(gridpoint):
    """Get active alerts for the zone"""
    try:
        zone = gridpoint.get('forecastZone', '').split('/')[-1]
        if not zone:
            return []
            
        url = f"https://api.weather.gov/alerts/active?zone={zone}"
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('features', [])
    except Exception as e:
        print(f"NWS alerts error: {e}", file=sys.stderr)
    return []


def get_station_observation(gridpoint):
    """Get current observation from first observation station"""
    try:
        # observationStations is a URL to a list of stations
        stations_url = gridpoint.get('observationStations', '')
        if not stations_url:
            return None
        
        # Fetch the list of stations
        req = urllib.request.Request(stations_url, headers={'User-Agent': 'ClawdWeather/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            stations = data.get('features', [])
            if not stations:
                return None
        
        # Parse station ID from first station
        # Station identifier is in properties.stationIdentifier
        first_station = stations[0]
        station_id = first_station.get('properties', {}).get('stationIdentifier', '')
        if not station_id:
            # Fallback: parse from ID URL
            station_id = first_station.get('id', '').split('/')[-1]
        
        if not station_id:
            return None
        
        # Fetch latest observation
        url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('properties', {})
    except Exception as e:
        print(f"Station observation error: {e}", file=sys.stderr)
    return None


def get_airnow_current(lat, lon):
    """Get current AQI from AirNow API"""
    try:
        api_key = os.environ.get('AIRNOW_API_KEY', '')
        url = f"https://www.airnowapi.org/aq/observation/latLong/current/?latitude={lat}&longitude={lon}&format=application/json"
        if api_key:
            url += f"&API_KEY={api_key}"
            
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data if data else None
    except Exception as e:
        print(f"AirNow current error: {e}", file=sys.stderr)
    return None


def get_airnow_forecast(lat, lon):
    """Get forecast AQI from AirNow API"""
    try:
        api_key = os.environ.get('AIRNOW_API_KEY', '')
        url = f"https://www.airnowapi.org/aq/forecast/latLong/?latitude={lat}&longitude={lon}&format=application/json"
        if api_key:
            url += f"&API_KEY={api_key}"
            
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data if data else None
    except Exception as e:
        print(f"AirNow forecast error: {e}", file=sys.stderr)
    return None


def parse_aqi_category(aqi):
    """Get AQI category info based on value"""
    for (low, high), info in AQI_CATEGORIES.items():
        if low <= aqi <= high:
            return info
    return AQI_CATEGORIES[(301, 500)]  # Hazardous fallback


# ===== Phase 3: Astronomical, Aviation, Fire Weather =====

def get_astronomical_data(gridpoint):
    """Extract astronomical data from gridpoint (sunrise, sunset, twilight)"""
    try:
        astronomical = gridpoint.get('astronomicalData', {})
        if astronomical:
            return {
                'sunrise': astronomical.get('sunrise'),
                'sunset': astronomical.get('sunset'),
                'civilTwilightBegin': astronomical.get('civilTwilightBegin'),
                'civilTwilightEnd': astronomical.get('civilTwilightEnd')
            }
    except Exception as e:
        print(f"Astronomical data error: {e}", file=sys.stderr)
    return None


def calculate_moon_phase(date):
    """Calculate approximate moon phase (0-7, where 0=new, 4=full)"""
    try:
        # Known new moon: January 6, 2000
        known_new_moon = datetime(2000, 1, 6, 18, 14, 0)
        
        if isinstance(date, str):
            date = datetime.fromisoformat(date.replace('Z', '+00:00').replace('+00:00', ''))
        elif hasattr(date, 'year') and not isinstance(date, datetime):
            date = datetime.combine(date, datetime.min.time())
        
        # Lunar cycle is 29.53059 days
        lunar_cycle = 29.53059
        diff = (date - known_new_moon).total_seconds() / 86400
        
        # Calculate days into current cycle
        days_into_cycle = diff % lunar_cycle
        
        # Calculate phase (0-7)
        phase = int((days_into_cycle / lunar_cycle) * 8) % 8
        
        # Phase names
        phase_names = [
            "🌑 New Moon",
            "🌒 Waxing Crescent",
            "🌓 First Quarter",
            "🌔 Waxing Gibbous",
            "🌕 Full Moon",
            "🌖 Waning Gibbous",
            "🌗 Last Quarter",
            "🌘 Waning Crescent"
        ]
        
        # Phase illumination percentage (0=new=0%, 4=full=100%, symmetric)
        illumination = (1 - abs(phase - 4) / 4) * 100
        
        return {
            'phase': phase,
            'name': phase_names[phase],
            'illumination': round(illumination, 1)
        }
    except Exception as e:
        print(f"Moon phase calculation error: {e}", file=sys.stderr)
        return {'phase': 0, 'name': '🌑 Moon phase unknown', 'illumination': 0}


def format_time_until(iso_datetime):
    """Format time until/ago as human-readable string"""
    try:
        from datetime import datetime, timezone
        
        if not iso_datetime:
            return ""
        
        dt = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo if dt.tzinfo else timezone.utc)
        
        diff = dt - now
        hours = abs(diff.total_seconds()) / 3600
        
        if diff.total_seconds() > 0:  # In the future
            if hours < 1:
                mins = int(hours * 60)
                return f"(in {mins} min)"
            elif hours < 24:
                return f"(in {int(hours)}h)"
            else:
                days = int(hours / 24)
                rem_hours = int(hours % 24)
                return f"(in {days}d {rem_hours}h)"
        else:  # In the past
            if hours < 1:
                mins = int(hours * 60)
                return f"({mins} min ago)"
            elif hours < 24:
                return f"({int(hours)}h ago)"
            else:
                days = int(hours / 24)
                return f"({days}d ago)"
    except Exception:
        return ""


def calculate_daylight_hours(sunrise, sunset):
    """Calculate hours of daylight"""
    try:
        from datetime import datetime
        
        sr = datetime.fromisoformat(sunrise.replace('Z', '+00:00'))
        ss = datetime.fromisoformat(sunset.replace('Z', '+00:00'))
        
        diff = ss - sr
        hours = diff.total_seconds() / 3600
        hours_int = int(hours)
        mins = int((hours - hours_int) * 60)
        
        return f"{hours_int}h {mins}m"
    except Exception:
        return "?"


def format_astronomical_output(astro_data, location_name):
    """Format astronomical data into readable output"""
    if not astro_data:
        return ""
    
    output = []
    output.append(f"☀️ **Astronomical Times — {location_name}**")
    output.append("")
    
    # Parse and format times
    sunrise = astro_data.get('sunrise')
    sunset = astro_data.get('sunset')
    twilight_begin = astro_data.get('civilTwilightBegin')
    twilight_end = astro_data.get('civilTwilightEnd')
    
    today = datetime.now().strftime('%Y-%m-%d')
    moon_info = calculate_moon_phase(today)
    
    if sunrise:
        time_str = format_simple_time(sunrise)
        until = format_time_until(sunrise)
        output.append(f"🌅 **Sunrise:** {time_str} {until}")
    
    if sunset:
        time_str = format_simple_time(sunset)
        until = format_time_until(sunset)
        output.append(f"🌇 **Sunset:** {time_str} {until}")
    
    if twilight_begin and twilight_end:
        begin_str = format_simple_time(twilight_begin)
        end_str = format_simple_time(twilight_end)
        output.append(f"💡 **Civil Twilight:** {begin_str} – {end_str}")
    
    if sunrise and sunset:
        daylight = calculate_daylight_hours(sunrise, sunset)
        output.append(f"⏱️ **Daylight:** {daylight}")
    
    if moon_info:
        output.append(f"🌙 **Moon:** {moon_info['name']} ({moon_info['illumination']}%)")
    
    return "\n".join(output)


def format_simple_time(iso_datetime):
    """Format ISO datetime to simple time string (e.g., '6:32 AM')"""
    try:
        dt = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
        return dt.strftime('%I:%M %p').lstrip('0')
    except Exception:
        return iso_datetime


def get_aviation_taf(gridpoint):
    """Get Terminal Aerodrome Forecast (TAF) for the nearest station"""
    try:
        stations = gridpoint.get('observationStations', [])
        if not stations:
            return None
        
        # Get first station ID
        station_url = stations[0]
        station_id = station_url.split('/')[-1]
        
        url = f"https://api.weather.gov/stations/{station_id}/tafs"
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            features = data.get('features', [])
            if features:
                return features[0].get('properties', {})
    except Exception as e:
        print(f"TAF fetch error: {e}", file=sys.stderr)
    return None


def decode_taf_wind(wind_str):
    """Decode TAF wind string (e.g., '27012KT' or 'VRB05KT')"""
    if not wind_str:
        return "Calm"
    
    # Variable wind
    if wind_str.startswith('VRB'):
        match = re.search(r'VRB(\d+)KT', wind_str)
        if match:
            return f"Variable {match.group(1)} kt"
        return "Variable"
    
    # Gusting wind
    match = re.search(r'(\d{3})(\d{2,3})G(\d{2,3})KT', wind_str)
    if match:
        direction = int(match.group(1))
        speed = int(match.group(2))
        gust = int(match.group(3))
        cardinal = wind_direction_to_cardinal(direction)
        return f"{cardinal} {speed} kt, gusts {gust} kt"
    
    # Regular wind
    match = re.search(r'(\d{3})(\d{2,3})KT', wind_str)
    if match:
        direction = int(match.group(1))
        speed = int(match.group(2))
        cardinal = wind_direction_to_cardinal(direction)
        return f"{cardinal} {speed} kt"
    
    return wind_str


def format_taf_output(taf_data, location_name):
    """Format TAF data into readable output"""
    if not taf_data:
        return ""
    
    output = []
    output.append(f"✈️ **Aviation Forecast (TAF) — {location_name}**")
    output.append("")
    
    # Station info
    station_id = taf_data.get('stationId', 'Unknown')
    output.append(f"📍 **Station:** {station_id}")
    
    # Raw TAF text (if available, decoded)
    raw_taf = taf_data.get('rawTAF', '')
    if raw_taf:
        # Show first part of raw TAF (base conditions)
        lines = raw_taf.split(' FM')
        if lines:
            base = lines[0]
            # Decode base conditions
            output.append(f"📝 **Current Base Conditions:**")
            
            # Extract wind, visibility, ceiling from base
            parts = base.split()
            if len(parts) >= 2:
                # Station and time
                output.append(f"   *Issued: {parts[1][:2]}:{parts[1][2:4]}Z*")
            
            # Find wind
            for part in parts:
                if 'KT' in part:
                    wind = decode_taf_wind(part)
                    output.append(f"   💨 Wind: {wind}")
                if part.endswith('SM'):
                    vis = part.replace('SM', '')
                    output.append(f"   👀 Visibility: {vis} statute miles")
    
    output.append("")
    output.append("*Note: TAFs are designed for aviation use. Check with official sources for flight planning.*")
    
    return "\n".join(output)


def get_fire_weather(gridpoint):
    """Get fire weather information for the zone"""
    try:
        fire_zone_url = gridpoint.get('fireWeatherZone', '')
        if not fire_zone_url:
            return None
        
        zone_id = fire_zone_url.split('/')[-1]
        
        # Try to get fire weather forecast
        url = f"https://api.weather.gov/zones/fire/{zone_id}/forecast"
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('properties', {})
    except Exception as e:
        print(f"Fire weather error: {e}", file=sys.stderr)
    return None


def check_fire_alerts(gridpoint):
    """Check for fire-related alerts (Red Flag Warning, etc.)"""
    try:
        alerts = get_nws_alerts(gridpoint)
        fire_alerts = []
        
        for alert in alerts:
            event = alert.get('properties', {}).get('event', '').lower()
            if any(term in event for term in ['red flag', 'fire weather', 'fire warning']):
                fire_alerts.append(alert)
        
        return fire_alerts
    except Exception:
        return []


def format_fire_weather_output(fire_data, fire_alerts, location_name):
    """Format fire weather into readable output"""
    output = []
    output.append(f"🔥 **Fire Weather — {location_name}**")
    output.append("")
    
    # Fire alerts first
    if fire_alerts:
        output.append("🚨 **Active Fire Alerts:**")
        for alert in fire_alerts:
            event = alert.get('properties', {}).get('event', 'Fire Alert')
            severity = alert.get('properties', {}).get('severity', 'Unknown')
            headline = alert.get('properties', {}).get('headline', '')
            output.append(f"   {ALERT_SEVERITY_STYLES.get(severity, {}).get('emoji', '⚠️')} [{severity}] {event}")
            if headline:
                output.append(f"   {headline}")
        output.append("")
    
    # Fire weather forecast
    if fire_data:
        forecast = fire_data.get('text', '')
        if forecast:
            # Extract key fire weather elements
            dangerous_terms = ['critical', 'extreme', 'very high', 'high']
            is_dangerous = any(term in forecast.lower() for term in dangerous_terms)
            
            if is_dangerous:
                output.append("⚠️ **Fire Danger Level:** Elevated")
            else:
                output.append("✅ **Fire Danger Level:** Normal")
            
            # Show first sentence of forecast
            sentences = forecast.split('. ')
            if sentences:
                summary = sentences[0] + '.' if not sentences[0].endswith('.') else sentences[0]
                output.append(f"📝 **Forecast:** {summary}")
    else:
        output.append("ℹ️ Fire weather data not available for this location.")
    
    output.append("")
    output.append("*Source: National Weather Service Fire Weather Zone*")
    
    return "\n".join(output)


# ===== End Phase 3 =====


def convert_c_to_f(celsius):
    """Convert Celsius to Fahrenheit"""
    if celsius is None:
        return None
    return (celsius * 9/5) + 32


def convert_pa_to_inhg(pascals):
    """Convert Pascals to inches of mercury"""
    if pascals is None:
        return None
    return pascals / 3386.39


def wind_direction_to_cardinal(degrees):
    """Convert wind direction degrees to cardinal direction"""
    if degrees is None:
        return "N/A"
    
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]


def convert_kmh_to_mph(kmh):
    """Convert km/h to mph"""
    if kmh is None:
        return None
    return kmh * 0.621371


def convert_meters_to_miles(meters):
    """Convert meters to miles"""
    if meters is None:
        return None
    return meters / 1609.34


def parse_iso_datetime(dt_string):
    """Parse ISO datetime string, with or without dateutil"""
    if not dt_string:
        return None
    try:
        if DATEUTIL_AVAILABLE:
            return date_parser.parse(dt_string)
        else:
            # Fallback: handle ISO format manually
            # Try common ISO formats
            for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                try:
                    if fmt == '%Y-%m-%dT%H:%M:%S%z' and dt_string.endswith('Z'):
                        dt_string = dt_string[:-1] + '+00:00'
                    return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
                except:
                    continue
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
    except:
        return None


def format_period_emoji(desc):
    """Get emoji based on forecast description"""
    if not desc:
        return "🌤️"
    lower = desc.lower()
    if 'snow' in lower or 'blizzard' in lower:
        return "❄️"
    elif 'rain' in lower or 'shower' in lower:
        return "🌧️"
    elif 'sun' in lower or 'clear' in lower:
        return "☀️"
    elif 'cloud' in lower:
        return "☁️"
    elif 'wind' in lower or 'blowing' in lower:
        return "💨"
    elif 'storm' in lower or 'thunder' in lower:
        return "⛈️"
    elif 'fog' in lower or 'mist' in lower:
        return "🌫️"
    return "🌤️"


def calculate_alert_priority(alert_props):
    """Calculate alert priority score based on severity, urgency, certainty"""
    severity = alert_props.get('severity', 'Unknown')
    urgency = alert_props.get('urgency', 'Unknown')
    certainty = alert_props.get('certainty', 'Unknown')
    
    severity_weight = ALERT_SEVERITY_WEIGHTS.get(severity, 0)
    urgency_weight = ALERT_URGENCY_WEIGHTS.get(urgency, 0)
    certainty_weight = ALERT_CERTAINTY_WEIGHTS.get(certainty, 0)
    
    return severity_weight + urgency_weight + certainty_weight


def sort_alerts_by_priority(alerts):
    """Sort alerts by priority (highest first)"""
    def get_priority(alert):
        props = alert.get('properties', {})
        return calculate_alert_priority(props)
    
    return sorted(alerts, key=get_priority, reverse=True)


def format_alert_datetime(dt_string):
    """Format ISO datetime for display"""
    dt = parse_iso_datetime(dt_string)
    if not dt:
        return dt_string
    return dt.strftime('%I:%M %p').lstrip('0')


def format_alert(alert):
    """Format a single alert with enhanced details"""
    props = alert.get('properties', {})
    
    event = props.get('event', 'Unknown Alert')
    severity = props.get('severity', 'Unknown')
    urgency = props.get('urgency', 'Unknown')
    certainty = props.get('certainty', 'Unknown')
    headline = props.get('headline', '')
    description = props.get('description', '')
    instruction = props.get('instruction', '')
    onset = props.get('onset', '')
    expires = props.get('expires', '')
    response = props.get('response', 'Monitor')
    
    # Get severity styling
    style = ALERT_SEVERITY_STYLES.get(severity, ALERT_SEVERITY_STYLES['Unknown'])
    emoji = style['emoji']
    badge = style['badge']
    
    # Get urgency tag
    urgency_tag = ALERT_URGENCY_TAGS.get(urgency, ALERT_URGENCY_TAGS['Unknown'])
    
    # Get response action
    response_action = ALERT_RESPONSE_ACTIONS.get(response, ALERT_RESPONSE_ACTIONS['Monitor'])
    
    # Build formatted output
    lines = []
    lines.append(f"{emoji} [**{badge}**] **{event}**")
    lines.append(f"   {urgency_tag} | *{headline}*")
    
    # Time range
    if onset and expires:
        onset_str = format_alert_datetime(onset)
        onset_date = parse_iso_datetime(onset)
        expires_str = format_alert_datetime(expires)
        expires_date = parse_iso_datetime(expires)
        
        if onset_date and expires_date and onset_date.date() == expires_date.date():
            lines.append(f"   🕐 {onset_str} → {expires_str}")
        else:
            expires_full = expires_date.strftime('%a %I:%M %p').lstrip('0') if expires_date else expires_str
            lines.append(f"   🕐 Until {expires_full}")
    
    # Description (first sentence only for brevity)
    if description:
        first_sentence = description.split('.')[0][:100]
        if first_sentence:
            lines.append(f"   📝 {first_sentence}...")
    
    # Response action
    lines.append(f"   👉 {response_action}")
    
    return "\n".join(lines)


def format_observation(obs, forecast_temp=None):
    """Format current observation with optional forecast comparison"""
    if not obs:
        return None
    
    # Extract values
    temp_c = obs.get('temperature', {}).get('value')
    wind_speed_kmh = obs.get('windSpeed', {}).get('value')
    wind_dir = obs.get('windDirection', {}).get('value')
    pressure_pa = obs.get('barometricPressure', {}).get('value')
    humidity = obs.get('relativeHumidity', {}).get('value')
    dewpoint_c = obs.get('dewpoint', {}).get('value')
    visibility_m = obs.get('visibility', {}).get('value')
    text_desc = obs.get('textDescription', 'Unknown')
    
    # Convert units
    temp_f = convert_c_to_f(temp_c) if temp_c is not None else None
    wind_speed_mph = convert_kmh_to_mph(wind_speed_kmh) if wind_speed_kmh is not None else None
    pressure_inhg = convert_pa_to_inhg(pressure_pa) if pressure_pa is not None else None
    dewpoint_f = convert_c_to_f(dewpoint_c) if dewpoint_c is not None else None
    visibility_mi = convert_meters_to_miles(visibility_m) if visibility_m is not None else None
    
    # Build output
    lines = []
    lines.append(f"🌡️ **Observed Conditions**")
    
    # Temperature with forecast comparison
    if temp_f is not None:
        temp_str = f"{round(temp_f)}°F"
        if forecast_temp is not None:
            diff = round(temp_f - forecast_temp)
            if abs(diff) <= 2:
                temp_str += f" (matches forecast 🎯)"
            elif diff > 0:
                temp_str += f" ({diff}° warmer than {round(forecast_temp)}° forecast)"
            else:
                temp_str += f" ({abs(diff)}° cooler than {round(forecast_temp)}° forecast)"
        lines.append(f"   **Actually {temp_str}**")
    
    # Conditions
    lines.append(f"   {format_period_emoji(text_desc)} {text_desc}")
    
    # Additional details
    details = []
    
    if wind_speed_mph is not None and wind_dir is not None:
        cardinal = wind_direction_to_cardinal(wind_dir)
        details.append(f"💨 {cardinal} {round(wind_speed_mph)} mph")
    elif wind_speed_mph is not None:
        details.append(f"💨 {round(wind_speed_mph)} mph")
    
    if humidity is not None:
        details.append(f"💧 {round(humidity)}% humidity")
    
    if dewpoint_f is not None:
        details.append(f"🌫️ Dewpoint {round(dewpoint_f)}°F")
    
    if pressure_inhg is not None:
        details.append(f"📊 Pressure {pressure_inhg:.2f} inHg")
    
    if visibility_mi is not None:
        if visibility_mi >= 10:
            details.append(f"👀 Visibility 10+ mi")
        else:
            details.append(f"👀 Visibility {round(visibility_mi, 1)} mi")
    
    if details:
        lines.append(f"   {' • '.join(details)}")
    
    return "\n".join(lines)


def format_nws_output(forecast, alerts, location_name):
    """Format NWS 12-hour forecast into clean, actionable output"""
    output = []
    
    # Header with alerts
    if alerts:
        alert_titles = [a['properties']['event'] for a in alerts[:2]]
        output.append(f"🚨 **{location_name} — Alert Active**")
        output.append(f"⚠️  {', '.join(alert_titles)}")
    else:
        output.append(f"🌦️ **{location_name} Forecast**")
    
    output.append("")
    
    # Get periods (today, tonight, tomorrow)
    periods = forecast.get('periods', [])[:4]  # Get first 4 periods
    
    for period in periods:
        name = period.get('name', '')
        desc = period.get('detailedForecast', '')
        
        if not desc:
            continue
            
        icon = format_period_emoji(desc)
        
        output.append(f"**{icon} {name}**")
        output.append(desc)
        output.append("")
    
    # Bottom line if severe weather
    if alerts:
        output.append("**⚡ Bottom line:**")
        for alert in alerts[:1]:
            props = alert['properties']
            headline = props.get('headline', '')
            instr = props.get('instruction', '')
            if instr:
                # Take first sentence of instruction
                instr_short = instr.split('.')[0] + '.' if '.' in instr else instr[:100]
                output.append(f"{headline}")
                output.append(f"→ {instr_short}")
    
    return "\n".join(output)


def format_enhanced_alerts(alerts):
    """Format alerts with enhanced priority-based display"""
    if not alerts:
        return None
    
    output = []
    output.append("🚨 **Active Alerts**")
    output.append("")
    
    # Sort by priority
    sorted_alerts = sort_alerts_by_priority(alerts)
    
    for alert in sorted_alerts:
        formatted = format_alert(alert)
        output.append(formatted)
        output.append("")  # Empty line between alerts
    
    return "\n".join(output)


def format_hourly_output(periods, location_name, target_time=None):
    """Format hourly forecast into clean output"""
    output = []
    output.append(f"⏰ **{location_name} — Hourly Forecast**")
    output.append("")
    
    now = datetime.now()
    
    # If we have a target time, find relevant periods around that time
    if target_time:
        # Make target_time offset-naive for comparison
        target_naive = target_time.replace(tzinfo=None) if target_time.tzinfo else target_time
        
        # Find periods within +/- 6 hours of target
        relevant_periods = []
        for period in periods:
            period_time = parse_iso_datetime(period.get('startTime', ''))
            if period_time:
                period_naive = period_time.replace(tzinfo=None) if period_time.tzinfo else period_time
                if target_naive - timedelta(hours=3) <= period_naive <= target_naive + timedelta(hours=6):
                    relevant_periods.append((period_naive, period))
        
        if relevant_periods:
            output.append(f"*Showing hours around {target_time.strftime('%I:%M %p')}*")
            output.append("")
            
            for period_time, period in sorted(relevant_periods, key=lambda x: x[0])[:8]:  # Max 8 periods
                time_str = period_time.strftime('%I:%M %p').lstrip('0')
                temp = period.get('temperature', '')
                temp_unit = period.get('temperatureUnit', 'F')
                short_forecast = period.get('shortForecast', '')
                precip_prob = period.get('probabilityOfPrecipitation', {}).get('value', 0)
                
                icon = format_period_emoji(short_forecast)
                precip_str = f" 💧{precip_prob}%" if precip_prob else ""
                
                output.append(f"**{icon} {time_str}:** {temp}°{temp_unit} — {short_forecast}{precip_str}")
        else:
            output.append("*No hourly data available for the requested time.*")
    else:
        # Show next 12 hours
        output.append("*Next 12 hours:*")
        output.append("")
        
        for period in periods[:12]:
            period_time = parse_iso_datetime(period.get('startTime', ''))
            if not period_time:
                continue
            time_str = period_time.strftime('%I:%M %p').lstrip('0')
            temp = period.get('temperature', '')
            temp_unit = period.get('temperatureUnit', 'F')
            short_forecast = period.get('shortForecast', '')
            precip_prob = period.get('probabilityOfPrecipitation', {}).get('value', 0)
            
            icon = format_period_emoji(short_forecast)
            precip_str = f" 💧{precip_prob}%" if precip_prob else ""
            
            output.append(f"**{icon} {time_str}:** {temp}°{temp_unit} — {short_forecast}{precip_str}")
    
    return "\n".join(output)


def format_aqi_output(current_data, forecast_data, location_name):
    """Format AQI data into clean output"""
    output = []
    output.append(f"💨 **{location_name} — Air Quality**")
    output.append("")
    
    # Current AQI
    if current_data and len(current_data) > 0:
        # Get the first/current observation
        obs = current_data[0] if isinstance(current_data, list) else current_data
        aqi = obs.get('AQI', 0)
        category = obs.get('Category', {}).get('Name', 'Unknown')
        pollutant = obs.get('ParameterName', 'PM2.5')
        
        cat_info = parse_aqi_category(aqi)
        
        output.append(f"**Current:**")
        output.append(f"{cat_info['emoji']} **AQI {aqi}** — {category}")
        output.append(f"Primary pollutant: {pollutant}")
        output.append(f"💡 {cat_info['recommendation']}")
        output.append("")
    
    # Forecast AQI
    if forecast_data and len(forecast_data) > 0:
        seen_dates = set()
        forecast_lines = []
        for forecast in forecast_data[:3]:  # Next 3 forecasts
            date = forecast.get('DateForecast', '')
            if date in seen_dates:
                continue
            seen_dates.add(date)

            aqi = forecast.get('AQI', 0)
            if aqi < 0:
                continue  # -1 means no forecast available for this pollutant/date
            category = forecast.get('Category', {}).get('Name', 'Unknown')
            cat_info = parse_aqi_category(aqi)
            forecast_lines.append(f"{cat_info['emoji']} {date}: AQI {aqi} — {category}")

        if forecast_lines:
            output.append("**Forecast:**")
            output.extend(forecast_lines)
    
    return "\n".join(output)


def convert_to_inches(value, unit):
    """Convert various units to inches. Returns 0 if value <= 0."""
    if not value or value <= 0:
        return 0
    unit_lower = str(unit).lower()
    if 'mm' in unit_lower:
        return value * 0.03937  # mm to inches
    elif 'cm' in unit_lower:
        return value * 0.3937   # cm to inches
    elif 'm' in unit_lower and 'mm' not in unit_lower:
        return value * 39.37    # meters to inches
    return value  # Assume inches if no unit matched


def extract_accumulations_from_grid(grid_data):
    """Extract structured accumulation data from grid response"""
    accumulations = []
    
    if not grid_data:
        return accumulations
    
    # Extract time series and unit codes
    pop_data = grid_data.get('probabilityOfPrecipitation', {})
    snow_data = grid_data.get('snowfallAmount', {})
    ice_data = grid_data.get('iceAccumulation', {})
    
    pop_vals = pop_data.get('values', []) if isinstance(pop_data, dict) else []
    snow_vals = snow_data.get('values', []) if isinstance(snow_data, dict) else []
    ice_vals = ice_data.get('values', []) if isinstance(ice_data, dict) else []
    
    # Get unit codes (wmoUnit:mm, wmoUnit:m, etc.)
    snow_unit = snow_data.get('uom', '') if isinstance(snow_data, dict) else ''
    ice_unit = ice_data.get('uom', '') if isinstance(ice_data, dict) else ''
    
    def to_inches(value, unit):
        """Convert WMO units to inches"""
        if not value or value <= 0:
            return 0
        if 'mm' in unit:      # millimeters
            return value * 0.03937
        elif 'cm' in unit:    # centimeters  
            return value * 0.3937
        elif 'm' in unit:     # meters (not mm)
            return value * 39.37
        return value
    
    # Process snowfall
    for item in snow_vals[:8]:
        try:
            value = item.get('value', 0)
            if value and value > 0:
                valid_time = item.get('validTime', '')
                if 'T' in valid_time:
                    time_part = valid_time.split('/')[0] if '/' in valid_time else valid_time
                    dt = parse_iso_datetime(time_part)
                    if dt:
                        inches = to_inches(value, snow_unit)
                        if inches >= 0.1:  # Only show if measurable
                            time_str = dt.strftime('%a %I%p').lower().replace(':00', '')
                            accumulations.append({
                                'type': 'Snow',
                                'amount': round(inches, 1),
                                'unit': 'inches',
                                'time': time_str,
                                'icon': ''
                            })
        except:
            continue
    
    # Process ice
    for item in ice_vals[:8]:
        try:
            value = item.get('value', 0)
            if value and value > 0:
                valid_time = item.get('validTime', '')
                time_part = valid_time.split('/')[0] if '/' in valid_time else valid_time
                dt = parse_iso_datetime(time_part)
                if dt:
                    inches = to_inches(value, ice_unit)
                    if inches >= 0.01:  # Show even small ice
                        time_str = dt.strftime('%a %I%p').lower().replace(':00', '')
                        accumulations.append({
                            'type': 'Ice',
                            'amount': round(inches, 2),
                            'unit': 'inches',
                            'time': time_str,
                            'icon': ''
                        })
        except:
            continue
    
    # Process precipitation probability
    for item in pop_vals[:8]:
        try:
            value = item.get('value', 0)
            if value and value >= 30:
                valid_time = item.get('validTime', '')
                time_part = valid_time.split('/')[0] if '/' in valid_time else valid_time
                dt = parse_iso_datetime(time_part)
                if dt:
                    time_str = dt.strftime('%a %I%p').lower().replace(':00', '')
                    accumulations.append({
                        'type': 'Precipitation Chance',
                        'amount': value,
                        'unit': 'percent',
                        'time': time_str,
                        'icon': ''
                    })
        except:
            continue
    
    return accumulations


def format_accumulations_output(accumulations, location_name, forecast_periods=None):
    """Format structured accumulation data"""
    output = []
    output.append(f"🌨️ **{location_name} — Accumulations**")
    output.append("")
    
    if not accumulations:
        # Fallback: try to parse from text forecast
        if forecast_periods:
            parsed = parse_accumulations_from_text(forecast_periods)
            if parsed:
                output.append("*From forecast text:*")
                for item in parsed:
                    output.append(f"{item['icon']} {item['time']}: {item['type']} — {item['amount']}")
            else:
                output.append("No accumulation data available for this location/period.")
        else:
            output.append("No accumulation data available for this location/period.")
        return "\n".join(output)
    
    # Sort by time
    sorted_accums = sorted(accumulations, key=lambda x: x.get('time', ''))
    
    for item in sorted_accums:
        icon = item.get('icon', '📊')
        time = item.get('time', '')
        acc_type = item.get('type', '')
        amount = item.get('amount', '')
        unit = item.get('unit', '')
        
        if unit == 'inches':
            formatted = f"{amount:.1f}\"" if isinstance(amount, float) else f"{amount}\""
        elif unit == 'percent':
            formatted = f"{amount}%"
        else:
            formatted = f"{amount} {unit}"
        
        output.append(f"{icon} **{time}:** {acc_type} — {formatted}")
    
    return "\n".join(output)


def parse_accumulations_from_text(periods):
    """Fallback: Parse accumulation data from text forecast"""
    import re
    accumulations = []
    
    snow_pattern = r'(?:new )?snow (?:accumulation )?(?:of )?((?:\d+(?:\.\d+)?(?: to |-))?\d+(?:\.\d+)?) (?:inch|inches)'
    rain_pattern = r'precipitation amounts? (?:of |between )?((?:\d+(?:\.\d+)?(?: to |-))?\d+(?:\.\d+)?) (?:inch|inches)'
    
    for period in periods[:4]:
        desc = period.get('detailedForecast', '').lower()
        name = period.get('name', '')
        
        # Check for snow
        snow_matches = re.findall(snow_pattern, desc)
        if snow_matches:
            for match in snow_matches:
                accumulations.append({
                    'type': 'Snow',
                    'amount': match,
                    'time': name,
                    'icon': '❄️'
                })
        
        # Check for rain
        rain_matches = re.findall(rain_pattern, desc)
        if rain_matches:
            for match in rain_matches:
                accumulations.append({
                    'type': 'Rain',
                    'amount': match,
                    'time': name,
                    'icon': '🌧️'
                })
    
    return accumulations


def get_wttr_forecast(location):
    """Get forecast from wttr.in as fallback"""
    try:
        encoded = urllib.parse.quote(location)
        url = f"https://wttr.in/{encoded}?format=v2"
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode()
    except Exception as e:
        print(f"wttr.in error: {e}", file=sys.stderr)
    return None


def get_wttr_current(location):
    """Get current conditions from wttr.in"""
    try:
        encoded = urllib.parse.quote(location)
        url = f"https://wttr.in/{encoded}?format=%C|%t|%w|%h|%p"
        req = urllib.request.Request(url, headers={'User-Agent': 'ClawdWeather/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            parts = response.read().decode().strip().split('|')
            return {
                'condition': parts[0] if len(parts) > 0 else 'Unknown',
                'temp': parts[1] if len(parts) > 1 else '',
                'wind': parts[2] if len(parts) > 2 else '',
                'humidity': parts[3] if len(parts) > 3 else '',
                'precip': parts[4] if len(parts) > 4 else ''
            }
    except Exception as e:
        print(f"wttr.in current error: {e}", file=sys.stderr)
    return None


def format_wttr_output(forecast_text, current, location_name):
    """Format wttr.in output into consistent structure"""
    output = []
    output.append(f"🌦️ **{location_name} Forecast** (Global source)")
    output.append("")
    
    if current:
        output.append(f"**Now:** {current.get('condition', '')} {current.get('temp', '')}")
        output.append(f"Wind: {current.get('wind', '')} | Humidity: {current.get('humidity', '')}")
        output.append("")
    
    if forecast_text:
        # Include the ASCII art forecast but note it's from global source
        output.append("**3-Day Outlook:**")
        output.append("```")
        output.append(forecast_text)
        output.append("```")
    else:
        output.append("*Forecast data unavailable for this location.*")
    
    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("""Usage: get_weather.py 'Location Name' [options]

Options:
  --source nws|wttr|auto     Force specific source (default: auto)
  --aqi                      Include AirNow AQI data
  --hourly                   Force hourly forecast (auto-detected for time queries)
  --current                  Show current station observation vs forecast
  --astro                    Show sunrise/sunset and astronomical data
  --taf                       Show aviation forecast (TAF)
  --fire                      Show fire weather information

Examples:
  get_weather.py "Boston, MA"
  get_weather.py "Boston at 8 PM"       # Auto-detects hourly
  get_weather.py "Boston" --aqi         # Weather + AQI
  get_weather.py "Boston" --current     # Observed vs forecast
  get_weather.py "Boston" --astro       # Sunrise/sunset times
  get_weather.py "SFO" --taf          # Aviation forecast
  get_weather.py "California" --fire    # Fire weather
  get_weather.py "Seattle" --aqi --current --astro  # All features combined
""")
        sys.exit(1)
    
    location = sys.argv[1]
    source_pref = 'auto'
    show_aqi = False
    force_hourly = False
    show_current = False
    show_astro = False
    show_taf = False
    show_fire = False
    
    # Parse arguments
    if '--source' in sys.argv:
        idx = sys.argv.index('--source')
        if idx + 1 < len(sys.argv):
            source_pref = sys.argv[idx + 1]
    
    if '--aqi' in sys.argv:
        show_aqi = True
    
    if '--hourly' in sys.argv:
        force_hourly = True
    
    if '--current' in sys.argv:
        show_current = True
    
    if '--astro' in sys.argv:
        show_astro = True
    
    if '--taf' in sys.argv:
        show_taf = True
    
    if '--fire' in sys.argv:
        show_fire = True
    
    # Detect temporal query
    temporal_detected = is_temporal_query(location) or force_hourly
    target_time = parse_target_time(location) if temporal_detected else None
    
    # Step 1: Geocode (strip temporal qualifiers first for cleaner geocoding)
    clean_location = strip_temporal_qualifiers(location)
    lat, lon, display_name = geocode_location(clean_location)
    
    if lat is None or lon is None:
        print(f"❌ Could not locate: {location}")
        sys.exit(1)
    
    # Step 2: Determine source
    use_nws = False
    if source_pref == 'nws':
        use_nws = True
    elif source_pref == 'wttr':
        use_nws = False
    elif source_pref == 'auto':
        use_nws = is_us_location(lat, lon)
    
    outputs = []
    current_obs = None
    forecast_temp = None
    
    # Step 3: Fetch from appropriate source
    if use_nws:
        gridpoint = get_nws_gridpoint(lat, lon)
        
        if gridpoint:
            # Get current observation if requested
            if show_current:
                current_obs = get_station_observation(gridpoint)
            
            # Get appropriate forecast type
            if temporal_detected:
                hourly_forecast = get_nws_hourly_forecast(gridpoint)
                if hourly_forecast:
                    # Get forecast temperature for comparison with observation
                    if show_current and current_obs:
                        # Get current hour forecast
                        now = datetime.now()
                        for period in hourly_forecast.get('periods', []):
                            period_time = parse_iso_datetime(period.get('startTime', ''))
                            if period_time:
                                period_naive = period_time.replace(tzinfo=None) if period_time.tzinfo else period_time
                                if abs((period_naive - now).total_seconds()) / 3600 < 1:
                                    forecast_temp = period.get('temperature')
                                    break
                    
                    outputs.append(format_hourly_output(
                        hourly_forecast.get('periods', []),
                        display_name,
                        target_time
                    ))
                else:
                    # Fallback to regular forecast
                    forecast = get_nws_forecast(gridpoint)
                    if forecast:
                        alerts = get_nws_alerts(gridpoint)
                        # Get forecast temp from first period for comparison
                        if show_current and current_obs:
                            periods = forecast.get('periods', [])
                            if periods:
                                forecast_temp = periods[0].get('temperature')
                        
                        outputs.append(format_nws_output(forecast, alerts, display_name))
                        
                        # Add enhanced alerts if present
                        if alerts:
                            outputs.append(format_enhanced_alerts(alerts))
            else:
                # Regular 12-hour forecast
                forecast = get_nws_forecast(gridpoint)
                if forecast:
                    alerts = get_nws_alerts(gridpoint)
                    # Get forecast temp from first period for comparison
                    if show_current and current_obs:
                        periods = forecast.get('periods', [])
                        if periods:
                            forecast_temp = periods[0].get('temperature')
                    
                    outputs.append(format_nws_output(forecast, alerts, display_name))
                    
                    # Add enhanced alerts if present
                    if alerts:
                        outputs.append(format_enhanced_alerts(alerts))
                    
                    # Check if user asked about winter weather/storms - show accumulations
                    location_lower = location.lower()
                    if any(x in location_lower for x in ['snow', 'storm', 'accumulation', 'january', 'february', 'march']):
                        grid_data = get_nws_grid_data(gridpoint)
                        accums = extract_accumulations_from_grid(grid_data)
                        outputs.append(format_accumulations_output(accums, display_name, forecast.get('periods', [])))
            
            # Add current observation if requested
            if show_current:
                formatted_obs = format_observation(current_obs, forecast_temp)
                if formatted_obs:
                    # Insert observation after the forecast, before any other data
                    outputs.insert(1, formatted_obs)
                else:
                    outputs.append("\n🌡️ **Current Observation**")
                    outputs.append("   *Station data temporarily unavailable*")
            
            # Get AQI if requested (US only has AirNow)
            if show_aqi:
                aqi_current = get_airnow_current(lat, lon)
                aqi_forecast = get_airnow_forecast(lat, lon)
                outputs.append(format_aqi_output(aqi_current, aqi_forecast, display_name))
            
            # Phase 3: Astronomical data
            if show_astro:
                astro_data = get_astronomical_data(gridpoint)
                if astro_data:
                    outputs.append(format_astronomical_output(astro_data, display_name))
            
            # Phase 3: Aviation TAF
            if show_taf:
                taf_data = get_aviation_taf(gridpoint)
                if taf_data:
                    outputs.append(format_taf_output(taf_data, display_name))
                else:
                    outputs.append(f"\n✈️ **Aviation Forecast — {display_name}**")
                    outputs.append("")
                    outputs.append("*No TAF available for nearest station.*")
            
            # Phase 3: Fire weather
            if show_fire:
                fire_data = get_fire_weather(gridpoint)
                fire_alerts = check_fire_alerts(gridpoint)
                outputs.append(format_fire_weather_output(fire_data, fire_alerts, display_name))
            
            if outputs:
                print("\n\n".join(outputs))
                return
            else:
                print("⚠️  NWS forecast unavailable, falling back to global weather...")
        else:
            print("⚠️  NWS gridpoint not found, falling back to global weather...")
    
    # Step 4: Fallback to wttr.in
    if show_aqi and not use_nws:
        outputs.append(f"💨 **{display_name} — Air Quality**")
        outputs.append("")
        outputs.append("*AirNow AQI data is only available for US locations.*")
        outputs.append("")
    
    if show_current and not use_nws:
        # Note: wttr.in current conditions shown, but not a station comparison
        pass
    
    forecast_text = get_wttr_forecast(location)
    current = get_wttr_current(location)
    
    if forecast_text or current:
        outputs.append(format_wttr_output(forecast_text, current, display_name))
        print("\n\n".join(outputs))
    else:
        print(f"❌ Unable to fetch weather for: {location}")
        sys.exit(1)


if __name__ == '__main__':
    main()
