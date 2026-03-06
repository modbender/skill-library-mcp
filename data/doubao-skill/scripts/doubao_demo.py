#!/usr/bin/env python3
"""
Doubao Demo Script - Doubao API调用实现
支持文生图、文生视频和任务状态查询
"""

import sys
import json
import os
import time
import requests
from datetime import datetime


class DoubaoClient:
    """Doubao API 客户端"""

    def __init__(self):
        self.api_key = os.getenv("ARK_API_KEY")
        if not self.api_key:
            print(json.dumps({
                "status": "error",
                "error": "ARK_API_KEY environment variable not set"
            }))
            sys.exit(1)

        # Volcengine ARK API 端点
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.image_endpoint = f"{self.base_url}/images/generations"
        self.video_endpoint = f"{self.base_url}/videos/generations"
        self.task_endpoint = f"{self.base_url}/tasks"

    def generate_image(self, prompt):
        """生成图片"""
        try:
            response = requests.post(
                self.image_endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "doubao-seedream-3-0-t2i-250415",
                    "prompt": prompt,
                    "n": 1
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    return {
                        "status": "success",
                        "image_url": data["data"][0]["url"],
                        "prompt": prompt
                    }
                else:
                    return {
                        "status": "error",
                        "error": "No image generated"
                    }
            else:
                return {
                    "status": "error",
                    "error": f"API Error: {response.status_code} - {response.text}"
                }

        except requests.Timeout:
            return {
                "status": "error",
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def generate_video(self, prompt, sync_mode="async"):
        """生成视频"""
        try:
            response = requests.post(
                self.video_endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "duration": 5
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()

                if "data" in data and "id" in data["data"]:
                    task_id = data["data"]["id"]

                    if sync_mode == "sync":
                        # 同步模式：等待完成
                        return self._wait_for_task(task_id)
                    else:
                        # 异步模式：立即返回任务ID
                        return {
                            "status": "success",
                            "task_id": task_id,
                            "prompt": prompt
                        }
                else:
                    return {
                        "status": "error",
                        "error": "No task ID returned"
                    }
            else:
                return {
                    "status": "error",
                    "error": f"API Error: {response.status_code} - {response.text}"
                }

        except requests.Timeout:
            return {
                "status": "error",
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def check_status(self, task_id):
        """检查任务状态"""
        try:
            response = requests.get(
                f"{self.task_endpoint}/{task_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                if "data" in data:
                    task_data = data["data"]
                    status = task_data.get("status", "unknown")

                    if status == "succeeded":
                        return {
                            "status": "succeeded",
                            "result_url": task_data.get("result", {}).get("url"),
                            "progress": 100,
                            "task_id": task_id
                        }
                    elif status == "failed":
                        return {
                            "status": "failed",
                            "error": task_data.get("error", "Unknown error"),
                            "task_id": task_id
                        }
                    elif status in ["running", "pending", "processing"]:
                        return {
                            "status": "running",
                            "progress": task_data.get("progress", 0),
                            "task_id": task_id
                        }
                    else:
                        return {
                            "status": status,
                            "task_id": task_id
                        }
                else:
                    return {
                        "status": "error",
                        "error": "No task data returned"
                    }
            else:
                return {
                    "status": "error",
                    "error": f"API Error: {response.status_code} - {response.text}"
                }

        except requests.Timeout:
            return {
                "status": "error",
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _wait_for_task(self, task_id, max_wait_time=600, check_interval=10):
        """等待任务完成"""
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            result = self.check_status(task_id)

            if result["status"] == "succeeded":
                return result
            elif result["status"] == "failed":
                return {
                    "status": "error",
                    "error": result.get("error", "Task failed")
                }

            time.sleep(check_interval)

        return {
            "status": "error",
            "error": "Task timeout (max wait time exceeded)"
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error",
            "error": "Usage: python doubao_demo.py <action> [args...]"
        }))
        sys.exit(1)

    action = sys.argv[1]
    client = DoubaoClient()

    result = None

    if action == "img":
        if len(sys.argv) < 3:
            print(json.dumps({
                "status": "error",
                "error": "Missing prompt argument for img action"
            }))
            sys.exit(1)

        prompt = sys.argv[2]
        result = client.generate_image(prompt)

    elif action == "vid":
        if len(sys.argv) < 3:
            print(json.dumps({
                "status": "error",
                "error": "Missing prompt argument for vid action"
            }))
            sys.exit(1)

        prompt = sys.argv[2]
        sync_mode = sys.argv[3] if len(sys.argv) > 3 else "async"
        result = client.generate_video(prompt, sync_mode)

    elif action == "status":
        if len(sys.argv) < 3:
            print(json.dumps({
                "status": "error",
                "error": "Missing task_id argument for status action"
            }))
            sys.exit(1)

        task_id = sys.argv[2]
        result = client.check_status(task_id)

    else:
        print(json.dumps({
            "status": "error",
            "error": f"Unknown action: {action}. Supported: img, vid, status"
        }))
        sys.exit(1)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
