"""
scorer.py – Segelflug-Thermik-Scoring Engine v2.1
Berechnet Thermik-Score 0–10 mit Alpen-spezifischer Logik:
  - Windscherung 10m → 850hPa
  - Relative Feuchte 700hPa
  - Föhn-Erkennung
  - Hangflug-Bonus
  - Überentwicklungs-Warnung
  - Thermik-Zeitfenster & Typ (Neu in V2.1)
  - Inversions-Erkennung (Lapse Rate)
"""

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HourlyData:
    hour: int                          # 0–23
    temp_2m: float                     # °C
    dewpoint_2m: float                 # °C
    precip: float                      # mm
    cloudcover: float                  # % gesamt
    cloudcover_low: float              # %
    cloudcover_mid: float              # %
    direct_radiation: float            # W/m²
    wind_speed_10m: float              # km/h
    wind_dir_10m: float                # °
    wind_speed_850hpa: float           # km/h
    wind_dir_850hpa: float             # °
    wind_u_10m: float                  # m/s
    wind_v_10m: float                  # m/s
    wind_u_850hpa: float               # m/s
    wind_v_850hpa: float               # m/s
    rh_700hpa: float                   # %
    
    # Defaults
    rh_850hpa: float = 50.0            # %
    cape: float = 0.0                  # J/kg
    lifted_index: float = 0.0
    cin: float = 0.0                   # J/kg (Convective Inhibition)
    blh: float = 0.0                   # m AGL
    soil_moisture: float = 0.25        # m³/m³
    temp_850hpa: Optional[float] = None
    temp_700hpa: Optional[float] = None


@dataclass
class DailyScore:
    date: str
    score: float                       # 0–10
    label: str
    emoji: str
    # Thermik-Kern
    avg_climb_rate: float              # m/s
    cloud_base_msl: float              # m MSL
    blh_max: float                     # m AGL
    cape_max: float                    # J/kg
    # Wind
    wind_avg: float                    # km/h
    wind_shear_avg: float              # km/h
    # Warnungen
    warnings: list = field(default_factory=list)
    foehn_detected: bool = False
    overdevelopment_risk: str = "none" # none / moderate / high
    ridge_lift_bonus: float = 0.0
    # Tagesablauf
    phases: list = field(default_factory=list)   # 4 Phasen
    # Parameter-Details für Debugging
    param_scores: dict = field(default_factory=dict)
    # Neu V2.1
    thermik_start: Optional[int] = None
    thermik_end: Optional[int] = None
    thermik_duration: int = 0
    thermik_type: str = "Cumulus" # Blau/Cumulus


# ──────────────────────────────────────────────
# Hilfsfunktionen
# ──────────────────────────────────────────────

def _wind_shear(u10, v10, u850, v850) -> float:
    """Windscherung in km/h zwischen 10m und 850hPa."""
    du = u850 - u10
    dv = v850 - v10
    return math.sqrt(du**2 + dv**2) * 3.6


def _cloud_base_msl(temp_2m, dewpoint_2m, elevation_m) -> float:
    """Wolkenbasis MSL nach Spread-Methode."""
    spread = temp_2m - dewpoint_2m
    return elevation_m + spread * 125.0


def _estimated_climb_rate(cape, blh, cloudcover_low, wind_10m, wind_shear_kmh) -> float:
    """Steigwert-Schätzung in m/s."""
    if cape <= 0 or blh <= 100:
        return 0.0
    base = math.sqrt(2 * cape) * 0.04
    blh_f = min(blh / 2000.0, 1.5)
    cc_f = max(0.3, 1.0 - cloudcover_low / 150.0)
    wind_f = max(0.3, 1.0 - max(0, wind_10m - 15) / 40.0)
    shear_f = max(0.5, 1.0 - wind_shear_kmh / 60.0)
    return round(min(base * blh_f * cc_f * wind_f * shear_f, 5.0), 2)


