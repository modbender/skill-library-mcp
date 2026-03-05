#!/usr/bin/env python3
"""
Joplin 连接测试

用法: python3 joplin_ping.py
"""
import sys
import requests
from joplin_config import get_base_url, check_config

def ping():
    """测试 Joplin API 连接"""
    # 检查配置
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        return False
    
    base_url = get_base_url()
    
    try:
        # 根据官方文档：GET /ping 测试服务是否可用
        url = f"{base_url}/ping"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            result = response.text.strip()
            if result == 'JoplinClipperServer':
                print("✅ 连接成功!")
                print(f"   服务器：{base_url}")
                print(f"   响应：{result}")
                return True
            else:
                print(f"⚠️  连接成功但响应异常：{result}")
                return True
        else:
            print(f"❌ 连接失败：HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 Joplin 服务器")
        print(f"   地址：{base_url}")
        print(f"\n请检查:")
        print(f"   1. Joplin 桌面版是否运行")
        print(f"   2. Web Clipper 服务是否启用")
        print(f"   3. 主机地址和端口是否正确")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    success = ping()
    sys.exit(0 if success else 1)
