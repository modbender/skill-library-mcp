import os
import time
import jwt
import requests

class KlingAPI:
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = "https://api.kling.ai"

    def _get_token(self):
        payload = {
            "exp": int(time.time()) + 3600,  # Token valid for 1 hour
            "nbf": int(time.time()) - 5,
            "iat": int(time.time()) - 10,
            "iss": self.access_key,
            "jti": f"idt{int(time.time() * 1000)}"
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token

    def _make_request(self, endpoint, method="POST", json_data=None):
        headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data)
            else:
                response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if e.response is not None:
                print(f"Response content: {e.response.text}")
            return None

    def create_omni_video_task(self, payload):
        """Creates a video generation task using the omni-video endpoint."""
        return self._make_request("/v1/videos/omni-video", method="POST", json_data=payload)

    def get_task_status(self, task_id):
        """Retrieves the status of a specific task."""
        return self._make_request(f"/v1/videos/{task_id}", method="GET")

    def poll_for_completion(self, task_id, timeout=600, interval=15):
        """Polls for task completion and returns the final result."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status_response = self.get_task_status(task_id)
            if status_response and status_response.get("code") == 0:
                task_data = status_response.get("data", {})
                state = task_data.get("state")
                print(f"Task {task_id} state: {state}")
                if state == "completed":
                    return task_data
                elif state in ["failed", "cancelled"]:
                    print(f"Task {task_id} failed or was cancelled.")
                    return task_data
            else:
                print(f"Failed to get status for task {task_id}.")
            time.sleep(interval)
        print(f"Polling timed out for task {task_id}.")
        return None

if __name__ == '__main__':
    # Example usage:
    access_key = os.environ.get("KLING_ACCESS_KEY")
    secret_key = os.environ.get("KLING_SECRET_KEY")

    if not access_key or not secret_key:
        print("Please set KLING_ACCESS_KEY and KLING_SECRET_KEY environment variables.")
    else:
        api = KlingAPI(access_key, secret_key)

        # Example 1: Text-to-Video
        payload = {
            "model_name": "kling-v3-omni",
            "prompt": "A beautiful sunset over the ocean, cinematic, 8k, high detail",
            "aspect_ratio": "16:9",
            "duration": "5"
        }
        task_response = api.create_omni_video_task(payload)
        if task_response and task_response.get("code") == 0:
            task_id = task_response.get("data", {}).get("task_id")
            print(f"Task created successfully: {task_id}")
            result = api.poll_for_completion(task_id)
            if result:
                print("Final result:", result)
        else:
            print("Failed to create task.")
