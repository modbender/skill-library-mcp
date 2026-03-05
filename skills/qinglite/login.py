import requests
import json
import sys

def qinglite_login(mobile, code):
    url = "https://www.qinglite.cn/api/interface/user/user_mobile/login"
    payload = {
        "mobile": mobile,
        "code": code,
        "prefix": "86",
        "act": 1
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_json = response.json()

        if response_json.get("code") == 20000 and "token" in response_json.get("data", {}):
            token = response_json["data"]["token"]
            print(f"Login successful. Token: {token}")
            return token
        else:
            print(f"Login failed: {response_json.get('msg', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from response: {response.text}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python login.py <mobile> <code>")
        sys.exit(1)
    
    mobile = sys.argv[1]
    code = sys.argv[2]
    qinglite_login(mobile, code)
