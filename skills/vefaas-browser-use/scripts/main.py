#!/usr/bin/env python3
import requests
import sys
from datetime import datetime

def fetch_vefaas_info():
    repo = "volcengine/ai-app-lab"
    path = "demohouse/vefaas-browser-use"
    
    print("=== veFaas 浏览器使用智能体信息 ===")
    print("更新时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # 获取 README
        print("\n--- 项目描述 ---")
        readme = fetch_file_from_github(repo, path + "/README.md")
        if readme:
            lines = readme.splitlines()
            count = 0
            for line in lines:
                if line.strip() and count < 20:
                    print(line)
                    count += 1
        
        # 获取 requirements
        print("\n--- 依赖包 ---")
        requirements = fetch_file_from_github(repo, path + "/requirements.txt")
        if requirements:
            print(requirements.strip())
            
    except Exception as e:
        print("\n❌ 错误:", e)

def fetch_file_from_github(repo, file_path, branch="main"):
    url = "https://github.com/" + repo + "/raw/" + branch + "/" + file_path
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print("获取", file_path, "失败:", e)
    return None

if __name__ == "__main__":
    fetch_vefaas_info()
    print("\nℹ️ 项目详细信息请访问: https://github.com/volcengine/ai-app-lab/tree/main/demohouse/vefaas-browser-use")
