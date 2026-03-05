#!/usr/bin/env python3
"""Daily 17TRACK report - sync, auto-remove delivered, and send formatted status"""

import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

# Load config
CONFIG_PATH = Path("/home/node/clawd/config/track17/config.json")
DB_PATH = Path("/home/node/clawd/packages/track17/track17.sqlite3")
TRACK17_SCRIPT = Path("/home/node/clawd/skills/track17/scripts/track17.py")

def load_token():
    """Load 17TRACK token from config"""
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
            return config.get("token")
    except Exception as e:
        print(f"❌ ERRORE: Impossibile leggere token: {e}")
        return None

def sync_packages():
    """Sync packages via track17.py"""
    token = load_token()
    if not token:
        return False
    
    os.environ["TRACK17_TOKEN"] = token
    
    # Run sync
    result = subprocess.run(
        ["python3", str(TRACK17_SCRIPT), "sync"],
        capture_output=True,
        text=True,
        cwd="/home/node/clawd/skills/track17"
    )
    
    return result.returncode == 0

def get_packages():
    """Get packages from SQLite database"""
    if not DB_PATH.exists():
        return []
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, label, number, carrier, last_status,
                last_event_desc, last_location, last_event_time_utc, last_update_at
            FROM packages
            WHERE archived = 0
            ORDER BY id
        """)
        
        packages = []
        for row in cursor.fetchall():
            packages.append({
                "id": row[0],
                "label": row[1],
                "number": row[2],
                "carrier": row[3],
                "status": row[4],
                "last_event": row[5],
                "location": row[6],
                "last_event_time": row[7],
                "last_updated": row[8]
            })
        
        conn.close()
        return packages
    
    except Exception as e:
        print(f"❌ ERRORE DATABASE: {e}")
        return []

def remove_package(pkg_id):
    """Remove a package from tracking"""
    token = load_token()
    if not token:
        return False
    
    os.environ["TRACK17_TOKEN"] = token
    
    result = subprocess.run(
        ["python3", str(TRACK17_SCRIPT), "remove", str(pkg_id)],
        capture_output=True,
        text=True,
        cwd="/home/node/clawd/skills/track17"
    )
    
    return result.returncode == 0

def auto_remove_delivered(packages):
    """Automatically remove delivered packages and return list of removed"""
    removed = []
    
    for pkg in packages:
        if pkg['status'] == 'Delivered':
            if remove_package(pkg['id']):
                removed.append(pkg)
    
    return removed

def format_status(status):
    """Format status with emoji"""
    STATUS_MAP = {
        "InTransit": "🚚 In Transito",
        "Delivered": "✅ Consegnato",
        "NotFound": "❌ Non Trovato",
        "Exception": "⚠️ Problema",
        "Expired": "⏱️ Scaduto",
        "InfoReceived": "📋 Info Ricevute",
        "PickedUp": "📦 Ritirato",
        "AvailableForPickup": "📮 Pronto per Ritiro",
    }
    return STATUS_MAP.get(status, status or "❓ Sconosciuto")

def format_date(iso_date):
    """Format ISO date to DD/MM/YYYY"""
    if not iso_date:
        return None
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y")
    except:
        return iso_date.split('T')[0]

def main():
    """Generate daily report with auto-cleanup"""
    
    # Sync packages
    if not sync_packages():
        print("⚠️ *ERRORE SINCRONIZZAZIONE 17TRACK*")
        print("")
        print("API temporaneamente non disponibile.")
        return
    
    # Get packages
    all_packages = get_packages()
    
    # Auto-remove delivered packages
    removed_packages = auto_remove_delivered(all_packages)
    
    # Filter out removed packages from active list
    active_packages = [p for p in all_packages if p['status'] != 'Delivered']
    
    # Show removed packages notification if any
    if removed_packages:
        print("*🗑️ PACCHI CONSEGNATI RIMOSSI*")
        print("")
        for pkg in removed_packages:
            print(f"✅ #{pkg['id']} {pkg['label']} - {pkg['number']}")
        print("")
        print("---")
        print("")
    
    # Show active packages
    if not active_packages:
        print("*📦 TRACCIAMENTI 17TRACK*")
        print("")
        print("Nessun pacco in tracking.")
        return
    
    # Build report
    now = datetime.now().strftime("%d %b %Y, %H:%M")
    print(f"*📦 TRACCIAMENTI 17TRACK*")
    print("")
    print(f"_Aggiornamento: {now}_")
    print("")
    
    for pkg in active_packages:
        print(f"*#{pkg['id']} {pkg['label']}*")
        print(f"• Codice: {pkg['number']}")
        print(f"• Status: {format_status(pkg['status'])}")
        
        if pkg.get('last_event'):
            print(f"• Evento: {pkg['last_event']}")
        
        if pkg.get('location'):
            print(f"• Location: {pkg['location']}")
        
        if pkg.get('last_event_time'):
            date_str = format_date(pkg['last_event_time'])
            if date_str:
                print(f"• Data: {date_str}")
        
        print("")
    
    print("---")
    print("")
    print("💡 _Per dettagli completi: \"Dettagli pacco [codice]\"_")

if __name__ == "__main__":
    main()
