#!/usr/bin/env python3
"""
Save a transcript result to the local library.
Usage: save_transcript.py <video_id> <json_data>
"""

import sys
import json
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent
TRANSCRIPTS_DIR = SKILL_DIR / "transcripts"
TRANSCRIPTS_DIR.mkdir(exist_ok=True)


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: save_transcript.py <video_id> <json_data>"}))
        sys.exit(1)

    video_id = sys.argv[1]
    raw = sys.argv[2]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON data"}))
        sys.exit(1)

    data["saved_at"] = datetime.now().isoformat()
    cache_file = TRANSCRIPTS_DIR / f"{video_id}.json"

    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)

    print(json.dumps({"saved": True, "path": str(cache_file)}))


if __name__ == "__main__":
    main()
