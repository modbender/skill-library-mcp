#!/usr/bin/env python3
"""
LobsterGuard Auto-Scan Script
Runs check.py periodically and alerts via Telegram on score changes
"""

import os
import json
import re
import sys
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
from telegram_utils import get_telegram_config, send_telegram



SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_SCRIPT = os.path.join(SCRIPT_DIR, "check.py")
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
SCORE_FILE = os.path.join(DATA_DIR, "last_score.json")



def get_last_score():
    """Read the last saved score from file"""
    if not os.path.exists(SCORE_FILE):
        return None
    
    try:
        with open(SCORE_FILE, 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error reading score file: {e}", file=sys.stderr)
        return None


def save_score(score, checks, total_checks, details):
    """Save the current score to file"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        data = {
            'score': score,
            'checks': checks,
            'total_checks': total_checks,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        with open(SCORE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving score file: {e}", file=sys.stderr)


def run_scan():
    """Run the check.py script and process results"""
    try:
        # Run check.py with --compact flag
        result = subprocess.run(
            ['python3', CHECK_SCRIPT, '--compact'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = result.stdout + result.stderr
        
        # Parse score from output
        score_match = re.search(r'Score:\s*(\d+)/100', output)
        if not score_match:
            send_telegram("⚠️ LobsterGuard — Error!\n\nCould not parse score from check.py output")
            return
        
        current_score = int(score_match.group(1))
        
        # Parse checks from output
        checks_match = re.search(r'(\d+)/(\d+)\s*checks', output)
        if checks_match:
            checks = int(checks_match.group(1))
            total_checks = int(checks_match.group(2))
        else:
            checks = 0
            total_checks = 0
        
        # Collect failing details
        failing_details = []
        for line in output.split('\n'):
            if line.strip().startswith('[FAIL]'):
                # Extract the detail after [FAIL]
                detail = line.replace('[FAIL]', '', 1).strip()
                if detail:
                    failing_details.append(detail)
        
        # Get last score for comparison
        last_score_data = get_last_score()
        
        # First run
        if last_score_data is None:
            message = f"🛡 LobsterGuard Auto-Scan\n\nPrimer escaneo automático registrado.\n\nScore: {current_score}/100 — {checks}/{total_checks} checks\n\nFirst automatic scan recorded."
            send_telegram(message)
            save_score(current_score, checks, total_checks, failing_details)
            return
        
        last_score = last_score_data.get('score', 0)
        
        # Score unchanged
        if current_score == last_score:
            print(f"Score unchanged: {current_score}/100")
            save_score(current_score, checks, total_checks, failing_details)
            return
        
        # Score dropped
        if current_score < last_score:
            details_text = ""
            if failing_details:
                details_text = "\n\nChecks fallidos/Failed checks:\n" + "\n".join(f"• {detail}" for detail in failing_details[:10])
            
            message = f"🔴 LobsterGuard — Score Drop!\n\nAnterior/Previous: {last_score}/100\nActual/Current: {current_score}/100{details_text}"
            send_telegram(message)
            save_score(current_score, checks, total_checks, failing_details)
            return
        
        # Score improved
        if current_score > last_score:
            message = f"🟢 LobsterGuard — Score Improved!\n\nAnterior/Previous: {last_score}/100\nActual/Current: {current_score}/100\n\n¡El sistema ha mejorado! / System has improved!"
            send_telegram(message)
            save_score(current_score, checks, total_checks, failing_details)
            return
            
    except subprocess.TimeoutExpired:
        send_telegram("⚠️ LobsterGuard — Error!\n\ncheck.py timed out (>300s)")
    except Exception as e:
        send_telegram(f"⚠️ LobsterGuard — Error!\n\n{str(e)}")


def main():
    """Main entry point"""
    try:
        run_scan()
    except Exception as e:
        error_msg = f"⚠️ LobsterGuard — Critical Error!\n\n{str(e)}"
        send_telegram(error_msg)
        raise


if __name__ == "__main__":
    main()
