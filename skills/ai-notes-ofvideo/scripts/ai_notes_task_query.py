import os
import sys
import requests
import json


def ai_notes_task_query(api_key: str, task_id: str):
    url = "https://qianfan.baidubce.com/v2/tools/ai_note/query"
    headers = {
        "Authorization": "Bearer %s" % api_key,
        "Content-Type": "application/json"
    }
    params = {
        "task_id": task_id,
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    result = response.json()
    if "code" in result:
        raise RuntimeError(result["detail"])
    if "errno" in result and result["errno"] == 10000:
        print("task status code: %s, message: %s" % (result["errno"], result["show_msg"]))
        return {}
    if "errno" in result and result["errno"] != 0:
            raise RuntimeError(result["show_msg"])
    return result.get("data", {})


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_notes_task_create.py <url>")
        sys.exit(1)

    task_id = sys.argv[1]

    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print("Error: BAIDU_API_KEY  must be set in environment.")
        sys.exit(1)
    try:
        results = ai_notes_task_query(api_key, task_id)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
