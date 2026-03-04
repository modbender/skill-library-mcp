#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装验证脚本
检查环境、依赖、配置
"""

import sys
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"  ❌ Python版本过低: {version.major}.{version.minor}")
        print(f"  需要Python 3.8+")
        return False
    
    print(f"  ✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """检查依赖库"""
    print("\n检查依赖库...")
    
    required = ['feedparser', 'requests', 'yaml']
    all_installed = True
    
    for dep in required:
        try:
            __import__(dep)
            print(f"  ✅ {dep} 已安装")
        except ImportError:
            print(f"  ❌ {dep} 未安装")
            all_installed = False
    
    if not all_installed:
        print("\n  运行以下命令安装依赖：")
        print("  pip install feedparser requests pyyaml")
    
    return all_installed

def check_config_file():
    """检查配置文件"""
    print("\n检查配置文件...")
    
    config_file = PROJECT_ROOT / 'config.yaml'
    example_file = PROJECT_ROOT / 'config.yaml.example'
    
    if config_file.exists():
        print(f"  ✅ config.yaml 存在")
        return True
    else:
        if example_file.exists():
            print(f"  ⚠️  config.yaml 不存在")
            print(f"  请复制 config.yaml.example 并修改：")
            print(f"  cp config.yaml.example config.yaml")
        else:
            print(f"  ❌ config.yaml.example 不存在")
        return False

def check_api_key():
    """检查API Key配置"""
    print("\n检查API Key配置...")
    
    try:
        import yaml
        config_file = PROJECT_ROOT / 'config.yaml'
        
        if not config_file.exists():
            print(f"  ⚠️  配置文件不存在")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        api_key = config.get('api', {}).get('api_key', '')
        
        if api_key == 'YOUR_API_KEY_HERE' or not api_key:
            print(f"  ⚠️  API Key未配置")
            print(f"  请在config.yaml中设置api_key")
            return False
        else:
            # 检查API Key格式（简单验证）
            if len(api_key) < 10:
                print(f"  ⚠️  API Key格式可能不正确")
                return False
            print(f"  ✅ API Key已配置")
            return True
    
    except Exception as e:
        print(f"  ❌ 配置读取失败: {e}")
        return False

def check_network():
    """检查网络连接"""
    print("\n检查网络连接...")
    
    try:
        import requests
        response = requests.get('https://www.google.com', timeout=5)
        if response.status_code == 200:
            print(f"  ✅ 网络连接正常")
            return True
    except:
        pass
    
    try:
        import requests
        response = requests.get('https://www.baidu.com', timeout=5)
        if response.status_code == 200:
            print(f"  ✅ 网络连接正常（国内）")
            return True
    except:
        print(f"  ❌ 网络连接失败")
        print(f"  请检查网络设置")
        return False
    
    return False

def main():
    """主函数"""
    print("=" * 50)
    print("literature-report 安装验证")
    print("=" * 50)
    
    results = {
        'Python版本': check_python_version(),
        '依赖库': check_dependencies(),
        '配置文件': check_config_file(),
        'API Key': check_api_key(),
        '网络连接': check_network(),
    }
    
    print("\n" + "=" * 50)
    print("验证结果：")
    print("=" * 50)
    
    all_passed = True
    for item, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {item}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n🎉 所有检查通过！系统已准备就绪。")
        print("\n下一步：")
        print("  python3 scripts/fetch_papers.py")
    else:
        print("\n⚠️  部分检查未通过，请按上述提示修复。")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)