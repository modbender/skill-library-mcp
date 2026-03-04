#!/usr/bin/env python3
"""Decode Apple serial numbers (old 12-character format).
Usage: python3 decode_serial.py <serial_number>
"""

import sys
import json

# Manufacturing location codes (first 1-3 characters)
# Sources: Beetstech, Techable, Apple Community, MacRumors
LOCATIONS = {
    # USA
    "FC": "Fountain Colorado, USA",
    "F": "Fremont, California, USA",
    "XA": "USA",
    "XB": "USA",
    "QP": "USA",
    "G8": "USA",
    # Americas
    "RN": "Mexico",
    "GQ": "Foxconn, Brazil",
    # Europe
    "CK": "Cork, Ireland",
    "VM": "Foxconn, Pardubice, Czech Republic",
    # Asia-Pacific
    "SG": "Singapore",
    "E": "Singapore",
    "MB": "Malaysia",
    "PT": "Korea",
    "CY": "Korea",
    "EE": "Taiwan",
    "QT": "Taiwan",
    "UV": "Taiwan",
    # China - Foxconn
    "FK": "Foxconn, Zhengzhou, China",
    "F1": "Foxconn, Zhengzhou, China",
    "F2": "Foxconn, Zhengzhou, China",
    "F7": "China",
    "DL": "Foxconn, China",
    "DM": "Foxconn, China",
    "DN": "Foxconn, Chengdu, China",
    "D2": "Foxconn, China",
    "DX": "Foxconn, Zhengzhou, China",
    "D2": "Foxconn, China",
    "C3": "Foxconn, Shenzhen, China",
    "C6": "Foxconn, Zhengzhou, China",
    "C6K": "Foxconn, Zhengzhou, China",
    # China - Quanta
    "C0": "Tech Com/Quanta, China",
    "C02": "Quanta, Shanghai, China",
    "C07": "Quanta, Shanghai, China",
    "C17": "Quanta, Shanghai, China",
    # China - Pegatron
    "G0": "Pegatron, Shanghai, China",
    "G6": "Foxconn, Shenzhen, China",
    "J2": "Pegatron, Shanghai, China",
    # China - Other
    "C7": "Pentragon, Shanghai, China",
    "W8": "Shanghai, China",
    "YM": "Hon Hai/Foxconn, China",
    "7J": "Hon Hai/Foxconn, China",
    "1C": "China",
    "4H": "China",
    "WQ": "China",
    # India
    "H0": "Foxconn, India",
    "HN": "Foxconn, India",
    # Other
    "RM": "Refurbished/Remanufactured",
}

# Year codes (4th character) - each letter = one half-year
# Letters I, O, U are skipped. S IS used (= 2016 H2).
# Source: Beetstech, Techable, multiple repair sites
YEAR_CODES = {
    "C": (2010, "H1"), "D": (2010, "H2"),
    "F": (2011, "H1"), "G": (2011, "H2"),
    "H": (2012, "H1"), "J": (2012, "H2"),
    "K": (2013, "H1"), "L": (2013, "H2"),
    "M": (2014, "H1"), "N": (2014, "H2"),
    "P": (2015, "H1"), "Q": (2015, "H2"),
    "R": (2016, "H1"), "S": (2016, "H2"),
    "T": (2017, "H1"), "V": (2017, "H2"),
    "W": (2018, "H1"), "X": (2018, "H2"),
    "Y": (2019, "H1"), "Z": (2019, "H2"),
}

# Week codes (5th character)
# 1-9 = weeks 1-9, then letters (skipping A,B,E,I,O,S,U)
# For H2 devices, add 26 to get actual week of year
WEEK_CODES = {
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9,
    "C": 10, "D": 11, "F": 12, "G": 13, "H": 14,
    "J": 15, "K": 16, "L": 17, "M": 18, "N": 19,
    "P": 20, "Q": 21, "R": 22, "T": 23, "V": 24,
    "W": 25, "X": 26, "Y": 27,
}


def get_location(serial):
    """Try 3-char, then 2-char, then 1-char prefix for location."""
    for length in (3, 2, 1):
        prefix = serial[:length]
        if prefix in LOCATIONS:
            return prefix, LOCATIONS[prefix]
    return serial[:3], "Unknown"