def _calculate_lapse_rate(t_low, h_low, t_high, h_high):
    """Berechnet Temperaturgradient in °C pro 100m."""
    if t_low is None or t_high is None or h_low is None or h_high is None:
        return 0.0
    if h_high <= h_low:
        return 0.0
    diff_t = t_low - t_high
    diff_h = h_high - h_low
    return (diff_t / diff_h) * 100.0


# ──────────────────────────────────────────────
# Föhn-Erkennung
# ──────────────────────────────────────────────

def detect_foehn(h: HourlyData) -> bool:
    """
    Föhn-Kriterien für Bayerischer Alpenordrand:
    - Südwind am Boden (150–240°)
    - Wind > 25 km/h
    - Sehr trockene Luft (Spread > 8°C)
    - Kein Niederschlag
    """
    wind_from_south = 150 <= h.wind_dir_10m <= 240
    wind_strong = h.wind_speed_10m > 25
    dry_air = (h.temp_2m - h.dewpoint_2m) > 8
    no_precip = h.precip < 0.1
    return wind_from_south and wind_strong and dry_air and no_precip


# ──────────────────────────────────────────────
# Hangflug-Bonus (Alpen)
# ──────────────────────────────────────────────

def ridge_lift_bonus(h: HourlyData, terrain_bearing: float, region_type: str) -> float:
    """
    Hangflug-Bonus wenn Wind aus optimaler Richtung für den Hangkamm.
    """
    if region_type != "alpine":
        return 0.0
    if detect_foehn(h):
        return 0.0  # Kein Bonus bei Föhn
    if h.precip > 0.2:
        return 0.0

    optimal_dir = (terrain_bearing + 90) % 360
    diff = abs(h.wind_dir_10m - optimal_dir)
    if diff > 180:
        diff = 360 - diff

    if diff > 45:
        return 0.0

    speed = h.wind_speed_10m
    if speed < 15:
        return 0.0
    elif 15 <= speed <= 35:
        direction_factor = 1.0 - (diff / 45.0)
        return round(1.5 * direction_factor, 2)
    elif 35 < speed <= 50:
        direction_factor = 1.0 - (diff / 45.0)
        return round(1.0 * direction_factor, 2)
    else:
        return 0.0  # Zu stark


# ──────────────────────────────────────────────
# Parameter-Scoring (0–10 pro Parameter)
# ──────────────────────────────────────────────

def _score_cape(v) -> float:
    if v < 50:   return 1.0
    if v < 150:  return 3.0 + (v - 50) / 100 * 2
    if v < 400:  return 5.0 + (v - 150) / 250 * 2
    if v < 900:  return 7.0 + (v - 400) / 500 * 2
    if v < 1500: return 9.0 + (v - 900) / 600
    return 10.0

def _score_blh(v) -> float:
    if v < 500:  return 1.0 + v / 500 * 2
    if v < 1000: return 3.0 + (v - 500) / 500 * 2
    if v < 1800: return 5.0 + (v - 1000) / 800 * 2
    if v < 2500: return 7.0 + (v - 1800) / 700 * 2
    if v < 4000: return 9.0 + (v - 2500) / 1500
    return 10.0

def _score_li(v) -> float:
    if v > 2:    return 1.0
    if v > 0:    return 2.0 + (2 - v) / 2 * 2
    if v > -2:   return 4.0 + (-v) / 2 * 2
    if v > -4:   return 6.0 + (-v - 2) / 2 * 2
    if v > -6:   return 8.0 + (-v - 4) / 2 * 2
    return 10.0

def _score_cloudcover(v) -> float:
    # Invertiert: niedrige Bewölkung = besser
    if v < 20:  return 10.0
    if v < 40:  return 8.0 - (v - 20) / 20 * 2
    if v < 60:  return 6.0 - (v - 40) / 20 * 2
    if v < 80:  return 4.0 - (v - 60) / 20 * 2
    return max(0.0, 2.0 - (v - 80) / 20 * 2)

