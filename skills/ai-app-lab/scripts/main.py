#!/usr/bin/env python3
import requests
import sys
import json
from datetime import datetime

def fetch_ai_app_lab_info():
    repo = "volcengine/ai-app-lab"
    
    print("=== AI 应用实验室 (ai-app-lab) 信息 ===")
    print("更新时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        url = "https://api.github.com/repos/" + repo + "/contents/demohouse"
        headers = {"Accept": "application/vnd.github+json"}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n--- demohouse 目录下的项目 ---")
            projects = []
            for item in data:
                if item.get("type") == "dir":
                    projects.append(item.get("name"))
            
            print("项目数量:", len(projects))
            for i, project in enumerate(projects, 1):
                print("%2d. %s" % (i, project))
            
            print("\n✅ 项目详情请访问: https://github.com/" + repo)
            
    except Exception as e:
        print("\n❌ 错误:", e)

if __name__ == "__main__":
    fetch_ai_app_lab_info()
    print("\nℹ️ 项目详细信息请访问: https://github.com/volcengine/ai-app-lab")
