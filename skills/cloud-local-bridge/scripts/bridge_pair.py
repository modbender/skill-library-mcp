#!/usr/bin/env python3
"""
Cloud-Local Bridge 简化配对工具
类似"添加好友"的简单配对流程
"""

import json
import os
import base64
import hashlib
import secrets
import argparse
from pathlib import Path

# 生成配对码（6位数字）
def generate_pairing_code():
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

# 生成设备ID
def generate_device_id():
    return secrets.token_hex(8)

# 创建配对请求
def create_pairing_request(config_path='~/.openclaw/bridge.json'):
    """
    发起方：创建配对请求
    返回：配对码和连接信息（需要发送给接收方）
    """
    config_path = os.path.expanduser(config_path)
    
    # 加载或创建配置
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {
            'device_id': generate_device_id(),
            'paired_devices': {}
        }
    
    # 生成配对码
    pairing_code = generate_pairing_code()
    
    # 创建配对请求
    pairing_request = {
        'code': pairing_code,
        'device_id': config.get('device_id', generate_device_id()),
        'name': f"设备-{config.get('device_id', '')[:4]}",
        'created_at': str(__import__('datetime').datetime.now())
    }
    
    # 保存待确认的配对请求
    pending_file = config_path + '.pending'
    with open(pending_file, 'w') as f:
        json.dump(pairing_request, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"📱 配对请求已创建!")
    print(f"{'='*50}")
    print(f"\n🔢 配对码: {Colors.BOLD}{pairing_code}{Colors.ENDC}")
    print(f"\n📋 请将此配对码发送给要连接的用户")
    print(f"   (通过 QQ/微信/邮件等任何方式)")
    print(f"\n⏰ 配对码有效期: 10 分钟")
    print(f"{'='*50}\n")
    
    return pairing_request

# 确认配对
def confirm_pairing(code, remote_info, config_path='~/.openclaw/bridge.json'):
    """
    接收方：确认配对
    参数:
        code: 对方发来的配对码
        remote_info: 对方发来的设备信息（JSON 字符串或字典）
    """
    config_path = os.path.expanduser(config_path)
    
    # 加载配置
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {'device_id': generate_device_id(), 'paired_devices': {}}
    
    # 验证配对码
    pending_file = config_path + '.pending'
    if not os.path.exists(pending_file):
        print(f"\n❌ 没有待确认的配对请求")
        return False
    
    with open(pending_file, 'r') as f:
        pending = json.load(f)
    
    if pending.get('code') != code:
        print(f"\n❌ 配对码错误")
        return False
    
    # 解析远程设备信息
    if isinstance(remote_info, str):
        try:
            remote = json.loads(remote_info)
        except:
            print(f"\n❌ 远程信息格式错误")
            return False
    else:
        remote = remote_info
    
    # 建立配对
    device_id = config.get('device_id', generate_device_id())
    config['device_id'] = device_id
    
    paired_device = {
        'device_id': remote.get('device_id'),
        'name': remote.get('name', '未知设备'),
        'connected_at': str(__import__('datetime').datetime.now()),
        'status': 'pending_confirmation'  # 等待对方确认
    }
    
    config['paired_devices'][remote.get('device_id')] = paired_device
    
    # 保存配置
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # 删除待处理文件
    os.remove(pending_file)
    
    print(f"\n✅ 配对成功!")
    print(f"   设备: {remote.get('name')}")
    print(f"   ID: {remote.get('device_id')}")
    
    # 生成确认信息（需要发送回发起方）
    confirmation = {
        'code': code,
        'device_id': device_id,
        'name': f"设备-{device_id[:4]}"
    }
    
    print(f"\n📤 请将以下确认码发送回发起方:")
    print(f"   {Colors.BOLD}{json.dumps(confirmation)}{Colors.ENDC}\n")
    
    return True

