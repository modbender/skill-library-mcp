#!/usr/bin/env python3
"""
火山引擎余额查询脚本
从 OpenClaw 配置或环境变量读取 AK/SK，查询余额信息
"""

import os
import sys
import json
import argparse
from pathlib import Path

def get_config_path():
    """获取 OpenClaw 配置文件路径"""
    home = Path.home()
    config_paths = [
        home / ".openclaw" / "openclaw.json",
        home / ".openclaw" / "clawdbot.json",
    ]
    
    for path in config_paths:
        if path.exists():
            return path
    return None

def get_credentials_from_config():
    """从 OpenClaw 配置中获取火山引擎凭证"""
    config_path = get_config_path()
    if not config_path:
        return None, None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 尝试从 env 配置获取
        if 'env' in config:
            env_config = config['env']
            access_key = env_config.get('VOLCENGINE_ACCESS_KEY')
            secret_key = env_config.get('VOLCENGINE_SECRET_KEY')
            if access_key and secret_key:
                return access_key, secret_key
        
    except Exception:
        pass
    
    return None, None

def get_credentials():
    """获取火山引擎凭证，优先从环境变量，然后从配置"""
    # 1. 从环境变量获取
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    
    if access_key and secret_key:
        return access_key, secret_key
    
    # 2. 从 OpenClaw 配置获取
    return get_credentials_from_config()

def query_balance(access_key, secret_key):
    """查询火山引擎余额"""
    try:
        import volcenginesdkbilling
        import volcenginesdkcore
        from volcenginesdkcore.rest import ApiException
    except ImportError:
        return None
    
    try:
        configuration = volcenginesdkcore.Configuration()
        configuration.ak = access_key
        configuration.sk = secret_key
        configuration.region = "cn-beijing"
        
        api_client = volcenginesdkcore.ApiClient(configuration)
        api_instance = volcenginesdkbilling.BILLINGApi(api_client)
        request = volcenginesdkbilling.QueryBalanceAcctRequest()
        response = api_instance.query_balance_acct(request)
        
        return response
        
    except Exception:
        return None

def format_balance(response, quiet=False):
    """格式化余额响应"""
    if not response:
        return "无法获取余额信息"
    
    if hasattr(response, 'to_dict'):
        result = response.to_dict()
    elif isinstance(response, dict):
        result = response
    else:
        result = response

    def get_val(obj, key):
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key, None)
    
    if quiet:
        # 简洁输出，适合嵌入到 balance-checker
        lines = []
        if get_val(result, 'available_balance') is not None:
            lines.append(f"- 可用余额: {get_val(result, 'available_balance')} CNY")
        if get_val(result, 'cash_balance') is not None:
            lines.append(f"- 现金余额: {get_val(result, 'cash_balance')} CNY")
        if get_val(result, 'freeze_amount') is not None and float(get_val(result, 'freeze_amount') or 0) > 0:
            lines.append(f"- 冻结金额: {get_val(result, 'freeze_amount')} CNY")
        return "\n".join(lines)
    
    # 完整输出
    output_lines = []
    output_lines.append("💰 火山引擎余额")
    output_lines.append("=" * 30)
    
    balance_info = []
    if get_val(result, 'available_balance') is not None:
        balance_info.append(("可用余额", f"{get_val(result, 'available_balance')} CNY"))
    if get_val(result, 'cash_balance') is not None:
        balance_info.append(("现金余额", f"{get_val(result, 'cash_balance')} CNY"))
    if get_val(result, 'freeze_amount') is not None:
        balance_info.append(("冻结金额", f"{get_val(result, 'freeze_amount')} CNY"))
    if get_val(result, 'credit_limit') is not None:
        balance_info.append(("信控额度", f"{get_val(result, 'credit_limit')} CNY"))
    if get_val(result, 'arrears_balance') is not None:
        balance_info.append(("欠费金额", f"{get_val(result, 'arrears_balance')} CNY"))
    
    max_label_len = max(len(label) for label, _ in balance_info) if balance_info else 0
    for label, value in balance_info:
        padding = " " * (max_label_len - len(label))
        output_lines.append(f"{label}:{padding} {value}")
    
    output_lines.append("")
    output_lines.append("💡 可用余额 = (现金余额 - 冻结金额) + 信控额度 - 欠费金额")
    
    return "\n".join(output_lines)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='查询火山引擎余额')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    parser.add_argument('--quiet', '-q', action='store_true', help='简洁输出（用于嵌入其他脚本）')
    args = parser.parse_args()
    
    if not args.quiet:
        print("火山引擎余额查询工具")
        print("=" * 50)
    
    access_key, secret_key = get_credentials()
    
    if not access_key or not secret_key:
        if args.quiet:
            print("- 查询失败: AK/SK 未配置")
        else:
            print("\n错误: 无法获取火山引擎凭证")
            print("\n配置方法:")
            print("1. 设置环境变量:")
            print("   export VOLCENGINE_ACCESS_KEY=你的AccessKey ID")
            print("   export VOLCENGINE_SECRET_KEY=你的AccessKey Secret")
            print("\n2. 或在 OpenClaw 配置文件 env 中添加")
            print("\n获取 AK/SK: https://console.volcengine.com/iam/keymanage/")
        sys.exit(1)
    
    if args.verbose:
        print(f"使用 AccessKey: {access_key[:8]}...")
    
    if not args.quiet:
        print("正在查询...")
    
    response = query_balance(access_key, secret_key)
    
    if response:
        formatted = format_balance(response, quiet=args.quiet)
        if args.quiet:
            print(formatted)
        else:
            print("\n" + formatted)
        
        if args.verbose:
            print("\n" + "=" * 50)
            print("原始响应:")
            print(response)
    else:
        if args.quiet:
            print("- 查询失败")
        else:
            print("\n查询失败，请检查网络连接和凭证是否正确")
        sys.exit(1)

if __name__ == "__main__":
    main()
