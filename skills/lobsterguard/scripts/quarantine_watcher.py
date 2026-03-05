#!/usr/bin/env python3
"""
Quarantine Watcher - Monitors ~/.openclaw/quarantine/ for new skills
and analyzes them using skill_scanner layers.
"""

import os
import sys
import time
import requests
import pyinotify
from telegram_utils import get_telegram_config, send_telegram

BOT_TOKEN, CHAT_ID = get_telegram_config()



QUARANTINE_DIR = os.path.expanduser("~/.openclaw/quarantine")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"



def _friendly(desc):
    """
    Look up description in FRIENDLY_DESC dict.
    Returns "es / en" format or original description if not found.
    """
    if desc in FRIENDLY_DESC:
        es, en = FRIENDLY_DESC[desc]
        return f"{es} / {en}"
    return desc


def scan_quarantined_skill(skill_path):
    """
    Scan a quarantined skill using all analysis layers.
    
    1. Send scanning notification
    2. Run layers 1, 2, and optionally 3 and 4
    3. Count critical and suspicious findings
    4. Determine verdict and build report
    5. Send report to Telegram
    """
    skill_name = os.path.basename(skill_path)
    
    scanning_msg = f"🔍 Escaneando skill en cuarentena: {skill_name}...\nScanning quarantined skill: {skill_name}..."
    send_telegram(scanning_msg)
    print(f"[*] Scanning: {skill_name}")
    
    all_critical = []
    all_suspicious = []
    all_info = []
    
    try:
        # Layer 1
        l1 = analyze_layer1(skill_path)
        if isinstance(l1, dict):
            all_critical.extend(l1.get("critical", []))
            all_suspicious.extend(l1.get("suspicious", []))
            all_info.extend(l1.get("info", []))
        
        # Layer 2
        l2 = analyze_layer2(skill_path)
        if isinstance(l2, dict):
            all_critical.extend(l2.get("critical", []))
            all_suspicious.extend(l2.get("suspicious", []))
            all_info.extend(l2.get("info", []))
        
        # Layer 3 & 4 only if issues found
        l12_issues = len(all_critical) + len(all_suspicious)
        if l12_issues > 0:
            l3 = analyze_layer3(skill_path)
            if isinstance(l3, dict):
                all_critical.extend(l3.get("critical", []))
                all_suspicious.extend(l3.get("suspicious", []))
                all_info.extend(l3.get("info", []))
            
            l4 = analyze_layer4(skill_path, skill_name)
            if isinstance(l4, dict):
                all_critical.extend(l4.get("critical", []))
                all_suspicious.extend(l4.get("suspicious", []))
                all_info.extend(l4.get("info", []))
        
        crit = len(all_critical)
        susp = len(all_suspicious)
        
        # Verdict
        if crit > 0:
            verdict = "🔴 PELIGROSA / DANGEROUS"
            rec = f"rm -rf {skill_path}"
        elif susp > 0:
            verdict = "🟡 SOSPECHOSA / SUSPICIOUS"
            rec = f"Revisar manualmente / Review: {skill_path}"
        else:
            verdict = "🟢 SEGURA / SAFE"
            rec = f"mv {skill_path} ~/.openclaw/skills/"
        
        # Build report with ACTUAL findings
        lines = [
            f"🛡 <b>Quarantine Scan / Escaneo de Cuarentena</b>",
            f"",
            f"<b>Skill:</b> {skill_name}",
            f"<b>Veredicto / Verdict:</b> {verdict}",
            f""
        ]
        
        if all_critical:
            lines.append(f"<b>🔴 Criticos / Critical ({crit}):</b>")
            for finding in all_critical:
                friendly = _friendly(finding)
                lines.append(f"  • {friendly}")
            lines.append("")
        
        if all_suspicious:
            lines.append(f"<b>🟡 Sospechosos / Suspicious ({susp}):</b>")
            for finding in all_suspicious:
                friendly = _friendly(finding)
                lines.append(f"  • {friendly}")
            lines.append("")
        
        if all_info and not all_critical and not all_suspicious:
            lines.append(f"<b>ℹ️ Info:</b>")
            for info in all_info:
                lines.append(f"  • {info}")
            lines.append("")
        
        lines.append(f"<b>Recomendacion / Recommendation:</b>")
        lines.append(f"<code>{rec}</code>")
        
        report = "\n".join(lines)
        send_telegram(report)
        print(f"[+] Report sent for: {skill_name}")
        
    except Exception as e:
        error_msg = f"❌ Error scanning {skill_name}: {str(e)}"
        send_telegram(error_msg)
        print(f"[-] Error: {error_msg}")


class QuarantineHandler(pyinotify.ProcessEvent):
    """Handle inotify events for quarantine directory."""
    
    def __init__(self):
        super().__init__()
        self._debounce = {}  # Track recently scanned paths with timestamps
        self.debounce_seconds = 30
    
    def process_IN_CREATE(self, event):
        """Handle IN_CREATE events."""
        if event.dir:
            path = event.pathname
            current_time = time.time()
            
            # Check debounce
            if path in self._debounce:
                last_scan = self._debounce[path]
                if current_time - last_scan < self.debounce_seconds:
                    return
            
            # Update debounce
            self._debounce[path] = current_time
            
            # Wait for files to finish copying
            time.sleep(3)
            
            # Scan the skill
            if os.path.exists(path):
                scan_quarantined_skill(path)
    
    def process_IN_MOVED_TO(self, event):
        """Handle IN_MOVED_TO events."""
        self.process_IN_CREATE(event)


def main():
    """Main function to set up and run quarantine watcher."""
    
    # Create quarantine directory if it doesn't exist
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    print(f"[*] Quarantine directory: {QUARANTINE_DIR}")
    
    # Scan existing skills in quarantine on startup
    print("[*] Scanning existing skills in quarantine...")
    if os.path.exists(QUARANTINE_DIR):
        for item in os.listdir(QUARANTINE_DIR):
            item_path = os.path.join(QUARANTINE_DIR, item)
            if os.path.isdir(item_path):
                scan_quarantined_skill(item_path)
    
    # Set up pyinotify
    try:
        wm = pyinotify.WatchManager()
        handler = QuarantineHandler()
        notifier = pyinotify.Notifier(wm, handler)
        
        # Watch for IN_CREATE and IN_MOVED_TO events
        wm.add_watch(QUARANTINE_DIR, pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO)
        
        print(f"[+] Quarantine watcher started. Monitoring: {QUARANTINE_DIR}")
        send_telegram("🔐 Quarantine Watcher initialized / Observador de cuarentena inicializado")
        
        # Main loop
        notifier.loop()
        
    except ImportError:
        print("Error: pyinotify is not installed.")
        print("Install it with: pip3 install pyinotify")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Fatal error in quarantine watcher: {str(e)}"
        print(f"[-] {error_msg}")
        send_telegram(f"❌ {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
