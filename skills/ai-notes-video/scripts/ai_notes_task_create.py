import os
import sys
import requests
import json


def ai_notes_task_create(api_key: str, video_url):
    url = "https://qianfan.baidubce.com/v2/tools/ai_note/task_create"
    headers = {
        "Authorization": "Bearer %s" % api_key,
        "Content-Type": "application/json"
    }
    params = {
        "url": video_url,
    }
    response = requests.post(url, headers=headers, json=params)
    response.raise_for_status()
    result = response.json()
    if "code" in result:
        raise RuntimeError(result["detail"])
    if "errno" in result and result["errno"] != 0:
        raise RuntimeError(result["errmsg"])
    return result["data"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_notes_task_create.py <url>")
        sys.exit(1)

    video_url = sys.argv[1]

    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print("Error: BAIDU_API_KEY  must be set in environment.")
        sys.exit(1)
    try:
        results = ai_notes_task_create(api_key, video_url)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
