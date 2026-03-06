"""
fetcher.py – Open-Meteo API Abruf für Segelflug-Wettervorhersage
Ruft ICON-D2 (2km) mit erweiterten Parametern inkl. Windscherung und Höhenfeuchte ab.
Nutzt GFS als Fallback für fehlende Parameter (BLH, CAPE).
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import sys

# Regionen-Konfiguration
REGIONS = {
    "werdenfels": {
        "name": "Werdenfels / Bayerischer Alpenordrand",
        "emoji": "🏔️",
        "lat": 47.50,
        "lon": 11.10,
        "elevation_m": 705,      # Flugplatz Peißenberg
        "type": "alpine",
        "terrain_bearing": 270,  # Alpenrandkamm: West-Ost (Hangflug aus Nord)
        "dhv_region": "nordalpen",
    },
    "inntal": {
        "name": "Inntal / Nordtiroler Alpen",
        "emoji": "🏔️",
        "lat": 47.27,
        "lon": 11.40,
        "elevation_m": 560,
        "type": "alpine",
        "terrain_bearing": 270,
        "dhv_region": "nordalpen",
    },
    "schwaebische_alb": {
        "name": "Schwäbische Alb",
        "emoji": "⛰️",
        "lat": 48.40,
        "lon": 9.50,
        "elevation_m": 760,
        "type": "mittelgebirge",
        "terrain_bearing": 230,
        "dhv_region": "deutschland",
    },
    "schwarzwald": {
        "name": "Schwarzwald",
        "emoji": "🌲",
        "lat": 48.30,
        "lon": 8.10,
        "elevation_m": 900,
        "type": "mittelgebirge",
        "terrain_bearing": 270,
        "dhv_region": "deutschland",
    },
    "norddeutschland": {
        "name": "Norddeutsches Flachland",
        "emoji": "🌾",
        "lat": 53.00,
        "lon": 10.00,
        "elevation_m": 50,
        "type": "flachland",
        "terrain_bearing": None,
        "dhv_region": "deutschland",
    },
}


def list_regions():
    result = []
    for key, r in REGIONS.items():
        result.append({
            "id": key,
            "name": r["name"],
            "emoji": r["emoji"],
            "type": r["type"],
        })
    return result


def fetch_forecast(lat: float, lon: float, days: int = 3) -> dict:
    """
    Ruft Open-Meteo ICON-D2 und GFS ab und merged die Ergebnisse.
    Gibt stündliche Daten für die nächsten `days` Tage zurück.
    """
    
    # Korrigierte Parameter-Namen nach Open-Meteo Standard
    hourly_vars = [
        # Boden
        "temperature_2m",
        "dewpoint_2m",
        "precipitation",
        "cloud_cover",
        "cloud_cover_low",
        "cloud_cover_mid",
        "cloud_cover_high",
        "wind_speed_10m",
        "wind_direction_10m",
        "direct_radiation",
        "soil_moisture_0_to_1cm",
        
        # Instabilität / Grenzschicht (oft modellabhängig)
        "cape",
        "lifted_index",
        "boundary_layer_height",
        "convective_inhibition",
        
        # Druckniveaus
        "wind_speed_850hPa",
        "wind_direction_850hPa",
        "wind_speed_700hPa",
        "wind_direction_700hPa",
        
        "relative_humidity_700hPa",
        "relative_humidity_850hPa",
        
        "temperature_850hPa",
        "temperature_700hPa",
        "geopotential_height_850hPa"
    ]

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(hourly_vars),
        "daily": "precipitation_sum",
        "forecast_days": days,
        "models": "icon_d2,gfs_seamless", # Hole BEIDE Modelle
        "timezone": "Europe/Berlin",
        "wind_speed_unit": "kmh",
        "timeformat": "iso8601",
    }

    base_url = "https://api.open-meteo.com/v1/forecast"
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
        # Open-Meteo liefert bei mehreren Modellen EIN Dictionary mit Keys "variable_modellname"
        # ODER eine Liste von Dicts, je nach API Version.
        # Mein Debug Output zeigte Keys mit Suffix im GLEICHEN Dict -> Also kein List-Return, sondern Dict.
        # Korrektur meiner vorherigen Annahme (die auf Liste basierte).
        
        hourly = data.get("hourly", {})
        
        # Wir bauen ein neues 'normalized' hourly Dict
        normalized_hourly = {"time": hourly.get("time", [])}
        
        # Suffixe
        s_icon = "_icon_d2"
        s_gfs = "_gfs_seamless"
        
        for var in hourly_vars:
            # Suche ICON Daten
            vals_icon = hourly.get(f"{var}{s_icon}")
            vals_gfs = hourly.get(f"{var}{s_gfs}")
            
            # Wenn ICON Key nicht gefunden (manchmal ohne Suffix? Nein, Debug zeigte überall Suffix)
            # Aber wenn API nur ein Modell liefert, dann ohne Suffix. Checken.
            if vals_icon is None:
                # Versuch ohne Suffix (falls API Verhalten variiert)
                vals_icon = hourly.get(var)
            
            if vals_icon is None:
                # Weder mit noch ohne Suffix -> Variable fehlt im ICON
                vals_final = vals_gfs # Fallback GFS komplett
            else:
                # ICON Daten da. Prüfe auf Lücken.
                if vals_gfs:
                    # Merge Logik
                    merged = []
                    for i in range(len(vals_icon)):
                        v_icon = vals_icon[i]
                        # Sicherstellen dass GFS Index existiert
                        v_gfs = vals_gfs[i] if i < len(vals_gfs) else None
                        
                        # Merge Regel: Nimm GFS wenn ICON None oder (bei bestimmten Vars) 0.0 ist
                        if v_icon is None:
                            merged.append(v_gfs)
                        elif var in ["boundary_layer_height", "lifted_index", "cape", "convective_inhibition"]:
                             # Spezielle Regel für instabile Parameter
                             if (v_icon == 0 or v_icon is None) and v_gfs is not None and v_gfs != 0:
                                 merged.append(v_gfs)
                             else:
                                 merged.append(v_icon)
                        else:
                            merged.append(v_icon)
                    vals_final = merged
                else:
                    vals_final = vals_icon
            
            # Speichere unter dem Basis-Namen (ohne Suffix)
            if vals_final:
                normalized_hourly[var] = vals_final
            else:
                # Fallback: leere Liste oder Nullen, damit Scorer nicht crasht
                # Aber get_value fängt das eh ab.
                pass

        # Ersetze hourly im data objekt
        data["hourly"] = normalized_hourly
        return data

    except urllib.error.HTTPError as e:
        print(f"[WARN] API Error {e.code}: {e.reason}", file=sys.stderr)
        # Fallback auf reines GFS, falls ICON komplett failt?
        # Oder einfach Error raisen.
        raise e
    except Exception as e:
        print(f"[ERROR] Fetch Error: {e}", file=sys.stderr)
        raise e


def fetch_daily_precip_yesterday(lat: float, lon: float) -> float:
    """Ruft den Niederschlag des Vortages ab."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum",
        "start_date": yesterday,
        "end_date": yesterday,
        "timezone": "Europe/Berlin",
        "models": "icon_d2" 
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get("daily", {}).get("precipitation_sum", [0])[0] or 0.0
    except Exception:
        return 0.0
