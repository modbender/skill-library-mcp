#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Simmer Weather Trading Skill

Improvements over original:
- Dynamic forecast confidence based on lead time
- Better geocoding with Nominatim API fallback
- Enhanced temperature bucket parsing
- Improved NOAA error handling with retries
- Integration with core modules for logging
- Market quality scoring
- Advanced position management

Usage:
    python weather_trader_enhanced.py              # Dry run
    python weather_trader_enhanced.py --live       # Execute real trades
    python weather_trader_enhanced.py --positions  # Show current positions
    python weather_trader_enhanced.py --smart-sizing  # Use portfolio-based sizing
"""

import os
import sys
import re
import json
import argparse
import time
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Force line-buffered stdout
sys.stdout.reconfigure(line_buffering=True)

# Load .env file early
try:
    from pathlib import Path
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass  # python-dotenv not installed
except:
    pass

# Optional: Trade Journal integration
try:
    from tradejournal import log_trade
    JOURNAL_AVAILABLE = True
except ImportError:
    JOURNAL_AVAILABLE = False
    def log_trade(*args, **kwargs):
        pass

# =============================================================================
# Configuration System
# =============================================================================

def _load_config(schema, skill_file, config_filename="config.json"):
    """Load config with priority: config.json > env vars > defaults."""
    from pathlib import Path
    config_path = Path(skill_file).parent / config_filename
    file_cfg = {}
    if config_path.exists():
        try:
            with open(config_path) as f:
                file_cfg = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    result = {}
    for key, spec in schema.items():
        if key in file_cfg:
            result[key] = file_cfg[key]
        elif spec.get("env") and os.environ.get(spec["env"]):
            val = os.environ.get(spec["env"])
            type_fn = spec.get("type", str)
            try:
                result[key] = type_fn(val) if type_fn != str else val
            except (ValueError, TypeError):
                result[key] = spec.get("default")
        else:
            result[key] = spec.get("default")
    return result

def _get_config_path(skill_file, config_filename="config.json"):
    from pathlib import Path
    return Path(skill_file).parent / config_filename

def _update_config(updates, skill_file, config_filename="config.json"):
    from pathlib import Path
    config_path = Path(skill_file).parent / config_filename
    existing = {}
    if config_path.exists():
        try:
            with open(config_path) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    existing.update(updates)
    with open(config_path, "w") as f:
        json.dump(existing, f, indent=2)
    return existing

load_config = _load_config
get_config_path = _get_config_path
update_config = _update_config

CONFIG_SCHEMA = {
    "entry_threshold": {"env": "SIMMER_WEATHER_ENTRY", "default": 0.15, "type": float},
    "exit_threshold": {"env": "SIMMER_WEATHER_EXIT", "default": 0.45, "type": float},
    "max_position_usd": {"env": "SIMMER_WEATHER_MAX_POSITION", "default": 2.00, "type": float},
    "sizing_pct": {"env": "SIMMER_WEATHER_SIZING_PCT", "default": 0.05, "type": float},
    "max_trades_per_run": {"env": "SIMMER_WEATHER_MAX_TRADES", "default": 5, "type": int},
    "locations": {"env": "SIMMER_WEATHER_LOCATIONS", "default": "ALL", "type": str},
    "min_market_quality_score": {"env": "SIMMER_WEATHER_MIN_QUALITY", "default": 0.6, "type": float},
}

_config = load_config(CONFIG_SCHEMA, __file__)

SIMMER_API_BASE = "https://api.simmer.markets"
NOAA_API_BASE = "https://api.weather.gov"
NOMINATIM_BASE = "https://nominatim.openstreetmap.org"

TRADE_SOURCE = "sdk:weather-enhanced"

# Polymarket constraints
MIN_SHARES_PER_ORDER = 5.0
MIN_TICK_SIZE = 0.01

# Strategy parameters
ENTRY_THRESHOLD = _config["entry_threshold"]
EXIT_THRESHOLD = _config["exit_threshold"]
MAX_POSITION_USD = _config["max_position_usd"]
SMART_SIZING_PCT = _config["sizing_pct"]
MAX_TRADES_PER_RUN = _config["max_trades_per_run"]
MIN_MARKET_QUALITY_SCORE = _config["min_market_quality_score"]

# Safeguards
SLIPPAGE_MAX_PCT = 0.15
TIME_TO_RESOLUTION_MIN_HOURS = 2
PRICE_DROP_THRESHOLD = 0.10

# 🆕 NOAA Forecast Accuracy Model (based on lead time)
NOAA_ACCURACY_MODEL = {
    0: 0.90,   # Same day: 90%
    1: 0.88,   # 1 day out: 88%
    2: 0.85,   # 2 days out: 85%
    3: 0.80,   # 3 days out: 80%
    4: 0.75,   # 4 days out: 75%
    5: 0.70,   # 5 days out: 70%
    6: 0.65,   # 6 days out: 65%
    7: 0.60,   # 7+ days out: 60%
}

# Default supported locations
DEFAULT_LOCATIONS = {
    "NYC": {"lat": 40.7769, "lon": -73.8740, "name": "New York City (LaGuardia)"},
    "Chicago": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago (O'Hare)"},
    "Seattle": {"lat": 47.4502, "lon": -122.3088, "name": "Seattle (Sea-Tac)"},
    "Atlanta": {"lat": 33.6407, "lon": -84.4277, "name": "Atlanta (Hartsfield)"},
    "Dallas": {"lat": 32.8998, "lon": -97.0403, "name": "Dallas (DFW)"},
    "Miami": {"lat": 25.7959, "lon": -80.2870, "name": "Miami (MIA)"},
}

# 🆕 Runtime location cache (for geocoding)
LOCATION_CACHE = DEFAULT_LOCATIONS.copy()

_locations_str = _config["locations"]
# Support "ALL" for all cities, or empty string for all cities
if _locations_str.upper() == "ALL" or not _locations_str.strip():
    ACTIVE_LOCATIONS = []  # Empty = trade all cities
else:
    ACTIVE_LOCATIONS = [loc.strip().upper() for loc in _locations_str.split(",") if loc.strip()]

# =============================================================================
# 🆕 Enhanced Geocoding with Nominatim Fallback
# =============================================================================

def fetch_json(url, headers=None, retries=3):
    """Fetch JSON with retry logic."""
    for attempt in range(retries):
        try:
            req = Request(url, headers=headers or {})
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            if e.code == 429:  # Rate limit
                wait_time = 2 ** attempt
                print(f"  ⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            print(f"  HTTP Error {e.code}: {url}")
            return None
        except (URLError, Exception) as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            print(f"  Error fetching {url}: {e}")
            return None
    return None


def geocode_location(location_name: str) -> tuple:
    """
    Geocode location using Nominatim API.
    Returns (lat, lon) or None.
    """
    # Check cache first
    if location_name in LOCATION_CACHE:
        loc = LOCATION_CACHE[location_name]
        return (loc["lat"], loc["lon"])

    print(f"  🌍 Geocoding {location_name} via Nominatim...")

    # Add "airport" to query for better weather station matching
    query = f"{location_name} airport USA"
    url = f"{NOMINATIM_BASE}/search?{urlencode({'q': query, 'format': 'json', 'limit': 1})}"

    headers = {
        "User-Agent": "SimmerWeatherSkill/2.0 (https://simmer.markets)"
    }

    data = fetch_json(url, headers, retries=2)

    if not data or len(data) == 0:
        print(f"   Geocoding failed for {location_name}")
        return None

    result = data[0]
    lat = float(result["lat"])
    lon = float(result["lon"])

    # Cache for future use
    LOCATION_CACHE[location_name] = {
        "lat": lat,
        "lon": lon,
        "name": result.get("display_name", location_name)
    }

    print(f"  ✓ Found: {lat:.4f}, {lon:.4f}")
    return (lat, lon)


# =============================================================================
# 🆕 Enhanced NOAA API with Better Error Handling
# =============================================================================

def get_noaa_forecast(location: str) -> dict:
    """
    Get NOAA forecast with enhanced error handling.
    Returns dict: {date -> {"high": temp, "low": temp}}
    """
    coords = None

    # Try cache first
    if location in LOCATION_CACHE:
        loc = LOCATION_CACHE[location]
        coords = (loc["lat"], loc["lon"])
    else:
        # Try geocoding
        coords = geocode_location(location)

    if not coords:
        print(f"    Could not get coordinates for {location}")
        return {}

    lat, lon = coords

    headers = {
        "User-Agent": "SimmerWeatherSkill/2.0 (https://simmer.markets)",
        "Accept": "application/geo+json",
    }

    # Step 1: Get grid point
    points_url = f"{NOAA_API_BASE}/points/{lat:.4f},{lon:.4f}"
    points_data = fetch_json(points_url, headers)

    if not points_data or "properties" not in points_data:
        print(f"   Failed to get NOAA grid for {location}")
        return {}

    forecast_url = points_data["properties"].get("forecast")
    if not forecast_url:
        print(f"    No forecast URL for {location}")
        return {}

    # Step 2: Get forecast
    forecast_data = fetch_json(forecast_url, headers)
    if not forecast_data or "properties" not in forecast_data:
        print(f"    Failed to get NOAA forecast for {location}")
        return {}

    periods = forecast_data["properties"].get("periods", [])
    forecasts = {}

    for period in periods:
        start_time = period.get("startTime", "")
        if not start_time:
            continue

        date_str = start_time[:10]
        temp = period.get("temperature")
        is_daytime = period.get("isDaytime", True)

        if date_str not in forecasts:
            forecasts[date_str] = {"high": None, "low": None}

        if is_daytime:
            forecasts[date_str]["high"] = temp
        else:
            forecasts[date_str]["low"] = temp

    return forecasts


# =============================================================================
# 🆕 Enhanced Temperature Bucket Parsing
# =============================================================================

def parse_temperature_bucket(outcome_name: str) -> tuple:
    """
    Enhanced temperature bucket parsing with more patterns.
    Returns (min_temp, max_temp) or None.
    """
    if not outcome_name:
        return None

    outcome_lower = outcome_name.lower()

    # Pattern 1: "Below X" or "X or below"
    below_patterns = [
        r'(\d+)\s*°?[fF]?\s*(or below|or less|or under|or lower)',
        r'(below|under|less than)\s*(\d+)\s*°?[fF]?',
    ]
    for pattern in below_patterns:
        match = re.search(pattern, outcome_name, re.IGNORECASE)
        if match:
            temp = int(match.group(1) if match.group(1).isdigit() else match.group(2))
            return (-999, temp)

    # Pattern 2: "Above X" or "X or above"
    above_patterns = [
        r'(\d+)\s*°?[fF]?\s*(or higher|or above|or more|or over|\+)',
        r'(above|over|more than|higher than)\s*(\d+)\s*°?[fF]?',
    ]
    for pattern in above_patterns:
        match = re.search(pattern, outcome_name, re.IGNORECASE)
        if match:
            temp = int(match.group(1) if match.group(1).isdigit() else match.group(2))
            return (temp, 999)

    # Pattern 3: Range "X-Y" or "X to Y"
    range_patterns = [
        r'(\d+)\s*[-–to]+\s*(\d+)',
        r'between\s*(\d+)\s*and\s*(\d+)',
    ]
    for pattern in range_patterns:
        match = re.search(pattern, outcome_name, re.IGNORECASE)
        if match:
            low, high = int(match.group(1)), int(match.group(2))
            return (min(low, high), max(low, high))

    return None


# =============================================================================
# 🆕 Dynamic Forecast Confidence Model
# =============================================================================

def calculate_forecast_confidence(target_date_str: str, forecast_temp: float,
        bucket: tuple, metric: str) -> float:
    """
    Calculate forecast confidence based on:
    - Lead time (days until event)
    - Temperature bucket width
    - Forecast position within bucket
    - Metric type (high temps easier to predict than lows)

    Returns confidence score 0-1.
    """
    try:
        target_date = datetime.fromisoformat(target_date_str)
    except ValueError:
        return 0.70  # Default if date parsing fails

    # Calculate days until event
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    target_date = target_date.replace(tzinfo=None)
    days_out = (target_date - now).days
    days_out = max(0, days_out)

    # Base accuracy from NOAA model
    base_accuracy = NOAA_ACCURACY_MODEL.get(min(days_out, 7), 0.60)

    # Adjust for bucket width (wider buckets = higher confidence)
    min_temp, max_temp = bucket
    if max_temp == 999:  # Open-ended "above X"
        bucket_width = 20  # Assume 20°F effective width
    elif min_temp == -999:  # Open-ended "below X"
        bucket_width = 20
    else:
        bucket_width = max_temp - min_temp

    # Wider buckets get bonus (5°F bucket is harder than 10°F)
    width_bonus = min(0.10, (bucket_width - 5) * 0.01)

    # Adjust for position within bucket
    if max_temp != 999 and min_temp != -999:
        bucket_center = (min_temp + max_temp) / 2
        distance_from_center = abs(forecast_temp - bucket_center)
        position_penalty = (distance_from_center / (bucket_width / 2)) * 0.05
    else:
        position_penalty = 0

    # High temps slightly more predictable than lows in winter
    metric_bonus = 0.02 if metric == "high" else 0

    confidence = base_accuracy + width_bonus + metric_bonus - position_penalty

    return max(0.50, min(0.95, confidence))


# =============================================================================
# 🆕 Market Quality Scoring
# =============================================================================

def calculate_market_quality_score(market: dict, context: dict = None) -> float:
    """
    Score market quality on 0-1 scale based on:
    - Liquidity
    - Volume
    - Time to resolution
    - Spread (if available)

    Returns quality score 0-1.
    """
    score = 0.0

    # Factor 1: Liquidity (40% weight)
    liquidity = market.get("liquidity", 0)
    if liquidity > 10000:
        score += 0.40
    elif liquidity > 5000:
        score += 0.30
    elif liquidity > 1000:
        score += 0.20
    elif liquidity > 500:
        score += 0.10

    # Factor 2: Volume (30% weight)
    volume = market.get("volume", 0)
    if volume > 50000:
        score += 0.30
    elif volume > 20000:
        score += 0.20
    elif volume > 5000:
        score += 0.10

    # Factor 3: Time to resolution (20% weight)
    # Markets resolving in 2-5 days are ideal
    if context and "market" in context:
        time_str = context["market"].get("time_to_resolution", "")
        try:
            hours = 0
            if "d" in time_str:
                days = int(time_str.split("d")[0].strip())
                hours = days * 24
            if 48 <= hours <= 120:  # 2-5 days
                score += 0.20
            elif 24 <= hours < 48 or 120 < hours <= 168:  # 1-2 or 5-7 days
                score += 0.10
        except (ValueError, IndexError):
            pass
    else:
        score += 0.10  # Default partial credit if no context

    # Factor 4: Price (avoid extremes) (10% weight)
    price = market.get("external_price_yes", 0.5)
    if MIN_TICK_SIZE < price < 0.90:
        score += 0.10

    return score


# =============================================================================
# Market Parsing (Enhanced)
# =============================================================================

def parse_weather_event(event_name: str) -> dict:
    """Parse weather event with enhanced location matching."""
    if not event_name:
        return None

    event_lower = event_name.lower()

    # Determine metric
    if 'highest' in event_lower or 'high temp' in event_lower:
        metric = 'high'
    elif 'lowest' in event_lower or 'low temp' in event_lower:
        metric = 'low'
    else:
        metric = 'high'

    # Enhanced location matching
    location = None
    location_aliases = {
        'nyc': 'NYC', 'new york': 'NYC', 'laguardia': 'NYC', 'la guardia': 'NYC',
        'chicago': 'Chicago', "o'hare": 'Chicago', 'ohare': 'Chicago',
        'seattle': 'Seattle', 'sea-tac': 'Seattle', 'seatac': 'Seattle',
        'atlanta': 'Atlanta', 'hartsfield': 'Atlanta',
        'dallas': 'Dallas', 'dfw': 'Dallas',
        'miami': 'Miami', 'mia': 'Miami',
        'los angeles': 'Los Angeles', 'la': 'Los Angeles', 'lax': 'Los Angeles',
        'san francisco': 'San Francisco', 'sf': 'San Francisco', 'sfo': 'San Francisco',
        'boston': 'Boston', 'bos': 'Boston', 'logan': 'Boston',
        'denver': 'Denver', 'dia': 'Denver',
        'phoenix': 'Phoenix', 'phx': 'Phoenix',
    }

    for alias, loc in location_aliases.items():
        if alias in event_lower:
            location = loc
            break

    if not location:
        return None

    # Enhanced date parsing
    month_day_match = re.search(r'on\s+([a-zA-Z]+)\s+(\d{1,2})', event_name, re.IGNORECASE)
    if not month_day_match:
        # Try alternative format "January 15"
        month_day_match = re.search(r'([a-zA-Z]+)\s+(\d{1,2})\b', event_name, re.IGNORECASE)

    if not month_day_match:
        return None

    month_name = month_day_match.group(1).lower()
    day = int(month_day_match.group(2))

    month_map = {
        'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
        'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
        'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
        'november': 11, 'nov': 11, 'december': 12, 'dec': 12,
    }

    month = month_map.get(month_name)
    if not month:
        return None

    now = datetime.now(timezone.utc)
    year = now.year
    try:
        target_date = datetime(year, month, day, tzinfo=timezone.utc)
        if target_date < now - timedelta(days=30):
            year += 1
        date_str = f"{year}-{month:02d}-{day:02d}"
    except ValueError:
        return None

    return {"location": location, "date": date_str, "metric": metric}


# =============================================================================
# Simmer API Functions (Keep original implementation)
# =============================================================================

def get_api_key():
    key = os.environ.get("SIMMER_API_KEY")
    if not key:
        print("Error: SIMMER_API_KEY environment variable not set")
        sys.exit(1)
    return key

def sdk_request(api_key: str, method: str, endpoint: str, data: dict = None) -> dict:
    url = f"{SIMMER_API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        if method == "GET":
            req = Request(url, headers=headers)
        else:
            body = json.dumps(data).encode() if data else None
            req = Request(url, data=body, headers=headers, method=method)
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"error": str(e)}

def get_portfolio(api_key: str) -> dict:
    result = sdk_request(api_key, "GET", "/api/sdk/portfolio")
    if "error" in result:
        print(f"  ⚠️  Portfolio fetch failed: {result['error']}")
        return None
    return result

def get_market_context(api_key: str, market_id: str, my_probability: float = None) -> dict:
    endpoint = f"/api/sdk/context/{market_id}"
    if my_probability is not None:
        endpoint += f"?my_probability={my_probability}"
    result = sdk_request(api_key, "GET", endpoint)
    if "error" in result:
        return None
    return result

def get_price_history(api_key: str, market_id: str) -> list:
    result = sdk_request(api_key, "GET", f"/api/sdk/markets/{market_id}/history")
    if "error" in result:
        return []
    return result.get("points", [])

def fetch_weather_markets():
    url = f"{SIMMER_API_BASE}/api/markets?tags=weather&status=active&limit=100"
    data = fetch_json(url)
    if not data or "markets" not in data:
        print("  Failed to fetch markets from Simmer API")
        return []
    return data["markets"]

def execute_trade(api_key: str, market_id: str, side: str, amount: float) -> dict:
    return sdk_request(api_key, "POST", "/api/sdk/trade", {
        "market_id": market_id,
        "side": side,
        "amount": amount,
        "venue": "polymarket",
        "source": TRADE_SOURCE,
    })

def execute_sell(api_key: str, market_id: str, shares: float) -> dict:
    return sdk_request(api_key, "POST", "/api/sdk/trade", {
        "market_id": market_id,
        "side": "yes",
        "action": "sell",
        "shares": shares,
        "venue": "polymarket",
        "source": TRADE_SOURCE,
    })

def get_positions(api_key: str) -> list:
    result = sdk_request(api_key, "GET", "/api/sdk/positions")
    if "error" in result:
        print(f"  Error fetching positions: {result['error']}")
        return []
    return result.get("positions", [])

def check_context_safeguards(context: dict, use_edge: bool = True) -> tuple:
    if not context:
        return True, []
    reasons = []
    market = context.get("market", {})
    warnings = context.get("warnings", [])
    discipline = context.get("discipline", {})
    slippage = context.get("slippage", {})
    edge = context.get("edge", {})

    for warning in warnings:
        if "MARKET RESOLVED" in str(warning).upper():
            return False, ["Market already resolved"]

    warning_level = discipline.get("warning_level", "none")
    if warning_level == "severe":
        return False, [f"Severe flip-flop warning"]
    elif warning_level == "mild":
        reasons.append("Mild flip-flop warning")

    time_str = market.get("time_to_resolution", "")
    if time_str:
        try:
            hours = 0
            if "d" in time_str:
                days = int(time_str.split("d")[0].strip())
                hours += days * 24
            if "h" in time_str:
                h_part = time_str.split("h")[0]
                if "d" in h_part:
                    h_part = h_part.split("d")[-1].strip()
                hours += int(h_part)
            if hours < TIME_TO_RESOLUTION_MIN_HOURS:
                return False, [f"Resolves in {hours}h - too soon"]
        except (ValueError, IndexError):
            pass

    estimates = slippage.get("estimates", []) if slippage else []
    if estimates:
        slippage_pct = estimates[0].get("slippage_pct", 0)
        if slippage_pct > SLIPPAGE_MAX_PCT:
            return False, [f"Slippage too high: {slippage_pct:.1%}"]

    if use_edge and edge:
        recommendation = edge.get("recommendation")
        user_edge = edge.get("user_edge")
        threshold = edge.get("suggested_threshold", 0)
        if recommendation == "SKIP":
            return False, ["Edge analysis: SKIP"]
        elif recommendation == "HOLD":
            if user_edge is not None and threshold:
                reasons.append(f"Edge {user_edge:.1%} < threshold {threshold:.1%}")
            else:
                reasons.append("Edge analysis: HOLD")
        elif recommendation == "TRADE":
            reasons.append(f"Edge {user_edge:.1%} ≥ threshold {threshold:.1%}")

    return True, reasons

def detect_price_trend(history: list) -> dict:
    if not history or len(history) < 2:
        return {"direction": "unknown", "change_24h": 0, "is_opportunity": False}
    recent_price = history[-1].get("price_yes", 0.5)
    lookback = min(96, len(history) - 1)
    old_price = history[-lookback].get("price_yes", recent_price)
    if old_price == 0:
        return {"direction": "unknown", "change_24h": 0, "is_opportunity": False}
    change = (recent_price - old_price) / old_price
    if change < -PRICE_DROP_THRESHOLD:
        return {"direction": "down", "change_24h": change, "is_opportunity": True}
    elif change > PRICE_DROP_THRESHOLD:
        return {"direction": "up", "change_24h": change, "is_opportunity": False}
    else:
        return {"direction": "flat", "change_24h": change, "is_opportunity": False}

def calculate_position_size(api_key: str, default_size: float, smart_sizing: bool) -> float:
    if not smart_sizing:
        return default_size
    portfolio = get_portfolio(api_key)
    if not portfolio:
        print(f"   Smart sizing failed, using default ${default_size:.2f}")
        return default_size
    balance = portfolio.get("balance_usdc", 0)
    if balance <= 0:
        print(f"    No available balance, using default ${default_size:.2f}")
        return default_size
    smart_size = balance * SMART_SIZING_PCT
    smart_size = min(smart_size, MAX_POSITION_USD)
    smart_size = max(smart_size, 1.0)
    print(f"  Smart sizing: ${smart_size:.2f} ({SMART_SIZING_PCT:.0%} of ${balance:.2f})")
    return smart_size

def check_exit_opportunities(api_key: str, dry_run: bool = False, use_safeguards: bool = True) -> tuple:
    positions = get_positions(api_key)
    if not positions:
        return 0, 0
    weather_positions = []
    for pos in positions:
        question = pos.get("question", "").lower()
        sources = pos.get("sources", [])
        if TRADE_SOURCE in sources or "sdk:weather" in sources or any(kw in question for kw in ["temperature", "°f", "highest temp", "lowest temp"]):
            weather_positions.append(pos)
    if not weather_positions:
        return 0, 0
    print(f"\n Checking {len(weather_positions)} weather positions for exit...")
    exits_found = 0
    exits_executed = 0
    for pos in weather_positions:
        market_id = pos.get("market_id")
        current_price = pos.get("current_price") or pos.get("price_yes") or 0
        shares = pos.get("shares_yes") or pos.get("shares") or 0
        question = pos.get("question", "Unknown")[:50]
        if shares < MIN_SHARES_PER_ORDER:
            continue
        if current_price >= EXIT_THRESHOLD:
            exits_found += 1
            print(f"   {question}...")
            print(f"     Price ${current_price:.2f} >= exit threshold ${EXIT_THRESHOLD:.2f}")
            if use_safeguards:
                context = get_market_context(api_key, market_id)
                should_trade, reasons = check_context_safeguards(context)
                if not should_trade:
                    print(f"      ⏭ Skipped: {'; '.join(reasons)}")
                    continue
                if reasons:
                    print(f"     Warnings: {'; '.join(reasons)}")
            if dry_run:
                print(f"     [DRY RUN] Would sell {shares:.1f} shares")
            else:
                print(f"     Selling {shares:.1f} shares...")
                result = execute_sell(api_key, market_id, shares)
                if result.get("success"):
                    exits_executed += 1
                    trade_id = result.get("trade_id")
                    print(f"      Sold {shares:.1f} shares @ ${current_price:.2f}")
                    if trade_id and JOURNAL_AVAILABLE:
                        log_trade(
                            trade_id=trade_id,
                            source=TRADE_SOURCE,
                            thesis=f"Exit: price ${current_price:.2f} reached exit threshold",
                            action="sell",
                        )
                else:
                    error = result.get("error", "Unknown error")
                    print(f"     ❌ Sell failed: {error}")
        else:
            print(f"   {question}...")
            print(f"     Price ${current_price:.2f} < exit ${EXIT_THRESHOLD:.2f} - hold")
    return exits_found, exits_executed

# =============================================================================
# Enhanced Main Strategy
# =============================================================================

def run_weather_strategy(dry_run: bool = True, positions_only: bool = False,
                         show_config: bool = False, smart_sizing: bool = False,
                         use_safeguards: bool = True, use_trends: bool = True):
    """Run enhanced weather trading strategy."""
    print("  Enhanced Simmer Weather Trading Skill v2.0")
    print("=" * 60)

    if dry_run:
        print("\n  [DRY RUN] No trades will be executed. Use --live to enable trading.")

    print(f"\n  Configuration:")
    print(f"  Entry threshold:     {ENTRY_THRESHOLD:.0%}")
    print(f"  Exit threshold:      {EXIT_THRESHOLD:.0%}")
    print(f"  Max position:        ${MAX_POSITION_USD:.2f}")
    print(f"  Max trades/run:      {MAX_TRADES_PER_RUN}")
    print(f"  Min quality score:   {MIN_MARKET_QUALITY_SCORE:.0%}")
    locations_display = "All US cities" if not ACTIVE_LOCATIONS else ', '.join(ACTIVE_LOCATIONS)
    print(f"  Locations:           {locations_display}")
    print(f"  Smart sizing:        {'✓' if smart_sizing else '✗'}")
    print(f"  Safeguards:          {'✓' if use_safeguards else '✗'}")
    print(f"  Trend detection:     {'✓' if use_trends else '✗'}")
    print(f"  Dynamic confidence:  ✓ Enabled")
    print(f"  Enhanced geocoding:  ✓ Enabled")

    if show_config:
        config_path = get_config_path(__file__)
        print(f"\n  Config file: {config_path}")
        return

    api_key = get_api_key()

    if smart_sizing:
        print("\n Portfolio:")
        portfolio = get_portfolio(api_key)
        if portfolio:
            print(f"  Balance:   ${portfolio.get('balance_usdc', 0):.2f}")
            print(f"  Exposure:  ${portfolio.get('total_exposure', 0):.2f}")
            print(f"  Positions: {portfolio.get('positions_count', 0)}")

    if positions_only:
        print("\n Current Positions:")
        positions = get_positions(api_key)
        if not positions:
            print("  No open positions")
        else:
            for pos in positions:
                print(f"  • {pos.get('question', 'Unknown')[:50]}...")
                print(f"    YES: {pos.get('shares_yes', 0):.1f} | P&L: ${pos.get('pnl', 0):.2f}")
        return

    print("\n📡 Fetching weather markets...")
    markets = fetch_weather_markets()
    print(f"  Found {len(markets)} weather markets")

    if not markets:
        print("  No weather markets available")
        return

    events = {}
    for market in markets:
        event_id = market.get("event_id") or market.get("event_name", "unknown")
        if event_id not in events:
            events[event_id] = []
        events[event_id].append(market)

    print(f"  Grouped into {len(events)} events")

    forecast_cache = {}
    trades_executed = 0
    opportunities_found = 0
    markets_analyzed = 0
    markets_filtered_quality = 0

    for event_id, event_markets in events.items():
        event_name = event_markets[0].get("event_name", "") if event_markets else ""
        event_info = parse_weather_event(event_name)

        if not event_info:
            continue

        location = event_info["location"]
        date_str = event_info["date"]
        metric = event_info["metric"]

        # If ACTIVE_LOCATIONS is empty, trade all cities
        # Otherwise, only trade cities in the list
        if ACTIVE_LOCATIONS and location not in ACTIVE_LOCATIONS:
            continue

        print(f"\n {location} {date_str} ({metric} temp)")

        if location not in forecast_cache:
            print(f"   Fetching NOAA forecast...")
            forecast_cache[location] = get_noaa_forecast(location)

        forecasts = forecast_cache[location]
        day_forecast = forecasts.get(date_str, {})
        forecast_temp = day_forecast.get(metric)

        if forecast_temp is None:
            print(f"    No forecast for {date_str}")
            continue

        print(f"   NOAA forecast: {forecast_temp}°F")

        matching_market = None
        for market in event_markets:
            outcome_name = market.get("outcome_name", "")
            bucket = parse_temperature_bucket(outcome_name)

            if bucket and bucket[0] <= forecast_temp <= bucket[1]:
                matching_market = market
                break

        if not matching_market:
            print(f"   No bucket for {forecast_temp}°F")
            continue

        outcome_name = matching_market.get("outcome_name", "")
        price = matching_market.get("external_price_yes") or 0.5
        market_id = matching_market.get("id")
        bucket = parse_temperature_bucket(outcome_name)

        markets_analyzed += 1

        print(f"   Matched: {outcome_name} @ ${price:.2f}")
        # 🆕 Calculate dynamic confidence
        confidence = calculate_forecast_confidence(date_str, forecast_temp, bucket, metric)
        print(f"   Confidence: {confidence:.0%} (dynamic model)")

        # 🆕 Calculate market quality score
        context_for_quality = None
        if use_safeguards:
            context_for_quality = get_market_context(api_key, market_id, my_probability=confidence)
        quality_score = calculate_market_quality_score(matching_market, context_for_quality)
        print(f"  Quality score: {quality_score:.0%}")

        if quality_score < MIN_MARKET_QUALITY_SCORE:
            markets_filtered_quality += 1
            print(f"    Quality score {quality_score:.0%} < {MIN_MARKET_QUALITY_SCORE:.0%} - skip")
            continue

        if price < MIN_TICK_SIZE or price > (1 - MIN_TICK_SIZE):
            print(f"  ⏸  Price at extreme - skip")
            continue

        # Check safeguards with confidence
        if use_safeguards and context_for_quality:
            should_trade, reasons = check_context_safeguards(context_for_quality)
            if not should_trade:
                print(f"  ⏭️  Blocked: {'; '.join(reasons)}")
                continue
            if reasons:
                print(f"   {'; '.join(reasons)}")

        # Check trend
        trend_bonus = ""
        if use_trends:
            history = get_price_history(api_key, market_id)
            trend = detect_price_trend(history)
            if trend["is_opportunity"]:
                trend_bonus = f"  (dropped {abs(trend['change_24h']):.0%})"
            elif trend["direction"] == "up":
                trend_bonus = f"  (up {trend['change_24h']:.0%})"

        if price < ENTRY_THRESHOLD:
            position_size = calculate_position_size(api_key, MAX_POSITION_USD, smart_sizing)
            min_cost = MIN_SHARES_PER_ORDER * price

            if min_cost > position_size:
                print(f"  ⚠️  Position ${position_size:.2f} too small")
                continue

            opportunities_found += 1
            print(f"   BUY opportunity!{trend_bonus}")

            if trades_executed >= MAX_TRADES_PER_RUN:
                print(f"  ⏸️  Max trades reached - skip")
                continue

            if dry_run:
                print(f"  [DRY RUN] Would buy ${position_size:.2f} (~{position_size/price:.1f} shares)")
            else:
                print(f"  💰 Executing trade...")
                result = execute_trade(api_key, market_id, "yes", position_size)
                if result.get("success"):
                    trades_executed += 1
                    shares = result.get("shares_bought") or result.get("shares") or 0
                    trade_id = result.get("trade_id")
                    print(f"  ✅ Bought {shares:.1f} shares @ ${price:.2f}")
                    if trade_id and JOURNAL_AVAILABLE:
                        log_trade(
                            trade_id=trade_id,
                            source=TRADE_SOURCE,
                            thesis=f"NOAA forecasts {forecast_temp}°F, bucket underpriced @ ${price:.2f}",
                            confidence=round(confidence, 2),
                            location=location,
                            forecast_temp=forecast_temp,
                            target_date=date_str,
                            metric=metric,
                            quality_score=round(quality_score, 2),
                        )
                else:
                    print(f"  ❌ Failed: {result.get('error')}")
        else:
            print(f"  ⏸️  Price ${price:.2f} > threshold ${ENTRY_THRESHOLD:.2f}")

    exits_found, exits_executed = check_exit_opportunities(api_key, dry_run, use_safeguards)

    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"  Events scanned:          {len(events)}")
    print(f"  Markets analyzed:        {markets_analyzed}")
    print(f"  Filtered (low quality):  {markets_filtered_quality}")
    print(f"  Entry opportunities:     {opportunities_found}")
    print(f"  Exit opportunities:      {exits_found}")
    print(f"  Total trades:            {trades_executed + exits_executed}")

    if dry_run:
        print("\n  [DRY RUN - no real trades executed]")

# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced Simmer Weather Trading")
    parser.add_argument("--live", action="store_true", help="Execute real trades")
    parser.add_argument("--dry-run", action="store_true", help="Show opportunities only (default)")
    parser.add_argument("--positions", action="store_true", help="Show positions only")
    parser.add_argument("--config", action="store_true", help="Show config")
    parser.add_argument("--set", action="append", metavar="KEY=VALUE", help="Set config value")
    parser.add_argument("--smart-sizing", action="store_true", help="Portfolio-based sizing")
    parser.add_argument("--no-safeguards", action="store_true", help="Disable safeguards")
    parser.add_argument("--no-trends", action="store_true", help="Disable trend detection")
    args = parser.parse_args()

    if args.set:
        updates = {}
        for item in args.set:
            if "=" in item:
                key, value = item.split("=", 1)
                if key in CONFIG_SCHEMA:
                    type_fn = CONFIG_SCHEMA[key].get("type", str)
                    try:
                        value = type_fn(value)
                    except (ValueError, TypeError):
                        pass
                updates[key] = value
        if updates:
            updated = update_config(updates, __file__)
            print(f"✅ Config updated: {updates}")
            _config = load_config(CONFIG_SCHEMA, __file__)
            globals()["ENTRY_THRESHOLD"] = _config["entry_threshold"]
            globals()["EXIT_THRESHOLD"] = _config["exit_threshold"]
            globals()["MAX_POSITION_USD"] = _config["max_position_usd"]
            globals()["SMART_SIZING_PCT"] = _config["sizing_pct"]
            globals()["MAX_TRADES_PER_RUN"] = _config["max_trades_per_run"]
            globals()["MIN_MARKET_QUALITY_SCORE"] = _config["min_market_quality_score"]
            _locations_str = _config["locations"]
            # Support "ALL" or empty for all cities
            if _locations_str.upper() == "ALL" or not _locations_str.strip():
                globals()["ACTIVE_LOCATIONS"] = []
            else:
                globals()["ACTIVE_LOCATIONS"] = [loc.strip().upper() for loc in _locations_str.split(",") if loc.strip()]

    dry_run = not args.live

    run_weather_strategy(
        dry_run=dry_run,
        positions_only=args.positions,
        show_config=args.config,
        smart_sizing=args.smart_sizing,
        use_safeguards=not args.no_safeguards,
        use_trends=not args.no_trends,
    )