def _score_wind(v) -> float:
    # Invertiert: weniger Wind = besser (für Thermik)
    if v < 10:  return 9.0
    if v < 20:  return 8.0 - (v - 10) / 10 * 2
    if v < 30:  return 6.0 - (v - 20) / 10 * 2
    if v < 40:  return 4.0 - (v - 30) / 10 * 2
    if v < 55:  return 2.0 - (v - 40) / 15 * 2
    return 0.0

def _score_spread(v) -> float:
    # T - Td: größer = trockener = besser
    if v < 2:  return 1.0
    if v < 4:  return 3.0 + (v - 2) / 2 * 2
    if v < 6:  return 5.0 + (v - 4) / 2 * 2
    if v < 10: return 7.0 + (v - 6) / 4 * 2
    return 9.0 + min(1.0, (v - 10) / 5)

def _score_radiation(v) -> float:
    if v < 100:  return 1.0
    if v < 300:  return 2.0 + (v - 100) / 200 * 3
    if v < 600:  return 5.0 + (v - 300) / 300 * 3
    if v < 900:  return 8.0 + (v - 600) / 300 * 2
    return 10.0

def _score_soil_moisture(v) -> float:
    if v < 0.10: return 10.0
    if v < 0.20: return 8.0 - (v - 0.10) / 0.10 * 2
    if v < 0.30: return 6.0 - (v - 0.20) / 0.10 * 2
    if v < 0.40: return 4.0 - (v - 0.30) / 0.10 * 2
    return max(0.0, 2.0 - (v - 0.40) / 0.20 * 2)

def _score_prev_precip(v) -> float:
    if v < 1:   return 10.0
    if v < 5:   return 8.0 - (v - 1) / 4 * 3
    if v < 15:  return 5.0 - (v - 5) / 10 * 3
    if v < 30:  return 2.0 - (v - 15) / 15 * 2
    return 0.0

def _score_wind_shear(v) -> float:
    if v < 8:   return 10.0
    if v < 15:  return 8.0 - (v - 8) / 7 * 2
    if v < 22:  return 6.0 - (v - 15) / 7 * 2
    if v < 30:  return 4.0 - (v - 22) / 8 * 3
    return max(0.0, 1.0 - (v - 30) / 20)

def _score_rh_700(v) -> float:
    if v < 25:  return 10.0
    if v < 40:  return 8.0 - (v - 25) / 15 * 2
    if v < 55:  return 6.0 - (v - 40) / 15 * 2
    if v < 70:  return 4.0 - (v - 55) / 15 * 3
    return max(0.0, 1.0 - (v - 70) / 30)


# ──────────────────────────────────────────────
# Gesamt-Scoring für eine Stunde
# ──────────────────────────────────────────────

WEIGHTS = {
    "cape":        0.12,
    "blh":         0.18,
    "li":          0.08,
    "cloudcover":  0.12,
    "wind":        0.08,
    "spread":      0.05,
    "radiation":   0.10,
    "soil":        0.08,
    "prev_precip": 0.05,
    "wind_shear":  0.07,
    "rh_700":      0.07,
}

