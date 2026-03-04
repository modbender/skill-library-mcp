import sys
import datetime
import os

JOURNAL_FILE = 'skills/crypto_trader/logs/analysis_journal.md'

def main():
    if len(sys.argv) < 2:
        print("Usage: python logger.py \"Your analysis text here\"")
        sys.exit(1)

    analysis_text = sys.argv[1]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"""
## Analysis - {timestamp}

{analysis_text}

---
"""
    
    try:
        with open(JOURNAL_FILE, 'a') as f:
            f.write(entry)
        print(f"Analysis saved to {JOURNAL_FILE}")
    except Exception as e:
        print(f"Error writing to journal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