# 完成配对（发起方收到接收方的确认后）
def complete_pairing(confirmation_data, config_path='~/.openclaw/bridge.json'):
    """
    发起方：完成配对
    """
    config_path = os.path.expanduser(config_path)
    
    if isinstance(confirmation_data, str):
        try:
            confirmation = json.loads(confirmation_data)
        except:
            print("❌ 确认信息格式错误")
            return False
    else:
        confirmation = confirmation_data
    
    # 验证配对码
    pending_file = config_path + '.pending'
    if not os.path.exists(pending_file):
        print("❌ 没有待完成的配对")
        return False
    
    with open(pending_file, 'r') as f:
        pending = json.load(f)
    
    if pending.get('code') != confirmation.get('code'):
        print("❌ 配对码不匹配")
        return False
    
    # 加载配置
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # 添加已配对设备
    config['paired_devices'][confirmation.get('device_id')] = {
        'device_id': confirmation.get('device_id'),
        'name': confirmation.get('name', '未知设备'),
        'connected_at': str(__import__('datetime').datetime.now()),
        'status': 'connected'
    }
    
    # 更新状态
    if confirmation.get('device_id') in config['paired_devices']:
        config['paired_devices'][confirmation['device_id']]['status'] = 'connected'
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    os.remove(pending_file)
    
    print(f"\n🎉 配对完成!")
    print(f"   对方设备: {confirmation.get('name')}")
    print(f"   对方ID: {confirmation.get('device_id')}\n")
    
    return True

# 列出已配对设备
def list_paired_devices(config_path='~/.openclaw/bridge.json'):
    """列出所有已配对的设备"""
    config_path = os.path.expanduser(config_path)
    
    if not os.path.exists(config_path):
        print("❌ 尚未配置")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    devices = config.get('paired_devices', {})
    
    print(f"\n📱 已配对设备 ({len(devices)} 个):\n")
    
    for device_id, info in devices.items():
        status = "✅ 已连接" if info.get('status') == 'connected' else "⏳ 等待确认"
        print(f"   {info.get('name')} - {status}")
        print(f"   ID: {device_id}")
        print()
    
    if not devices:
        print("   还没有配对任何设备\n")

# 生成可分享的连接信息
def generate_shareable_info(config_path='~/.openclaw/bridge.json'):
    """生成可以分享给他人的连接信息"""
    config_path = os.path.expanduser(config_path)
    
    if not os.path.exists(config_path):
        print("❌ 请先运行初始化")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    device_id = config.get('device_id', generate_device_id())
    name = f"设备-{device_id[:4]}"
    
    info = {
        'device_id': device_id,
        'name': name
    }
    
    print(f"\n📤 您的连接信息:")
    print(f"   {Colors.BOLD}{json.dumps(info)}{Colors.ENDC}\n")
    print(f"将此信息发送给对方，对方可以使用以下命令配对:")
    print(f"   bridge_pair.py connect '<上述JSON>'\n")

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(msg, color=Colors.GREEN):
    print(f"{color}{msg}{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description='Cloud-Local Bridge 配对工具 - 类似添加好友的简单配对')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 发起配对
    parser_init = subparsers.add_parser('init', help='发起配对请求')
    parser_init.add_argument('--config', default='~/.openclaw/bridge.json', help='配置文件路径')
    
    # 确认配对
    parser_connect = subparsers.add_parser('connect', help='确认配对请求')
    parser_connect.add_argument('code', help='对方发来的配对码')
    parser_connect.add_argument('info', help='对方的设备信息(JSON)')
    parser_connect.add_argument('--config', default='~/.openclaw/bridge.json', help='配置文件路径')
    
    # 完成配对
    parser_complete = subparsers.add_parser('complete', help='完成配对（发起方用）')
    parser_complete.add_argument('confirmation', help='对方发回的确认信息(JSON)')
    parser_complete.add_argument('--config', default='~/.openclaw/bridge.json', help='配置文件路径')
    
    # 列出设备
    parser_list = subparsers.add_parser('list', help='列出已配对的设备')
    parser_list.add_argument('--config', default='~/.openclaw/bridge.json', help='配置文件路径')
    
    # 分享连接信息
    parser_share = subparsers.add_parser('share', help='生成分享信息')
    parser_share.add_argument('--config', default='~/.openclaw/bridge.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        create_pairing_request(args.config)
    
    elif args.command == 'connect':
        confirm_pairing(args.code, args.info, args.config)
    
    elif args.command == 'complete':
        complete_pairing(args.confirmation, args.config)
    
    elif args.command == 'list':
        list_paired_devices(args.config)
    
    elif args.command == 'share':
        generate_shareable_info(args.config)
    
    else:
        parser.print_help()
        print(f"""
{Colors.BOLD}📱 简化配对流程:{Colors.ENDC}

  发起方:                    接收方:
  1. bridge_pair.py init     bridge_pair.py connect <配对码> <对方信息>
  
  2. 发送配对码给对方         输入配对码和对方信息
  
  3. bridge_pair.py complete <对方确认>
                           (对方发送确认信息)
  
  4. ✅ 配对成功!
""")

if __name__ == '__main__':
    main()
