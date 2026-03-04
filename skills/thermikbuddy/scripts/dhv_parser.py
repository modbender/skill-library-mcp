"""
dhv_parser.py – Liest DHV-Wetterinfos und generiert Warnungen/Score-Mods.
"""

import urllib.request
import re
from datetime import datetime

DHV_URL = "https://www.dhv.de/wetter/dhv-wetter/"

# Einfaches Mapping von Skill-Regionen auf DHV-Überschriften (Teilstrings)
REGION_MAP = {
    "werdenfels": "Alpen",  # Bayerischer Alpenrand -> Alpen allgemein? DHV unterscheidet oft Nordalpen
    "inntal": "Alpen",
    "schwaebische_alb": "Mittelgebirge",
    "schwarzwald": "Mittelgebirge",
    "norddeutschland": "Flachland", # Oder Mittelgebirge/Nordhälfte
}

# Keywords, die den Score massiv drücken (Hard Cap auf "nicht fliegbar" oder "eingeschränkt")
KILLER_PHRASES = [
    "nicht fliegbar",
    "kein flugwetter",
    "dauerregen",
    "sturm",
    "orkam",
    "schneefall",
    "gewitter",
    "unfliegbar",
]

BAD_PHRASES = [
    "regenschauer",
    "regen",
    "böig",
    "föhn",
    "starkwind",
    "bedeckt",
    "abschirmung",
]

def fetch_dhv_text():
    try:
        req = urllib.request.Request(DHV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        return html
    except Exception as e:
        print(f"[WARN] DHV-Fetch failed: {e}")
        return ""

def analyze_dhv(region_id: str):
    """
    Analysiert DHV-Text für eine Region.
    Gibt zurück: {
        "text_snippet": "...", 
        "score_modifier": -5.0 (Abzug), 
        "cap": 10.0 (Max Score),
        "warning": "DHV: Regen gemeldet"
    }
    """
    html = fetch_dhv_text()
    if not html:
        return None

    # Suche grob nach dem Bereich für die Region (sehr heuristisch, da HTML-Parsing ohne bs4 schwer ist)
    # DHV gliedert oft in "Alpenraum", "Mittelgebirge", "Norddeutschland"
    
    dhv_region_keyword = REGION_MAP.get(region_id, "Deutschland")
    
    # Extrahiere Text (entferne HTML-Tags grob)
    # Wir suchen nach Abschnitten. Das ist ohne bs4 fragil, aber wir versuchen es.
    # Suche nach <h3>...Keyword...</h3> und nimm den Text danach bis zum nächsten <h3>
    
    pattern = re.compile(r'<h3>(.*?)' + re.escape(dhv_region_keyword) + r'(.*?)</h3>(.*?)(?=<h3>|<div class="news-list-view">|$)', re.DOTALL | re.IGNORECASE)
    match = pattern.search(html)
    
    if not match:
        return None
        
    content = match.group(3)
    # Tags entfernen
    text = re.sub('<[^<]+?>', ' ', content).strip()
    text = re.sub(r'\s+', ' ', text)
    
    # Analyse
    text_lower = text.lower()
    
    cap = 10.0
    mod = 0.0
    warnings = []
    
    # Killer-Phrasen (machen den Tag quasi unfliegbar)
    for phrase in KILLER_PHRASES:
        if phrase in text_lower:
            cap = 2.0  # Max Score: Eingeschränkt/Nicht fliegbar
            warnings.append(f"DHV-Warnung: '{phrase}'")
            mod -= 5.0
            
    # Schlechte Phrasen (verschlechtern den Score)
    for phrase in BAD_PHRASES:
        if phrase in text_lower:
            mod -= 1.5
            if cap > 6.0: cap = 6.0 # Max "Ordentlich"
            warnings.append(f"DHV-Hinweis: '{phrase}'")

    return {
        "text_snippet": text[:200] + "..." if len(text) > 200 else text,
        "score_modifier": mod,
        "score_cap": cap,
        "warnings": list(set(warnings)) # Unique
    }

if __name__ == "__main__":
    import sys
    region = sys.argv[1] if len(sys.argv) > 1 else "werdenfels"
    print(analyze_dhv(region))