def score_hour(h: HourlyData, prev_precip: float, terrain_bearing: float,
               region_type: str) -> dict:
    """Berechnet Score und Details für eine Stunde."""
    shear = _wind_shear(h.wind_u_10m, h.wind_v_10m, h.wind_u_850hpa, h.wind_v_850hpa)
    spread = h.temp_2m - h.dewpoint_2m

    # Lapse Rate
    h_ground = 700 # Annahme Alpenvorland
    h_850 = 1500
    h_700 = 3000
    
    lapse_low = _calculate_lapse_rate(h.temp_2m, h_ground, h.temp_850hpa, h_850)
    lapse_high = _calculate_lapse_rate(h.temp_850hpa, h_850, h.temp_700hpa, h_700)

    param_scores = {
        "cape":        _score_cape(h.cape),
        "blh":         _score_blh(h.blh),
        "li":          _score_li(h.lifted_index),
        "cloudcover":  _score_cloudcover(h.cloudcover_low + h.cloudcover_mid * 0.5),
        "wind":        _score_wind(h.wind_speed_10m),
        "spread":      _score_spread(spread),
        "radiation":   _score_radiation(h.direct_radiation),
        "soil":        _score_soil_moisture(h.soil_moisture),
        "prev_precip": _score_prev_precip(prev_precip),
        "wind_shear":  _score_wind_shear(shear),
        "rh_700":      _score_rh_700(h.rh_700hpa),
    }

    base_score = sum(WEIGHTS[k] * v for k, v in param_scores.items())
    
    # Initialisiere Warnungen
    warnings = []
    
    # Neu V2.1: Thermik Typ & Trigger
    is_active = False
    thermik_type = "Cumulus"
    
    # Thermik aktiv?
    # Radiation Threshold: Im Februar sind 150W/m2 schon ordentlich, im Sommer eher 250
    rad_threshold = 150 
    if lapse_low >= 0.5 and h.direct_radiation > rad_threshold:
        is_active = True
        
    # Spreitung / Abschattung (Spread am Top der BLH)
    spread_top = 99.0
    if is_active:
        # Wo ist der Deckel? 850 oder 700?
        if 1000 < h.blh < 2200 and h.temp_850hpa is not None:
             td_850 = h.temp_850hpa - ((100 - h.rh_850hpa)/5.0)
             spread_top = h.temp_850hpa - td_850
        elif h.blh >= 2200 and h.temp_700hpa is not None:
             td_700 = h.temp_700hpa - ((100 - h.rh_700hpa)/5.0)
             spread_top = h.temp_700hpa - td_700
        
        if spread_top < 2.0:
            base_score = max(0.0, base_score - 2.5)
            warnings.append(f"☁️ Ausbreitungsgefahr (Spread Top {spread_top:.1f}K) – Abschattung!")
            thermik_type = "Ausbreitung"

    # Blau vs Cu
    ccl = _cloud_base_msl(h.temp_2m, h.dewpoint_2m, 705)
    ccl_agl = ccl - 705
    if is_active and thermik_type != "Ausbreitung":
        # Wenn Kondensationsniveau deutlich über der Arbeitshöhe (BLH) liegt -> Blau
        if ccl_agl > h.blh + 300: 
            thermik_type = "Blau"
            base_score -= 0.5 
            if h.direct_radiation > 400:
                warnings.append("🔵 Blauthermik (Trocken)")
        elif abs(ccl_agl - h.blh) < 300:
             thermik_type = "Cumulus"


    # Föhn
    foehn = detect_foehn(h)
    if foehn:
        base_score = max(0.0, base_score - 3.0)

    # Lapse Rate Checks
    if lapse_low < 0:
        base_score = max(0.0, base_score - 4.0)
        warnings.append(f"⛔ Inversion unten ({lapse_low:.1f}°C/100m) – Thermik gesperrt")
    elif lapse_low < 0.4:
        base_score = max(0.0, base_score - 2.0)
        warnings.append(f"📉 Sehr stabile Schichtung ({lapse_low:.1f}°C/100m) – zähe Thermik")
    elif lapse_low > 0.9:
        base_score = min(10.0, base_score + 1.0) 

    if lapse_high < 0.2:
        base_score = max(0.0, base_score - 1.5)
        warnings.append(f"⛔ Inversion oben ({lapse_high:.1f}°C/100m) – Deckel drauf")

    # Hard Checks
    if h.precip > 0.1:
        base_score = 0.0
        warnings.append("🌧️ Regen – nicht fliegbar")
    
    elif h.cloudcover > 90 and h.wind_speed_10m < 15:
        base_score = min(base_score, 1.0)
        warnings.append("☁️ Bedeckt – keine Thermik zu erwarten")

    if h.wind_speed_10m > 35:
        base_score = 0.0
        warnings.append("💨 Sturm am Boden (>35 km/h) – Start gefährlich/unmöglich")
    
    if h.cape > 2000 or h.lifted_index < -6:
        base_score = min(base_score, 3.0)
        warnings.append("⛈️ Hohe Gewittergefahr")
    elif h.rh_700hpa > 65 and h.cape > 800:
        base_score = max(0.0, base_score - 3.0)

    if h.blh < 800 and h.wind_speed_10m < 15:
        if h.blh < 500:
            base_score = min(base_score, 2.5)
            warnings.append(f"📉 Extrem niedrige Arbeitshöhe ({h.blh:.0f}m)")
        else:
            base_score = min(base_score, 4.5)
            warnings.append(f"📉 Niedrige Arbeitshöhe ({h.blh:.0f}m)")

    # Hangflug
    ridge_bonus = ridge_lift_bonus(h, terrain_bearing, region_type)
    total_score = min(10.0, base_score + ridge_bonus)

    # Overdev
    overdev = "none"
    if h.cape > 600 and h.rh_700hpa > 55 and h.cloudcover_mid > 30:
        overdev = "high" if (h.cape > 1000 or h.rh_700hpa > 70) else "moderate"

    cloud_base = _cloud_base_msl(h.temp_2m, h.dewpoint_2m, 705)
    climb = _estimated_climb_rate(h.cape, h.blh, h.cloudcover_low, h.wind_speed_10m, shear)

    return {
        "hour": h.hour,
        "score": round(total_score, 2),
        "base_score": round(base_score, 2),
        "ridge_bonus": round(ridge_bonus, 2),
        "foehn": foehn,
        "overdev": overdev,
        "warnings": warnings,
        "param_scores": param_scores,
        "shear_kmh": round(shear, 1),
        "cloud_base_msl": round(cloud_base),
        "climb_rate": climb,
        "blh": h.blh,
        "cape": h.cape,
        "wind_speed": h.wind_speed_10m,
        "wind_dir": h.wind_dir_10m,
        "rh_700": h.rh_700hpa,
        "is_active": is_active,
        "thermik_type": thermik_type,
    }


