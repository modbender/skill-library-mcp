#!/usr/bin/env python3
"""
Weather module for daily briefing.
Fetches current weather and forecast using wttr.in (primary) and Open-Meteo (fallback).
"""

import sys
import json
import urllib.request
import urllib.parse
import subprocess
from datetime import datetime

# Default location (Leyton, London)
DEFAULT_LAT = 51.5667
DEFAULT_LON = -0.0167
DEFAULT_CITY = "Leyton,London"


def fetch_wttr(city=DEFAULT_CITY):
    """Fetch weather from wttr.in (primary source)."""
    try:
        encoded_city = urllib.parse.quote(city)
        
        # Current conditions
        current_url = f"https://wttr.in/{encoded_city}?format=j1"
        
        req = urllib.request.Request(
            current_url,
            headers={
                'User-Agent': 'curl/7.64.1',  # wttr.in works best with curl UA
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        return None


def fetch_openmeteo(lat=DEFAULT_LAT, lon=DEFAULT_LON):
    """Fetch weather from Open-Meteo (fallback)."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&"
            f"timezone=Europe/London"
        )
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return None


def format_weather_wttr(data):
    """Format wttr.in data into readable output."""
    if not data or 'current_condition' not in data:
        return None
    
    current = data['current_condition'][0]
    
    # Extract data
    temp_c = current.get('temp_C', '?')
    temp_f = current.get('temp_F', '?')
    condition = current.get('weatherDesc', [{}])[0].get('value', 'Unknown')
    humidity = current.get('humidity', '?')
    wind_kmph = current.get('windspeedKmph', '?')
    wind_dir = current.get('winddir16Point', '')
    
    # Get today's forecast for high/low
    forecast = data.get('weather', [{}])[0]
    max_temp = forecast.get('maxtempC', '?')
    min_temp = forecast.get('mintempC', '?')
    rain_chance = forecast.get('hourly', [{}])[0].get('chanceofrain', '?')
    
    # Weather emoji mapping
    emoji_map = {
        'sunny': '☀️',
        'clear': '🌙',
        'partly cloudy': '⛅',
        'cloudy': '☁️',
        'overcast': '☁️',
        'rain': '🌧️',
        'light rain': '🌦️',
        'heavy rain': '⛈️',
        'snow': '❄️',
        'sleet': '🌨️',
        'thunder': '⛈️',
        'fog': '🌫️',
        'mist': '🌫️',
    }
    
    condition_lower = condition.lower()
    emoji = '🌤️'  # default
    for key, em in emoji_map.items():
        if key in condition_lower:
            emoji = em
            break
    
    output = []
    output.append(f"{emoji} {condition}, {temp_c}°C / {temp_f}°F")
    output.append(f"   High: {max_temp}°C · Low: {min_temp}°C")
    output.append(f"   💧 {rain_chance}% rain · 💨 {wind_kmph}km/h {wind_dir}")
    
    return '\n'.join(output)


def format_weather_openmeteo(data):
    """Format Open-Meteo data into readable output."""
    if not data or 'current_weather' not in data:
        return None
    
    current = data['current_weather']
    daily = data.get('daily', {})
    
    temp = current.get('temperature', '?')
    wind = current.get('windspeed', '?')
    
    max_temp = daily.get('temperature_2m_max', ['?'])[0]
    min_temp = daily.get('temperature_2m_min', ['?'])[0]
    rain_chance = daily.get('precipitation_probability_max', ['?'])[0]
    
    output = []
    output.append(f"🌤️ Current: {temp}°C")
    output.append(f"   High: {max_temp}°C · Low: {min_temp}°C")
    output.append(f"   💧 {rain_chance}% rain chance · 💨 {wind}km/h wind")
    
    return '\n'.join(output)


def get_weather(city=DEFAULT_CITY, lat=DEFAULT_LAT, lon=DEFAULT_LON):
    """Get weather, trying wttr.in first, then Open-Meteo."""
    # Try wttr.in first
    data = fetch_wttr(city)
    if data:
        formatted = format_weather_wttr(data)
        if formatted:
            return formatted
    
    # Fallback to Open-Meteo
    data = fetch_openmeteo(lat, lon)
    if data:
        formatted = format_weather_openmeteo(data)
        if formatted:
            return formatted
    
    return "⚠️ Weather data unavailable"


if __name__ == "__main__":
    # Allow city override from command line
    city = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CITY
    lat = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LAT
    lon = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_LON
    
    print(get_weather(city, lat, lon))