# Model code database - basic mappings compiled from various sources
# Format: model_code -> (model_identifier, device_name, ram, storage_options, notes)
MODEL_CODES = {
    # MacBook Pro 2012-2013
    "DKQ": ("MacBookPro10,1", "MacBook Pro 15\" Retina Mid-2012", "8-16GB", "256-768GB SSD", "First Retina MacBook Pro"),
    "DL4": ("MacBookPro9,1", "MacBook Pro 15\" Mid-2012", "4-8GB", "500GB-1TB HDD", "Non-Retina"),
    "F": ("MacBookPro10,1", "MacBook Pro 15\" Retina Early 2013", "8-16GB", "256-768GB SSD", ""),
    "G": ("MacBookPro10,2", "MacBook Pro 13\" Retina", "8-16GB", "128-768GB SSD", "Late 2012/Early 2013"),
    
    # iPhone 7 (2016)
    "HG7": ("iPhone9,1", "iPhone 7 4.7\"", "2GB", "32/128/256GB", "GSM, A10 Fusion"),
    "MN": ("iPhone9,3", "iPhone 7 4.7\"", "2GB", "32/128/256GB", "CDMA, A10 Fusion"),
    "NG": ("iPhone9,2", "iPhone 7 Plus 5.5\"", "3GB", "32/128/256GB", "Dual camera"),
    "NF": ("iPhone9,4", "iPhone 7 Plus 5.5\"", "3GB", "32/128/256GB", "CDMA variant"),
}


def lookup_model_info(model_code):
    """Look up model information from the model code (last 3-4 chars)."""
    if not model_code:
        return None
    
    # Try exact match first
    if model_code in MODEL_CODES:
        return MODEL_CODES[model_code]
    
    # Try prefix matches for partial codes (e.g., "DKQ" matches "DKQ2")
    for length in range(min(len(model_code), 3), 0, -1):
        prefix = model_code[:length]
        if prefix in MODEL_CODES:
            return MODEL_CODES[prefix]
    
    return None


def decode_old_format(serial):
    serial = serial.upper().strip()
    result = {"serial": serial, "format": "old_12char", "length": len(serial)}

    loc_code, loc_name = get_location(serial)
    result["manufacturing_location"] = {"code": loc_code, "name": loc_name}

    year_char = serial[3]
    week_char = serial[4]
    day_char = serial[5] if len(serial) > 5 else "?"

    if year_char in YEAR_CODES:
        year, half = YEAR_CODES[year_char]
        if week_char in WEEK_CODES:
            week_in_half = WEEK_CODES[week_char]
            if half == "H2":
                actual_week = week_in_half + 26
            else:
                actual_week = week_in_half

            half_label = "Jan-Jun" if half == "H1" else "Jul-Dec"
            result["manufacture_date"] = {
                "year": year,
                "half": half,
                "week_code": week_char,
                "week_number": actual_week,
                "day_code": day_char,
                "estimated": f"~Week {actual_week}, {half_label} {year}",
            }
        else:
            result["manufacture_date"] = {
                "year": year, "half": half,
                "week_code": week_char, "error": "Unknown week code"
            }
    else:
        result["manufacture_date"] = {
            "year_code": year_char, "error": "Unknown year code"
        }

    # Model code analysis (last 3-4 characters)
    model_code = serial[8:11] if len(serial) >= 11 else "?"
    config_code = serial[11:] if len(serial) > 11 else "?"
    last_four = serial[-4:] if len(serial) >= 12 else serial[-3:]
    
    result["model_code"] = model_code
    result["config_code"] = config_code
    result["last_four"] = last_four

    # Try to identify the specific model
    model_info = lookup_model_info(model_code) or lookup_model_info(last_four)
    if model_info:
        identifier, device, ram, storage, notes = model_info
        result["device_info"] = {
            "model_identifier": identifier,
            "device_name": device,
            "ram": ram,
            "storage_options": storage,
            "notes": notes
        }
    else:
        result["device_info"] = {
            "status": "Unknown model code - use web lookup for identification"
        }

    return result


def detect_format(serial):
    """Detect old (11-12 char decodable) vs new (randomized) format."""
    serial = serial.strip().upper()
    if len(serial) in (11, 12):
        # Check if 4th char is a valid year code
        if len(serial) >= 4 and serial[3] in YEAR_CODES:
            return "old"
        # Even without known year code, 12-char is likely old format
        if len(serial) == 12:
            return "old"
    if len(serial) == 10:
        return "new"  # Post-2021 randomized
    return "unknown"


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: decode_serial.py <serial_number>"}))
        sys.exit(1)

    serial = sys.argv[1].strip().upper()
    fmt = detect_format(serial)

    if fmt == "old":
        result = decode_old_format(serial)
    elif fmt == "new":
        result = {
            "serial": serial,
            "format": "new_randomized",
            "length": len(serial),
            "note": "Post-2021 randomized serial. Cannot decode locally — use web lookup for device identification.",
        }
    else:
        result = {
            "serial": serial,
            "format": "unknown",
            "length": len(serial),
            "note": f"Unrecognized format ({len(serial)} chars). Verify the serial number is correct.",
        }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
