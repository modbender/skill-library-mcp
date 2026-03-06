#!/usr/bin/env python3
"""
AI Picture Book - Poll Task
Automatically poll task until completion with progress updates.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any

STATUS_CODES = {
    0: "in_progress",
    1: "in_progress",
    2: "completed",
    3: "in_progress",
}


def query_task(api_key: str, task_id: str) -> Dict[str, Any]:
    """Query task status."""
    url = "https://qianfan.baidubce.com/v2/tools/ai_picture_book/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }
    params = {"task_ids": [task_id]}

    response = requests.post(url, headers=headers, json=params, timeout=5)
    response.raise_for_status()
    result = response.json()

    if "errno" in result and result["errno"] != 0:
        raise RuntimeError(result.get("errmsg", "Unknown error"))

    return result["data"]


def poll_task(api_key: str, task_id: str, max_attempts: int = 20, interval: int = 5):
    """Poll task until completion or timeout.

    Args:
        api_key: Baidu API key
        task_id: Task ID
        max_attempts: Maximum poll attempts (default 20)
        interval: Seconds between polls (default 5)

    Returns:
        Final task data
    """
    data = None
    for attempt in range(max_attempts):
        try:
            data = query_task(api_key, task_id)
            if not data or len(data) == 0:
                print(f"\n✗ No task data returned")
                return data

            status = data[0].get("status")
            result = data[0].get("result", {})
            if result and "video_bos_url" in result:
                result = {"video_bos_url": result["video_bos_url"]}

            if status == 2:
                print("\n" + "=" * 50)
                print("✓ PICTURE BOOK GENERATED SUCCESSFULLY")
                print("=" * 50)
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return data

            elif status in [0, 1, 3]:
                print(f"[{attempt + 1}/{max_attempts}] Processing...")
                time.sleep(interval)

            else:
                print(f"\n✗ Task failed: status={status}")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return data

        except RuntimeError as e:
            print(f"\n✗ Error: {str(e)}")
            return data
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"\n✗ Unexpected error: {str(e)}")
                return data
            time.sleep(interval)

    print(f"\n✗ Timeout after {max_attempts * interval} seconds")
    print("Task may still be running. Try querying manually:")
    print(f"  python scripts/ai_picture_book_task_query.py {task_id}")
    return data


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Missing task ID",
            "usage": "python ai_picture_book_poll.py <task_id> [max_attempts] [interval_seconds]"
        }, indent=2))
        sys.exit(1)

    task_id = sys.argv[1]
    max_attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    interval = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print(json.dumps({
            "error": "BAIDU_API_KEY environment variable not set"
        }, indent=2))
        sys.exit(1)

    print(f"Polling task: {task_id}")
    print(f"Max attempts: {max_attempts}, Interval: {interval}s")
    print("-" * 50)

    poll_task(api_key, task_id, max_attempts, interval)


if __name__ == "__main__":
    main()
