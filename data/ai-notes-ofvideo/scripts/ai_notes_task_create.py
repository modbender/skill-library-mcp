#!/usr/bin/env python3
"""
AI Video Notes - Create Task
Submit a video URL for AI note generation.
"""

import os
import sys
import json
import requests
from typing import Dict, Any


def create_note_task(api_key: str, video_url: str) -> Dict[str, Any]:
    """Create an AI note generation task.

    Args:
        api_key: Baidu API key
        video_url: Public video URL

    Returns:
        Task data with task_id

    Raises:
        RuntimeError: If API returns error
    """
    url = "https://qianfan.baidubce.com/v2/tools/ai_note/task_create"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Appbuilder-From": "openclaw",
        "Content-Type": "application/json"
    }
    data = {"url": video_url}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "code" in result:
            raise RuntimeError(result.get("detail", "API error"))
        if "errno" in result and result["errno"] != 0:
            raise RuntimeError(result.get("errmsg", "Unknown error"))

        return result["data"]

    except requests.exceptions.Timeout:
        raise RuntimeError("Request timeout. Video URL may be inaccessible.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {str(e)}")


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Missing video URL",
            "usage": "python ai_notes_task_create.py <video_url>"
        }, indent=2))
        sys.exit(1)

    video_url = sys.argv[1]
    api_key = os.getenv("BAIDU_API_KEY")

    if not api_key:
        print(json.dumps({
            "error": "BAIDU_API_KEY environment variable not set"
        }, indent=2))
        sys.exit(1)

    try:
        task_data = create_note_task(api_key, video_url)
        print(json.dumps({
            "status": "success",
            "message": "Task created successfully",
            "task_id": task_data.get("task_id"),
            "next_step": f"Query task status: python ai_notes_task_query.py {task_data.get('task_id')}"
        }, indent=2))

    except RuntimeError as e:
        print(json.dumps({
            "status": "error",
            "error": str(e)
        }, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