# ──────────────────────────────────────────────
# Tages-Aggregation
# ──────────────────────────────────────────────

PHASE_WINDOWS = [
    ("09-12", range(9, 12)),
    ("12-15", range(12, 15)),
    ("15-18", range(15, 18)),
    ("18-20", range(18, 20)),
]

SCORE_LABELS = [
    (0,  2,  "❌", "Kein Segelflugwetter"),
    (2,  4,  "🌥️", "Eingeschränkt"),
    (4,  6,  "⛅", "Ordentlicher Tag"),
    (6,  8,  "☀️", "Guter Tag"),
    (8,  10, "🔥", "Hammertag!"),
]


def _score_to_label(score: float):
    for lo, hi, emoji, label in SCORE_LABELS:
        if lo <= score < hi:
            return emoji, label
    return "🔥", "Hammertag!"


def _bar(score: float, total=5) -> str:
    filled = round(score / 10 * total)
    return "◉" * filled + "◎" * (total - filled)


def score_day(date: str, hourly_results: list, prev_precip: float) -> DailyScore:
    """Aggregiert Stunden-Scores zu einem Tages-Score."""
    flight_hours = [r for r in hourly_results if 9 <= r["hour"] < 20]
    
    # Trigger / Ende berechnen
    active_hours = [r["hour"] for r in flight_hours if r["is_active"]]
    start_hour = min(active_hours) if active_hours else None
    end_hour = max(active_hours) + 1 if active_hours else None # +1 weil Ende der Stunde
    duration = len(active_hours)
    
    # Thermik Typ (Mehrheit)
    types = [r["thermik_type"] for r in flight_hours if r["is_active"]]
    main_type = max(set(types), key=types.count) if types else "N/A"
    
    if not flight_hours:
        emoji, label = _score_to_label(0)
        return DailyScore(date=date, score=0, label=label, emoji=emoji,
                          avg_climb_rate=0, cloud_base_msl=0, blh_max=0, cape_max=0,
                          wind_avg=0, wind_shear_avg=0)

    peak_hours = [r for r in hourly_results if 10 <= r["hour"] <= 17]
    if peak_hours:
        peak_score = max(r["score"] for r in peak_hours)
        avg_score = sum(r["score"] for r in peak_hours) / len(peak_hours)
        day_score = round(0.6 * peak_score + 0.4 * avg_score, 1)
    else:
        day_score = round(sum(r["score"] for r in flight_hours) / len(flight_hours), 1)

    # Malus für kurze Dauer
    if start_hour and duration < 4:
         day_score = max(0, day_score - 1.5) # Zu kurz für Strecke

    emoji, label = _score_to_label(day_score)

    phases = []
    for name, hrs in PHASE_WINDOWS:
        ph = [r for r in hourly_results if r["hour"] in hrs]
        if ph:
            ph_score = sum(r["score"] for r in ph) / len(ph)
            ph_climb = sum(r["climb_rate"] for r in ph) / len(ph)
            ph_blh = max(r["blh"] for r in ph)
            desc = f"⌀{ph_climb:.1f}m/s · BLH {ph_blh:.0f}m"
            phases.append({
                "name": name,
                "score": round(ph_score, 1),
                "bar": _bar(ph_score),
                "desc": desc,
            })

    blh_max = max(r["blh"] for r in flight_hours)
    cape_max = max(r["cape"] for r in flight_hours)
    cloud_base = sum(r["cloud_base_msl"] for r in flight_hours) / len(flight_hours)
    avg_climb = sum(r["climb_rate"] for r in flight_hours) / len(flight_hours)
    wind_avg = sum(r["wind_speed"] for r in flight_hours) / len(flight_hours)
    shear_avg = sum(r["shear_kmh"] for r in flight_hours) / len(flight_hours)

    all_warnings = []
    seen = set()
    
    # Füge Timing Info als "Warnung" hinzu (damit user es sieht)
    if start_hour:
        all_warnings.append(f"⏱️ Thermik-Zeitfenster: {start_hour}:00 - {end_hour}:00 ({duration}h)")
    else:
        all_warnings.append("⏱️ Keine nutzbare Thermik erwartet")
        
    if main_type != "N/A":
        all_warnings.append(f"🎨 Thermik-Typ: {main_type}")

    for r in hourly_results:
        for w in r["warnings"]:
            if w not in seen:
                all_warnings.append(w)
                seen.add(w)

    foehn = any(r["foehn"] for r in flight_hours)
    overdev_scores = [r["overdev"] for r in flight_hours]
    overdev = "high" if "high" in overdev_scores else ("moderate" if "moderate" in overdev_scores else "none")
    ridge_bonus = max(r["ridge_bonus"] for r in flight_hours)

    return DailyScore(
        date=date,
        score=day_score,
        label=label,
        emoji=emoji,
        avg_climb_rate=round(avg_climb, 2),
        cloud_base_msl=round(cloud_base),
        blh_max=round(blh_max),
        cape_max=round(cape_max),
        wind_avg=round(wind_avg, 1),
        wind_shear_avg=round(shear_avg, 1),
        warnings=all_warnings,
        foehn_detected=foehn,
        overdevelopment_risk=overdev,
        ridge_lift_bonus=round(ridge_bonus, 2),
        phases=phases,
        thermik_start=start_hour,
        thermik_end=end_hour,
        thermik_duration=duration,
        thermik_type=main_type
    )
